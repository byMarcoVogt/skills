"""The scheduled sweep on this machine: bring the skills up to date, then build the issues marked ready.

    python loop.py --next       take the next ready issue and print its builder's instructions (app sessions)
    python loop.py              build every ready issue with a command-line builder (the Windows task)
    python loop.py --dry-run    show what it would build, start nothing

Only an open issue with the label 'ready' is built, and only once: the loop moves it to 'in-progress' before
the builder starts. Each issue gets a fresh Claude session in its own worktree. Everything is logged to
~/.claude/skill-pipeline/.

With --next the builder is the session that called it: a scheduled task in the Claude app runs this command and
follows what it prints, or ends when it prints nothing. Without it, the script starts a command-line builder
itself, and an error there gives the issue the label 'needs-you' and a comment.
"""
import argparse
import contextlib
import datetime
import subprocess
import sys
from pathlib import Path

from common import NO_WINDOW, Failed, api, config, main, paged, run
from sync import sync

HERE = Path(__file__).resolve().parent
LOGS = Path.home() / ".claude" / "skill-pipeline"
LABELS = {"ready": ("0e8a16", "The loop may build this"), "in-progress": ("fbca04", "A builder is on it"),
          "needs-you": ("d93f0b", "Waiting for the owner"), "owner-approved": ("5319e7", "The owner allows a change of the pipeline files")}


def log(text: str, quiet: bool = False) -> None:
    """quiet: write to the log file only. With --next, what is printed is the builder's instructions."""
    LOGS.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {text}"
    if not quiet:
        print(line)
    with open(LOGS / "loop.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ready_issues(slug: str) -> list[dict]:
    """The filter: open, labelled ready, not a pull request, not already taken."""
    issues = paged(f"repos/{slug}/issues?state=open&labels=ready")
    return [i for i in issues if "pull_request" not in i
            and not {"in-progress", "needs-you"} & {l["name"] for l in i["labels"]}]


def clear_leftover(tree: Path, live: Path) -> None:
    """A folder left by an earlier try must not block this one. It is removed only when it holds no work:
    no changed files and no commit that is not on main."""
    run(["git", "worktree", "prune"], cwd=live, check=False)
    if not tree.exists():
        return
    dirty = run(["git", "status", "--porcelain"], cwd=tree, check=False).strip()
    ahead = run(["git", "rev-list", "--count", "origin/main..HEAD"], cwd=tree, check=False).strip()
    if dirty or ahead != "0":
        raise Failed(f"{tree} is left from an earlier try and holds work; it was not touched")
    run(["git", "worktree", "remove", "--force", str(tree)], cwd=live)


def claim(slug: str, n: int) -> bool:
    """Put 'in-progress' on the issue and say whether it is really there. If the answer got lost on the way,
    GitHub is asked again before anything is concluded."""
    path = f"repos/{slug}/issues/{n}/labels"
    try:
        labels = api(path, "POST", {"labels": ["in-progress"]})
    except Exception:
        try:
            labels = api(path)
        except Exception:
            return False
    return isinstance(labels, list) and any(isinstance(l, dict) and l.get("name") == "in-progress" for l in labels)


def take(repo: dict, issue: dict, cfg: dict) -> tuple[Path, str]:
    """Make the issue's worktree, mark the issue as taken, and return the worktree and the builder's prompt.

    Nothing may be left half done: the prompt is filled in first, a leftover folder without work is cleared,
    the worktree is made, and the label comes last and must be confirmed by GitHub. If it is not, the worktree
    is removed again, so the issue keeps 'ready' alone and the next run can try once more."""
    slug, live, n = repo["slug"], Path(repo["path"]), issue["number"]
    tree = Path(cfg["worktrees"]) / slug.split("/")[1] / f"issue-{n}"
    prompt = (HERE / "loop-prompt.md").read_text(encoding="utf-8").format(
        number=n, slug=slug, pipeline=HERE.as_posix(), tree=tree.as_posix())
    clear_leftover(tree, live)
    run(["git", "worktree", "add", str(tree), "-B", f"issue-{n}", "origin/main"], cwd=live)
    if not claim(slug, n):
        try:
            run(["git", "worktree", "remove", "--force", str(tree)], cwd=live)
        except Failed as e:
            log(f"{slug}#{n}: could not remove {tree} after a failed claim: {e}", quiet=True)
        raise Failed(f"GitHub did not confirm the 'in-progress' label on {slug}#{n}")
    return tree, prompt


def stale(issues: list[dict], now: datetime.datetime, hours: int = 24) -> list[dict]:
    """Taken, but nothing has happened on the issue for a day: its builder is most likely gone."""
    out = []
    for i in issues:
        names = {l["name"] for l in i.get("labels", [])}
        if "pull_request" in i or "in-progress" not in names or "needs-you" in names:
            continue
        seen = datetime.datetime.fromisoformat(i["updated_at"].replace("Z", "+00:00"))
        if now - seen > datetime.timedelta(hours=hours):
            out.append(i)
    return out


def flag_stale(slug: str) -> None:
    """Silence must mean it works: an issue that sits as taken with no sign of life gets 'needs-you'."""
    now = datetime.datetime.now(datetime.timezone.utc)
    for i in stale(paged(f"repos/{slug}/issues?state=open&labels=in-progress"), now):
        n = i["number"]
        api(f"repos/{slug}/issues/{n}/labels", "POST", {"labels": ["needs-you"]})
        api(f"repos/{slug}/issues/{n}/comments", "POST", {"body":
            "This issue has been marked as taken for more than a day and nothing has happened on it since. "
            "Its builder has most likely stopped. To have it built again, remove the labels `in-progress` and "
            "`needs-you`."})
        log(f"{slug}#{n}: taken for over a day with no activity, flagged for the owner", quiet=True)


def build(repo: dict, issue: dict, cfg: dict) -> None:
    slug, n = repo["slug"], issue["number"]
    tree, prompt = take(repo, issue, cfg)
    out = LOGS / f"{slug.split('/')[1]}-issue-{n}.log"
    log(f"{slug}#{n}: builder starts in {tree}")
    with open(out, "a", encoding="utf-8") as f:
        code = subprocess.run(["claude", "-p", prompt, "--permission-mode", "acceptEdits", "--allowedTools",
                               "Bash,PowerShell,Read,Edit,Write,Glob,Grep,Agent,Skill"],
                              cwd=tree, stdout=f, stderr=subprocess.STDOUT, creationflags=NO_WINDOW).returncode
    log(f"{slug}#{n}: builder ended with code {code}")
    if code:
        api(f"repos/{slug}/issues/{n}/labels", "POST", {"labels": ["needs-you"]})
        api(f"repos/{slug}/issues/{n}/comments", "POST",
            {"body": f"The builder stopped with an error (code {code}). Its log is `{out}` on the build machine."})


def cli() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--next", action="store_true", help="take one ready issue and print its builder's instructions")
    mode.add_argument("--labels", action="store_true", help="create the pipeline's labels in every repo, then stop")
    a = ap.parse_args()
    if a.next and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")     # before anything is taken: an issue title may hold any character
    cfg = config()

    if a.labels:
        for repo in cfg["repos"]:
            have = {l["name"] for l in paged(f"repos/{repo['slug']}/labels")}
            for name, (color, text) in LABELS.items():
                if name not in have:
                    api(f"repos/{repo['slug']}/labels", "POST", {"name": name, "color": color, "description": text})
                    print(f"{repo['slug']}: label {name}")
        return 0

    with contextlib.redirect_stdout(sys.stderr if a.next else sys.stdout):   # --next prints only the instructions
        problems = sync()
    for problem in problems:
        log(f"needs attention: {problem}", quiet=a.next)
    for repo in cfg["repos"]:
        if not a.dry_run:
            try:
                flag_stale(repo["slug"])
            except Failed as e:
                log(f"{repo['slug']}: could not check for stale issues: {e}", quiet=a.next)
        for issue in ready_issues(repo["slug"]):
            if a.dry_run:
                log(f"would build {repo['slug']}#{issue['number']}: {issue['title']}")
                continue
            try:
                if a.next:
                    tree, prompt = take(repo, issue, cfg)
                    print(prompt, flush=True)       # first: once the issue is taken, the prompt must get out
                    try:
                        log(f"{repo['slug']}#{issue['number']}: handed to the calling session, worktree {tree}",
                            quiet=True)
                    except OSError:
                        pass
                    return 0        # one issue per session
                build(repo, issue, cfg)
            except Failed as e:
                log(f"{repo['slug']}#{issue['number']}: {e}", quiet=a.next)
    return 0


if __name__ == "__main__":
    main(cli)
