"""Attach review or QA evidence to a pull request, bound to the commit it was given for.

    python evidence.py --repo owner/name --pr 12 --kind review --result pass --file report.md \\
                       --model claude-fable-5-2 --effort medium
    python evidence.py --repo owner/name --pr 12 --kind qa --result pass --file report.md --route-run RUN

The report becomes a PR comment whose first line names the PR's current commit. A later commit has another
id, so the gate no longer counts this comment and the evidence has to be given again.

Every piece of evidence says which model produced it and at what reasoning effort; the gate does not count it
otherwise. The values come from whoever knows them, not from the checker describing itself: for a run through
route, from route's own record of that run (--route-run); for an agent, the model and effort it was started
with (--model, --effort). A value that cannot be had is given as 'unknown', never guessed.
"""
import argparse
import json
import os
import re
from pathlib import Path

import rules
from common import Failed, api, main


RUN_ID = re.compile(r"[A-Za-z0-9-]+")


def route_record(run: str, report: str) -> tuple[str, str, str]:
    """Model and effort of one route run, read from the record route itself wrote for it, and the folder it was
    found in. The report must carry that run's answer: another run's record cannot sign it."""
    if not RUN_ID.fullmatch(run):
        raise Failed(f"'{run}' is not a route run id (letters, digits and hyphens)")
    where = os.environ.get("ROUTE_RUNS") or (os.environ.get("LOCALAPPDATA") and
                                             str(Path(os.environ["LOCALAPPDATA"]) / "route" / "runs"))
    if not where:
        raise Failed("Cannot find route's runs: neither ROUTE_RUNS nor LOCALAPPDATA is set")
    runs = Path(where)
    folders = [runs / run] + ([d / run for d in sorted(runs.iterdir()) if d.is_dir()] if runs.is_dir() else [])
    hits = [f for f in folders if (f / "meta.json").is_file()]
    if len(hits) != 1:
        raise Failed(f"Found {len(hits)} records for route run '{run}' under {runs}; expected one")
    try:
        meta = json.loads((hits[0] / "meta.json").read_text(encoding="utf-8"))
        answer = (hits[0] / "answer.md").read_text(encoding="utf-8")
    except (OSError, ValueError) as e:
        raise Failed(f"Cannot read the record of route run '{run}': {e}")
    if not isinstance(meta, dict) or meta.get("state") not in ("ok", "review"):
        state = meta.get("state") if isinstance(meta, dict) else "unreadable"
        raise Failed(f"route run '{run}' ended as '{state}': a run without an answer is not evidence")
    squeeze = lambda text: " ".join(text.split())
    if not squeeze(answer) or squeeze(answer) not in squeeze(report):
        raise Failed(f"The report does not contain the answer of route run '{run}'; it must go in as it came")
    return str(meta.get("model") or "unknown"), str(meta.get("effort") or "unknown"), hits[0].as_posix()


def cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--kind", choices=("review", "qa"), required=True)
    ap.add_argument("--result", choices=("pass", "fail"), required=True)
    ap.add_argument("--file", required=True, help="the report: what was looked at or run, and what came out")
    ap.add_argument("--by", default="", help="who gave it, for example 'second Claude agent' or 'GPT through route'")
    ap.add_argument("--route-run", help="the id of the route run that produced the report; model and effort are read from it")
    ap.add_argument("--model", help="the exact model id the checker ran on, or 'unknown'")
    ap.add_argument("--effort", help="the reasoning effort the checker ran at, or 'unknown'")
    a = ap.parse_args()

    report = Path(a.file).read_text(encoding="utf-8").strip()
    if not report:
        raise Failed("The report file is empty")
    if a.route_run:
        if a.model or a.effort:
            raise Failed("Give --route-run or --model with --effort, not both: route's record is the source")
        model, effort, folder = route_record(a.route_run, report)
        source = f"read from route's record of that run, `{folder}`"
    elif a.model and a.effort:
        model, effort = a.model, a.effort
        source = "as given by the session that started the checker"
    else:
        raise Failed("Say who checked: --route-run RUN, or --model with --effort ('unknown' where a value cannot be had)")
    # the same two patterns the gate reads the marker with: what is posted here must count there
    if not re.fullmatch(rules.MODEL, model):
        raise Failed(f"'{model}' is not a model id (letters, digits, . _ : / -)")
    if not re.fullmatch(rules.EFFORT, effort):
        raise Failed(f"'{effort}' is not an effort level (letters, digits, . _ -)")

    pr = api(f"repos/{a.repo}/pulls/{a.pr}")
    if pr is None:
        raise Failed(f"{a.repo} has no pull request {a.pr}")
    sha = pr["head"]["sha"]
    title = {"review": "Review", "qa": "QA"}[a.kind]
    body = (f"<!-- pipeline-evidence kind={a.kind} sha={sha} result={a.result} model={model} effort={effort} -->\n"
            f"### {title} evidence: {a.result}, by `{model}` at effort `{effort}`\n\n"
            f"Model and effort {source}. For commit `{sha[:10]}`" +
            (f", by {a.by}" if a.by else "") + f".\n\n{report}\n")
    comment = api(f"repos/{a.repo}/issues/{a.pr}/comments", "POST", {"body": body})
    print(comment["html_url"])
    return 0


if __name__ == "__main__":
    main(cli)
