# Think it through

![Many scrambled ideas, shapes and notes flow from the left along thin threads into one framed, clear picture on the right.](../visual-assets/think-it-through/hero.webp)

<h4 align="center">What does it do?</h4>

<p align="center">It turns a raw idea, a brain dump or a half-formed wish into one plan file<br>
that an agent can build from without the conversation.</p>

<h4 align="center">How?</h4>

<p align="center">It reads what exists before it asks. It asks one real decision at a time, with options and a recommendation,<br>
and names the weakest assumption, a cheaper path and the option to build nothing.<br>
It stops when the plan holds the intent, a done-when, the touchpoints, how building fits daily use, and the few open questions left.<br>
When there is nothing to decide and no file was asked for, it says so and writes no plan.</p>

It feeds `ship-it`, a private build pipeline, and works without it: the plan then goes to `plans/` as Markdown.

## Install

```bash
npx skills add byMarcoVogt/skills --skill think-it-through -g
```

Or copy manually:

| Agent | Put the folder in |
|:---:|:---:|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Other agents that read `SKILL.md` | that agent's skills folder |

## License

[MIT](LICENSE). Inspired by [grill-me](https://github.com/mattpocock/skills) by Matt Pocock (MIT).
