# Design notes

The figure is set like an atlas plate: a white page, mostly air, where every mark is a measurement.
The rules below are what keep it that way when you edit the data or add a layout.

## Composition

- **The diagonal carries the figure.** The half-plane below t = L/c is a flat warm gray (`#f7f6f2`)
  that also covers the grid there. Gridlines exist only where systems can exist. Regions are
  clipped to the line, so they never enter the field.
- **The legend lives in the empty half.** It is right-aligned to the axes, rests just above the CCM
  band, and has no box: the field is its background. `render()` checks that the block stays below
  the line with a margin, and reports `legend_clear = False` (and warns) if it doesn't.
- **References on the outer edges.** Familiar objects run along the top axis and familiar durations
  along the right, in gray italic serif. The data axes (left and bottom) are darker; the reference
  axes are a light frame.
- **One minor tick per decade** on both data axes, a steady rhythm that makes the logarithmic
  scale countable. Major gridlines every 4 decades in length and 5 in time, as faint hairlines.

## Color

Each center owns one hue, used three ways.

| Center | Hue (`color`) | Label (`label_color`) | Wash alpha |
|---|---|---|---|
| CCQ | `#A86BDB` violet | `#6B3A9E` | 0.17 |
| ICC | `#1F4FA3` blue | `#163C7E` | 0.12 |
| CCB | `#6BAF2E` green | `#3E6D12` | 0.18 |
| CCN | `#14A3AE` turquoise | `#0A6770` | 0.17 |
| CCA | `#B8202E` red | `#8E1621` | 0.13 |
| CCM | `#E8862A` orange | `#97520F` | 0.24 (band) |

- **Hue families follow the centers' web banners:** CCA red, ICC blue, CCB green, CCN turquoise,
  CCQ violet, CCM orange. The exact values are tuned for this figure, not sampled brand colors.
- **Wash alpha is per hue,** so every wash lands at about the same lightness on white. Dark,
  saturated hues (blue, red) get less opacity than light ones (violet, green). Without this, ICC and
  CCA look heavier than the others.
- **Labels use a darker shade of their region's hue** (4.8–8.8:1 contrast on their own wash,
  5.9–10.6:1 on white, all above WCAG AA), so the eye links label and region without the legend.
- **Neutrals carry structure:** ink `#1b1b19`, axes and the t = L/c line `#3b3a37`, reference
  frame `#c9c7c0`, gridlines `#efeeea`, landmarks and footnote `#8a8882`.

**Color-vision caveat.** CCA red, CCB green and CCM orange are hard to tell apart under
deuteranopia. This is tolerable here because those three never touch and every region carries its
acronym. If you need strict CVD separation, run the colors through a simulator and change hue
families rather than lightness alone.

## Typography

- **Instrument Serif** for the title, the italic landmarks and the t = L/c label: the "human" voice.
- **Instrument Sans** for numerals, acronyms, axis labels and names: the "data" voice.
- Few sizes, and hierarchy by weight and value: acronyms are bold, names regular, landmarks light
  gray italic. Tick labels are typeset as 10ⁿ with true superscripts and minus signs.
- The title block is flush with the outer edge of the y-axis label, not with the plot frame.
- Both fonts ship in `fonts/` under the SIL Open Font License and are embedded in every PDF, so
  text stays editable.

## Layering

1. major gridlines
2. excluded field (covers the grid below the line)
3. CCM band and its caption
4. region washes, **largest area first** (CCA, CCB, CCN, ICC, CCQ); computed, not hard-coded
5. region outlines, all drawn after all washes, so every edge stays crisp through overlaps
6. the t = L/c line, region labels, title block, legend

## Labels

- In-region acronyms are placed to avoid gridlines where possible. ICC sits inside its narrow box;
  CCQ is too small and sits to its left. The 16:9 layout adds a short leader ending in a dot on the
  region edge; in the narrower 3:2 layouts the label sits directly beside the box.
- The t = L/c label is rotated to the line's on-screen slope and offset perpendicular to it, so it
  stays correct at any aspect ratio.
- Legend columns (swatch, acronym, name) are measured from the rendered text, so the block adapts to
  font changes or longer names. The 3:2 layouts use short names because the official ones do not
  fit below the line at that width.
