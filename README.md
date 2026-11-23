[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/kingpoogh-stack/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/kingpoogh-stack/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World Today — Monday, 23 November 2026

An entry for make.fun's [“Sum up 23 November's world news in one image” bounty](https://make.fun/bounty/news-image-20261123).

A dense one-page broadsheet front page summing up Monday, 23 November
2026's world news in a single 1024×1024 image. The date runs in the
masthead dateline, the markets ticker, the World in Brief header and
the folio line.

The lead story is the collapse of the COP31 climate summit in Antalya,
Türkiye — an oversize headline, a plenary-hall illustration with caption
and credit, a byline, and the story set in three newspaper columns.
Around it, each with its own panel, headline and column text: the global
AI sell-off (Nikkei 225 −5.06%), the deadly strike on an apartment block
in Dymer near Kyiv (10 killed), the Trump–Putin–Xi "Declaration toward
Peace" signed in Shenzhen, burning tankers near the Strait of Hormuz,
the Democrats' largest US House majority since 1992, and a claimed proof
of the Riemann Hypothesis. A boxed Sport section covers Verstappen's
Las Vegas Grand Prix win and the New York Mets' record $450 million
deal for Tarik Skubal, and a six-item World in Brief strip covers Libya,
Indonesia, Japan, South Korea, Bahrain and Hong Kong.

## How it works

- `tools/render_page.py` — build-time renderer (uses Pillow on the build
  machine only). It composes the page with fixed, deterministic layout:
  masthead, markets ticker, an "Inside today" strip, procedurally drawn
  press-illustration panels with captions and credits, and stories set
  in real newspaper columns. It writes `assets/final-page.png`.
- `assets/final-page.png` — the committed front-page image.
- `main.py` — the entry point. Pure Python 3 standard library only: it
  copies `assets/final-page.png` to `entry.png` in the output directory
  (`$MAKEFUN_OUTPUT_DIR` if set, otherwise `/output`). It runs from any
  working directory and always produces byte-identical output.
