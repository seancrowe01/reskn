"""Export the HOT leads (score 70+) as a Sheets-friendly CSV.

Usage:
  python scripts/export_hot_csv.py [dataset]   # default: ni-full
"""
import csv, sys, io, pathlib, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / 'data'

p = argparse.ArgumentParser()
p.add_argument('dataset', nargs='?', default='ni-full')
args = p.parse_args()

src_path = DATA / f'{args.dataset}_clean_scored.csv'
if not src_path.exists():
    sys.exit(f'No clean dataset at {src_path}. Run refine_leads.py first.')
src = csv.DictReader(open(src_path, encoding='utf-8'))
hot = [r for r in src if int(r['score']) >= 70]

def site_type(url):
    if not url: return 'NONE'
    u = url.lower()
    if 'facebook.com' in u or 'fb.com' in u: return 'FB'
    if 'instagram.com' in u: return 'IG'
    return 'OTHER'

# Sheets-friendly columns, ordered for usefulness
cols = ['Score', 'Business', 'Town', 'Phone', 'Rating', 'Reviews',
        'Site Type', 'Website', 'Category', 'Address', 'Google Maps URL', 'Place ID']
out = []
for r in hot:
    out.append({
        'Score': r['score'],
        'Business': r['title'],
        'Town': r['town'],
        'Phone': r['phone'],
        'Rating': r['rating'],
        'Reviews': r['reviews'],
        'Site Type': site_type(r['website']),
        'Website': r['website'] or '',
        'Category': r.get('category',''),
        'Address': r['address'],
        'Google Maps URL': r['url'],
        'Place ID': r['placeId'],
    })

# Sort by score desc, then reviews desc
out.sort(key=lambda x: (-int(x['Score']), -int(x['Reviews'] or 0)))

path = DATA / 'HOT-leads.csv'
with open(path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(out)

print(f'Exported {len(out)} HOT leads to:')
print(f'  {path}')
print(f'\nSheets-ready columns: {", ".join(cols)}')
print('UTF-8 BOM included so Sheets reads emoji/special chars correctly.')
