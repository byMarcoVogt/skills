"""Attach review or QA evidence to a pull request, bound to the commit it was given for.

    python evidence.py --repo owner/name --pr 12 --kind review --result pass --file report.md

The report becomes a PR comment whose first line names the PR's current commit. A later commit has another
id, so the gate no longer counts this comment and the evidence has to be given again.
"""
import argparse
from pathlib import Path

from common import Failed, api, main


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--kind", choices=("review", "qa"), required=True)
    ap.add_argument("--result", choices=("pass", "fail"), required=True)
    ap.add_argument("--file", required=True, help="the report: what was looked at or run, and what came out")
    ap.add_argument("--by", default="", help="who gave it, for example 'second Claude agent' or 'GPT through route'")
    a = ap.parse_args()

    report = Path(a.file).read_text(encoding="utf-8").strip()
    if not report:
        raise Failed("The report file is empty")
    pr = api(f"repos/{a.repo}/pulls/{a.pr}")
    if pr is None:
        raise Failed(f"{a.repo} has no pull request {a.pr}")
    sha = pr["head"]["sha"]
    title = {"review": "Review", "qa": "QA"}[a.kind]
    body = (f"<!-- pipeline-evidence kind={a.kind} sha={sha} result={a.result} -->\n"
            f"### {title} evidence: {a.result}\n\nFor commit `{sha[:10]}`" + (f", by {a.by}" if a.by else "") +
            f".\n\n{report}\n")
    comment = api(f"repos/{a.repo}/issues/{a.pr}/comments", "POST", {"body": body})
    print(comment["html_url"])
    return 0


if __name__ == "__main__":
    main(cli)
