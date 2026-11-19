"""Make this machine match main: pull each live clone and link its skills into the skills folder.

    python sync.py                      all pipeline repos
    python sync.py --adopt route        replace an existing plain folder by the link; the folder is moved to a backup

A skill is linked, never copied: ~/.claude/skills/<name> is a directory junction onto <live clone>/<name>, so
what is on main is what Claude loads. An existing folder is never replaced without --adopt.
"""
import argparse
import datetime
import os
import shutil
import subprocess
from pathlib import Path

from common import Failed, config, main, run


def same(a: Path, b: Path) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def link(target: Path, at: Path) -> None:
    # bytes, not text: cmd answers in the console's code page, which Python cannot always decode
    p = subprocess.run(["cmd", "/c", "mklink", "/J", str(at), str(target)], capture_output=True)
    if p.returncode:
        raise Failed(f"Could not link {at}: {(p.stderr or p.stdout).decode('ascii', 'replace').strip()}")


def pull(path: Path) -> list[str]:
    """Fast-forward the live clone to origin/main. Returns what stands in the way, in plain words."""
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path).strip()
    if branch != "main":
        return [f"{path} is on branch '{branch}', not on main. Skills are live from main only."]
    run(["git", "fetch", "origin", "--tags", "--prune", "--quiet"], cwd=path)
    p = subprocess.run(["git", "merge", "--ff-only", "--quiet", "origin/main"], cwd=path, capture_output=True, text=True)
    if p.returncode:
        return [f"{path} could not move to the newest main: {(p.stderr or p.stdout).strip()[:300]}"]
    return []


def sync(adopt: tuple[str, ...] = ()) -> list[str]:
    cfg = config()
    skills_dir = Path(cfg["skills_dir"]).expanduser()
    problems = []
    for repo in cfg["repos"]:
        path = Path(repo["path"])
        problems += pull(path)
        dirty = run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=path).strip()
        if dirty:
            problems.append(f"{path} has edits that are not on main: {dirty.splitlines()[0].strip()} ...")
        for skill_md in sorted(path.glob("*/SKILL.md")):
            target, at = skill_md.parent, skills_dir / skill_md.parent.name
            if target.name in cfg.get("not_linked", []) or (at.exists() and same(target, at)):
                continue
            if at.exists() or at.is_symlink():
                if at.name not in adopt:
                    problems.append(f"{at} is a separate folder, not the link to {target}. Run sync.py --adopt {at.name}")
                    continue
                backup = skills_dir.parent / "skills-backup" / f"{at.name}-{datetime.datetime.now():%Y-%m-%d-%H%M%S}"
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(at), str(backup))
                print(f"moved the old {at.name} folder to {backup}")
            link(target, at)
            print(f"linked {at} -> {target}")
    return problems


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adopt", action="append", default=[])
    a = ap.parse_args()
    problems = sync(tuple(a.adopt))
    for p in problems:
        print(f"needs attention: {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    main(cli)
