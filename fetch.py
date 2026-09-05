import requests, os, re, html, json

UA = {'User-Agent': 'Mozilla/5.0'}
OUT = "site"
SEEN_FILE = f"{OUT}/seen_urls.txt"
LIMIT = 24  # new articles fetched per run, spread evenly across categories
KEYWORDS = ["hendelser", "folk", "byliv", "innenriks", "utenriks", "nyheter/okonomi",
            "helse", "klima-og-miljoe", "krim", "politikk", "trafikk", "karriere","bolig"]


def scrape_links():
    """Returns {category: [urls]}, newest first (bt.no category pages list articles in
    reverse-chronological order) - callers must preserve this order, not re-sort it."""
    by_category = {}
    for kw in KEYWORDS:
        try:
            r = requests.get(f"https://www.bt.no/{kw}", headers=UA, timeout=10)
            r.raise_for_status()
        except Exception:
            continue
        found = re.findall(rf'https://www\.bt\.no/{kw}/i/[^"\s<&]+', r.text, re.I)
        by_category[kw] = list(dict.fromkeys(found))  # de-dupe, keep page order
    return by_category


def parse_url(url):
    m = re.search(r'bt\.no/(.+?)/i/([a-zA-Z0-9]+)', url)
    return (m.group(1), m.group(2)) if m else (None, None)


def download(url, path, timeout=15):
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        r.raise_for_status()
        open(path, 'wb').write(r.content)
        return True
    except Exception:
        return False


def best_image_url(asset):
    best, best_w = None, -1
    for u in asset.get('urls', []):
        u_url = u.get('url', '')
        w = int((re.search(r'[?&]w=(\d+)', u_url) or [0, 0])[1] or 0)
        if w > best_w:
            best, best_w = u_url, w
    return best


def fetch_article(article_id, folder):
    """Fetches article JSON, embeds every image and the main video inline at their original
    position, downloads them all. Some 'closed'/paywalled articles are video-format: no text
    body, just a video component whose title matches the article title. Returns None only when
    there's neither real text, an image, nor a real video (e.g. title + Publisert/Oppdatert
    stamp only, or just a TTS narration of the headline)."""
    r = requests.get(f"https://iris-core-bt.schibsted.tech/v1/articles/{article_id}",
                      headers={**UA, 'Accept': 'application/json', 'Referer': 'https://www.bt.no/'}, timeout=10)
    r.raise_for_status()
    data = r.json()
    title = data.get('title', {}).get('value', article_id)
    parts, thumb, video_file, img_i, has_body = [], None, None, 0, False
    for c in data.get('components', []):
        v = (c.get('text') or {}).get('value')
        if v:
            if v.strip() != title.strip() and not re.match(r'^(Publisert|Oppdatert):', v.strip()):
                has_body = True
            parts.append(v if v.startswith('<') else f"<p>{html.escape(v)}</p>")
        asset = c.get('imageAsset')
        if c.get('type') == 'image' and isinstance(asset, dict):
            src = best_image_url(asset)
            if src:
                fname = f"{article_id}_{img_i}.jpg"
                if download(src, f"{folder}/{fname}"):
                    parts.append(f'<img src="{fname}" alt="">')
                    thumb = thumb or fname
                    img_i += 1
        if c.get('type') == 'video' and c.get('subtype') != 'tts':
            mp4 = (c.get('videoAsset') or {}).get('streamUrls', {}).get('mp4')
            if mp4:
                fname = f"{article_id}_video.mp4"
                if download(mp4, f"{folder}/{fname}", timeout=60):
                    parts.append(f'<video controls src="{fname}"></video>')
                    video_file = video_file or fname
                    has_body = True
    if not has_body and not thumb:
        return None
    return {
        'title': title,
        'pub': data.get('changes', {}).get('firstPublished', ''),
        'body': '\n'.join(parts),
        'image_file': thumb,
        'video_file': video_file,
    }


def article_page(art):
    return f"""<!DOCTYPE html><html lang="no"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(art['title'])}</title>
<style>
:root{{--accent:#d93025;--ink:#1a1a1a;--muted:#767676}}
body{{font-family:Georgia,'Times New Roman',serif;max-width:700px;margin:0 auto;padding:2.5rem 1.5rem 4rem;line-height:1.75;color:var(--ink);background:#fff}}
a.back{{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:.9rem;color:var(--accent);text-decoration:none;font-weight:600}}
a.back:hover{{text-decoration:underline}}
.tag{{display:inline-block;font-family:-apple-system,Helvetica,Arial,sans-serif;text-transform:uppercase;font-size:.7rem;letter-spacing:.06em;color:var(--accent);font-weight:700;margin-top:1.2rem}}
h1{{font-family:-apple-system,Helvetica,Arial,sans-serif;font-size:2rem;line-height:1.25;margin:.4rem 0 .3rem;color:var(--ink)}}
.meta{{font-family:-apple-system,Helvetica,Arial,sans-serif;color:var(--muted);font-size:.85rem;margin-bottom:1.5rem}}
img,video{{max-width:100%;border-radius:10px;display:block;margin:0 0 1.8rem}}
p{{margin:0 0 1.3rem}}
</style></head><body>
<a class="back" href="../index.html">&larr; Tilbake til arkivet</a>
<p class="tag">{html.escape(art['category'])}</p>
<h1>{html.escape(art['title'])}</h1>
<p class="meta">{art['pub'][:16].replace('T', ' ')}</p>
{art['body']}
</body></html>"""


def index_page(manifest):
    cards = []
    for a in manifest:
        if a.get('image_file'):
            img = f'<img class="card-img" src="articles/{a["image_file"]}" loading="lazy">'
        elif a.get('video_file'):
            img = '<div class="card-img video-thumb"><span class="play-icon"></span><span>VIDEO</span></div>'
        else:
            img = ''
        cards.append(f'''<a class="card" href="articles/{a['id']}.html" data-category="{html.escape(a['category'])}">
  {img}
  <div class="card-body">
    <span class="cat">{html.escape(a['category'])}</span>
    <h3>{html.escape(a['title'])}</h3>
    <span class="date">{a['pub'][:16].replace('T', ' ')}</span>
  </div>
</a>''')
    filters = ''.join(
        f'<button class="filter-btn{" active" if c == "all" else ""}" data-filter="{c}">{html.escape(c)}</button>'
        for c in ['all'] + KEYWORDS
    )
    return f"""<!DOCTYPE html><html lang="no"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BT Archive</title>
<style>
:root{{--accent:#d93025;--ink:#1a1a1a;--muted:#767676;--bg:#f4f4f2}}
*{{box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink);margin:0}}
header{{background:#fff;border-bottom:3px solid var(--accent);padding:1.6rem 1rem;text-align:center;position:sticky;top:0;z-index:10}}
header h1{{margin:0;font-size:1.5rem;letter-spacing:-.02em}}
header p{{margin:.3rem 0 0;color:var(--muted);font-size:.85rem}}
.filters{{display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem;max-width:900px;margin:1rem auto 0}}
.filter-btn{{flex:0 0 auto;font:inherit;font-size:.78rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em;border:1px solid #ddd;background:#fff;color:var(--muted);padding:.4rem .9rem;border-radius:999px;cursor:pointer;transition:all .15s ease}}
.filter-btn:hover{{border-color:var(--accent);color:var(--accent)}}
.filter-btn.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
@media (max-width:640px){{
  header{{padding:1rem 0 .8rem;text-align:left}}
  header h1,header p{{padding:0 1rem}}
  header h1{{font-size:1.2rem}}
  .filters{{flex-wrap:nowrap;justify-content:flex-start;overflow-x:auto;-webkit-overflow-scrolling:touch;margin:.8rem 0 0;padding:0 1rem .3rem;max-width:none}}
}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:1.5rem;max-width:1200px;margin:2rem auto;padding:0 1.5rem}}
.card{{background:#fff;border-radius:12px;overflow:hidden;text-decoration:none;color:inherit;box-shadow:0 1px 3px rgba(0,0,0,.08);display:flex;flex-direction:column;transition:transform .15s ease,box-shadow .15s ease}}
.card:hover{{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,.12)}}
.card-img{{width:100%;height:170px;object-fit:cover}}
.video-thumb{{background:linear-gradient(135deg,#2b2b2b,#111);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.5rem}}
.play-icon{{width:2.4rem;height:2.4rem;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center}}
.play-icon::after{{content:'';border-style:solid;border-width:.5rem 0 .5rem .8rem;border-color:transparent transparent transparent #fff;margin-left:.15rem}}
.video-thumb span:last-child{{font-size:.7rem;font-weight:700;letter-spacing:.1em;color:#ccc}}
.card-body{{padding:1.1rem 1.2rem 1.3rem;display:flex;flex-direction:column;gap:.5rem}}
.cat{{text-transform:uppercase;font-size:.68rem;letter-spacing:.06em;color:var(--accent);font-weight:700}}
.card h3{{margin:0;font-size:1.05rem;line-height:1.4;font-weight:600}}
.date{{color:var(--muted);font-size:.78rem}}
</style></head><body>
<header>
  <h1>BT Archive</h1>
  <p>{len(manifest)} artikler, nyeste øverst</p>
  <div class="filters">{filters}</div>
</header>
<div class="grid">{''.join(cards)}</div>
<script>
document.querySelectorAll('.filter-btn').forEach(btn => btn.addEventListener('click', () => {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const f = btn.dataset.filter;
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = (f === 'all' || c.dataset.category === f) ? '' : 'none';
  }});
}}));
</script>
</body></html>"""


def pick_round_robin(by_category, seen, limit):
    """Interleaves categories so a run's picks span all of them, not just one. Keeps each
    category's newest-first order intact (no re-sorting) so the newest articles win."""
    queues = {kw: [u for u in urls if u not in seen and 'direkte' not in u.lower()]
              for kw, urls in by_category.items()}
    picked = []
    while len(picked) < limit and any(queues.values()):
        for kw in KEYWORDS:
            if queues.get(kw):
                picked.append(queues[kw].pop(0))
            if len(picked) >= limit:
                break
    return picked


def main():
    os.makedirs(f"{OUT}/articles", exist_ok=True)
    manifest_path = f"{OUT}/manifest.json"
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else []
    known = {a['id'] for a in manifest}

    seen = set(open(SEEN_FILE, encoding='utf-8').read().split()) if os.path.exists(SEEN_FILE) else set()
    by_category = scrape_links()
    print(f"[*] Found {sum(len(v) for v in by_category.values())} article links across {len(by_category)} categories.")

    new_urls = pick_round_robin(by_category, seen, LIMIT)
    for url in new_urls:
        category, article_id = parse_url(url)
        if not article_id or article_id in known:
            seen.add(url)
            continue
        try:
            art = fetch_article(article_id, f"{OUT}/articles")
        except Exception as e:
            print(f"    [!] Failed {url}: {e}")
            continue
        if art is None:
            print(f"    [x] Skipped (paywall stub, no body): {url}")
            seen.add(url)
            continue
        print(f"[+] {art['title']}")

        art['id'], art['category'] = article_id, category
        open(f"{OUT}/articles/{article_id}.html", 'w', encoding='utf-8').write(article_page(art))
        del art['body']
        manifest.append(art)
        known.add(article_id)
        seen.add(url)

    manifest.sort(key=lambda a: a['pub'], reverse=True)
    json.dump(manifest, open(manifest_path, 'w'), ensure_ascii=False, indent=2)
    open(f"{OUT}/index.html", 'w', encoding='utf-8').write(index_page(manifest))
    open(SEEN_FILE, 'w', encoding='utf-8').write('\n'.join(sorted(seen)) + '\n')
    print(f"\nDone -> {len(manifest)} articles total ({len(new_urls)} new this run). Run: cd {OUT} && python3 -m http.server")


if __name__ == '__main__':
    main()
