---
name: think-it-through
description: Use when the user wants to think something through before it is built - an idea, a plan, a decision, a wish, or a pasted brain dump or voice note to sort out. Also "brainstorm", "rethink", "stress-test", "interview me", "grill me", in any language, mid-session too. Ends in one plan file that ship-it can build from.
metadata:
  version: "2.1.1"
  benchmark: "3946 bytes"
  origin: "Inspired by grill-me, github.com/mattpocock/skills (MIT)"
---

# think-it-through

The thinking before `ship-it`: turn what the user brings into one plan file that a builder can work from without this conversation. Do not build.

## Read first

Before the first question, read the repo and its instructions, the skills it touches, open and recently closed issues, earlier plans, everything the user names (even what the repo calls no source), and what this conversation already settled. Then a few lines: what you read, the goal as you understand it, the decisions you see, and the weakest assumption under the idea. Sort a brain dump; do not echo it. If nothing needs the user's choice and no file was asked for, say so and stop: `ship-it` builds without a plan.

## Ask

- One decision per question, one question at a time, and only what the user has to choose: goal, taste, risk, cost, what stays out, what only they can do. What the files answer is looked up. What a builder can settle stays open in the plan as the builder's call.
- Two or three options, context inside each, the recommendation first with one line why. Before sending, check the question and each option against what the files and the user already settled, and drop what they settled or ruled out. Use the question tool where there is one.
- Plain words: a term the user has not used gets its meaning in the same sentence. An unclear answer decides nothing: say how you read it and ask again, or leave it open. Left to you, it becomes your recommendation, recorded as delegated.
- Chat stays a few lines around the question. Pictures, comparisons and side material go into the trail, with one line in chat.
- For a hard-to-reverse choice the user cannot judge alone, get an independent view first (agents with other stances, or another model family through `route`).

## Challenge

Early on, offer a cheaper path to the same goal, where there is one, and building nothing, as options.

## Done

Stop asking when the plan inputs of `ship-it` ("Lane", and "Before the build" in its `orchestrate.md`) are settled:

- **Intent:** why, what we want, what we do not want.
- **Done-when:** each criterion binary, with who or what checks it.
- **Touchpoints:** what only the user can do, and when.
- **Live use:** what in daily use the change touches, and whether building may run alongside it.
- **Open questions:** at most four, each with options and a recommendation, so that "yes to all recommendations" is a full answer.

Slices, steps, budget and models are `ship-it`'s. Then a fresh agent that never saw the chat reads the plan as its builder: does every decision have a reason, can each done-when be checked while daily use goes on, do two lines contradict, is every point that needs the user a touchpoint, can `ship-it` build in that repo? Fix what would stop or mislead a builder; one read, not a loop. Say in one line that the plan is ready and where, and stop.

## The plan file

Markdown in `plans/` of the repo it will be built in. Open questions on top. Every decision with a one-line reason and its source: the user's, dated and as they gave it; delegated by the user; or marked as a proposal. No steps.

The trail (pictures, panel results, side questions, drafts) goes into a folder beside the plan, marked at its top as not a source.

When a calling skill names its own file and contents (`skill-trials`: `intent.md`), write that instead, by the same rules.
