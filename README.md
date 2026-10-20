# Skills

Agent Skills I built for my own daily work with Claude Code. Each one is a folder with a `SKILL.md` and its own README.

| Skill | What it does |
|---|---|
| [Think it through](think-it-through) | Interviews you about an idea, plan or decision, one question at a time, until you and the agent reach a shared understanding. |
| [Close the gap](close-the-gap) `experimental` | Finds the most worthwhile gap between how you work with AI and the frontier. Then it teaches you about it, from the frontier back to your work. |
| [House style](house-style) | Holds the agent to your style in how it writes, designs and communicates. |
| [Earn its place](earn-its-place) | Switches a skill off for a window of real work, then rebuilds only what went missing, or retires it. |

## Design principles

**Skills have to change faster than models.** Every skill is a hypothesis that the model can't do this on its own yet. Instructions written for previous models become dead weight, or even gate what newer models could do for you.

**1. A skill earns its place only if work goes worse without it.**
- Real use is the primary evidence. [Earn its place](earn-its-place) switches a skill off for a window of real work, then rebuilds what went missing or added value, or retires the skill.

*Example:* House style comes from 1,087 of my own corrections, choices and approvals since August 2026.

**2. A skill is valuable real estate.**
- Each word has to carry meaning and invoke the right behavior.
- The benchmark: each SKILL.md records its size at the last major release in `metadata.benchmark`.
  - Minor versions stay at or under it.
  - To add, condense first or cut what is no longer needed.
  - What became deterministic is left out of the text and moves into code or hooks.
  - Only a new major version resets it, ideally after an [Earn its place](earn-its-place) trial.

*Example:* Earn its place came from such a reset. It replaced my 106-line skill-writer with 17 lines.

## Install

```bash
npx skills add byMarcoVogt/skills
```

[`skills`](https://github.com/vercel-labs/skills) asks which skills to install and for which agents. It needs Node.js 22.20 or newer.

One skill only:

```bash
npx skills add byMarcoVogt/skills --skill think-it-through
```

## License

[MIT](LICENSE)
