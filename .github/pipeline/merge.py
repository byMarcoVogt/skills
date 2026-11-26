"""Merge a pull request once the gate is green, wait for its tag, and bring this machine up to date.

    python merge.py --repo owner/name --pr 12

This is the only way a merge happens. It merges the exact commit the gate judged, as one squash commit whose
subject is the PR title. On a repo without branch protection it is also what holds the line: it refuses a PR
whose four statuses are not all green.

A repo without a gate (no .github/pipeline on its main and not in the pipeline config, e.g. a project with only
a test workflow) is merged here too, so there stays one way to merge: it waits until every check and status on
the PR's head commit is green, merges exactly that commit, and then only fetches the live copy on this machine.
The owner keeps edits in such live copies, so they are never pulled or reset.
"""
import argparse
import time
from pathlib import Path

import rules
from common import CONTEXTS, Failed, api, config, main, paged, repo_entry, run
from sync import sync

OK = {"success", "neutral", "skipped"}      # a check run that ended like this does not stand in the way


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


def has_gate(repo: str) -> bool:
    """A pipeline repo from the config, or any repo with .github/pipeline on its main, has a gate."""
    try:
        repo_entry(repo)
        return True
    except Failed:
        pass
    return api(f"repos/{repo}/contents/.github/pipeline") is not None


def checks(repo: str, sha: str) -> dict:
    """Every check run and every status on this commit: {name: (state, text)}. state is success, pending or the
    red result GitHub gave."""
    got, page = {}, 1
    while True:
        batch = (api(f"repos/{repo}/commits/{sha}/check-runs?per_page=100&page={page}") or {}).get("check_runs", [])
        for c in batch:
            if c["status"] != "completed":
                got[c["name"]] = ("pending", c["status"])
            else:
                got[c["name"]] = ("success" if c["conclusion"] in OK else c["conclusion"] or "failure", "")
        if len(batch) < 100:
            break
        page += 1
    combined = api(f"repos/{repo}/commits/{sha}/status") or {"statuses": []}
    for st in combined["statuses"]:
        got[st["context"]] = (st["state"], st["description"] or "")
    return got


def wait_checks(repo: str, sha: str, seconds: int) -> None:
    """For a repo without a gate: wait until there is at least one check and every check is green. A red one
    refuses at once, a pending or missing one after the wait."""
    end = time.time() + seconds
    while True:
        got = checks(repo, sha)
        red = {n: v for n, v in got.items() if v[0] not in ("success", "pending")}
        if red:
            raise Failed("A check is red on this commit, nothing was merged:\n" +
                         "\n".join(f"  {n}: {state} {text}".rstrip() for n, (state, text) in red.items()))
        if got and all(state == "success" for state, _ in got.values()):
            return
        if time.time() > end:
            if not got:
                raise Failed("No check has reported on this commit, nothing was merged. A repo without a gate is "
                             "merged only on green checks.")
            raise Failed("Checks are still running on this commit, nothing was merged:\n" +
                         "\n".join(f"  {n}: {text}" for n, (state, text) in got.items() if state == "pending"))
        time.sleep(10)


def live_copy(repo: str, given: str | None) -> Path | None:
    """The clone of this repo on this machine: --live if given, else a folder of the repo's name next to the
    pipeline repos whose origin is this repo."""
    if given:
        return Path(given)
    try:
        parents = {Path(r["path"]).parent for r in config()["repos"]}
    except Failed:
        return None
    for parent in parents:
        path = parent / repo.split("/")[1]
        if (path / ".git").exists():
            url = run(["git", "remote", "get-url", "origin"], cwd=path, check=False).strip().lower()
            if url.removesuffix(".git").endswith(repo.lower()):
                return path
    return None


def merge_nogate(repo: str, number: int, pr: dict, wait: int, live: str | None = None) -> None:
    if not pr["merged"]:
        if pr["state"] != "open":
            raise Failed(f"Pull request {number} is closed, not merged.")
        sha = pr["head"]["sha"]
        wait_checks(repo, sha, wait)
        now = api(f"repos/{repo}/pulls/{number}")
        if now["head"]["sha"] != sha:
            raise Failed(f"The pull request moved on from {sha[:7]} to {now['head']['sha'][:7]} while its checks "
                         "ran, nothing was merged. Run merge.py again for the new commit.")
        api(f"repos/{repo}/pulls/{number}/merge", "PUT",
            {"merge_method": "squash", "sha": sha, "commit_title": f"{pr['title']} (#{number})", "commit_message": ""})
        try:
            api(f"repos/{repo}/git/refs/heads/{pr['head']['ref']}", "DELETE")
        except Failed:
            pass
        print(f"merged #{number}: {pr['title']}")
    path = live_copy(repo, live)
    if path is None:
        print(f"no live copy of {repo} found on this machine, nothing fetched (give it with --live <folder>)")
        return
    # fetch only: the owner keeps edits in such a live copy, a pull or reset could touch them
    try:
        run(["git", "fetch", "origin", "--prune", "--quiet"], cwd=path)
    except Failed as e:
        print(f"needs attention: merged, but {path} could not fetch: {e}")
        return
    print(f"fetched {path}, not pulled: it may hold edits that are not on main")


def merge(repo: str, number: int, wait: int = 180, live: str | None = None) -> None:
    pr = api(f"repos/{repo}/pulls/{number}")
    if pr is None:
        raise Failed(f"{repo} has no pull request {number}")
    if not has_gate(repo):
        return merge_nogate(repo, number, pr, wait, live)
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
    ap.add_argument("--wait", type=int, default=180, help="seconds to wait for the gate (or the checks) and for the tag")
    ap.add_argument("--live", help="repo without a gate: its clone on this machine, if not found by name")
    a = ap.parse_args()
    merge(a.repo, a.pr, a.wait, a.live)
    return 0


if __name__ == "__main__":
    main(cli)
