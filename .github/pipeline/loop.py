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


def take(repo: dict, issue: dict, cfg: dict) -> tuple[Path, str]:
    """Make the issue's worktree, mark the issue as taken, and return the worktree and the builder's prompt.

    Nothing may be left half done: the prompt is filled in first, the worktree is made second, the label comes
    last and must be confirmed by GitHub. If the label does not stick, the worktree is removed again, so the
    issue keeps 'ready' alone and the next run can try once more."""
    slug, live, n = repo["slug"], Path(repo["path"]), issue["number"]
    tree = Path(cfg["worktrees"]) / slug.split("/")[1] / f"issue-{n}"
    prompt = (HERE / "loop-prompt.md").read_text(encoding="utf-8").format(
        number=n, slug=slug, title=issue["title"], pipeline=HERE.as_posix(), tree=tree.as_posix())
    run(["git", "worktree", "add", str(tree), "-B", f"issue-{n}", "origin/main"], cwd=live)
    try:
        labels = api(f"repos/{slug}/issues/{n}/labels", "POST", {"labels": ["in-progress"]})
        if not any(l.get("name") == "in-progress" for l in labels or []):
            raise Failed(f"GitHub did not confirm the 'in-progress' label on {slug}#{n}")
    except Failed:
        run(["git", "worktree", "remove", "--force", str(tree)], cwd=live, check=False)
        raise
    return tree, prompt


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
        for issue in ready_issues(repo["slug"]):
            if a.dry_run:
                log(f"would build {repo['slug']}#{issue['number']}: {issue['title']}")
                continue
            try:
                if a.next:
                    tree, prompt = take(repo, issue, cfg)
                    log(f"{repo['slug']}#{issue['number']}: handed to the calling session, worktree {tree}", quiet=True)
                    print(prompt)
                    return 0        # one issue per session
                build(repo, issue, cfg)
            except Failed as e:
                log(f"{repo['slug']}#{issue['number']}: {e}", quiet=a.next)
    return 0


if __name__ == "__main__":
    main(cli)
