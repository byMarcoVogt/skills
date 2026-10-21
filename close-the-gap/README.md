# Close the gap `experimental`

<p align="center"><b>Frontier of AI</b><br>
↑<br>
<b>[ ? ]</b><br>
↑<br>
<b>Your Working Knowledge</b></p>

<p align="center"><i>What don't you know you're missing?<br>
Close the gap looks for it at the frontier of AI,<br>
and teaches you what matters most for your work.</i></p>

<p align="center">At the end of a session of real work, Close the gap reads what you did<br>
and proposes a few bodies of knowledge worth learning next.<br>
You pick one, and it teaches you over many prompts.</p>

## The map

![A map. A small, dark region labelled "My Working Knowledge" holds Verification, Skills and Hooks. A line runs from it through Claude Mods to Learning Layer. Around it lie much larger pale regions, Evals, Tokenconomics and Learning Layer, and many smaller unnamed ones, all inside a wide outer rim.](../visual-assets/close-the-gap/map.webp)

Imagine a space. How you work and think is a small shape somewhere in it, the dark region on the map. How the best people in the field work and think is a much larger shape around yours, and its outer rim is the frontier. That rim moves every month.

The space between is not empty. It is full of bodies of knowledge, some of them science, some of them practice, of different sizes, overlapping and connected. Each session adds one of them, and your own shape grows by that much.

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

```bash
npx skills add byMarcoVogt/skills --skill close-the-gap -g
```

Or copy manually:

| Agent | Put the folder in |
|:---:|:---:|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Other agents that read `SKILL.md` | that agent's skills folder |

## What's in the folder

| File | What it is |
|:---:|:---:|
| `SKILL.md` | The skill itself |
| `references/lessons.md` | Your history, one line per session, newest last |
| `agents/openai.yaml` | Tells Codex to start the skill only when you call it |

## License

[MIT](LICENSE)
