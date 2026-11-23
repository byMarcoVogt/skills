---
name: think-it-through
description: Use when the user wants to think something through before it gets built - an idea, a plan, a decision, a wish that is not a plan yet, or a pasted brain dump or voice note to sort out. Also "brainstorm", "rethink", "stress-test", "interview me", "grill me", in any language and mid-session. Ends in one plan file that ship can build from.
metadata:
  version: "2.1.0"
  benchmark: "3946 bytes"
  origin: "Inspired by grill-me, github.com/mattpocock/skills (MIT)"
---

# think-it-through

The thinking before `ship`: turn what the user brings into one plan file that a builder can work from without this conversation. Do not build.

## Read first

Before the first question, read what exists: the repo and its instructions, the skills it touches, open and recently closed issues, earlier plans, and what this conversation already settled. What the files answer is a lookup, never a question. Then a few lines: what you read, the goal as you understand it, the decisions you see. A brain dump gets sorted, not echoed. If nothing needs the user's choice, say so and stop: `ship` builds without a plan.

## Ask

- One question at a time, and only a choice the user has to make: goal, taste, risk, cost, what stays out, what only they can do. What a builder can settle stays open in the plan, marked as the builder's call.
- Two or three options, context inside each, your recommendation first and marked, one line why. Use the question tool where there is one.
- Plain words: a term the user has not used gets its meaning in the same sentence.
- Chat stays a few lines around the question. Pictures, comparisons and side material go into the trail, with one line in chat.
- For a hard-to-reverse choice the user cannot judge alone, get an independent view first (agents with different stances, or another model family through `route`) and fold it into the options.

## Challenge

Early, and at least once where they apply: the weakest assumption under the idea, a cheaper path to the same goal, and what happens if nothing is built. Offer them as options.

## Done

Stop asking when the plan inputs of `ship` ("Before a plan", "Lane") are settled:

- **Intent:** why, what we want, what we do not want.
- **Done-when:** each criterion binary, with who or what checks it.
- **Touchpoints:** what only the user can do, and when.
- **Live use:** what in daily use the change touches, and whether building may run alongside it.
- **Open questions:** at most four left, each with options and a recommendation, so that "yes to all recommendations" is a full answer.

Slices, steps, budget and models belong to `ship`, not to questions here. Write the plan, say in one line that it is ready and where, and stop.

## The plan file

Where and in the form `ship`'s Lane names; without `ship`, Markdown in `plans/`. Open questions on top. Every decision with a one-line reason and its source: the user's with the date, anything else marked as a proposal. No steps.

The trail (pictures, panel results, side questions, drafts) goes into a folder beside the plan, marked at its top as not a source.

When a calling skill names its own file and contents (`skill-trials`: `intent.md`), write that instead, by the same rules.
