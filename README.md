# Reskn

We help small local businesses get a proper website. The robot builds the first draft. A real human polishes it. We sell it for £800. The owner owns it forever.

This repo holds everything that makes that work.

## Who this is for

- **Sean** — runs the show, scrapes leads, generates sites, deploys.
- **Jake** — calls the leads, sells the redesign.
- **Giezel** — polishes every site after a deal closes.

**If you are Giezel, open `START-HERE.md` now.** That's the only doc you need.

If you are a developer joining the project, keep reading this README.

## How it works end to end

```
1. Apify scrapes Google Maps for local plumbers in Northern Ireland
2. We filter them by review count, rating, and whether they have a website
3. Two lists come out:
   - HOT (37 leads, no website at all) -> robot generates from scratch
   - WARM (214 leads, has a bad website) -> robot redesigns existing site
4. Robot builds 251 draft sites, all live on Vercel preview URLs
5. Jake calls every lead, sends them their draft via SMS while on the call
6. When a deal closes, Giezel polishes the draft and deploys to client domain
7. Client owns it forever, no monthly fee. We move on.
```

## Quick start

You need Python 3.12+ and a few API keys.

```bash
# 1. Clone and install
git clone https://github.com/seancrowe01/reskn.git
cd reskn
pip install -r requirements.txt

# 2. Add your API keys
cp .env.example .env
# Edit .env and fill in:
#   ANTHROPIC_API_KEY  (required - for site generation)
#   APIFY_TOKEN        (required - for Google Maps scraping)
#   FIRECRAWL_API_KEY  (required for redesign mode)
#   VERCEL_TOKEN       (required for deploy)

# 3. Generate a site for one lead (no website case)
python scripts/generate_site.py "Kevin Brogan"

# 4. Generate sites for ALL leads in HOT-leads.csv
python scripts/batch_generate.py

# 5. Open any generated site in browser
# File: out/<slug>/index.html
```

## What's in here

| File / folder | What it is |
|---|---|
| `CLAUDE.md` | The project context Claude reads automatically |
| `polish-guide.md` | The 8-step delivery checklist Giezel follows |
| `prompts/generate-system.md` | The brief we give Claude to build sites from scratch |
| `prompts/redesign-system.md` | The brief we give Claude to rebuild an existing site |
| `scripts/scrape_leads.py` | Run Apify to scrape Google Maps |
| `scripts/refine_leads.py` | Filter raw leads into HOT and WARM |
| `scripts/generate_site.py` | Build one site from scratch (no existing website) |
| `scripts/redesign_site.py` | Rebuild a site that already exists (Firecrawl + Claude) |
| `scripts/batch_generate.py` | Loop through all leads, build sites in batch |
| `scripts/deploy_vercel.py` | Push a polished site live to a domain |
| `data/HOT-leads.csv` | The 37 highest-priority leads (gitignored) |
| `data/WARM-leads.csv` | The 214 leads with existing websites (gitignored) |
| `out/<slug>/` | Generated sites, one folder per lead (gitignored) |

## Lead scoring

We score every Google Maps result and bucket them into HOT, WARM, or SKIP.

| Signal | Points |
|---|---|
| No website at all | +40 |
| Facebook page as only web presence | +35 |
| 10 to 100 reviews (sweet spot) | +30 |
| Rating 4.0 or higher | +15 |
| Recent activity or 10+ photos | +5 to +10 |

**Disqualifiers** (auto-skip): no phone number, fewer than 5 reviews, rating below 3.5, chain or franchise.

- **HOT** (score 70+) → call first, generate from scratch
- **WARM** (score 50 to 69) → redesign mode (we have their existing site)
- **SKIP** (score under 50) → ignore

## Tech stack

- **Python 3.12** for the pipeline
- **Apify** (`compass/crawler-google-places`) for Google Maps scraping
- **Firecrawl** for scraping existing client websites in redesign mode
- **Anthropic Claude Sonnet 4.6** for HTML generation
- **Tailwind CSS via CDN** in the output (no build step, single self-contained file)
- **Vercel** for hosting and domain management

## Costs (rough)

- Apify Google Maps scrape: about £4 per 1,000 leads
- Claude site generation: about £0.16 per site (Sonnet 4.6)
- Firecrawl scrape: about £0.04 per site
- Vercel hosting: free tier covers up to a few hundred sites
- Domain: about £15 per year per client (we pass this through)

For 251 sites, total upfront robot cost is around £55. Each closed deal nets ~£605 after costs.

## Repo rules

- Never commit anything from `.env`. Use `.env.example` as the template.
- Never commit lead data (`data/HOT-leads.csv`, `data/WARM-leads.csv`, `data/*.json`). It's gitignored.
- Never commit generated sites (`out/*`). Also gitignored.
- All client photos go in `out/<slug>/assets/`. Also gitignored.
- The repo is private. Do not share access without Sean's say so.

## Questions

Ping Sean. If something is broken or unclear, do not guess.
