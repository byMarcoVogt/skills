"""The privacy check: nothing private leaves this machine for a public repo.

    python privacy.py push --url <remote url> --base origin/main --head <sha>     the pre-push hook runs this
    python privacy.py text --repo owner/name --file body.md                        check a text before posting it

Comments, pull request titles and texts that the pipeline posts go through common.api, which calls guard()
before anything is sent. A push is checked by the pre-push hook: the lines it adds and its commit messages.

Two sources say what is private. Fixed patterns that are always private: a home path with a user name in it,
an app-data or temp path, a session id. And the owner's own list, one term per line, in a local file outside
every repo (TERMS), read at run time. A hit names its kind and where it is, never the term or the path itself:
the refusal may end up in a log or a session. A private repo is not checked.
"""
import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from common import Failed, api, main, run

TERMS = Path(os.environ.get("SKILL_PIPELINE_TERMS", Path.home() / ".claude" / "skill-pipeline" / "private-terms.txt"))
PATTERNS = [
    ("home path", re.compile(r"(?:\b[a-z]:[\\/]+|(?<![\w./:-])/(?:[a-z]/)?)(?:users|home)[\\/]+"
                             r"(?!(?:public|default|shared|all users)\b)[\w.-]+", re.I)),
    ("app-data path", re.compile(r"\bappdata[\\/]+(?:local|locallow|roaming)\b", re.I)),
    ("temp path", re.compile(r"\b[a-z]:[\\/]+(?:windows[\\/]+)?te?mp[\\/]|(?<![\w./:-])/tmp/[\w.-]", re.I)),
    ("session id", re.compile(r"(?<![\w-])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![\w-])", re.I)),
]
TEXT_FIELDS = ("title", "body", "commit_title", "commit_message")   # what GitHub shows as text; labels are names
_said_missing = False
_public: dict[str, bool] = {}


@dataclass
class Hit:
    kind: str
    line: int
    column: int
    where: str = ""


def load_terms() -> list[str]:
    """The owner's list, read fresh each time. Missing: the fixed patterns still apply, and this says so once."""
    global _said_missing
    try:
        lines = TERMS.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        if not _said_missing:
            print("pipeline: no owner list of private terms was found (~/.claude/skill-pipeline/private-terms.txt); "
                  "only the fixed patterns were checked", file=sys.stderr)
            _said_missing = True
        return []
    return [t.strip() for t in lines if t.strip() and not t.strip().startswith("#")]


def scan(text: str, terms: list[str], where: str = "", first_line: int = 1) -> list[Hit]:
    hits = []
    for i, line in enumerate((text or "").splitlines()):
        found = [(m.start(), kind) for kind, pattern in PATTERNS for m in pattern.finditer(line)]
        low = line.lower()
        for term in terms:
            at = low.find(term.lower())
            while at >= 0:
                found.append((at, "owner's term"))
                at = low.find(term.lower(), at + 1)
        hits += [Hit(kind, first_line + i, col + 1, where) for col, kind in sorted(found)]
    return hits


def describe(hits: list[Hit], what: str) -> str:
    """The refusal: kind and position of each hit, never what was found."""
    spots = [f"{h.kind} at {h.where + ', ' if h.where else ''}line {h.line}, column {h.column}" for h in hits[:10]]
    more = f" and {len(hits) - 10} more" if len(hits) > 10 else ""
    return (f"{what} holds private details, so nothing was sent: " + "; ".join(spots) + more +
            ". Take them out and try again.")


def is_public(slug: str) -> bool:
    """Whether GitHub shows this repo to everyone. When that cannot be learned, it counts as public."""
    if slug not in _public:
        try:
            info = api(f"repos/{slug}")
            _public[slug] = not (isinstance(info, dict) and info.get("private") is True)
        except Failed:
            _public[slug] = True
    return _public[slug]


def guard(slug: str, fields: dict, public: bool | None = None, terms: list[str] | None = None) -> None:
    """Refuse to send these fields to a public repo if a text in them holds something private."""
    texts = [(k, fields[k]) for k in TEXT_FIELDS if isinstance(fields.get(k), str)]
    if not texts or not (is_public(slug) if public is None else public):
        return
    terms = load_terms() if terms is None else terms
    hits = [h for key, text in texts for h in scan(text, terms, where=f"the {key.replace('_', ' ')}")]
    if hits:
        raise Failed(describe(hits, f"What was about to be posted to {slug}"))


def slug_of(url: str) -> str | None:
    m = re.search(r"github\.com[:/]+([\w.-]+/[\w.-]+?)(?:\.git)?/*$", url.strip())
    return m.group(1) if m else None


HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,\d+)? @@")


def scan_push(base: str, head: str, terms: list[str], cwd=None) -> list[Hit]:
    """What the push adds: the added lines of its diff against main, and the messages of its commits."""
    hits, path, number = [], "", 0
    diff = run(["git", "diff", "--unified=0", "--no-color", "--no-ext-diff", f"{base}...{head}"], cwd=cwd)
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else line[4:]
        elif HUNK.match(line):
            number = int(HUNK.match(line).group(1))
        elif line.startswith("+"):
            hits += scan(line[1:], terms, where=path, first_line=number)
            number += 1
    log = run(["git", "log", "--format=%H%x00%B%x01", f"{base}..{head}"], cwd=cwd)
    for entry in log.split("\x01"):
        sha, _, message = entry.strip().partition("\x00")
        if sha:
            hits += scan(message, terms, where=f"the commit message of {sha[:10]}")
    return hits


def cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("push")
    p.add_argument("--url", required=True, help="the remote's URL, as git gives it to the pre-push hook")
    p.add_argument("--base", default="origin/main")
    p.add_argument("--head", default="HEAD")
    t = sub.add_parser("text")
    t.add_argument("--repo", required=True)
    t.add_argument("--file", required=True)
    a = ap.parse_args()

    if a.mode == "text":
        guard(a.repo, {"body": Path(a.file).read_text(encoding="utf-8")})
        return 0
    slug = slug_of(a.url)
    if slug and not is_public(slug):
        return 0
    hits = scan_push(a.base, a.head, load_terms())
    if hits:
        raise Failed(describe(hits, f"This push to {slug or 'a repo that may be public'}"))
    return 0


if __name__ == "__main__":
    main(cli)
