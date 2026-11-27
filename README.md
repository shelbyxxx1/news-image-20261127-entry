# news-image-20261127-entry

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/shelbyxxx1/news-image-20261127-entry/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/shelbyxxx1/news-image-20261127-entry/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

The World in One Day — a broadsheet front page that sums up the world news of Friday, 27 November 2026 in a single 1024 × 1024 image. `render.py` typesets and draws the whole page with Pillow from a fixed, date-checked news brief: a masthead with the day's date, drones over Kuwait as the lead with a generated night-scene illustration of the air-defence station, two medium stories (US Thanksgiving storms; the World Chess Championship draw), a six-number strip, a dot-matrix world map with numbered pins, 27 more dated briefs, and a DATE CHECK box — no downloaded assets, fully deterministic. The graded entrypoint `main.py` uses only the Python standard library: it copies the committed `entry.png` into the output directory.

## How to run

```sh
python3 render.py   # redraw entry.png from the brief (local only; needs Pillow + DejaVu/Noto fonts)
python3 main.py     # copy entry.png to /output (or $MAKEFUN_OUTPUT_DIR)
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=rtcpv23d&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
