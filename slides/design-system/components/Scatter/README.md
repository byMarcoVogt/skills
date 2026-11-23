# Scatter

Two measures per item in the house frame: the only chart with two named axes, the items the message is about in navy and labelled, the rest in grey, and a dashed average line.

The example plots unit cost against capacity utilisation for twelve plants in 2025 (illustrative values).

## Anatomy

1. **Sticker**: top right, `stamp` in a 2px `navy-700` outline with `radius-stamp`; "Illustrative" because the values are made up.
2. **Action title**: one sentence in `action-title` (Newsreader 500, 52/60), `navy-700`, at most two lines, each under 95% of the title width.
3. **Title rule**: 3px `navy-700`, full width, `space-4` above and below.
4. **Chart title**: `chart-title`, `navy-700`, the two measures, the items and the period.
5. **Legend**: small icons for the colours that carry meaning (`navy-700` dot, `slate-300` dot) and the average line (dashed `slate-500`), with the average's scope in words.
6. **Y-axis title**: above the plot, `footnote` bold `muted`, the measure with its unit; tick values at the left in `footnote`/`muted` with 1px `hairline` gridlines, no axis line.
7. **Dots**: 20px; message items `navy-700`, labelled with a short name in `footnote` bold `navy-700`, `space-2` to the right; other items `slate-300`, unlabelled.
8. **Average line**: 3px dashed `slate-500`, labelled at its right end with the symbol and value only ("Ø 4.4"); one decimal, like the tick values.
9. **X-axis**: a 2px `hairline` baseline, tick values below and the axis title with its unit centred under them, `footnote` `muted`.
10. **So-what line**: `body-strong` "So what:" in `navy-700`, then `body`, under a 2px `slate-300` rule.
11. **Footer**: 3px `navy-700` rule at 98px from the bottom; source left; deck short name and page right.

## What the consumer provides

Two measures with units for each item, the items the message is about with a short name for each, the benchmark (average or trend) and its scope, source and vintage, and the one-sentence message.
