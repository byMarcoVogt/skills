"""Shared plumbing: run a command, talk to GitHub through gh, read this machine's pipeline config."""
import json
import os
import subprocess
import sys
from pathlib import Path

CONFIG = Path(os.environ.get("SKILL_PIPELINE_CONFIG", Path.home() / ".claude" / "skill-pipeline.json"))
CONTEXTS = ("pipeline/title", "pipeline/version", "pipeline/evidence", "pipeline/protected-files")


class Failed(Exception):
    pass


def run(args: list[str], cwd=None, check=True, stdin: str | None = None) -> str:
    p = subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and p.returncode:
        raise Failed(f"{' '.join(args[:4])} ...: {(p.stderr or p.stdout).strip()[:400]}")
    return p.stdout


def api(path: str, method: str = "GET", fields: dict | None = None, raw: bool = False):
    """One GitHub API call through gh. A 404 gives None."""
    args = ["gh", "api", path, "-X", method]
    if raw:
        args += ["-H", "Accept: application/vnd.github.raw"]
    stdin = None
    if fields is not None:
        args += ["--input", "-"]
        stdin = json.dumps(fields)
    p = subprocess.run(args, input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        if "HTTP 404" in p.stderr:
            return None
        raise Failed(f"gh api {path}: {p.stderr.strip()[:400]}")
    return p.stdout if raw else (json.loads(p.stdout) if p.stdout.strip() else None)


def paged(path: str) -> list:
    out, page = [], 1
    while True:
        batch = api(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}") or []
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def config() -> dict:
    """{'skills_dir': ..., 'worktrees': ..., 'repos': [{'slug': 'owner/name', 'path': 'C:/...'}]}"""
    if not CONFIG.exists():
        raise Failed(f"No pipeline config at {CONFIG}")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def repo_entry(key: str) -> dict:
    """A configured repo by slug, by name or by local path."""
    for r in config()["repos"]:
        if key.lower() in (r["slug"].lower(), r["slug"].split("/")[1].lower()) or Path(key) == Path(r["path"]):
            return r
    raise Failed(f"{key} is not a pipeline repo in {CONFIG}")


def main(fn) -> None:
    try:
        sys.exit(fn() or 0)
    except Failed as e:
        print(f"pipeline: {e}", file=sys.stderr)
        sys.exit(1)
