"""The PR gate. Reads a pull request and says, per rule, whether it may merge.

    python gate.py pr --repo owner/name --pr 12 [--post]     GitHub runs this; --post writes commit statuses
    python gate.py local --base origin/main --head HEAD      the pre-push hook runs this

It never runs code from the PR: it reads titles, file lists and file contents through the API. The statuses
belong to one exact commit, so a new commit starts with none. Evidence still counts at a new commit when the PR's
changed files are the same (a merge of main that leaves them alone); a change to one of them voids it.
"""
import argparse

import rules
from common import CONTEXTS, Failed, api, main, paged, run


def _skills(paths, read_base, read_head) -> dict:
    found = {}
    for d in sorted({rules.top_dir(p) for p in paths} - {None}):
        base, head = read_base(f"{d}/SKILL.md"), read_head(f"{d}/SKILL.md")
        if base is not None or head is not None:
            found[d] = (base, head)
    return found


def _tree(repo: str, ref: str, skill: str) -> dict | None:
    tree = api(f"repos/{repo}/git/trees/{ref}?recursive=1")
    if tree is None or tree.get("truncated"):
        return None
    return {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob" and e["path"].startswith(skill + "/")}


def _undo_of(repo: str, title: str, head: str, skills: dict) -> str | None:
    """The tag this PR goes back to, if its skill folder equals that release except for the version line."""
    m = rules.UNDO_TITLE.match(title or "")
    if not m or list(skills) != [m.group("skill")]:
        return None
    skill, version = m.group("skill"), rules.parse_version(m.group("version"))
    tags = [t["name"] for t in paged(f"repos/{repo}/tags")]
    tag = next((t for t in tags if t.rpartition("--v")[0] == skill
                and rules.parse_version(t.rpartition("--v")[2]) == version), None)
    if not tag:
        return None
    old, new = _tree(repo, tag, skill), _tree(repo, head, skill)
    if old is None or new is None or set(old) != set(new):
        return None
    for path in old:
        if old[path] == new[path]:
            continue
        if path != f"{skill}/SKILL.md":
            return None
        a = api(f"repos/{repo}/contents/{path}?ref={tag}", raw=True)
        b = api(f"repos/{repo}/contents/{path}?ref={head}", raw=True)
        if rules.without_version(a) != rules.without_version(b):
            return None
    return tag


def evaluate_pr(repo: str, number: int) -> tuple[str, dict]:
    pr = api(f"repos/{repo}/pulls/{number}")
    if pr is None:
        raise Failed(f"{repo} has no pull request {number}")
    owner, head, base, title = repo.split("/")[0], pr["head"]["sha"], pr["base"]["ref"], pr["title"]
    files = paged(f"repos/{repo}/pulls/{number}/files")
    paths = [f["filename"] for f in files] + [f["previous_filename"] for f in files if f.get("previous_filename")]
    skills = _skills(paths,
                     lambda p: api(f"repos/{repo}/contents/{p}?ref={base}", raw=True),
                     lambda p: api(f"repos/{repo}/contents/{p}?ref={head}", raw=True))

    comments = [{"author": c["user"]["login"], "body": c["body"]}
                for c in paged(f"repos/{repo}/issues/{number}/comments")]
    needed = bool(skills) or bool(rules.protected_files(paths))
    found = rules.find_evidence(comments, head, owner, rules.files_hash(files))
    return head, {
        "pipeline/title": rules.check_title(title),
        "pipeline/version": rules.check_version(title, skills),
        "pipeline/evidence": rules.check_evidence(found, needed, _undo_of(repo, title, head, skills)),
        "pipeline/protected-files": rules.check_protected(paths),
    }


def evaluate_local(base: str, head: str) -> dict:
    """What can be known before a PR exists: one skill per change, and a version that one of the titles allows."""
    def show(ref):
        return lambda p: run(["git", "show", f"{ref}:{p}"], check=False) or None
    paths = run(["git", "diff", "--name-only", f"{base}...{head}"]).split()
    merge_base = run(["git", "merge-base", base, head]).strip()
    skills = _skills(paths, show(merge_base), show(head))
    tries = [rules.check_version(f"{kind}: x", skills) for kind in rules.BUMP]
    ok = next((t for t in tries if t[0]), None)
    return {"pipeline/version": ok or (False, tries[0][1].split(":")[0] + ": the version must go up by one step. Run bump.py")}


def cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("pr")
    p.add_argument("--repo", required=True)
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--post", action="store_true")
    q = sub.add_parser("local")
    q.add_argument("--base", default="origin/main")
    q.add_argument("--head", default="HEAD")
    a = ap.parse_args()

    if a.mode == "local":
        results = evaluate_local(a.base, a.head)
    else:
        head, results = evaluate_pr(a.repo, a.pr)
        assert set(results) == set(CONTEXTS)
    for context, (ok, text) in results.items():
        print(f"{'ok  ' if ok else 'FAIL'} {context}: {text}")
        if a.mode == "pr" and a.post:
            api(f"repos/{a.repo}/statuses/{head}", "POST", {
                "state": "success" if ok else "failure", "context": context, "description": text[:140],
                "target_url": f"https://github.com/{a.repo}/pull/{a.pr}"})
    if a.mode == "pr" and a.post:
        return 0        # the statuses carry the verdict; a red run would only send mail
    return 0 if all(ok for ok, _ in results.values()) else 1


if __name__ == "__main__":
    main(cli)
