"""Export the WARM leads (score 50-69) as a Sheets-friendly CSV.
WARM leads have an existing website. The redesign tool scrapes them
and bumps any with bad sites up to HOT.

Usage:
  python scripts/export_warm_csv.py [dataset]   # default: ni-full
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
warm = [r for r in src if 50 <= int(r['score']) < 70]

# Sort by score desc then by reviews desc
def sort_key(r):
    try: revs = int(r.get('reviews') or r.get('reviewsCount') or 0)
    except: revs = 0
    return (-int(r['score']), -revs)
warm.sort(key=sort_key)

out_path = DATA / 'WARM-leads.csv'
with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Score', 'Business', 'Town', 'Address', 'Phone', 'Rating', 'Reviews', 'Website', 'Category'])
    for r in warm:
        w.writerow([
            r['score'],
            r.get('title', ''),
            r.get('town', ''),
            r.get('address', ''),
            r.get('phone', ''),
            r.get('rating') or r.get('totalScore', ''),
            r.get('reviews') or r.get('reviewsCount', ''),
            r.get('website', ''),
            r.get('category') or r.get('categoryName', ''),
        ])

print(f'Exported {len(warm)} WARM leads to:')
print(f'  {out_path}')
print()
print('Each one has a website URL the redesign tool can scrape.')
