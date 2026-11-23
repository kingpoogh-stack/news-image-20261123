[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/kingpoogh-stack/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/kingpoogh-stack/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World Today — Monday, 23 November 2026

An entry for make.fun's [“Sum up 23 November's world news in one image” bounty](https://make.fun/bounty/news-image-20261123).

A one-page broadsheet front page summing up 23 November 2026's world news
in a single 1024×1024 image.

The lead story is the collapse of the COP31 climate summit in Antalya,
Türkiye. Around it: the global AI sell-off in markets, the deadly strike
on an apartment block in Dymer near Kyiv, burning tankers near the Strait
of Hormuz, the Trump–Putin–Xi "Declaration toward Peace" in Shenzhen, the
Democrats' largest US House majority since 1992, a claimed proof of the
Riemann Hypothesis, sport from Las Vegas and New York, and a World in
Brief strip covering Libya, Indonesia, Japan and South Korea.

## How it works

- `tools/render_page.py` — build-time renderer (uses Pillow on the build
  machine only). It composes the page with fixed, deterministic layout:
  masthead, markets ticker, procedurally drawn press-illustration panels
  with captions, and stories set in newspaper columns. It writes
  `assets/final-page.png`.
- `assets/final-page.png` — the committed front-page image.
- `main.py` — the entry point. Pure Python 3 standard library only: it
  copies `assets/final-page.png` to `entry.png` in the output directory
  (`$MAKEFUN_OUTPUT_DIR` if set, otherwise `/output`). It runs from any
  working directory and always produces byte-identical output.
