"""Claude Code PreToolUse hook: blocks the git and GitHub moves that would go around the pipeline.

Install (user settings, PreToolUse, matcher "Bash|PowerShell|Edit|Write|NotebookEdit"):
    python -I <path>/git_guard.py

It only looks at commands and files that concern a pipeline repo (see ~/.claude/skill-pipeline.json), so other
projects are untouched. The pipeline's own scripts call git and gh themselves, not through a tool, so the hook
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
REMOVE = re.compile(r"\b(rm|rmdir|rd|del|erase|remove-item|ri|move-item|mv|move|ren|rename-item)\b")

RULES = [   # (pattern on the lower-cased command, what to do instead)
    (r"\bgit\b[^\n;&|]*\bpush\b[^\n;&|]*(\s--force(?!-with-lease)|\s-f\b|\s\+\S)",
     "Force pushes are blocked. Use --force-with-lease on your own PR branch if you rebased it."),
    (r"\bgit\b[^\n;&|]*\bpush\b[^\n;&|]*([\s:]|refs/heads/)(main|master)(?![\w./-])",
     "Nobody pushes to main. Push your branch and open a pull request."),
    (r"--no-verify\b|\bhookspath\b",
     "The local git hooks may not be skipped or re-pointed."),
    (r"\bgit\b[^\n;&|]*\bpush\b[^\n;&|]*(--tags|--follow-tags|refs/tags)"
     r"|\bgit\b[^\n;&|]*\btag\s+(?!-l\b|--list\b|-n|--contains|--points-at|--sort)\S"
     r"|\bgh(\.exe)?\s+release\s+(create|delete|edit)",
     "Tags and releases come from the release workflow after a merge, not by hand."),
    (r"\bgh(\.exe)?\s+pr\s+merge\b",
     "Merge through the pipeline: python .github/pipeline/merge.py --repo <owner/name> --pr <number>."),
    (r"\bgh(\.exe)?\s+api\b[^\n;&|]*(protection|rulesets|/statuses|actions/permissions|/hooks|/merge\b)"
     r"|\bgh(\.exe)?\s+(ruleset|secret)\b|\bgh(\.exe)?\s+repo\s+(edit|delete|rename|archive)\b"
     r"|\bgh(\.exe)?\s+workflow\s+(disable|enable)\b|owner-approved",
     "Branch protection, statuses, repo settings, secrets and the owner-approved label belong to the owner."),
    (r"\bgit\b[^\n;&|]*\b(remote\s+(add|remove|rm|rename|set-url)|branch\s+(-d|-m|--delete|--move)\s+(main|master)\b)",
     "The pipeline repos keep their remote and their main branch."),
]


def norm(text: str) -> str:
    return text.replace("\\", "/").lower()


def at(path: str) -> str:
    """A regex that finds this path in a lower-cased command, not as the start of a longer name."""
    return re.escape(norm(path).rstrip("/")) + r"(?![\w.-])"


def inside(child: str, parent: str) -> bool:
    c, p = norm(child).rstrip("/"), norm(parent).rstrip("/")
    return c == p or c.startswith(p + "/")


def decide(payload: dict, cfg: dict) -> str | None:
    """The reason to deny this tool call, or None."""
    tool, args, cwd = payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("cwd") or ""
    live = [r["path"] for r in cfg.get("repos", [])]
    slugs = [r["slug"] for r in cfg.get("repos", [])]
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
    command = raw.lower()
    cwd_live = any(inside(cwd, p) for p in live)
    in_scope = cwd_live or inside(cwd, worktrees) or any(re.search(at(x), command) for x in live + slugs + linked + [worktrees])
    if not in_scope:
        return None
    for pattern, reason in RULES:
        if re.search(pattern, command):
            return reason

    moved_into_live = any(re.search(r"\b(cd|pushd|set-location|sl|chdir)\s+(/d\s+)?[\"']?" + at(p), command) for p in live)
    for m in GIT.finditer(raw):
        target = DASH_C.search(m.group("opts"))
        where = target.group(1).strip("\"'") if target else None
        on_live = any(inside(where, p) for p in live) if where else (cwd_live or moved_into_live)
        if on_live and m.group("sub") not in READ_ONLY:
            return (f"'git {m.group('sub')}' would change the live copy of main. It is read-only here: "
                    "create a worktree (git worktree add) and work on a branch there.")
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
