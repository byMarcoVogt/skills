"""Write the version the PR title asks for. The script picks the number, not the model.

    python bump.py --title "fix: stop asking twice"        run inside the branch's worktree

It finds the one skill this branch changes against origin/main and sets its version in SKILL.md.
"""
import argparse
from pathlib import Path

import rules
from common import Failed, main, run


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()

    kind = rules.title_kind(a.title)
    if not kind:
        raise Failed(rules.check_title(a.title)[1])
    root = Path(run(["git", "rev-parse", "--show-toplevel"]).strip())
    base = run(["git", "merge-base", a.base, "HEAD"]).strip()
    changed = run(["git", "diff", "--name-only", base], cwd=root).split()
    changed += run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root).split()
    skills = sorted({d for d in map(rules.top_dir, changed) if d and (root / d / "SKILL.md").exists()})
    if len(skills) != 1:
        raise Failed(f"Expected one changed skill, found {skills or 'none'}")
    path = root / skills[0] / "SKILL.md"
    old = rules.skill_version(run(["git", "show", f"{base}:{skills[0]}/SKILL.md"], check=False))
    text = path.read_text(encoding="utf-8")
    new = rules.bump(old, kind) if old else (rules.skill_version(text) or (0, 1, 0))
    path.write_text(rules.set_skill_version(text, new), encoding="utf-8", newline="\n")
    print(f"{skills[0]}: {rules.fmt(old) if old else 'new'} -> {rules.fmt(new)}")
    return 0


if __name__ == "__main__":
    main(cli)
