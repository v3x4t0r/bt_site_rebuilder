# BT Archive

Proof-of-concept scraper + static site for bt.no articles. Scrapes 12 category
pages, fetches full article text/images/video via the Iris API, and renders a
static site with a live category filter, newest articles first.

## Files

- `fetch.py` — does everything: scrape, fetch, download media, render HTML
- `site/` — generated output (git-ignored data): `index.html`, `articles/`, `manifest.json`
- `site/seen_urls.txt` — every article URL processed so far, so re-runs never re-download an article
- `Dockerfile` / `entrypoint.sh` — container that scrapes once, then re-scrapes on a timer

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 fetch.py          # scrape + build site/ (run again anytime for new articles)
cd site && python3 -m http.server
```

Then open http://localhost:8000.

## Run with Docker

```bash
docker build -t bt-archive .
docker run -d --name bt-archive --restart unless-stopped \
  -p 8010:8000 -v "$(pwd)/site:/app/site" bt-archive
```

Re-scrapes every 20 minutes by default. Override with `-e SCRAPE_INTERVAL=<seconds>`.

## Notes

- Categories: `hendelser`, `folk`, `byliv`, `innenriks`, `utenriks`,
  `nyheter/okonomi`, `helse`, `klima-og-miljoe`, `krim`, `politikk`,
  `trafikk`, `karriere`.
- Each run picks up to 24 new articles, round-robined evenly across
  categories (`LIMIT` in `fetch.py`).
- Paywalled articles with no real body (just a title/date stamp) are
  skipped automatically; video-format articles (no text, just a clip)
  are kept and the video is embedded.
