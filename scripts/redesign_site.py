"""Redesign an existing website for a WARM lead.

Pipeline:
  1. Firecrawl scrapes the lead's existing website (markdown form).
  2. We pull the lead's metadata (rating, reviews, town, phone) from WARM-leads.csv.
  3. We feed both to Claude Sonnet 4.6 with the redesign system prompt.
  4. Claude returns a complete index.html that preserves the business identity
     but modernises the design.

Usage:
  python scripts/redesign_site.py "Huston Heating"
  python scripts/redesign_site.py --row 0
  python scripts/redesign_site.py --slug huston-heating
"""
import os, sys, io, json, csv, re, argparse, pathlib, time
import urllib.request, urllib.error

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
WARM_CSV = ROOT / 'data' / 'WARM-leads.csv'
PROMPT_PATH = ROOT / 'prompts' / 'redesign-system.md'
OUT_DIR = ROOT / 'out'
SCRAPE_CACHE = ROOT / 'data' / 'firecrawl-cache'

MODEL = 'claude-sonnet-4-6'

def _client():
    """Lazy-import anthropic to avoid Windows httpx WPAD hang at module import time."""
    from anthropic import Anthropic
    return Anthropic()

def slugify(s):
    s = re.sub(r'[^\w\s-]', '', (s or '').lower()).strip()
    return re.sub(r'[\s_]+', '-', s)[:60]

def load_warm():
    return list(csv.DictReader(open(WARM_CSV, encoding='utf-8-sig')))

def find_lead(query, rows):
    q = query.lower().strip()
    for r in rows:
        if q in (r['Business'] or '').lower(): return r
        if q == slugify(r['Business']): return r
    return None

def firecrawl_scrape(url, slug):
    """Scrape an existing site via Firecrawl. Returns markdown content.
    Caches per-slug so we don't re-scrape on retries.
    """
    SCRAPE_CACHE.mkdir(parents=True, exist_ok=True)
    cache_path = SCRAPE_CACHE / f'{slug}.md'
    if cache_path.exists():
        print(f'  using cached scrape: {cache_path.name}')
        return cache_path.read_text(encoding='utf-8')

    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        raise RuntimeError('FIRECRAWL_API_KEY not set in .env')

    print(f'  Firecrawl scraping: {url}')
    req = urllib.request.Request(
        'https://api.firecrawl.dev/v1/scrape',
        data=json.dumps({
            'url': url,
            'formats': ['markdown'],
            'onlyMainContent': True,
            'waitFor': 1500,
        }).encode(),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'Firecrawl HTTP {e.code}: {body[:300]}')
    except urllib.error.URLError as e:
        raise RuntimeError(f'Firecrawl network error: {e}')

    if not data.get('success'):
        raise RuntimeError(f'Firecrawl returned failure: {str(data)[:300]}')

    md = data.get('data', {}).get('markdown', '')
    if not md.strip():
        raise RuntimeError('Firecrawl returned empty markdown')

    cache_path.write_text(md, encoding='utf-8')
    print(f'  scraped {len(md):,} chars, cached to {cache_path.name}')
    return md

def build_user_message(lead, scraped_md):
    """Compose the structured input for Claude."""
    return f"""Redesign this existing trade website. Preserve the business identity, modernise the design.

## Business
- **Name:** {lead['Business']}
- **Trade:** {lead.get('Category','plumber / heating engineer')}
- **Town:** {lead['Town']}
- **Address:** {lead['Address']}
- **Phone:** {lead['Phone']}
- **Existing website:** {lead['Website']}

## Social proof (from Google)
- **Rating:** {lead['Rating']}★
- **Reviews:** {lead['Reviews']} reviews on Google

## Geographic context
This business serves {lead['Town']} and surrounding areas in Northern Ireland. Cross-reference the scraped content for the towns they actually cover.

## Scraped content from their existing website (source of truth for services, areas, story, accreditations)

{scraped_md[:25000]}

---

Now produce the redesigned `index.html`. Pull real services, areas, accreditations, and owner story from the scrape above. Modernise the design. Return the complete HTML, no preamble.
"""

def redesign(lead, force=False):
    slug = slugify(lead['Business'])
    out = OUT_DIR / slug
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'index.html'
    if target.exists() and not force:
        print(f'  exists, skip: {target}')
        return target

    url = lead.get('Website', '').strip()
    if not url:
        raise RuntimeError(f'No website URL for {lead["Business"]} — use generate_site.py instead')

    scraped = firecrawl_scrape(url, slug)

    sys_prompt = PROMPT_PATH.read_text(encoding='utf-8')
    user = build_user_message(lead, scraped)
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
    html = re.sub(r'^```(?:html)?\s*\n', '', html.strip())
    html = re.sub(r'\n```\s*$', '', html.strip())
    target.write_text(html, encoding='utf-8')
    (out / 'input.json').write_text(json.dumps({**lead, 'mode': 'redesign'}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'  redesigned in {time.time()-t0:.1f}s — {target}')
    print(f'  size: {len(html):,} chars')
    return target

def main():
    p = argparse.ArgumentParser()
    p.add_argument('query', nargs='?', help='Business name (substring) or slug')
    p.add_argument('--row', type=int, help='Index into WARM-leads.csv (0-based)')
    p.add_argument('--slug', help='Force a specific slug')
    p.add_argument('--force', action='store_true', help='Regenerate even if exists')
    args = p.parse_args()
    rows = load_warm()
    if args.row is not None:
        if args.row >= len(rows):
            print(f'Row {args.row} out of range (0..{len(rows)-1})'); sys.exit(1)
        lead = rows[args.row]
    elif args.query:
        lead = find_lead(args.query, rows)
        if not lead:
            print(f'No lead matched "{args.query}"'); sys.exit(1)
    else:
        lead = rows[0]
    print(f'\n=== Redesigning site for: {lead["Business"]} ({lead["Town"]}) ===')
    print(f'    Existing site: {lead["Website"]}')
    redesign(lead, force=args.force)

if __name__ == '__main__':
    main()
