[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/kingpoogh-stack/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/kingpoogh-stack/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World Today — Monday, 23 November 2026 (v3)

An entry for make.fun's [“Sum up 23 November's world news in one image” bounty](https://make.fun/bounty/news-image-20261123).

Version 3 of the one-page broadsheet front page summing up Monday,
23 November 2026's world news in a single 1024×1024 image. The date
runs in the folio line, the World in Brief header and the footer, so
the day is named wherever a reader's eye lands. Compared with v2,
every story now carries fuller newspaper copy — several sentences of
figures, places and names rather than a headline and a one-liner —
and the page adds a pull-quote, a markets data box and a weather box.

The lead story is the collapse of the COP31 climate summit in
Antalya, Türkiye: an oversize headline and deck, a plenary-hall
illustration with caption and credit, a byline, two full columns of
report, and a pull-quote rail carrying a negotiator's words from the
final night. Around it, each with its own panel, headline and column
text: the global AI sell-off (Nikkei 225 −5.06%, with a dealing-room
chart panel), the deadly strike on an apartment block in Dymer near
Kyiv (10 killed, with a rescue-lights panel), the Trump–Putin–Xi
"Declaration toward Peace" signed in Shenzhen (flags panel), burning
tankers near the Strait of Hormuz, the Democrats' largest US House
majority since 1992, and a claimed proof of the Riemann Hypothesis.
A boxed Sport section covers Verstappen's Las Vegas Grand Prix win
and the New York Mets' record $450 million deal for Tarik Skubal. A
"Markets at a Glance" data box (Nikkei, KOSPI, S&P 500, Nasdaq,
Brent, gold, VIX, Hang Seng) sits beside a six-city weather box, and
a six-item World in Brief strip covers Libya, Indonesia, Japan,
South Korea, Bahrain and Hong Kong.

## How it works

- `tools/render_page.py` — build-time renderer (uses Pillow on the
  build machine only). It draws the page at twice its final size and
  downscales it, for a smoother printed finish: masthead and folio
  line, markets ticker, an "Inside today" strip, procedurally drawn
  press-illustration panels with captions and credits, stories set
  in real newspaper columns with column rules, a pull-quote box, a
  markets data box and a weather box. It writes
  `assets/final-page.png`.
- `assets/final-page.png` — the committed front-page image
  (1024×1024, well under the 1 MiB limit).
- `main.py` — the entry point. Pure Python 3 standard library only:
  it copies `assets/final-page.png` to `entry.png` in the output
  directory (`$MAKEFUN_OUTPUT_DIR` if set, otherwise `/output`). It
  runs from any working directory and always produces byte-identical
  output.
