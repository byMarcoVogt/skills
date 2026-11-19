"""The scheduled sweep on this machine: bring the skills up to date, then build the issues marked ready.

    python loop.py              what the scheduled task runs
    python loop.py --dry-run    show what it would build, start nothing

Only an open issue with the label 'ready' is built, and only once: the loop moves it to 'in-progress' before
the builder starts. Each issue gets a fresh Claude session in its own worktree. If the builder ends with an
error, the issue gets the label 'needs-you' and a comment. Everything is logged to ~/.claude/skill-pipeline/.
"""
import argparse
import datetime
import subprocess
from pathlib import Path

from common import NO_WINDOW, Failed, api, config, main, paged, run
from sync import sync

HERE = Path(__file__).resolve().parent
LOGS = Path.home() / ".claude" / "skill-pipeline"
LABELS = {"ready": ("0e8a16", "The loop may build this"), "in-progress": ("fbca04", "A builder is on it"),
          "needs-you": ("d93f0b", "Waiting for the owner"), "owner-approved": ("5319e7", "The owner allows a change of the pipeline files")}


def log(text: str) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {text}"
    print(line)
    with open(LOGS / "loop.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ready_issues(slug: str) -> list[dict]:
    """The filter: open, labelled ready, not a pull request, not already taken."""
    issues = paged(f"repos/{slug}/issues?state=open&labels=ready")
    return [i for i in issues if "pull_request" not in i
            and not {"in-progress", "needs-you"} & {l["name"] for l in i["labels"]}]


def build(repo: dict, issue: dict, cfg: dict) -> None:
    slug, live, n = repo["slug"], Path(repo["path"]), issue["number"]
    tree = Path(cfg["worktrees"]) / slug.split("/")[1] / f"issue-{n}"
    api(f"repos/{slug}/issues/{n}/labels", "POST", {"labels": ["in-progress"]})
    run(["git", "worktree", "add", str(tree), "-B", f"issue-{n}", "origin/main"], cwd=live)
    prompt = (HERE / "loop-prompt.md").read_text(encoding="utf-8").format(
        number=n, slug=slug, title=issue["title"], pipeline=HERE.as_posix())
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
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--labels", action="store_true", help="create the pipeline's labels in every repo, then stop")
    a = ap.parse_args()
    cfg = config()

    if a.labels:
        for repo in cfg["repos"]:
            have = {l["name"] for l in paged(f"repos/{repo['slug']}/labels")}
            for name, (color, text) in LABELS.items():
                if name not in have:
                    api(f"repos/{repo['slug']}/labels", "POST", {"name": name, "color": color, "description": text})
                    print(f"{repo['slug']}: label {name}")
        return 0

    for problem in sync():
        log(f"needs attention: {problem}")
    for repo in cfg["repos"]:
        for issue in ready_issues(repo["slug"]):
            if a.dry_run:
                log(f"would build {repo['slug']}#{issue['number']}: {issue['title']}")
                continue
            try:
                build(repo, issue, cfg)
            except Failed as e:
                log(f"{repo['slug']}#{issue['number']}: {e}")
    return 0


if __name__ == "__main__":
    main(cli)
