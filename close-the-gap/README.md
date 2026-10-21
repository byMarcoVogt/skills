# Close the gap `experimental`

<p align="center"><b>Frontier of AI</b><br>
↑<br>
<b>[ ? ]</b><br>
↑<br>
<b>Your Working Knowledge</b></p>

<p align="center"><i>What don't you know you're missing?</i><br>
At the end of a session, Close the gap proposes a few things worth learning<br>
from the frontier of AI. You pick one, and it teaches you.</p>

## The map

![A map. A small, dark region labelled "My Working Knowledge" holds Verification, Skills and Hooks. A line runs from it through Claude Mods to Learning Layer. Around it lie much larger pale regions, Evals, Tokenconomics and Learning Layer, and many smaller unnamed ones, all inside a wide outer rim.](../visual-assets/close-the-gap/map.webp)

Your working knowledge is the dark region. The frontier is the outer rim, and it moves every month. In between lie bodies of knowledge, and each session adds one.

The model finds its way along three axes:

- **Layer**: is it about the model itself, the context you give it, the system you wire around it, or the people involved?
- **Altitude**: is it a tool, a method, a principle, or something closer to first principles?
- **Mode**: do you need to grasp it, judge it, or do it yourself?

## It remembers lightly

Each session leaves one line in `references/lessons.md`, stored locally:

```
2026-10-19 | agent security as information flow | <session id> | "a body should be the most key ones, the rest should be explained in simple terms"
```

A line of history stays true, where a profile of you would go stale. Back up `lessons.md` before you reinstall or update the skill.

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
