"""Merge a pull request once the gate is green, wait for its tag, and bring this machine up to date.

    python merge.py --repo owner/name --pr 12

This is the only way a merge happens. It merges the exact commit the gate judged, as one squash commit whose
subject is the PR title. On a repo without branch protection it is also what holds the line: it refuses a PR
whose four statuses are not all green.
"""
import argparse
import time

import rules
from common import CONTEXTS, Failed, api, main, paged, repo_entry
from sync import sync


def statuses(repo: str, sha: str) -> dict:
    combined = api(f"repos/{repo}/commits/{sha}/status") or {"statuses": []}
    return {s["context"]: (s["state"], s["description"] or "") for s in combined["statuses"] if s["context"] in CONTEXTS}


def wait_green(repo: str, sha: str, seconds: int) -> None:
    """Wait until all four statuses are green. A red one may be stale (the gate needs some seconds to judge
    fresh evidence or a new title), so red gets a short grace period before it counts."""
    start = time.time()
    end, grace = start + seconds, start + min(seconds, 60)
    while True:
        got = statuses(repo, sha)
        bad = {c: got.get(c, ("missing", "the gate has not reported yet")) for c in CONTEXTS
               if got.get(c, ("missing",))[0] != "success"}
        if not bad:
            return
        waiting = all(state in ("missing", "pending") for state, _ in bad.values())
        if time.time() > (end if waiting else grace):
            raise Failed("The gate is not green for this commit:\n" +
                         "\n".join(f"  {c}: {state}: {text}" for c, (state, text) in bad.items()))
        time.sleep(5)


def merge(repo: str, number: int, wait: int = 180) -> None:
    pr = api(f"repos/{repo}/pulls/{number}")
    if pr is None:
        raise Failed(f"{repo} has no pull request {number}")
    if not pr["merged"]:
        sha = pr["head"]["sha"]
        wait_green(repo, sha, wait)
        api(f"repos/{repo}/pulls/{number}/merge", "PUT",
            {"merge_method": "squash", "sha": sha, "commit_title": f"{pr['title']} (#{number})", "commit_message": ""})
        try:
            api(f"repos/{repo}/git/refs/heads/{pr['head']['ref']}", "DELETE")
        except Failed:
            pass        # GitHub already removed the branch
        print(f"merged #{number}: {pr['title']}")

    # the release workflow tags the new version; wait for it, then make it live here
    files = paged(f"repos/{repo}/pulls/{number}/files")
    skills = sorted({d for d in (rules.top_dir(f["filename"]) for f in files) if d})
    want = []
    for skill in skills:
        text = api(f"repos/{repo}/contents/{skill}/SKILL.md?ref=main", raw=True)
        version = rules.skill_version(text)
        if version:
            want.append((skill, version))
    end = time.time() + wait
    while want:
        have = {(t["name"].rpartition("--v")[0], rules.parse_version(t["name"].rpartition("--v")[2]))
                for t in paged(f"repos/{repo}/tags")}
        want = [w for w in want if w not in have]
        if not want:
            break
        if time.time() > end:
            raise Failed(f"Merged, but no tag yet for {want[0][0]} {rules.fmt(want[0][1])}. Check the Release workflow.")
        time.sleep(5)
    repo_entry(repo)
    for problem in sync():
        print(f"needs attention: {problem}")


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--wait", type=int, default=180, help="seconds to wait for the gate and for the tag")
    a = ap.parse_args()
    merge(a.repo, a.pr, a.wait)
    return 0


if __name__ == "__main__":
    main(cli)
