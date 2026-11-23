# Marco Vogt Slides

Marco's house style for consulting-grade decks: white slides, a navy serif action title, one exhibit that proves it, navy and greys only. Every slide makes one point the reader gets from the title alone, and every element on it earns its space.

## Messaging

- **The action title is the slide.** One full sentence with a verb that states the so-what ("Global growth has settled around 3.5%…"), never a topic or a chart description. About 15 words, at most two lines, and no line wider than 95% of the title width (measured).
- **One claim.** No semicolon, no "A, B and C" list of the boxes below it, and no "with" or "and" clause that adds a second number. The title says what the exhibit means.
- **Read in sequence, the titles tell the whole story.** The deck title on the cover is a statement too ("Slower growth is the new normal").
- **No repetition between layers.** Title, chart title, panel, bullets and so-what line each add something; none restates another in other words. A panel heading never counts its points ("Three forces …").
- **Numbers side by side measure the same thing** in the same unit and scope; a vendor figure names the vendor.
- **Always source.** Every content slide names its source and vintage in the footer, marks estimates and projections ('26P, "E = estimate"), and explains a self-built estimate in plain words.

## Slide frame (house frame)

| Zone | Rule |
| --- | --- |
| Canvas | 1920 × 1080, `surface`; margins `margin-top` 72, `margin-side` 80, `margin-bottom` 124 |
| Header | Nothing above the action title: no tracker, eyebrow or category line. The sticker (below) sits in the top-right corner |
| Title | `action-title` in `navy-700`, then a 3px `navy-700` rule across the full width, `space-4` apart |
| Body | The exhibit at the width its data needs; a panel only when it earns its space |
| Footer | A 3px `navy-700` rule at 98px from the bottom, the same weight as the title rule. Below it, left: the source in `footnote`/`muted`. Right: the deck's short name in `body-strong`/`navy-700`, two spaces, a `slate-300` "\|", two spaces, the page number |

## Marks

Three kinds of marks, never mixed:

| Kind | Examples | Where | Lifetime |
| --- | --- | --- | --- |
| **Slide sticker** | For discussion, Preliminary, Indicative, Illustrative, Backup | Top right (right 80px, top 16px), `stamp` in `navy-700`, 2px `navy-700` outline, `radius-stamp` | Stays in the final deck. Only on slides where it is true; one per slide |
| **Document status** | Draft, Confidential | On the cover, and in the footer label before the page number ("Draft \| 3") | Removed or changed when the deck is final |
| **Working mark** | Variant a/b/c | In the page number ("3b") and the speaker notes; never in the sticker box | Removed before the deck goes out |

"Illustrative" belongs on every slide with made-up example values. Nothing else may look like a sticker (no navy-outlined small boxes elsewhere).

## Form follows content

Choose the slide's form from what it must prove, before styling it:

- a series of one measure → **chart slide**;
- a mechanism or sequence → **process slide**;
- the same attributes across several items → **table**;
- a bridge from one total to another → **waterfall**; a development over time with many points → **line chart**; two measures per item → **scatter**; a total and its parts → **stacked chart**;
- independent findings → first check whether each has material for a slide of its own; if not, **cards** side by side.

Cards are allowed: choose them when the points are parallel and none of the forms above carries them, not out of habit. The **executive summary** answers the deck's question in its title, as a chart slide or as cards, with a panel only if it earns its space.

## Fill and balance

A slide looks full and evenly distributed: no empty holes, no blocks of text. When space is left, in this order: add real context (a fact, a figure, a source line), add icons that say something, distribute the content over the height, shrink the container and keep it symmetric, or separate with a rule. A card's height follows its content; never spread three short lines over a fixed height (`space-between`), and never push text down with an empty spacer. The reverse holds too: a chart stretched across the slide with little in it, or a big box with little in it, has not earned the slide. Check alignment and symmetry: equal gaps, icons aligned with their text, centred chains.

## Takeaways: chart, annotation, so-what line, callout

Put a takeaway in the first of these that fits:

1. **Into the chart:** a delta or label on the data.
2. **An annotation** on the chart (below).
3. **A so-what line** at the bottom of the exhibit or panel: `body-strong` "So what:" in `navy-700`, then `body`, under a 2px `slate-300` rule. On a decision slide the same line carries the next step: "Next step:" then one sentence with the condition that triggers it.
4. **A navy callout band** (`navy-700` fill, `callout` in white, centred, full width above the footer). It fits a twist that changes how the exhibit reads, a next step, a big point that is not obvious from the exhibit, or a line that sets up what comes next. It is not tied to one use: judge per slide whether the point deserves it. Two or three per deck at most; rarity gives them weight.

A **panel** (`panel` grey, right third, `space-6` padding, heading 24px above the first point) is a sidebox. It earns its space only with valuable information that fits none of the four above and is not a slide of its own. A panel that is mostly white space, or repeats the title, is removed.

## Boxes

A box has a full outline of equal weight or a fill, never a line on one side only. Grey `panel` is the default fill; `navy-700` fill is only for the callout band and the trend-arrow pills.

## Charts

- No y-axis. Values sit on or above the bars in `data-label`, all in one position per chart.
- The message data in `navy-700`, context data in `slate-300`, a second series in `navy-500`. Projections are white bars with a 3px dashed `navy-700` outline and a "P" on the year. A colour that carries meaning appears in the legend.
- One `hairline` baseline; horizontal bars get a vertical `hairline` baseline, not a box edge. A benchmark is a 3px dashed `slate-500` line labelled at its right end with the symbol only ("Ø 3.7"); the period goes in the legend.
- One measure per chart. The chart title names it with its unit after a comma: "World real GDP growth, in %". Years on the axis as '21, '22; totals as "Total '24".
- A change between two shares is written as both values ("14% → 80%"), never "pp", "pts" or "percentage points"; "+x%" only for the relative change of one measure.
- Thin `hairline` gridlines only on dense charts. Legends use small icons (a solid bar, a dashed bar, a dashed line), not words alone. No direction headers ("Growth", "Decline") where the signs already say it.
- An axis break is two short slanted `slate-300` lines that reach slightly past the bar, with white between them. It is allowed on one outlier bar only, never on the bars being compared.
- Square corners (`radius-none`).

**Trend arrow** (a change across several bars): a 4px `navy-700` line with an arrowhead, running between points `arrow-lift` (48px) above the bar tops, so it runs parallel to the change. The value sits in a pill just above the line, never on it: `navy-700` fill, `radius-full`, white `data-label`, the relative change ("−27%"). Not on every step, only where the message is.

**Double chart** (losers and gainers): horizontal bars diverging from a centre column of round flags, losses to the left, gains to the right; no country names when the flags are clear; the chart's width follows the longest bar, with notes in the spare end rather than empty space.

**Waterfall** (a bridge from one total to another): the start and end totals are full `navy-700` bars; each step floats from the level the previous one left, increases in `navy-500`, decreases in `slate-300`; a 2px `hairline` connector runs level from each bar to the next. Every value sits above its bar, steps signed ("+1.2", "−0.8" with a real minus sign, U+2212). The legend shows the two step colours. Total bars carry their label on the axis ("Total '24").

**Line chart** (many points over time): the message series as a 4px `navy-700` line, context series 3px `slate-300`, a projection as the same line dashed. Each series is named at its right end instead of a legend. Values only at the start, the end and the points the message needs, as `data-label` dots of 14px. `hairline` gridlines are allowed here; still no y-axis line.

**Scatter** (two measures per item): the only chart with two measures, so both axes are named with their unit, the x-axis below and the y-axis title above the plot. Dots of 20px, the items the message is about in `navy-700`, the rest in `slate-300`; only the message items are labelled (a flag or a short name). An average or trend line is 3px dashed `slate-500`, labelled at its end with its symbol.

**Stacked chart** (a total and its parts): at most three segments, `navy-700` at the base, then `navy-500`, then `slate-300`; more parts are grouped into "Other" or the form changes. The total sits above each bar in `data-label`; segment values inside where they fit, white on navy and `navy-700` on `slate-300`. Segments are named at the right end of the last bar, in the same order as stacked. A 100% stack says so in its chart title ("…, in % of total").

**Process slide** (a mechanism): nodes as outlined boxes in a centred chain, `navy-700` 2px connectors with arrowheads; a decision is a `navy-700`-outlined diamond; conditions sit on the connectors as grey (`panel`) tags; branches end in equal-height cards. Arrows only where items follow each other.

## Annotations

Two forms, nothing else:

- **Note** on one mark: the text sits directly on a 2px `muted` rule; the rule is the text box's bottom border and the box takes the width of its longest line (measured, never a fixed width). A 2px leader drops from the rule to a 14px `muted` dot that hovers just above the mark, never on or inside it. The leader may be angled.
- **Bracket** on a group of marks: a 2px `muted` bracket along the group, at the value ends, with the note beside it.

A note sits beyond the value end, on the side the bar runs. All notes on one chart use the same form and style.

## Icons and symbols

- Icons replace text labels where a symbol says it faster, and replace meaningless numbering ("01", "1 ·"). The icon depicts the thing named, never the nearest library word. When the platform set has none, draw an inline SVG on a 24px grid: 2px `navy-700` stroke, no fill, round caps and joins; all icons on one slide share this style.
- **Bullet icon:** a white `icon-circle` (48px) with a 28px `icon-glyph`, left of its text, centred on the first text line, `space-2` apart. On a card with a heading, the icon sits centred above the heading.
- **Flags** are round, `flag` (40px), with a 2px `hairline` ring; a group of countries is a stack of three grey discs, its members named in the footer. Flags and that stack are the only exception to navy and greys. In charts and tables the flag stands alone; in running text the country is named, never an ISO code. A globe for the world, Ø for an average.
- Status as wordless circles with a legend (empty, half, full for degree; one scale per deck, distinguished by fill and lightness, not hue). Either a legend or words, never both.
- No decorative icons.

## Layouts

- **Chart slide (default):** house frame, exhibit, optional panel. See `components/ChartSlide`.
- **Process slide, double chart, waterfall, line, scatter, stacked:** see Charts and `components/`.
- **Table:** same attributes across items. Text left-aligned, numbers right-aligned in `tabular-nums`; no vertical rules; a 2px `navy-700` rule under the header row, 1px `hairline` rules between rows; the header in `footnote` bold `muted`, the unit stated once in the header; totals bold with a 2px `navy-700` rule above. The column or row that carries the message is `navy-700` bold, or sits on a `panel` fill. See `components/Table`.
- **Agenda:** a content slide in the house frame whose title states the deck's answer, not "Agenda". Each section is a row: its title in `body-strong` `navy-700`, one line in `body` on what it answers, and its first page number right-aligned in `muted`; `hairline` rules between rows. Repeated before a section, the current row stays `navy-700` and the others turn `muted`. See `components/Agenda`.
- **Section divider:** a full `navy-700` slide with the section's place ("Section 2 of 3") in `footnote` bold `slate-300` over a short 4px `slate-300` bar, then the section's statement in `cover-title`, white. No footer rule, no source, page number in `slate-300` bottom right. See `components/SectionDivider`.
- **Appendix:** opens with a section divider titled "Appendix". Its slides keep the house frame and an action title, carry the "Backup" sticker and number their pages A1, A2. They may be denser (more rows, `hairline` gridlines) but keep the type sizes. See `components/AppendixSlide`.
- **Split slide:** two halves for a two-part story with a contrast or a shift (before/after, advanced/emerging); same house frame. Use rarely.
- **Cover:** see `components/DeckCover`.

## Numbers

- **Typeface:** all figures in the sans with even-height (lining) digits; equal-width digits (`font-variant-numeric: tabular-nums`) in tables and number columns, not in running text.
- **Big number:** `big-number`, bold, clearly larger than its label, the % sign at full size. One for a message; up to four as a row of equals.
- **Precision:** the same number of decimals within one chart or table, rounded to what the decision needs.
- **Unit:** stated once, in the chart title or the table header, not after every value.
- **Scale and currency:** follow the deck's language. English: m and bn ("€4.2bn"). German: Mio. and Mrd. ("4,2 Mrd. €"). Currency as a sign (€, $), not as text.
- **Separators:** follow the deck's language. English 40,000.5; German 40.000,5.
- **Tables:** numbers right-aligned; totals bold with a rule above.
- **Negatives:** a real minus sign (−, U+2212, not a hyphen or a dash), in charts and tables. No parentheses, no red.

## Type and colour

- Headlines in the serif family (Newsreader, weight 500), everything else in the sans (Inter). Both from Google Fonts, free and embeddable: `https://fonts.googleapis.com/css2?family=Newsreader:wght@400..700&family=Inter:wght@400..700&display=swap`. Fallbacks are Georgia and Arial.
- **All figures in the sans** (big numbers, data labels, deltas, tables), so digits and % share one height even when a deck falls back to basic fonts. See Numbers.
- Navy and greys only: no other accent colour, no bright or neon blue, no pure black. Emphasis comes from `navy-700`, weight, size and lightness.
