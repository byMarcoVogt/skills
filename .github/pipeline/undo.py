"""Go back one version of a skill. First aid when live use breaks: undo first, fix afterwards in a new PR.

    python undo.py think-it-through

It opens a PR that restores the skill's files from its previous tag, with the next patch number (every merge
gets its own version), and merges it. The gate lets it through without a new review because it can verify the
files are those of a release that already passed. Nothing is rewritten: main only moves forward.
"""
import argparse
import shutil
from pathlib import Path

import rules
from common import Failed, api, config, main, run
from merge import merge


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill")
    a = ap.parse_args()

    cfg = config()
    repo = next((r for r in cfg["repos"] if (Path(r["path"]) / a.skill / "SKILL.md").exists()), None)
    if not repo:
        raise Failed(f"No pipeline repo holds a skill named {a.skill}")
    live, slug = Path(repo["path"]), repo["slug"]
    run(["git", "fetch", "origin", "--tags", "--prune", "--quiet"], cwd=live)
    current = rules.skill_version(run(["git", "show", f"origin/main:{a.skill}/SKILL.md"], cwd=live))
    previous = rules.previous_release(run(["git", "tag", "--list", f"{a.skill}--v*"], cwd=live).split(), a.skill, current)
    if not previous:
        raise Failed(f"{a.skill} {rules.fmt(current)} has no earlier tag to go back to")
    tag, old = previous
    new = rules.bump(current, "fix")
    title = f"fix: undo {a.skill} to v{rules.fmt(old)}"
    branch = f"undo/{a.skill}-v{rules.fmt(current)}"
    tree = Path(cfg["worktrees"]) / slug.split("/")[1] / branch.replace("/", "-")

    run(["git", "worktree", "add", str(tree), "-b", branch, "origin/main"], cwd=live)
    try:
        run(["git", "rm", "-r", "-q", a.skill], cwd=tree)
        run(["git", "checkout", tag, "--", a.skill], cwd=tree)
        skill_md = tree / a.skill / "SKILL.md"
        skill_md.write_text(rules.set_skill_version(skill_md.read_text(encoding="utf-8"), new),
                            encoding="utf-8", newline="\n")
        run(["git", "add", "-A", a.skill], cwd=tree)
        run(["git", "commit", "-q", "-m", title], cwd=tree)
        run(["git", "push", "-q", "-u", "origin", branch], cwd=tree)
    finally:
        run(["git", "worktree", "remove", "--force", str(tree)], cwd=live, check=False)
        shutil.rmtree(tree, ignore_errors=True)
        run(["git", "branch", "-D", branch], cwd=live, check=False)
    pr = api(f"repos/{slug}/pulls", "POST", {
        "title": title, "head": branch, "base": "main",
        "body": f"Restores `{a.skill}` to the files of `{tag}`, as version {rules.fmt(new)}. "
                f"This undoes {rules.fmt(current)}; the fix follows in its own PR."})
    print(f"opened {pr['html_url']}")
    merge(slug, pr["number"])
    print(f"{a.skill} is back on the files of {tag}, live as {rules.fmt(new)}")
    return 0


if __name__ == "__main__":
    main(cli)
