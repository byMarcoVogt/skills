# Skills

Agent Skills I built for my own daily work with Claude Code and Codex. Each one is a folder with a `SKILL.md` and its own README.

| Skill | What it does |
|---|---|
| [Think it through](think-it-through) | Interviews you about an idea, plan or decision, one question at a time, until you and the agent reach a shared understanding. |
| [Close the gap](close-the-gap) `experimental` | Finds the most worthwhile gap between how you work with AI and the frontier. Then it teaches you about it, from the frontier back to your work. |
| [Skill trials](skill-trials) | Runs one ablation or variant of a skill through a window of real work, then keeps it, rebuilds only what went missing, or retires the skill. |

## Design principles

**Skills have to change faster than models.** Every skill is a hypothesis that the model can't do this on its own yet. Instructions written for previous models become dead weight, or even gate what newer models could do for you.

**1. A skill earns its place only if work goes worse without it.**
- Real use is the primary evidence. [Skill trials](skill-trials) runs one ablation or variant of a skill through a window of real work, then keeps it, rebuilds what went missing or added value, or retires the skill.

*How I measure:* a trial is written down before it starts: what should go worse or better, and over how many sessions. Afterwards I compare those sessions with recent ones on how often I had to step in (correct or re-explain). If I switch back during the trial, that settles it.

**2. A skill is valuable real estate.**
- Each word has to carry meaning and invoke the right behavior.
- The benchmark: each SKILL.md records its size in bytes at the last major release in `metadata.benchmark`. Lines don't count, so formatting for readers stays free.
  - Minor versions stay at or under it.
  - To add, condense first or cut what is no longer needed.
  - What became deterministic is left out of the text and moves into code or hooks.
  - Only a new major version resets it, ideally after a [Skill trials](skill-trials) trial.

*Example:* Skill trials, then called Earn its place, came from such a reset. It replaced my 106-line skill-writer with 17 lines.

## Install

```bash
# all skills, you pick in a menu
npx skills add byMarcoVogt/skills

# one skill, no questions (also for agents)
npx skills add byMarcoVogt/skills --skill think-it-through -a claude-code -g -y
```

For Codex, use `-a codex`. [`npx skills`](https://github.com/vercel-labs/skills) is Vercel's installer and needs Node.js 22.20 or newer. Skill trials needs Think it through.

Then start a new session. Ask in your own words and the agent picks the skill that fits (*"Grill me on this plan"* starts Think it through), or call one by name: `/think-it-through` in Claude Code, `$think-it-through` in Codex. [Close the gap](close-the-gap) starts only by name.

Update: `npx skills update -g`. Uninstall: `npx skills remove -g think-it-through` (the skill's folder name).

## Mods

Mods change the Claude desktop app's own interface, beside the skills. They live in [byMarcoVogt/mods](https://github.com/byMarcoVogt/mods), starting with Token Report: context, cache and cost above the prompt.

## License

[MIT](LICENSE)
