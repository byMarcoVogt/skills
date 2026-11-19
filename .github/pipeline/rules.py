"""The pipeline's rules as pure functions. GitHub (gate.py) and the local git hooks call the same code.

No network and no git in here, so every rule can be tested offline (tests/test_rules.py).
"""
import re

TITLE = re.compile(r"^(fix|feat|feat!): \S")
UNDO_TITLE = re.compile(r"^fix: undo (?P<skill>[a-z0-9][a-z0-9-]*) to v(?P<version>\d+(?:\.\d+){1,2})\b")
VERSION_LINE = re.compile(r"""^(?P<head>\s*version:\s*)(?P<q>["']?)(?P<v>\d+(?:\.\d+){1,2})(?P=q)\s*$""")
# Evidence is posted from the owner's account, so the marker itself has to say who checked: the model and the
# reasoning effort it ran at. 'unknown' is allowed where a value cannot be had; leaving them out is not.
EVIDENCE = re.compile(r"<!-- pipeline-evidence kind=(review|qa) sha=([0-9a-f]{40}) result=(pass|fail)"
                      r"(?: model=([A-Za-z0-9._:/-]+) effort=([A-Za-z0-9._-]+))? -->")
UNSIGNED = "unsigned"                # evidence that does not name its model and effort
EVIDENCE_KINDS = ("review", "qa")
PROTECTED = (".github/",)            # the checks that judge a PR; agents may not change them
OWNER_LABEL = "owner-approved"       # the owner's yes to a change of the protected files
BUMP = {"fix": 2, "feat": 1, "feat!": 0}   # which part of MAJOR.MINOR.PATCH goes up


def title_kind(title: str) -> str | None:
    """'fix', 'feat' or 'feat!' when the title follows the rule, else None."""
    m = TITLE.match(title or "")
    return m.group(1) if m else None


def parse_version(text: str | None) -> tuple[int, int, int] | None:
    """'2.0' and '2.0.0' both read as (2, 0, 0)."""
    if not text or not re.fullmatch(r"\d+(?:\.\d+){1,2}", text.strip()):
        return None
    parts = [int(p) for p in text.strip().split(".")]
    return tuple(parts + [0] * (3 - len(parts)))


def fmt(version: tuple[int, int, int]) -> str:
    return ".".join(str(p) for p in version)


def bump(version: tuple[int, int, int], kind: str) -> tuple[int, int, int]:
    i = BUMP[kind]
    return tuple(list(version[:i]) + [version[i] + 1] + [0] * (2 - i))


def _frontmatter(skill_md: str) -> tuple[list[str], int]:
    """The lines of SKILL.md and the index of the line that closes the frontmatter (0 if there is none)."""
    lines = (skill_md or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return lines, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines, i
    return lines, 0


def skill_version(skill_md: str | None) -> tuple[int, int, int] | None:
    """The version in the frontmatter of a SKILL.md (metadata.version, or a top-level version)."""
    lines, end = _frontmatter(skill_md or "")
    for line in lines[1:end]:
        m = VERSION_LINE.match(line)
        if m:
            return parse_version(m.group("v"))
    return None


def set_skill_version(skill_md: str, version: tuple[int, int, int]) -> str:
    """SKILL.md with the version written into the frontmatter, added under metadata if it is missing."""
    lines, end = _frontmatter(skill_md)
    if not end:
        raise ValueError("SKILL.md has no frontmatter")
    for i in range(1, end):
        m = VERSION_LINE.match(lines[i])
        if m:
            lines[i] = f'{m.group("head")}"{fmt(version)}"'
            break
    else:
        meta = next((i for i in range(1, end) if lines[i].rstrip() == "metadata:"), None)
        if meta is None:
            lines[end:end] = ["metadata:", f'  version: "{fmt(version)}"']
        else:
            lines.insert(meta + 1, f'  version: "{fmt(version)}"')
    return "\n".join(lines) + ("\n" if skill_md.endswith("\n") else "")


def without_version(skill_md: str) -> str:
    """SKILL.md with the version line blanked: two releases compare equal if only the number differs."""
    lines, end = _frontmatter(skill_md or "")
    return "\n".join("" if 0 < i < end and VERSION_LINE.match(line) else line for i, line in enumerate(lines))


def top_dir(path: str) -> str | None:
    return path.split("/", 1)[0] if "/" in path else None


def protected_files(paths: list[str]) -> list[str]:
    return [p for p in paths if p.startswith(PROTECTED)]


def check_title(title: str) -> tuple[bool, str]:
    if title_kind(title):
        return True, "Title starts with fix:, feat: or feat!:"
    return False, "Title must start with 'fix: ', 'feat: ' or 'feat!: '"


def check_version(title: str, skills: dict[str, tuple[str | None, str | None]]) -> tuple[bool, str]:
    """skills maps each skill folder the PR touches to (SKILL.md on main, SKILL.md in the PR)."""
    kind = title_kind(title)
    if len(skills) > 1:
        return False, "One PR is one change: it touches " + ", ".join(sorted(skills))
    if not skills:
        return True, "No skill changed, so no version is needed"
    (name, (base, head)), = skills.items()
    if head is None:
        return True, f"{name} is removed, so there is no version to bump"
    new = skill_version(head)
    if new is None:
        return False, f"{name}/SKILL.md has no valid version (MAJOR.MINOR.PATCH)"
    old = skill_version(base)
    if old is None:
        return True, f"{name} starts at {fmt(new)}"
    if kind is None:
        return False, "The version follows the title, and the title is not valid yet"
    want = bump(old, kind)
    if new == want:
        return True, f"{name} {fmt(old)} -> {fmt(new)} ({kind})"
    return False, f"{name}: '{kind}:' needs {fmt(old)} -> {fmt(want)}, found {fmt(new)}. Run bump.py"


def check_protected(paths: list[str], owner_approved: bool) -> tuple[bool, str]:
    hit = protected_files(paths)
    if not hit:
        return True, "No pipeline file changed"
    if owner_approved:
        return True, f"Pipeline files changed with the owner's '{OWNER_LABEL}' label"
    return False, f"Changes {hit[0]}: needs the owner's '{OWNER_LABEL}' label"


def find_evidence(comments: list[dict], head_sha: str, owner: str) -> dict[str, str]:
    """The newest evidence per kind that names this exact commit: {'review': 'pass', 'qa': 'fail'}.
    Evidence that does not name its model and effort comes back as 'unsigned' and does not count.

    comments: [{'author': login, 'body': text}] oldest first. Only the owner's account counts, and only a
    comment that carries a report below its marker line."""
    found = {}
    for c in comments:
        if (c.get("author") or "").lower() != owner.lower():
            continue
        body = c.get("body") or ""
        m = EVIDENCE.search(body)
        if m and m.group(2) == head_sha and body.replace(m.group(0), "").strip():
            found[m.group(1)] = m.group(3) if m.group(4) and m.group(5) else UNSIGNED
    return found


def check_evidence(found: dict[str, str], needed: bool, undo_of: str | None = None) -> tuple[bool, str]:
    if undo_of:
        return True, f"Undo: the files equal the released {undo_of}"
    if not needed:
        return True, "No skill or pipeline file changed, so no evidence is needed"
    missing = [k for k in EVIDENCE_KINDS if k not in found]
    failed = [k for k in EVIDENCE_KINDS if found.get(k) == "fail"]
    if failed:
        return False, "Evidence says fail: " + ", ".join(failed)
    unsigned = [k for k in EVIDENCE_KINDS if found.get(k) == UNSIGNED]
    if unsigned:
        return False, "Evidence does not name its model and effort: " + ", ".join(unsigned)
    if missing:
        return False, "No evidence for this exact commit: " + ", ".join(missing)
    return True, "Review and QA evidence passed for this exact commit"


def previous_release(tags: list[str], skill: str, current: tuple[int, int, int]) -> tuple[str, tuple] | None:
    """The newest tag of this skill below the current version: where undo goes back to."""
    older = []
    for tag in tags:
        name, sep, v = tag.rpartition("--v")
        version = parse_version(v)
        if sep and name == skill and version and version < current:
            older.append((version, tag))
    if not older:
        return None
    version, tag = max(older)
    return tag, version
