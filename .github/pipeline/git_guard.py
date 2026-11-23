"""Claude Code PreToolUse hook: blocks the git and GitHub moves that would go around the pipeline.

Install (user settings, PreToolUse, matcher "Bash|PowerShell|Edit|Write|NotebookEdit"):
    python -I <path>/git_guard.py

It judges each git or gh call by the repo it acts on (its -C, --repo/-R or repos/... target, else the last cd
before it, else the session's folder) and only when that is a pipeline repo (see ~/.claude/skill-pipeline.json),
so other projects are untouched and text inside quoted arguments is never taken for a call. The pipeline's own scripts call git and gh themselves, not through a tool, so the hook
never sees them: that is what makes merge.py the one way to merge.

Defence in depth, like route's guard: a text match can be spelled around. The boundary is GitHub's branch
protection where the plan allows it, and the local git hooks.
"""
import json
import os
import re
import sys
from pathlib import Path

CONFIG = Path(os.environ.get("SKILL_PIPELINE_CONFIG", Path.home() / ".claude" / "skill-pipeline.json"))
READ_ONLY = {"status", "log", "diff", "show", "fetch", "pull", "worktree", "branch", "tag", "rev-parse", "ls-files",
             "ls-remote", "remote", "describe", "blame", "grep", "cat-file", "for-each-ref", "merge-base", "config",
             "shortlog", "reflog", "check-ignore", "rev-list", "name-rev", "version", "help", "ls-tree", "gc"}
GIT = re.compile(r"""\bgit(?:\.exe)?(?P<opts>(?:\s+(?:-c\s+\S+|-C\s+(?:"[^"]*"|'[^']*'|\S+)|--[a-z-]+(?:=\S+)?))*)\s+(?P<sub>[a-z][a-z-]*)""")
DASH_C = re.compile(r"""-C\s+("[^"]*"|'[^']*'|\S+)""")
CD = re.compile(r"""\b(?:cd|pushd|set-location|sl|chdir)\s+(?:/d\s+)?("[a-z]:/[^"]*"|'[a-z]:/[^']*'|[a-z]:/[^\s;&|)]*)""")
REMOVE = re.compile(r"\b(rm|rmdir|rd|del|erase|remove-item|ri|move-item|mv|move|ren|rename-item)\b")

GH = re.compile(r"\bgh(?:\.exe)?\s+(?P<sub>[a-z]+)")
GH_REPO = re.compile(r"""(?<!\S)(?:--repo|-R)(?:\s+|=)("[^"]*"|'[^']*'|\S+)""")
GH_REPO_ARG = re.compile(r"^gh(?:\.exe)?\s+repo\s+[a-z]+\s+([\w.-]+/[\w.-]+)|\brepos/([\w.-]+/[\w.-]+)")
QUOTED = re.compile(r""""[^"]*"|'[^']*'""")
CALL_END = re.compile(r"[\n;&|]")
WRITE = r"(?=.*(\s-x\s*(post|put|patch|delete)|\s--method\b|\s-f\b|\s--field\b|\s--raw-field\b|\s--input\b))"

# Each rule is judged against one git or gh call (lower-cased, quoted text blanked) that acts on a pipeline repo.
# Main, tags and releases are held by the pre-push hook and by branch protection, so they are not repeated here.
GIT_RULES = [
    (r"\bpush\b.*(\s--force(?!-with-lease)|\s-f\b|\s\+\S)",
     "Force pushes are blocked. Use --force-with-lease on your own PR branch if you rebased it."),
    (r"(?<!\S)--no-verify\b|\bcore\.hookspath(=|\s+[^\s-])|--unset(-all)?\s+core\.hookspath\b",
     "The local git hooks may not be skipped or re-pointed."),
]
GH_RULES = [
    (r"^gh(\.exe)?\s+pr\s+merge\b|^gh(\.exe)?\s+api\b(?=.*/pulls/\d+/merge\b)" + WRITE,
     "Merge through the pipeline: python .github/pipeline/merge.py --repo <owner/name> --pr <number>."),
    (r"^gh(\.exe)?\s+repo\s+(delete|rename|archive)\b",
     "Deleting, renaming or archiving a pipeline repo is the owner's call."),
    (r"^gh(\.exe)?\s+api\b(?=.*/statuses/)" + WRITE,
     "Commit statuses are written by the gate on GitHub, not by hand."),
]


def norm(text: str) -> str:
    """Lower case, forward slashes, and Git Bash's /c/folder written as c:/folder."""
    return re.sub(r"(?<![\w:./~-])/([a-z])/", r"\1:/", text.replace("\\", "/").lower())


def inside(child: str, parent: str) -> bool:
    c, p = norm(child).rstrip("/"), norm(parent).rstrip("/")
    return c == p or c.startswith(p + "/")


def decide(payload: dict, cfg: dict) -> str | None:
    """The reason to deny this tool call, or None."""
    tool, args, cwd = payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("cwd") or ""
    live = [r["path"] for r in cfg.get("repos", [])]
    slugs = [r["slug"].lower() for r in cfg.get("repos", [])]
    worktrees = cfg.get("worktrees") or "\0"
    linked = [str(Path(cfg["skills_dir"]).expanduser() / d.name) for p in live if Path(p).is_dir()
              for d in Path(p).iterdir() if (d / "SKILL.md").exists()]

    if tool in ("Edit", "Write", "NotebookEdit"):
        path = args.get("file_path") or args.get("notebook_path") or ""
        for root in live:
            if inside(path, root) and not inside(path, root + "/plans"):
                return (f"{root} is the live copy of main: what is in it is what Claude loads. "
                        "Make the change on a branch in its own worktree and take it through a pull request.")
        if any(inside(path, l) for l in linked):
            return "This skill folder is a link onto main. Change it on a branch in a worktree, through a pull request."
        return None
    if tool not in ("Bash", "PowerShell"):
        return None

    raw = (args.get("command") or "").replace("\\", "/")      # case kept: git -C is not git -c
    command = norm(raw)
    # quoted text (an issue body, a commit message) is blanked, so only the calls that run are judged
    masked = QUOTED.sub(lambda q: q.group(0)[0] + "_" * (len(q.group(0)) - 2) + q.group(0)[-1], raw)

    def call(start: int) -> str:
        end = CALL_END.search(masked, start)
        return masked[start:end.start() if end else len(masked)]

    def folder(start: int) -> str:
        """The last absolute cd before this call, else the session's folder."""
        moves = [c.group(1).strip("\"'") for c in CD.finditer(norm(raw[:start])) if masked[c.start()] != "_"]
        return moves[-1] if moves else cwd

    def pipeline(where: str) -> bool:
        return any(inside(where, p) for p in live) or inside(where, worktrees)

    for m in GIT.finditer(masked):
        target = DASH_C.search(m.group("opts"))
        if target:
            pos = m.start("opts") + target.start(1)
            where = raw[pos:m.start("opts") + target.end(1)].strip("\"'")
        else:
            where = folder(m.start())
        if not pipeline(where):
            continue
        text = norm(call(m.start()))
        for pattern, reason in GIT_RULES:
            if re.search(pattern, text):
                return reason
        on_live = any(inside(where, p) for p in live)
        if on_live and m.group("sub") not in READ_ONLY:
            return (f"'git {m.group('sub')}' would change the live copy of main. It is read-only here: "
                    "create a worktree (git worktree add) and work on a branch there.")

    for m in GH.finditer(masked):
        text = call(m.start())
        named = GH_REPO.search(text)
        arg = GH_REPO_ARG.search(text)
        if named:
            repo = raw[m.start() + named.start(1):m.start() + named.end(1)].strip("\"'")
        else:
            repo = arg and (arg.group(1) or arg.group(2))
        if not (repo.lower() in slugs if repo else pipeline(folder(m.start()))):
            continue
        for pattern, reason in GH_RULES:
            if re.search(pattern, norm(text)):
                return reason
    if REMOVE.search(command) and any(re.search(re.escape(norm(x).rstrip("/")) + r"(/[\w.-]+)?[\"']?(\s|$)", command)
                                      for x in live + linked):
        return "Deleting or moving a live skill folder or its link is the owner's call."
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return 0
    reason = decide(payload, cfg)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "pipeline guard: " + reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
