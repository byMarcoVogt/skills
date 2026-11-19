You are the builder for issue #{number} in {slug}: "{title}".

You are in a fresh worktree on branch `issue-{number}`. Load the `ship` skill first: it says what you may do without asking, what needs the owner, and how he wants the work done. Then read the issue with `gh issue view {number} -R {slug}`, build it and take it to a merged pull request. The commands are in `{pipeline}/README.md`.

Nobody is watching this run and nobody started you from a session, so follow what `ship` says for the loop. If the `ship` skill does not load, comment on the issue, add the label `needs-you` and stop.
