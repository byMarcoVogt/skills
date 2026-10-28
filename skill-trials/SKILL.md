---
name: skill-trials
description: Tests whether a skill or set of skills still earns its place. Runs one ablation or variant through a window of real work, then keeps it, rebuilds what was missing or retires the skill. Use when the user wants to rework, test or retire a skill, asks whether one still pays off, or when a trial's window is up.
metadata:
  version: "3.0"
  benchmark: "1731 bytes"
---

A skill earns its place only if work goes worse without it.

## Before

- Settle with me via /think-it-through whether we need the skills and what they should do, in intent.md, with any rare harm a window can't show.
- If they never fire or are covered elsewhere, propose retiring now.
- Else propose one ablation (off, or a part cut) or variant (a part condensed or rewritten) and pre-register it in trial.md: what should go worse or better, how many sessions decide.
- Keep intent.md and trial.md in ~/skill-trials/<skill>/.
- Once I agree, make the change in every agent that has the skills.
- Copy recent sessions that used them, as the baseline.
- Schedule a task on this machine that copies the window's sessions and starts the second pass when the window ends.

## After

- In a fresh session, evaluate the window against the baseline and what we wrote.
- An ablation or a condensed part passes if work is no worse. A rewrite passes only if it does better where trial.md said it would.
- Audit the transcripts of both: how often did I intervene (correct or re-explain) per session?
- If I switched back during the window, that is the verdict.
- Look as hard for needs nobody wrote down.
- Record in trial.md: keep the change, rebuild only what is needed, or retire. If unclear, retire unless intent.md names a rare harm.
