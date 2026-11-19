# Pipeline

How a change gets from a branch to main in this repo and in the private skills repo. The rules are enforced by the gate on GitHub, by local git hooks and by a Claude Code hook. This page only lists the commands.

`P` stands for this folder in the live clone of `byMarcoVogt/skills` (the private repo uses the same scripts).

| Step | Command |
|---|---|
| Start | `git -C <live clone> worktree add <worktrees>/<repo>/<branch> -b <branch> origin/main` and work there. The live clone itself is read-only. |
| Version | `python P/bump.py --title "fix: ..."` writes the number the title asks for. One PR changes one skill. |
| Pull request | Push the branch and open a PR. The title starts with `fix: `, `feat: ` or `feat!: `. |
| Evidence | `python P/evidence.py --repo <owner/name> --pr <n> --kind review --result pass --file report.md --model <id> --effort <level>`, and the same with `--kind qa`. For a report that came through route, give `--route-run <run id>` in place of `--model` and `--effort`: the values are then read from route's own record. For an agent, they are the model and effort it was started with; write `unknown` where a value cannot be had. Review and QA come from agents other than the builder. A new commit voids both. |
| Merge | `python P/merge.py --repo <owner/name> --pr <n>` merges when the gate is green, waits for the tag and updates this machine. |
| Undo | `python P/undo.py <skill>` goes back one version. Do this first when live use breaks, then fix in a new PR. |
| Check | `python P/gate.py pr --repo <owner/name> --pr <n>` shows what the gate says, without writing anything. |

Privacy: before a comment, a pull request title or text, or a push goes to a public repo, `privacy.py` scans it for home, app-data and temp paths, session ids and the terms in the owner's local list `~/.claude/skill-pipeline/private-terms.txt` (one per line, never committed). A hit stops it and names the kind and the position, never the term. The scripts' own posts and the pre-push hook do this by themselves; for a text you post with `gh` yourself, run `python P/privacy.py text --repo <owner/name> --file <text.md>` first.

A change under `.github/` needs the owner's `owner-approved` label on the PR. Tags and releases are made by the release workflow, never by hand.

The loop: a scheduled task in the Claude app runs `python P/loop.py --next` every hour. It takes one issue marked `ready`, makes its worktree and prints the builder's instructions; when nothing is ready it prints nothing.

Tests: `python -m unittest discover -s .github/pipeline/tests`
