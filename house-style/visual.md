# Visual

Read before building anything rendered: HTML pages, artifacts, slides and decks, document layout, diagrams, charts, UI. Text on it also follows [writing.md](writing.md).

## Before building

- If the user has a reference look (a design system, an earlier page, a named site), start from it, not from the model's own style. If none is named and the look matters, ask for one.
- Measure the rendered result before showing it: alignment, overflow, empty space, early line breaks.

## Hard rules

Check that the output has:

- no thick or coloured bar on one side of a box (border-left, or a heavy top edge on a rounded box). An even thin outline, a fill, or no line instead.
- no middle dot as a separator between fields, labels or menu items.
- no body or label text in small light grey, and no display or pixel face below title size.
- nothing cut off, overflowing its box, colliding with a neighbour or scrolling sideways, and no list running past its block.

## Rations

| Pattern | Allowed when | Form |
|---|---|---|
| Label, kicker or callout line above a title | It names something the title does not, on a page with a full master (footer, page number). Readers otherwise take it as an AI sign. | At most one per page. Never on a title page. Not repeating the title. |
| Callout or "so what" band | One sentence the title does not already say: a surprise, or a lever with its size | Not on every page by default, one per page, no side bar. |
| Numbers on elements | Order or count is the content: a real sequence, a count next to an icon, named principles | Never on parallel cards or keywords, never anything that reads like a hotkey. |
| Diagrams | Structure, flow or comparison | Rendered (HTML, SVG, widget). ASCII only for a handful of parts. Never raw Mermaid or diagram source in chat. |
| Effects and motion (video, animated pages) | The effect directs focus: typing or a caret on the one focus item, an element carried across a cut | Never tile zoom with a fat centred number, before/after swipes, paper-craft decor (torn paper, tape, receipts), chapter or "part 2 of 3" cards in short video. |
| Credit line | A page meant to be shared | Under the last rule: name, link, version, date. |

## Checklist

Check that the output has:

- no element that does not earn its place: helper text, a label beside a self-explaining field, a subtitle repeating the title, raw ids, status or meta labels on rows, invented controls.
- explanations (method, assumptions, footnotes) behind an info mark or a small hover, not as inline boxes, notes under tables or an "Explain" toggle. What must survive print, such as the source line, stays on the page.
- no stock component that reads as cheap: browser dropdown, toggle switch as a list filter, framed text button, default table header with fill, plain white tooltip, × for delete (a bin icon instead). Toggles for real settings are fine.
- nothing that covers, jumps, re-sorts or vanishes when used: no hover that hides list content, no layout shift on hover or edit, no section that takes its control away when hidden.
- colour in restraint: one accent, near-black text, one meaning per colour, no neon or saturated fills, no filled or tinted icons. The palette itself belongs to the project.
- separator lines: never two rules where one separates, one line style per level, lines end where the content ends.
- icons from one consistent line family, few of them, no emoji as icons, a logo where an entity has one. Icons that name a step are welcome.
- visible hierarchy: headings that read as headings, a lead before grouped items, no wall of text and no flat bullet dump.
- no generic template look: PowerPoint-like bars and transitions, filter-pill rows with count boxes, static boxed sections of a medium website.
- even space and alignment: labels centred where boxes are centred, symmetric inner edges, no content crammed at the top of an empty page. When content does not fit, cut content, never spacing or margins.
- emphasis only where the point is. Secondary content is never the highlighted thing.
- parallel elements in one form: same-level labels in one font and colour, one muted grey, page titles alike, pieces of one set in one visual logic.
- every label visibly belongs to one thing, with no placement that pairs the wrong items.
- charts where every mark serves the stated comparison: built left to right, no hero number without meaning, one chart per view, nothing overlaid on the data.
- real material where it exists (screenshots, real footage), and a mock-up that matches its original. No stick figures, invented backdrops or typeset fake pages.
