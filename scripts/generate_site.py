"""Generate a landing page for a HOT lead with no current website.

Usage:
  python generate_site.py "Kevin Brogan Plumbing & Heating Ltd"
  python generate_site.py --slug ards-comber-boiler-services
  python generate_site.py --row 0   # first row of HOT-leads.csv
"""
import os, sys, io, json, csv, re, argparse, pathlib, time

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Load env from repo root
ENV_PATH = ROOT / '.env'
if ENV_PATH.exists():
    for line in open(ENV_PATH, encoding='utf-8'):
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.strip().split('=', 1)
            os.environ.setdefault(k, v.strip('"').strip("'"))
HOT_CSV = ROOT / 'data' / 'HOT-leads.csv'
PROMPT_PATH = ROOT / 'prompts' / 'generate-system.md'
OUT_DIR = ROOT / 'out'

MODEL = 'claude-sonnet-4-6'  # Sonnet 4.6 — current production model, fast for landing pages

def _client():
    """Lazy-import anthropic to avoid Windows httpx WPAD hang at module import time."""
    from anthropic import Anthropic
    return Anthropic()

def slugify(s):
    s = re.sub(r'[^\w\s-]', '', (s or '').lower()).strip()
    return re.sub(r'[\s_]+', '-', s)[:60]

def load_hot():
    rows = list(csv.DictReader(open(HOT_CSV, encoding='utf-8-sig')))
    return rows

def find_lead(query, rows):
    q = query.lower().strip()
    # Match on name (substring) or slug
    for r in rows:
        if q in (r['Business'] or '').lower(): return r
        if q == slugify(r['Business']): return r
    return None

def build_user_message(lead):
    """Compose the structured input for Claude — everything the prompt needs."""
    return f"""Build the landing page for this business:

## Business
- **Name:** {lead['Business']}
- **Trade:** {lead.get('Category','plumber / heating engineer')}
- **Town:** {lead['Town']}
- **Address:** {lead['Address']}
- **Phone:** {lead['Phone']}

## Social proof (from Google)
- **Rating:** {lead['Rating']}★
- **Reviews:** {lead['Reviews']} reviews on Google
- **Site type currently:** {lead['Site Type']} ({"no website" if lead['Site Type']=='NONE' else lead['Site Type']})

## Existing site (if any)
{lead.get('Website') or 'None — generate from scratch.'}

## Geographic context
This business serves {lead['Town']} and surrounding areas in Northern Ireland. Pick 8-12 nearby towns to list in the service area block.

Return the complete `index.html`. No preamble.
"""

def generate(lead, force=False):
    slug = slugify(lead['Business'])
    out = OUT_DIR / slug
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'index.html'
    if target.exists() and not force:
        print(f'  exists, skip: {target}')
        return target
    sys_prompt = PROMPT_PATH.read_text(encoding='utf-8')
    user = build_user_message(lead)
    client = _client()
    print(f'  calling Claude ({MODEL})...')
    t0 = time.time()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=sys_prompt,
        messages=[{'role': 'user', 'content': user}],
    )
    html = resp.content[0].text
    # Strip code fences if model added them
    html = re.sub(r'^```(?:html)?\s*\n', '', html.strip())
    html = re.sub(r'\n```\s*$', '', html.strip())
    target.write_text(html, encoding='utf-8')
    # Also save the input that produced it (for repeatability)
    (out / 'input.json').write_text(json.dumps(lead, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'  generated in {time.time()-t0:.1f}s — {target}')
    print(f'  size: {len(html):,} chars')
    return target

def main():
    p = argparse.ArgumentParser()
    p.add_argument('query', nargs='?', help='Business name (substring) or slug')
    p.add_argument('--row', type=int, help='Index into HOT-leads.csv (0-based)')
    p.add_argument('--slug', help='Force a specific slug')
    p.add_argument('--force', action='store_true', help='Regenerate even if exists')
    args = p.parse_args()
    rows = load_hot()
    if args.row is not None:
        if args.row >= len(rows):
            print(f'Row {args.row} out of range (0..{len(rows)-1})'); sys.exit(1)
        lead = rows[args.row]
    elif args.query:
        lead = find_lead(args.query, rows)
        if not lead:
            print(f'No lead matched "{args.query}"'); sys.exit(1)
    else:
        # Default: row 0 (highest-priority HOT lead)
        lead = rows[0]
    print(f'\n=== Generating site for: {lead["Business"]} ({lead["Town"]}) ===')
    generate(lead, force=args.force)

if __name__ == '__main__':
    main()
