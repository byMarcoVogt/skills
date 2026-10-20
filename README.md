# Skills

Agent Skills I built for my own daily work with Claude Code. Each one is a folder with a `SKILL.md` and its own README.

| Skill | What it does |
|---|---|
| [Think it through](think-it-through) | Interviews you about an idea, plan or decision, one question at a time, until you and the agent reach a shared understanding. |
| [Close the gap](close-the-gap) `experimental` | Finds the most worthwhile gap between how you work with AI and the frontier. Then it teaches you about it, from the frontier back to your work. |
| [House style](house-style) | Keeps a model's default habits out of what it writes and builds for you, in text, in rendered pages and in how it puts decisions to you. |
| [Earn its place](earn-its-place) | Switches a skill off for a window of real work, then rebuilds only what went missing, or retires it. |

## Design principles

**Skills have to change faster than models.** Every skill is a hypothesis that the model can't do this on its own yet. Instructions written for previous models become dead weight, or even gate what newer models could do for you.

**1. A skill earns its place only if work goes worse without it.**
- Real use is the evidence, not a synthetic test. Earn its place switches a skill off for a window of real work, then rebuilds what went missing or retires the skill.
- Every line traces back to my own work.

*Example.* House style comes from 1,087 of my own corrections, choices and approvals since August 2026.

**2. What the model can do on its own drops out.**
- What became deterministic moves into code or hooks.
- The text keeps only what needs judgment.

**3. A skill is valuable real estate.**
- Each word has to carry meaning and invoke the right behavior.
- Each SKILL.md records its size at the last major release in `metadata.benchmark`. Minor versions stay at or under it. To add, I condense first or cut what is no longer needed.
- Only a new major version resets the benchmark, ideally after an Earn its place trial.

*Example.* Earn its place came from such a reset. It replaced my 106-line, 7.7 KB skill-writer with 17 lines and 1.4 KB, after blind rebuilds and blind reviews by four models.

## Install

```bash
npx skills add byMarcoVogt/skills
```

This needs Node.js 22.20 or newer. [`skills`](https://github.com/vercel-labs/skills) lets you pick which skills to install and for which agents. Add `--skill <name>` to install one directly. Each skill's README also explains how to copy the folder by hand.

## License

[MIT](LICENSE)
