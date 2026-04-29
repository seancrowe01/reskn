"""Deploy a generated site to Vercel.

Two modes:
  --preview  (default) deploys to <slug>.vercel.app for cold-call demos
  --domain   adds a custom domain after deal closes

Requires Vercel CLI installed:
  npm i -g vercel

And one of:
  - vercel login (interactive, one-time)
  - VERCEL_TOKEN in .env (headless, for batch deploys)

Usage:
  python scripts/deploy_vercel.py kevin-brogan-plumbing
  python scripts/deploy_vercel.py kevin-brogan-plumbing --domain kevinbroganplumbing.co.uk
  python scripts/deploy_vercel.py --batch                    # deploy every out/<slug>/ folder
"""
import os, sys, io, json, re, argparse, pathlib, subprocess, shutil

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
OUT_DIR = ROOT / 'out'
DEPLOY_LOG = ROOT / 'data' / 'deploy-log.csv'

def find_vercel_cli():
    """Locate the vercel CLI. On Windows it's usually vercel.cmd."""
    for cmd in ['vercel', 'vercel.cmd']:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def ensure_project_config(site_dir, slug):
    """Drop a vercel.json in the site folder so the static HTML is served correctly."""
    cfg_path = site_dir / 'vercel.json'
    if not cfg_path.exists():
        cfg = {
            "cleanUrls": True,
            "trailingSlash": False,
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {"key": "X-Content-Type-Options", "value": "nosniff"},
                        {"key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains"},
                    ],
                }
            ],
        }
        cfg_path.write_text(json.dumps(cfg, indent=2), encoding='utf-8')

def deploy_preview(slug):
    """Deploy site to <slug>.vercel.app (or similar). Returns the production URL."""
    site_dir = OUT_DIR / slug
    if not (site_dir / 'index.html').exists():
        raise RuntimeError(f'No index.html at {site_dir}')

    ensure_project_config(site_dir, slug)
    cli = find_vercel_cli()
    if not cli:
        raise RuntimeError('Vercel CLI not found. Run: npm i -g vercel')

    cmd = [cli, 'deploy', '--yes', '--prod', '--name', slug]
    token = os.environ.get('VERCEL_TOKEN')
    if token:
        cmd += ['--token', token]

    print(f'  vercel deploy --prod --name {slug}')
    result = subprocess.run(cmd, cwd=str(site_dir), capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print('  STDOUT:', result.stdout[-500:])
        print('  STDERR:', result.stderr[-500:])
        raise RuntimeError(f'vercel deploy failed (exit {result.returncode})')

    # Vercel prints the production URL on the last line of stdout
    url_match = re.search(r'(https://[\w\-]+\.vercel\.app)', result.stdout + result.stderr)
    if not url_match:
        print('  raw output:', result.stdout, result.stderr)
        raise RuntimeError('Could not parse Vercel URL from output')

    url = url_match.group(1)
    print(f'  ✓ live: {url}')
    log_deploy(slug, 'preview', url, '')
    return url

def attach_domain(slug, domain):
    """Add a custom domain to a deployed project. Prints DNS records to send to client."""
    cli = find_vercel_cli()
    if not cli:
        raise RuntimeError('Vercel CLI not found')

    token = os.environ.get('VERCEL_TOKEN')
    base_args = []
    if token:
        base_args += ['--token', token]

    site_dir = OUT_DIR / slug
    print(f'  attaching domain {domain} to project {slug}')
    cmd = [cli, 'domains', 'add', domain, slug] + base_args
    result = subprocess.run(cmd, cwd=str(site_dir), capture_output=True, text=True, timeout=60)
    print(result.stdout)
    if result.returncode != 0:
        print('  STDERR:', result.stderr[-500:])
        raise RuntimeError(f'domain add failed')

    print('\n=== DNS RECORDS TO SEND TO CLIENT ===')
    print(f'At their domain provider, add these records:')
    print(f'  Type: A      | Name: @   | Value: 76.76.21.21')
    print(f'  Type: CNAME  | Name: www | Value: cname.vercel-dns.com')
    print(f'\nOnce added, https://{domain} will go live within an hour.')
    log_deploy(slug, 'domain', f'https://{domain}', '')

def log_deploy(slug, mode, url, notes):
    DEPLOY_LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not DEPLOY_LOG.exists()
    import csv, time
    with open(DEPLOY_LOG, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if new: w.writerow(['ts', 'slug', 'mode', 'url', 'notes'])
        w.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), slug, mode, url, notes])

def batch_deploy_all():
    """Deploy every site in out/<slug>/ that hasn't been deployed yet."""
    import csv, time
    deployed = set()
    if DEPLOY_LOG.exists():
        for r in csv.DictReader(open(DEPLOY_LOG, encoding='utf-8')):
            deployed.add(r['slug'])

    sites = sorted([d.name for d in OUT_DIR.iterdir() if d.is_dir() and (d / 'index.html').exists()])
    queue = [s for s in sites if s not in deployed]
    print(f'Found {len(sites)} built sites, {len(queue)} need deploying.')

    for i, slug in enumerate(queue, 1):
        print(f'\n[{i}/{len(queue)}] {slug}')
        try:
            deploy_preview(slug)
        except Exception as e:
            print(f'  FAIL: {e}')
            log_deploy(slug, 'preview-fail', '', str(e)[:200])

    print(f'\nDone. Log: {DEPLOY_LOG}')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('slug', nargs='?', help='Site slug (folder name in out/)')
    p.add_argument('--domain', help='Custom domain (after deal closes)')
    p.add_argument('--batch', action='store_true', help='Deploy every site in out/')
    args = p.parse_args()

    if args.batch:
        batch_deploy_all()
        return

    if not args.slug:
        print('Need a slug or --batch. Run with -h for help.')
        sys.exit(1)

    if args.domain:
        attach_domain(args.slug, args.domain)
    else:
        deploy_preview(args.slug)

if __name__ == '__main__':
    main()
