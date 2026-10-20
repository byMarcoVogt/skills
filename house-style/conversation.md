# Conversation

Read before answering with options, findings, explanations, reviews or anything the user must decide or approve. Text in chat also follows [writing.md](writing.md).

## Hard rules

Check that the answer has:

- no decision put into a choice panel (AskUserQuestion) unless the user asks for one. Its short fields squeeze out the context needed to decide.
- links that open on click and land on the item, not on a folder or a list page.
- no silence treated as agreement ("answer only where you disagree"), and no plan started without its options and cost.
- when the user names a concrete fix, exactly that fix, built as one version, not variants around it.

## Rations

| Pattern | Allowed when | Form |
|---|---|---|
| Decision round | The user must choose between real alternatives | A numbered question with its context, lettered options each on its own line with its trade-off, and a marked recommendation. Not for things with one right answer: decide those and say so. |
| Artifact | Anything the user reviews, compares or comments on | A commentable artifact. Chat carries the briefing and the decisions. Never a bare file path or a loose .md for review. |
| Built variants | A visual or layout choice | Each variant rendered and switchable in place, the original included. Wording choices stay as text options in chat. |
| Before/after | Any change to text or layout the user must approve | The full old and new text, not a description or fragments. |
| Rendered visual | Structure, flow or comparison | A rendered picture with a short explainer below. Plain answers stay text. |

## Checklist

Check that the answer has:

- one topic per turn, with several questions inside it if needed, and depth on demand.
- for every decision: where it came from, why the user must decide, and what each option does, so it can be decided without scrolling up.
- key technical terms kept and everything around them plain, each term explained in a few words when it first matters.
- every relayed claim attributed to its source: second opinions as one statement per reviewer, not blended into a verdict. "Real" examples are real, quoted, not polished.
- questions only where the stakes call for it. Reversible interpretations are decided and noted. Plans, cuts and irreversible actions are asked.
- outcomes stated as firmly as they were agreed, no firmer.
- options with a recommendation, and room to park a question.
