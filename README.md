[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/bavks/news-image-20261117-entry/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/bavks/news-image-20261117-entry/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# news-image-20261117 — the world on Tuesday, in one image

Entry for the make.fun bounty **"Sum up 17 November's world news in one
image"** (news-image-20261117).

## What it does

`main.py` copies the committed `entry.png` to the output directory
(`/output` by default, or `$MAKEFUN_OUTPUT_DIR` when set). It uses only
the Python standard library, needs no network, and writes byte-identical
output on every run.

## The image

A vintage newspaper front page for **Tuesday, 17 November 2026**,
typeset as "The Daily Meridian": a serif nameplate and dateline over
one lead story (the Kerch Bridge) and the other five stories in ruled
columns, each with a short headline and one factual sub-line. The
illustrations are drawn in code and run through an ordered-dither
newsprint pass, so they read as halftone newspaper art in black ink on
newsprint. All lettering was typeset programmatically (no generative
text), so nothing is garbled, and the page stays legible shrunk to
300 px across. `render_image.py` is the renderer that produces
`entry.png`.

## The six stories, as reported on the day

1. **Bahrain stops Iranian drones** — Iran's IRGC launched drones at a
   US radar system at Sheikh Isa Air Base in Bahrain; Bahrain said its
   air defences intercepted them and the US said the drones were
   intercepted with no damage or injuries.
   *Sources: Al Jazeera, 17 Nov 2026; Reuters reporting, 17 Nov 2026.*
2. **Ukraine drops Kerch Bridge span** — Overnight, Ukrainian drones
   and missiles struck the Kerch Bridge to Crimea; Ukraine's General
   Staff said an arch and a span of the road section collapsed into the
   strait, with the rail section damaged.
   *Sources: Associated Press via Montana Public Radio, updated 17 Nov
   2026; Military.com with Reuters-verified footage, 17 Nov 2026.*
3. **Japan scrambles jets at dawn** — Two suspected Russian aircraft
   entered Japanese airspace off Okinoshima Island, Fukuoka, for about
   three minutes each early on Tuesday; Japan scrambled fighters and
   lodged a "very stern protest" with Moscow — the first confirmed
   violation since September 2024.
   *Sources: Kyodo News and Reuters, 17 Nov 2026 (Japan Defence
   Ministry).*
4. **COP31 draft: phase out fossil fuels** — Ministers took over the
   COP31 talks in Antalya as the presidency's first draft deal —
   calling for an accelerated fossil-fuel phase-out and at least
   $120 billion a year in adaptation finance by 2035 — came under fire
   from all sides.
   *Sources: TBS News, 16 Nov 2026; AsiaToday, 17 Nov 2026.*
5. **Winter rains flood Gaza camps** — The World Food Programme and
   the International Organization for Migration warned that winter
   rains are deepening Gaza's crisis: more than 1.7 million people
   remain displaced and 1.4 million face acute hunger as floods damage
   shelters and food stocks.
   *Sources: UN News, 17 Nov 2026; WFP/IOM joint warning, 17 Nov 2026.*
6. **India beat Pakistan to SAFF title** — India beat Pakistan 2-1 in
   the final in Dhaka to win a record-extending 10th SAFF Championship
   title.
   *Sources: PTI via Nagaland Post, 17 Nov 2026; One Turn sports desk,
   17 Nov 2026.*

Stories considered and dropped after date-checking: the India–Pakistan
Under-19 Asia Cup final (played 14 Nov, misdated in one roundup) and
Germany's 5-0 Nations League win over the Netherlands (played the
evening of 16 Nov) — neither happened on 17 November.
