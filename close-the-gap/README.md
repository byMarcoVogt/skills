# Close the gap ![experimental](https://img.shields.io/badge/status-experimental-orange)

<p align="center"><b>Frontier of AI</b><br>
↑<br>
<b>[ ? ]</b><br>
↑<br>
<b>Your Working Knowledge</b></p>

<p align="center"><i>What don't you know you're missing?<br>
close-the-gap looks for it at the frontier of AI,<br>
and teaches you what matters most for your work.</i></p>

---

<h3 align="center">What happens when I call it?</h3>

<p align="center">Call it at the end of a session of real work.<br>
It proposes a few things worth learning.<br>
You pick one. It teaches it over many prompts,<br>
from the frontier back to your work.</p>

<h3 align="center">How does it know what I'm missing?</h3>

<p align="center">It reads the work you just did and your history in <code>lessons.md</code>.<br>
It refreshes its view of the frontier where it can.<br>
If it has little to go on, it asks you.</p>

<h3 align="center">Why is this skill so short?</h3>

<p align="center"><code>SKILL.md</code> is a handful of paragraphs, on purpose.<br>
It names no tools and no topics. Those would be out of date within months.<br>
It describes the space and lets the model find its own way.<br>
Every sentence earned its place in real runs. Many more were cut.</p>

---

## The map

![A map. A small, dark region labelled "My Working Knowledge" holds Verification, Skills and Hooks. A line runs from it through Claude Mods to Learning Layer. Around it lie much larger pale regions, Evals, Tokenconomics and Learning Layer, and many smaller unnamed ones, all inside a wide outer rim.](../visual-assets/close-the-gap/map.webp)

Imagine a space. How you work and think is a small shape somewhere in it, the dark region on the map. How the best people in the field work and think is a much larger shape around yours, and its outer rim is the frontier. That rim moves every month.

The space between is not empty. It is full of bodies of knowledge, some of them science, some of them practice, of different sizes, overlapping and connected. Each session, the model proposes a few of them, you pick one, and your own shape grows by that much.

To find its way around, the model looks at the space along three axes:

- **Layer**: is it about the model itself, the context you give it, the system you wire around it, or the people involved?
- **Altitude**: is it a tool, a method, a principle, or something closer to first principles?
- **Mode**: do you need to grasp it, judge it, or do it yourself?

These help the model see. You won't get a table of them back.

## It remembers lightly, on purpose

Every session leaves one line in `references/lessons.md`, and nothing more:

```
2026-10-19 | agent security as information flow | <session id> | "a body should be the most key ones, the rest should be explained in simple terms"
```

That is the date, the body you picked, the session it happened in, and what you said about how you like to learn.

A profile of you, what you know and how far you got, would describe a state, and states go stale. Every session would also nudge that profile toward whatever the last one thought. A line of history stays true. In Claude Code, the session id points back to the full conversation when a line is not enough.

The file ships with only its header. Your lines are stored locally, in the skill folder. Like everything your agent reads, they reach your model provider during a session. Back up `lessons.md` before you reinstall or update the skill, since that may replace the folder.

## Install

close-the-gap is a plain [Agent Skill](https://agentskills.io): a folder with a `SKILL.md`. Any agent that reads that format can run it.

**One command, for the agents you use:**

```bash
npx skills add byMarcoVogt/skills --skill close-the-gap -g
```

This needs Node.js 22.20 or newer. [`skills`](https://github.com/vercel-labs/skills) asks which agents to install for. Add `-a claude-code -a codex` to pick them up front.

**Or copy the folder yourself:**

| Agent | Put the folder in | Start it with |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `/close-the-gap` |
| Codex | `~/.agents/skills/` | `$close-the-gap` |
| Other agents that read `SKILL.md` | that agent's skills folder | its way of calling a skill |
| An agent that only reads `AGENTS.md` | anywhere | add one line to `AGENTS.md`: *"When I ask to close the gap, read `close-the-gap/SKILL.md` and follow it."* |

It only runs when you call it: Claude Code reads `disable-model-invocation` in `SKILL.md`, and Codex reads `agents/openai.yaml`. Neither will start it on its own in the middle of other work.

## What's in the folder

| File | What it is |
|---|---|
| `SKILL.md` | The skill itself |
| `references/lessons.md` | Your history, one line per session, newest last |
| `agents/openai.yaml` | Tells Codex to start the skill only when you call it |

## License

[MIT](LICENSE).
