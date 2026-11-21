# news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Daniikhwan/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Daniikhwan/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One image summing up the world news of Saturday 21 November 2026.

`main.py` (Python 3.13, standard library only, no network) draws the
infographic from scratch — a small rasteriser with a hand-built 5x7
bitmap font — and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`). The output is deterministic: two runs
write byte-identical PNG files.

## The stories

1. **Missiles land in Poland** — two Russian missiles and a suspected
   drone come down in south-eastern Poland during a huge overnight
   barrage on Ukraine; PM Tusk calls it a deliberate provocation,
   NATO calls it a grave violation, and NATO chief Rutte is due in
   Warsaw on Saturday as Poland seeks more allied forces.
2. **S&P 500 enters correction** — US stocks fall about 3.7% on Friday
   as AI shares sell off; the Dow joins the S&P in correction.
3. **UK and EU sign deals** — food trade, carbon markets and youth
   mobility, agreed at a Brussels summit.
4. **Missiles over Riyadh** — the Saudi-led coalition intercepts
   Houthi missiles fired at the capital and strikes back.
5. **India v New Zealand** — Rahul and Padikkal steady India on day
   three of the first Test.
6. **Also today** — a pancreatic-cancer pill hailed as a breakthrough;
   asteroid 2026 WA1 flies past Earth tonight; youth protests
   planned across Europe.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
