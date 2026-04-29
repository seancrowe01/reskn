"""Batch-generate sites for every lead.

Runs through HOT-leads.csv (no website -> generate_site.py) and
WARM-leads.csv (has website -> redesign_site.py).

Skips any slug that already has out/<slug>/index.html.
Resumable: if it dies, just rerun. Already-built sites are skipped.

Usage:
  python scripts/batch_generate.py                # everything
  python scripts/batch_generate.py --hot          # HOT only (37 sites)
  python scripts/batch_generate.py --warm         # WARM only (214 sites)
  python scripts/batch_generate.py --limit 5      # first 5 of each
  python scripts/batch_generate.py --dry-run      # show what would run
"""
import os, sys, io, csv, re, argparse, pathlib, time, traceback

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Make sibling scripts importable
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate_site import generate, slugify, load_hot
from redesign_site import redesign, load_warm

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'out'
LOG_PATH = ROOT / 'data' / 'batch-log.csv'

def already_built(slug):
    return (OUT_DIR / slug / 'index.html').exists()

def log_result(row):
    """Append one line to batch-log.csv (creates header on first write)."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG_PATH.exists()
    with open(LOG_PATH, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['ts', 'mode', 'slug', 'business', 'status', 'duration_s', 'error'])
        w.writerow(row)

def run_one(lead, mode, dry_run):
    slug = slugify(lead['Business'])
    if already_built(slug):
        print(f'  [skip] {slug} (already built)')
        return 'skip', 0, ''
    if dry_run:
        print(f'  [dry-run] would {mode}: {lead["Business"]}')
        return 'dry-run', 0, ''
    t0 = time.time()
    try:
        if mode == 'generate':
            generate(lead, force=False)
        else:
            redesign(lead, force=False)
        return 'ok', round(time.time() - t0, 1), ''
    except Exception as e:
        traceback.print_exc(limit=3)
        return 'fail', round(time.time() - t0, 1), str(e)[:200]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--hot', action='store_true', help='HOT only (no website -> generate)')
    p.add_argument('--warm', action='store_true', help='WARM only (has website -> redesign)')
    p.add_argument('--limit', type=int, help='Cap rows per list')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    do_hot = args.hot or not (args.hot or args.warm)
    do_warm = args.warm or not (args.hot or args.warm)

    queue = []
    if do_hot:
        hot = load_hot()
        if args.limit: hot = hot[:args.limit]
        queue += [('generate', r) for r in hot]
    if do_warm:
        warm = load_warm()
        if args.limit: warm = warm[:args.limit]
        queue += [('redesign', r) for r in warm]

    print(f'\nQueue: {len(queue)} total ({sum(1 for m,_ in queue if m=="generate")} HOT, {sum(1 for m,_ in queue if m=="redesign")} WARM)')
    print(f'Mode: {"DRY RUN" if args.dry_run else "live"}\n')

    stats = {'ok': 0, 'skip': 0, 'fail': 0, 'dry-run': 0}
    overall_start = time.time()

    for i, (mode, lead) in enumerate(queue, 1):
        print(f'[{i}/{len(queue)}] {mode} :: {lead["Business"]} ({lead["Town"]})')
        status, dur, err = run_one(lead, mode, args.dry_run)
        stats[status] = stats.get(status, 0) + 1
        log_result([
            time.strftime('%Y-%m-%d %H:%M:%S'),
            mode, slugify(lead['Business']), lead['Business'],
            status, dur, err,
        ])
        if status == 'ok' and not args.dry_run:
            elapsed = time.time() - overall_start
            done = stats['ok'] + stats['skip']
            remaining = len(queue) - i
            avg = elapsed / max(stats['ok'], 1)
            eta_min = (avg * remaining) / 60
            print(f'  cumulative: {stats["ok"]} ok, {stats["skip"]} skip, {stats["fail"]} fail | ETA ~{eta_min:.0f} min\n')

    print('\n=== BATCH COMPLETE ===')
    for k, v in stats.items():
        print(f'  {k:8} {v}')
    print(f'\nLog: {LOG_PATH}')
    print(f'Outputs: {OUT_DIR}')

if __name__ == '__main__':
    main()
