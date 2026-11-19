"""After a merge: give every skill whose version has no tag yet its tag and release. GitHub runs this on main.

    python release.py --repo owner/name [--root .]

The tag is skill-name--v1.5.0. The release notes are the title of the merged PR (the squash commit's subject).
"""
import argparse
from pathlib import Path

import rules
from common import main, paged, run


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--root", default=".")
    a = ap.parse_args()

    root = Path(a.root)
    sha = run(["git", "rev-parse", "HEAD"], cwd=root).strip()
    subject = run(["git", "log", "-1", "--format=%s"], cwd=root).strip()
    changed = {rules.top_dir(p) for p in run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], cwd=root, check=False).split()}
    released = set()
    for tag in (t["name"] for t in paged(f"repos/{a.repo}/tags")):
        name, sep, v = tag.rpartition("--v")
        if sep and rules.parse_version(v):
            released.add((name, rules.parse_version(v)))
    for skill_md in sorted(root.glob("*/SKILL.md")):
        skill = skill_md.parent.name
        version = rules.skill_version(skill_md.read_text(encoding="utf-8"))
        if version is None or (skill, version) in released:
            continue
        tag = f"{skill}--v{rules.fmt(version)}"
        notes = subject if skill in changed else "Baseline: the version on main when the pipeline started."
        run(["gh", "release", "create", tag, "-R", a.repo, "--target", sha,
             "--title", f"{skill} v{rules.fmt(version)}", "--notes", notes])
        print(f"released {tag} at {sha[:10]}")
    return 0


if __name__ == "__main__":
    main(cli)
