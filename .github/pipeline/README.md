# Pipeline

How a change gets from a branch to main in this repo and in the private skills repo. The rules are enforced by the gate on GitHub, by local git hooks and by a Claude Code hook. This page only lists the commands.

`P` stands for this folder in the live clone of `byMarcoVogt/skills` (the private repo uses the same scripts).

| Step | Command |
|---|---|
| Start | `git -C <live clone> worktree add <worktrees>/<repo>/<branch> -b <branch> origin/main` and work there. The live clone itself is read-only. |
| Version | `python P/bump.py --title "fix: ..."` writes the number the title asks for. One PR changes one skill. |
| Pull request | Push the branch and open a PR. The title starts with `fix: `, `feat: ` or `feat!: `. |
| Evidence | `python P/evidence.py --repo <owner/name> --pr <n> --commit <sha> --kind review --result pass --file report.md --model <id> --effort <level>`. For a report that came through route, give `--route-run <run id>` in place of `--model` and `--effort`: the values are then read from route's own record. For an agent, they are the model and effort it was started with; write `unknown` where a value cannot be had. The gate records what happened and does not ask anyone to certify a pass. For the review it needs one entry from an agent other than the builder, posted with `--result done` and the reviewer's report as it came: it says a review took place, not that it passed. (An older `pass` counts the same.) For qa it needs one of two things: a qa report (`--kind qa --result pass` meets it, `--result fail` blocks), or a statement that qa was left out: `--kind qa --result skipped --reason "<one sentence>"`, with no report file, where the reason is the report and an empty reason is refused. With no qa entry the check fails and says: post the qa report or say why qa was left out. Any evidence that says fail blocks, even when it does not name its model and effort. Evidence follows the PR's content: it counts at the commit it was given for and at any later commit whose changed files have the same blob ids, so a merge of `main` that leaves those files alone keeps it. A change to one of the PR's files voids it. `--commit <sha>` is required and names the commit the checker looked at: if the PR has moved on since, the evidence is posted only when its changed files are the same at both commits, else it is refused. |
| Merge | `python P/merge.py --repo <owner/name> --pr <n>` merges when the gate is green, waits for the tag and updates this machine. |
| Undo | `python P/undo.py <skill>` goes back one version. Do this first when live use breaks, then fix in a new PR. |
| Check | `python P/gate.py pr --repo <owner/name> --pr <n>` shows what the gate says, without writing anything. |

A change under `.github/` needs the same review as any other change; the status `pipeline/protected-files` stays only so branch protection need not change, and it passes. Tags and releases are made by the release workflow, never by hand.

The loop: a scheduled task in the Claude app runs `python P/loop.py --next` every hour. It takes one issue marked `ready`, makes its worktree and prints the builder's instructions; when nothing is ready it prints nothing.

Tests: `python -m unittest discover -s .github/pipeline/tests`
