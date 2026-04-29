"""Refine a scraped dataset — strict filters: must be NI + must be plumbing/heating category.

Usage:
  python scripts/refine_leads.py [dataset]   # default: ni-full
"""
import os, sys, io, json, csv, re, pathlib, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / 'data'

p = argparse.ArgumentParser()
p.add_argument('dataset', nargs='?', default='ni-full', help='Dataset name (default: ni-full)')
args = p.parse_args()

raw_path = DATA / f'{args.dataset}_raw.json'
if not raw_path.exists():
    sys.exit(f'No raw data at {raw_path}. Run scrape_leads.py first.')
raw = json.load(open(raw_path, encoding='utf-8'))
print(f'Raw: {len(raw)} records')

# NI signal: BT postcode OR +44 28 area code
BT_PATTERN = re.compile(r'\bBT\s?\d{1,2}\b', re.I)
def is_ni(lead):
    addr = (lead.get('address') or '')
    if BT_PATTERN.search(addr): return True
    phone = (lead.get('phone') or '').replace(' ', '')
    if phone.startswith('+4428') or phone.startswith('+4407') or phone.startswith('+447'):
        # mobile or NI landline — accept if address also has NI marker
        # but mobiles don't tell us NI; need address to confirm
        return BT_PATTERN.search(addr) is not None
    return False

# Plumbing/heating category match
CAT_KEYWORDS = ['plumb', 'heat', 'gas', 'boiler', 'drain']
def is_plumbing(lead):
    cat = (lead.get('categoryName') or '').lower()
    cats = [c.lower() for c in (lead.get('categories') or [])]
    title = (lead.get('title') or '').lower()
    blob = ' '.join([cat, ' '.join(cats), title])
    if any(k in blob for k in CAT_KEYWORDS):
        return True
    # Allow if category is exactly empty but title strongly implies
    return False

# Negative title keywords (not plumbers)
NEG_KEYWORDS = ['taxi', 'golf', 'e-cig', 'flatpack', 'motor works', 'cigarette', 'restaurant', 'cafe']

def is_excluded(lead):
    title = (lead.get('title') or '').lower()
    return any(k in title for k in NEG_KEYWORDS)

ni_only = [l for l in raw if is_ni(l)]
print(f'After NI filter: {len(ni_only)}')

plumbing_only = [l for l in ni_only if is_plumbing(l) and not is_excluded(l)]
print(f'After plumbing+exclusion filter: {len(plumbing_only)}')

# Town extractor: strip postcode, take first part of address before ", United Kingdom"
def extract_town(addr):
    if not addr: return '?'
    # remove ", United Kingdom" suffix
    a = re.sub(r',\s*United Kingdom\s*$', '', addr, flags=re.I).strip()
    # split, last part is usually "Town POSTCODE"
    parts = [p.strip() for p in a.split(',')]
    last = parts[-1]
    m = re.match(r'(.+?)\s+(BT\d+\s*\d?\w*)\s*$', last, re.I)
    if m: return m.group(1).strip()
    # If no postcode in last segment, return the segment itself
    return last

def site_status(url):
    if not url: return 'NONE'
    u = url.lower()
    if 'facebook.com' in u or 'fb.com' in u: return 'FB'
    if 'instagram.com' in u: return 'IG'
    return 'OTHER'

def looks_like_facebook_or_social(url):
    if not url: return False
    u = url.lower()
    return any(s in u for s in ['facebook.com', 'fb.com', 'instagram.com', 'linktr.ee', 'about.me'])

CHAINS = ['british gas', 'pimlico', 'homeserve', 'corgi', 'dyno-rod', 'dyno rod']

def score_lead(lead):
    site = (lead.get('website') or '').strip()
    reviews = lead.get('reviewsCount') or 0
    rating = lead.get('totalScore') or 0
    photos = len(lead.get('imageUrls') or []) + (1 if lead.get('imageUrl') else 0)
    has_phone = bool(lead.get('phone'))
    if not has_phone: return 0, ['NO_PHONE']
    if reviews < 5: return 0, ['TOO_FEW_REVIEWS']
    if rating and rating < 3.5: return 0, ['LOW_RATING']
    name = (lead.get('title') or '').lower()
    if any(c in name for c in CHAINS): return 0, ['CHAIN']
    score = 0; notes = []
    if not site: score += 40; notes.append('NO_WEBSITE')
    elif looks_like_facebook_or_social(site): score += 40; notes.append('FB_ONLY')
    else: score += 20; notes.append('HAS_SITE_TBD')
    if 10 <= reviews <= 100: score += 30; notes.append('REVIEW_SWEETSPOT')
    elif reviews > 100: score += 10; notes.append('MANY_REVIEWS')
    else: score += 5
    if rating >= 4.0: score += 15; notes.append('GOOD_RATING')
    if photos >= 10: score += 5; notes.append('PHOTOS')
    return score, notes

scored = []
for lead in plumbing_only:
    s, notes = score_lead(lead)
    scored.append({
        'score': s, 'notes': '|'.join(notes),
        'title': lead.get('title'),
        'town': extract_town(lead.get('address')),
        'phone': lead.get('phone'),
        'website': lead.get('website') or '',
        'rating': lead.get('totalScore'), 'reviews': lead.get('reviewsCount'),
        'category': lead.get('categoryName'),
        'address': lead.get('address'),
        'placeId': lead.get('placeId'),
        'url': lead.get('url'),
    })
scored.sort(key=lambda x: -x['score'])

csv_path = DATA / f'{args.dataset}_clean_scored.csv'
with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(scored[0].keys())); w.writeheader(); w.writerows(scored)

hot = [s for s in scored if s['score'] >= 70]
warm = [s for s in scored if 50 <= s['score'] < 70]
print(f'\n=== Cleaned NI plumbing+heating list ===')
print(f'  Total qualifying: {len(scored)}')
print(f'  HOT  (70+):   {len(hot)}')
print(f'  WARM (50-69): {len(warm)}')

# Town distribution of HOT
from collections import Counter
hot_towns = Counter(h['town'] for h in hot)
print(f'\n=== HOT by town ===')
for t, n in hot_towns.most_common(20):
    print(f'  {t:<30} {n}')

# Markdown dump
md = ['# Reskn — Cleaned HOT NI Plumbing/Heating Leads', '']
md.append(f'**{len(hot)} HOT leads** after strict filter: NI postcode + plumbing/heating category + 5+ reviews + ≥3.5★ + has phone + no chain.')
md.append('')
md.append('| # | Score | Business | Town | ⭐ | Rev | Site | Phone |')
md.append('|---|---|---|---|---|---|---|---|')
for i, r in enumerate(hot, 1):
    name = (r['title'] or '?').replace('|', '/')[:40]
    md.append(f"| {i} | {r['score']} | {name} | {r['town']} | {r['rating']} | {r['reviews']} | {site_status(r['website'])} | {r['phone']} |")

no_site = sum(1 for r in hot if not r['website'])
fb_only = sum(1 for r in hot if r['website'] and 'facebook' in (r['website'] or '').lower())
md.append('')
md.append(f'## Site breakdown')
md.append(f'- No website at all: **{no_site}** (generate from scratch)')
md.append(f'- Facebook-only: **{fb_only}** (scrape FB for content)')

(out / 'HOT-leads-clean.md').write_text('\n'.join(md), encoding='utf-8')
print(f'\nWrote clean leads to {out / "HOT-leads-clean.md"}')
