"""Reskn lead scraper — pulls plumbers + heating engineers from Google Maps via Apify, scores them.

Usage:
  python scrape_leads.py belfast   # pilot
  python scrape_leads.py ni-full   # full NI sweep
"""
import os, sys, io, json, time, urllib.request, urllib.error, csv, pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = REPO / '.env'
if ENV_PATH.exists():
    for line in open(ENV_PATH, encoding='utf-8'):
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.strip().split('=', 1)
            os.environ.setdefault(k, v.strip('"').strip("'"))

APIFY_TOKEN = os.environ['APIFY_TOKEN']
ACTOR_ID = 'compass~crawler-google-places'  # Google Maps scraper

CITIES = {
    'belfast': ['Belfast'],
    'ni-full': [
        'Belfast', 'Lisburn', 'Bangor NI', 'Newtownards', 'Derry',
        'Newry', 'Coleraine', 'Antrim', 'Ballymena', 'Carrickfergus',
        'Larne', 'Dungannon', 'Omagh', 'Armagh', 'Enniskillen',
    ],
}
TERMS = ['plumber', 'heating engineer']
MAX_PER_QUERY = 50  # tune for cost vs coverage

def post(url, body):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def run_actor(search_strings):
    print(f"  starting actor with {len(search_strings)} queries...")
    body = {
        'searchStringsArray': search_strings,
        'maxCrawledPlacesPerSearch': MAX_PER_QUERY,
        'language': 'en',
        'countryCode': 'gb',
        'scrapePlaceDetailPage': False,
    }
    url = f'https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}'
    run = post(url, body)['data']
    run_id = run['id']
    dataset_id = run['defaultDatasetId']
    print(f"  run {run_id}, dataset {dataset_id}, polling...")
    # Poll until done
    while True:
        time.sleep(8)
        info = get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}")['data']
        status = info['status']
        sys.stdout.write(f"  status: {status}\r"); sys.stdout.flush()
        if status in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
            print(f"\n  finished: {status}")
            break
    items = get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&clean=true")
    return items

def looks_like_facebook_or_social(url):
    if not url: return False
    u = url.lower()
    return any(s in u for s in ['facebook.com', 'fb.com', 'instagram.com', 'linktr.ee', 'about.me'])

def score_lead(lead):
    site = (lead.get('website') or '').strip()
    reviews = lead.get('reviewsCount') or 0
    rating = lead.get('totalScore') or 0
    photos_count = len(lead.get('imageUrls') or []) + (1 if lead.get('imageUrl') else 0)
    has_phone = bool(lead.get('phone'))
    score = 0
    notes = []
    # Disqualifiers — return 0
    if not has_phone:
        return 0, ['NO_PHONE']
    if reviews < 5:
        return 0, ['TOO_FEW_REVIEWS']
    if rating and rating < 3.5:
        return 0, ['LOW_RATING']
    name = (lead.get('title') or '').lower()
    chains = ['british gas', 'pimlico', 'homeserve', 'corgi', 'dyno-rod', 'dyno rod']
    if any(c in name for c in chains):
        return 0, ['CHAIN']
    # Positive signals
    if not site:
        score += 40; notes.append('NO_WEBSITE')
    elif looks_like_facebook_or_social(site):
        score += 40; notes.append('FB_ONLY')
    else:
        score += 20; notes.append('HAS_SITE_TBD')  # need manual check or scrape
    if 10 <= reviews <= 100:
        score += 30; notes.append('REVIEW_SWEETSPOT')
    elif reviews > 100:
        score += 10; notes.append('MANY_REVIEWS')
    else:
        score += 5
    if rating >= 4.0:
        score += 15; notes.append('GOOD_RATING')
    if photos_count >= 10:
        score += 5; notes.append('PHOTOS')
    return score, notes

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'belfast'
    if mode not in CITIES:
        print(f"Unknown mode {mode}. Options: {list(CITIES)}"); sys.exit(1)
    cities = CITIES[mode]
    queries = [f"{term} {city}" for city in cities for term in TERMS]
    print(f"=== Reskn lead scrape: {mode} ===")
    print(f"  {len(cities)} cities × {len(TERMS)} terms = {len(queries)} queries, {MAX_PER_QUERY}/query max")
    print(f"  queries: {queries}\n")
    t0 = time.time()
    raw = run_actor(queries)
    print(f"  pulled {len(raw)} raw records ({time.time()-t0:.0f}s)")
    # De-dupe by placeId
    seen = {}
    for r in raw:
        pid = r.get('placeId') or r.get('title','')
        if pid and pid not in seen:
            seen[pid] = r
    leads = list(seen.values())
    print(f"  {len(leads)} unique after dedupe")
    # Score
    scored = []
    for lead in leads:
        s, notes = score_lead(lead)
        scored.append({
            'score': s,
            'notes': '|'.join(notes),
            'title': lead.get('title'),
            'phone': lead.get('phone'),
            'website': lead.get('website') or '',
            'rating': lead.get('totalScore'),
            'reviews': lead.get('reviewsCount'),
            'address': lead.get('address'),
            'category': lead.get('categoryName'),
            'placeId': lead.get('placeId'),
            'url': lead.get('url'),
            'lat': (lead.get('location') or {}).get('lat'),
            'lng': (lead.get('location') or {}).get('lng'),
        })
    scored.sort(key=lambda x: -x['score'])
    out_dir = REPO / 'data'
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f'{mode}_raw.json'
    csv_path = out_dir / f'{mode}_scored.csv'
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(scored[0].keys()))
        w.writeheader(); w.writerows(scored)
    print(f"\n  raw  -> {raw_path}")
    print(f"  csv  -> {csv_path}")
    # Summary
    hot = [s for s in scored if s['score'] >= 70]
    warm = [s for s in scored if 50 <= s['score'] < 70]
    skip = [s for s in scored if s['score'] < 50]
    print(f"\n=== Score summary ({len(scored)} total) ===")
    print(f"  HOT  (70+):  {len(hot)}")
    print(f"  WARM (50-69): {len(warm)}")
    print(f"  SKIP (<50):  {len(skip)}")
    print(f"\n=== Top 10 HOT leads ===")
    for s in hot[:10]:
        site = s['website'][:40] or '(no site)'
        print(f"  [{s['score']:>3}] {s['title'][:35]:<35} | {s['phone'] or '?':<15} | {s['rating'] or '?':>3} ⭐ {s['reviews'] or 0:>3} rev | {site}")
        print(f"        {s['notes']}")

if __name__ == '__main__':
    main()
