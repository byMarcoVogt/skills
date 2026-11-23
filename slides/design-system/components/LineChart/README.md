# LineChart

A development over many years in the house frame: the message series as a bold navy line that turns dashed where it becomes a projection, one context series in grey, and each series named at its right end.

The example shows heat pumps installed in German homes from 2012 to 2025, projected at the 2025 rate to 2030, against a government target path (illustrative values).

## Anatomy

1. **Sticker**: top right, `stamp` in a 2px `navy-700` outline with `radius-stamp`; "Illustrative" because the values are made up.
2. **Action title**: one sentence in `action-title` (Newsreader 500, 52/60), `navy-700`, at most two lines, each under 95% of the title width.
3. **Title rule**: 3px `navy-700`, full width, `space-4` above and below.
4. **Chart title**: `chart-title`, `navy-700`, the measure with its unit after a comma.
5. **Lines**: the message series 4px `navy-700`, its projection the same line dashed; the context series (target path) 3px `slate-300`. No legend: each series is named at its right end (`footnote`; message name in `navy-700`, context name in `muted`).
6. **Values**: only at the start, the last actual year and the two end points, as 14px dots with `data-label` values in `navy-700`; one decimal throughout.
7. **Gridlines**: 1px `hairline` at round values, labelled at their left end in `footnote`/`muted`; a 2px `hairline` baseline; no y-axis line.
8. **Axis labels**: years as ’12 … ’25, projected years with "P" (’26P), `footnote`/`muted`.
9. **Note**: text on a 2px `muted` rule at its measured text width, a 2px `muted` leader to a 14px `muted` dot hovering above the point it explains.
10. **So-what line**: `body-strong` "So what:" in `navy-700`, then `body`, under a 2px `slate-300` rule.
11. **Footer**: 3px `navy-700` rule at 98px from the bottom; source with the projection basis ("P = …") left in `footnote`/`muted`; deck short name and page right.

## What the consumer provides

One message series over many years with the year the projection starts and how it was made, up to two context series (a target, a peer, an average) with their names, source and vintage, the one-sentence message, and optionally one note on the turning point.
