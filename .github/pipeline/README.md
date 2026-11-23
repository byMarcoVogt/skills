# Pipeline

How a change gets from a branch to main in this repo and in the private skills repo. The rules are enforced by the gate on GitHub, by local git hooks and by a Claude Code hook. This page only lists the commands.

`P` stands for this folder in the live clone of `byMarcoVogt/skills` (the private repo uses the same scripts).

| Step | Command |
|---|---|
| Start | `git -C <live clone> worktree add <worktrees>/<repo>/<branch> -b <branch> origin/main` and work there. The live clone itself is read-only. |
| Version | `python P/bump.py --title "fix: ..."` writes the number the title asks for. One PR changes one skill. |
| Pull request | Push the branch and open a PR. The title starts with `fix: `, `feat: ` or `feat!: `. |
| Evidence | `python P/evidence.py --repo <owner/name> --pr <n> --kind review --result pass --file report.md --model <id> --effort <level>`. For a report that came through route, give `--route-run <run id>` in place of `--model` and `--effort`: the values are then read from route's own record. For an agent, they are the model and effort it was started with; write `unknown` where a value cannot be had. The gate needs one passing `review` from an agent other than the builder. A `qa` (`--kind qa`) is optional: it is shown when given, and a `qa` that says fail blocks. Evidence follows the PR's content: it counts at the commit it was given for and at any later commit whose changed files have the same blob ids, so a merge of `main` that leaves those files alone keeps it. A change to one of the PR's files voids it. |
| Merge | `python P/merge.py --repo <owner/name> --pr <n>` merges when the gate is green, waits for the tag and updates this machine. |
| Undo | `python P/undo.py <skill>` goes back one version. Do this first when live use breaks, then fix in a new PR. |
| Check | `python P/gate.py pr --repo <owner/name> --pr <n>` shows what the gate says, without writing anything. |

A change under `.github/` needs the same review as any other change; the status `pipeline/protected-files` stays only so branch protection need not change, and it passes. Tags and releases are made by the release workflow, never by hand; the pre-push hook refuses pushes to `main` and of tags.

The Claude Code hook (`git_guard.py`) judges each git or gh call by the repo it acts on (`-C`, `--repo`/`-R`, a `repos/...` path, else the last `cd`, else the session's folder), so text inside quotes and calls in other repos are left alone. In a pipeline repo it blocks force pushes, skipping or re-pointing the git hooks, `gh pr merge` (use `merge.py`), `gh repo delete|rename|archive` and writing commit statuses; it also keeps the live clone read-only and blocks deleting or moving a live skill folder.

The loop: a scheduled task in the Claude app runs `python P/loop.py --next` every hour. It takes one issue marked `ready`, makes its worktree and prints the builder's instructions; when nothing is ready it prints nothing.

Tests: `python -m unittest discover -s .github/pipeline/tests`
