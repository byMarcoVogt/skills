"""Claude Code PreToolUse hook: blocks the git and GitHub moves that would go around the pipeline.

Install (user settings, PreToolUse, matcher "Bash|PowerShell|Edit|Write|NotebookEdit"):
    python -I <path>/git_guard.py

It only looks at commands and files that concern a pipeline repo (see ~/.claude/skill-pipeline.json), so other
projects are untouched. Each git call is judged by the folder it acts on, and text a command only carries (a
body, a commit message, a heredoc) is not read as a command. The pipeline's own scripts call git and gh themselves, not through a tool, so the hook
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
             "shortlog", "reflog", "check-ignore", "rev-list", "name-rev", "version", "help", "ls-tree", "gc",
             "show-ref", "archive"}     # archive writes to stdout or to its -o file; an -o inside a live clone is denied
GIT =re.compile(r"""\bgit(?:\.exe)?(?P<opts>(?:\s+(?:-c\s+\S+|-C\s+(?:"[^"]*"|'[^']*'|\S+)|--[a-z-]+(?:=\S+)?))*)\s+(?P<sub>[a-z][a-z-]*)""")
DASH_C = re.compile(r"""-C\s+("[^"]*"|'[^']*'|\S+)""")
CD = re.compile(r"""\b(?:cd|pushd|set-location|sl|chdir)\s+(?:/d\s+)?("[a-z]:/[^"]*"|'[a-z]:/[^']*'|[a-z]:/[^\s;&|)]*)""")
REMOVE = re.compile(r"(?<![\w.-])(rm|rmdir|rd|del|erase|remove-item|ri|move-item|mv|move|ren|rename-item)(?![\w.-])")
GIT_BEFORE = re.compile(r"\bgit(?:\.exe)?(?:\s+-[cC]\s+\S+)*\s+$")     # 'git rm' is judged by the per-call check
SEGMENT = re.compile(r"[^\n;&|]+")
OUTPUT = re.compile(r"""(?<!\S)(?:-o|--output)(?:=|\s+)("[^"]*"|'[^']*'|\S+)""")

# Text a command only carries (a body, a title, a commit message, a heredoc) is blanked before any rule looks,
# so that writing about a command is not taken for running it. A heredoc or here-string fed to a shell stays.
TEXT_FLAG = re.compile(r"""(?<!\S)(--body|--title|--message|--notes|--subject|-[bmt])(\s+|=)"""
                       r"""("(?:[^"\\`]|\\.|`.)*"|'[^']*')""", re.S)
HEREDOC = re.compile(r"""<<-?[ \t]*(["']?)([A-Za-z_][\w-]*)\1""")
HERESTRING = re.compile(r"""@(["'])[ \t]*\r?\n.*?\r?\n\1@""", re.S)
SHELL = re.compile(r"(?<![\w.-])(bash|sh|zsh|dash|pwsh|powershell|cmd|iex|invoke-expression)(\.exe)?(?![\w.-])", re.I)

# Judged against one git call (lower-cased, text blanked) that acts on a pipeline repo or names one.
GIT_RULES = [
    (r"\bpush\b.*(\s--force(?!-with-lease)|\s-f\b|\s\+\S)",
     "Force pushes are blocked. Use --force-with-lease on your own PR branch if you rebased it."),
    (r"\bpush\b.*([\s:]|refs/heads/)(main|master)(?![\w./-])",
     "Nobody pushes to main. Push your branch and open a pull request."),
    # reading the setting is fine; setting, unsetting or overriding it is not
    (r"(?<!\S)--no-verify\b|core\.hookspath\s*="
     r"|\bconfig\b(\s+(--?[\w-]+(=\S+)?|set))*\s+core\.hookspath\s+(?!\d?>)[^\s|;&)>]"
     r"|(--unset(-all)?|(?<!\S)unset)\s+(--?[\w-]+\s+)*core\.hookspath\b",
     "The local git hooks may not be skipped or re-pointed."),
    # a local tag is harmless: the pre-push hook refuses to push any tag
    (r"\bpush\b.*(--tags|--follow-tags|refs/tags)",
     "Tags and releases come from the release workflow after a merge, not by hand."),
    (r"\b(remote\s+(add|remove|rm|rename|set-url)|branch\s+(-d|-m|--delete|--move)\s+(main|master)\b)",
     "The pipeline repos keep their remote and their main branch."),
]
RULES = [   # (pattern on the lower-cased command, text blanked, what to do instead)
    (r"\bgh(\.exe)?\s+release\s+(create|delete|edit)",
     "Tags and releases come from the release workflow after a merge, not by hand."),
    (r"\bgh(\.exe)?\s+pr\s+merge\b",
     "Merge through the pipeline: python .github/pipeline/merge.py --repo <owner/name> --pr <number>."),
    (r"\bgh(\.exe)?\s+api\b(?=[^\n;&|]*(protection|rulesets|/statuses|actions/permissions|/hooks|/merge\b))"
     r"(?=[^\n;&|]*(\s-x\s*(post|put|patch|delete)|\s--method\b|\s-f\b|\s--field\b|\s--raw-field\b|\s--input\b))"   # reading is fine
     r"|\bgh(\.exe)?\s+(ruleset|secret)\b|\bgh(\.exe)?\s+repo\s+(edit|delete|rename|archive)\b"
     r"|\bgh(\.exe)?\s+workflow\s+(disable|enable)\b",
     "Branch protection, statuses, repo settings and secrets belong to the owner."),
]


def mask(command: str) -> str:
    """The command with the text it only carries removed: heredoc and here-string bodies (unless a shell runs
    them) and the quoted values of --body, --title, -m and the like."""
    out, pos = [], 0
    while m := HEREDOC.search(command, pos):
        eol = command.find("\n", m.end())
        end = re.compile(r"^[ \t]*" + re.escape(m.group(2)) + r"[ \t]*\r?$", re.M).search(command, eol + 1) if eol >= 0 else None
        if not end:
            break
        line = command[command.rfind("\n", 0, m.start()) + 1:eol]
        out.append(command[pos:eol + 1] if SHELL.search(line) is None else command[pos:end.start()])
        pos = end.start()
    command = "".join(out) + command[pos:]
    command = HERESTRING.sub(lambda h: h.group(0) if SHELL.search(
        command[command.rfind("\n", 0, h.start()) + 1:h.start()]) else f"@{h.group(1)}\n{h.group(1)}@", command)
    return TEXT_FLAG.sub(lambda t: t.group(1) + t.group(2) + t.group(3)[0] + "_" + t.group(3)[-1], command)


def norm(text: str) -> str:
    """Lower case, forward slashes, and Git Bash's /c/folder written as c:/folder."""
    return re.sub(r"(?<![\w:./~-])/([a-z])/", r"\1:/", text.replace("\\", "/").lower())


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

    raw = mask(args.get("command") or "").replace("\\", "/")      # case kept: git -C is not git -c
    command = norm(raw)
    cwd_live = any(inside(cwd, p) for p in live)
    names = lambda text: any(re.search(at(x), text) for x in live + slugs + linked + [worktrees])  # noqa: E731
    if not (cwd_live or inside(cwd, worktrees) or names(command)):
        return None
    for pattern, reason in RULES:
        if re.search(pattern, command):
            return reason

    def folder(start: int) -> str:
        """The last absolute cd before this point, else the session's folder."""
        moves = [c.group(1).strip("\"'") for c in CD.finditer(norm(raw[:start]))]
        return moves[-1] if moves else cwd

    for m in GIT.finditer(raw):
        target = DASH_C.search(m.group("opts"))
        where = target.group(1).strip("\"'") if target else folder(m.start())
        call = norm(SEGMENT.match(raw, m.start()).group(0))
        if inside(where, worktrees) or any(inside(where, p) for p in live) or names(call):
            for pattern, reason in GIT_RULES:       # one call, judged by the folder it acts on
                if re.search(pattern, call):
                    return reason
        on_live = any(inside(where, p) for p in live)
        sub = m.group("sub")
        out = OUTPUT.search(call) if sub == "archive" else None
        if on_live and out:     # an archive written into the live clone would change it
            path = norm(out.group(1).strip("\"'"))
            on_live = any(inside(path if re.match(r"[a-z]:/|/|~", path) else where + "/" + path, p) for p in live)
            sub = "archive -o"
        if on_live and (sub not in READ_ONLY):
            return (f"'git {sub}' would change the live copy of main. It is read-only here: "
                    "create a worktree (git worktree add) and work on a branch there.")

    live_path = [re.escape(norm(x).rstrip("/")) + r"(/[\w.-]+)?[\"']?(\s|$)" for x in live + linked]
    for s in SEGMENT.finditer(command):             # a removal is judged within its own call
        r = REMOVE.search(s.group(0))
        if not r or GIT_BEFORE.search(s.group(0)[:r.start()]):
            continue
        moves = [c.group(1).strip("\"'") for c in CD.finditer(command[:s.start()])]   # a cd into a live folder first
        if any(re.search(p, s.group(0)) for p in live_path) or (moves and any(inside(moves[-1], x) for x in live + linked)):
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
