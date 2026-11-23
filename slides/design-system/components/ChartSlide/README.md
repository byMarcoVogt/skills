# ChartSlide

The default content slide in the house frame: an action title, the chart that proves it, and a grey panel only when it earns its space.

The example shows world real GDP growth for 2021–2027 (IMF World Economic Outlook, October 2026).

## Anatomy

1. **Sticker** (optional): top right, `stamp` in a `navy-700` outline, only when true for this slide (here: For discussion).
2. **Action title**: one sentence in `action-title`, `navy-700`. Nothing above it.
3. **Title rule**: 3px `navy-700`, full width.
4. **Chart**: `chart-title` with its unit after a comma; a legend of small icons; message bars `navy-700` with white data labels, context bar `slate-300`, projections as dashed outlines with 'P years; a dashed `slate-500` benchmark labelled "Ø 3.7"; notes whose rule is the bottom border of a text box at its text width, with a dot hovering above the bar.
5. **Panel** (optional): `panel` grey, a heading that names the content without counting it, points with a bullet icon (48px white circle, 28px glyph, left of the text) and a bold lead-in, and a so-what line under a `slate-300` rule.
6. **Footer**: 3px `navy-700` rule; source left in `footnote`/`muted`; deck name and page number right in `navy-700`.

## What the consumer provides

The data series with source and vintage, the one-sentence message, and, for a panel, the reasons the chart cannot show. Without a panel, the chart takes the width it needs and the so-what goes on the chart or into a line at its foot.
