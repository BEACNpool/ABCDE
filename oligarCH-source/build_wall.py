#!/usr/bin/env python3
"""THE WALL — everyone who minted a custom oligarCH, read straight off the chain via Koios.

    python3 build_wall.py            # fetch chain state, bake out-pfp/wall/index.html
    python3 build_wall.py --check    # print chain vs baked drift, write nothing (cron probe)

This is the Koios runner David asked for, in two layers:
  * the BAKE — this script queries Koios (policy_asset_list -> asset_info -> asset_nft_address)
    and writes a static page with every mint embedded, so the wall loads instantly and works
    even if Koios is down;
  * the LIVE TOP-UP — the baked page ALSO asks Koios in the browser on every visit and appends
    any mints newer than the bake, so the wall is always current no matter how stale the bake.
  Suggested cadence once the wall is public: re-run + redeploy on new mints (cron + --check).

REMOVAL (David's hardwire): put an asset name (e.g. PFPa26f9dad) on its own line in
`wall_blocklist.txt` beside this script and rebuild. Blocked assets are dropped from the bake
AND filtered out of the browser top-up. The mint itself is permanent and public on chain —
the blocklist only governs this page. There is deliberately NO content filter upstream:
every mint is signed by a traceable wallet, and this list is the backstop.

⚠️ Metadata under the policy is UNTRUSTED — the validator forces the PFP name prefix and
qty 1, but a hand-built transaction can carry ANY label-721 payload. Everything that lands in
HTML is escaped, and the artwork is only shown when it is a well-formed svg data URI rendered
through <img> (which never executes scripts). Malformed entries are listed name-only.
"""
import argparse, datetime, html, json, pathlib, sys, urllib.request

HERE = pathlib.Path(__file__).parent
KOIOS = 'https://api.koios.rest/api/v1'
POLICY = json.load(open(HERE / 'applied-pfp9.json'))['validators'][0]['hash']
BLOCKFILE = HERE / 'wall_blocklist.txt'

ap = argparse.ArgumentParser()
ap.add_argument('--check', action='store_true', help='report drift, write nothing')
ap.add_argument('--out', default=str(HERE / 'out-pfp/wall'))
a = ap.parse_args()


def get(url):
    return json.load(urllib.request.urlopen(
        urllib.request.Request(url, headers={'accept': 'application/json'}), timeout=45))


def post(url, body):
    return json.load(urllib.request.urlopen(urllib.request.Request(
        url, data=json.dumps(body).encode(), method='POST',
        headers={'accept': 'application/json', 'content-type': 'application/json'}),
        timeout=60))


def load_blocklist():
    if not BLOCKFILE.exists():
        return set()
    names = set()
    for ln in BLOCKFILE.read_text().splitlines():
        ln = ln.split('#')[0].strip()
        if ln:
            names.add(ln.encode().hex())
    return names


BLOCK = load_blocklist()


def fmt_time(v):
    """Koios has served creation_time both as an ISO string and as an epoch int."""
    s = str(v)
    if s.isdigit():
        return datetime.datetime.fromtimestamp(int(s), datetime.timezone.utc).strftime('%Y-%m-%d')
    return s[:10]

# ── pull the chain state ──────────────────────────────────────────────────────
assets, off = [], 0
while True:
    page = get(f'{KOIOS}/policy_asset_list?_asset_policy={POLICY}&offset={off}')
    assets += page
    if len(page) < 1000:
        break
    off += 1000

names = [x['asset_name'] for x in assets]
blocked = [n for n in names if n in BLOCK]
names = [n for n in names if n not in BLOCK]

infos = []
for i in range(0, len(names), 50):
    infos += post(f'{KOIOS}/asset_info',
                  {'_asset_list': [[POLICY, n] for n in names[i:i + 50]]})

cards = []
for inf in infos:
    nhex = inf['asset_name']
    name = bytes.fromhex(nhex).decode('ascii', 'replace')
    md = (inf.get('minting_tx_metadata') or {}).get('721', {}).get(POLICY, {}).get(name, {})
    img = ''.join(md.get('image', []) if isinstance(md.get('image'), list)
                  else [md.get('image') or ''])
    if not img.startswith('data:image/svg+xml;base64,'):
        img = ''                                   # hand-built junk: keep the row, drop the art
    holder = ''
    try:
        h = get(f'{KOIOS}/asset_nft_address?_asset_policy={POLICY}&_asset_name={nhex}')
        holder = h[0]['payment_address'] if h else ''
    except Exception:
        pass
    cards.append(dict(
        n=nhex, name=name, img=img,
        line=str(md.get('Line', '') or ''),
        traits={k: str(md[k]) for k in
                ('Background', 'Headwear', 'Eyes', 'Mouth', 'Neck', 'Face') if k in md},
        tx=inf.get('minting_tx_hash', ''),
        time=fmt_time(inf.get('creation_time', '')),
        addr=holder))
cards.sort(key=lambda c: (c['time'], c['name']))          # mint order; page shows newest first

if a.check:
    print(f'  chain    {len(assets)} minted under {POLICY[:16]}…')
    print(f'  blocked  {len(blocked)}')
    print(f'  wall     {len(cards)}')
    sys.exit(0)

# ── bake the page ─────────────────────────────────────────────────────────────
esc = html.escape


def card_html(i, c):
    """One framed picture on the wall: gold frame + mat, the art, a brass plaque."""
    who = (f'<a href="https://pool.pm/{esc(c["addr"])}" target="_blank" rel="noopener">'
           f'{esc(c["addr"][:14])}…{esc(c["addr"][-4:])}</a>' if c['addr'] else '<span>—</span>')
    art = (f'<img src="{esc(c["img"])}" alt="{esc(c["name"])}" loading="lazy">' if c['img']
           else '<div class="noart">not renderable</div>')
    line = f'<div class="cline">&ldquo;{esc(c["line"])}&rdquo;</div>' if c['line'] else ''
    return (f'<div class="card"><div class="art">{art}</div>'
            f'<div class="plq">&#8470;{i} &middot; '
            f'<a href="https://cexplorer.io/tx/{esc(c["tx"])}" target="_blank" '
            f'rel="noopener">{esc(c["name"])}</a></div>'
            f'{line}<div class="cwho">{who}<span>{esc(c["time"])}</span></div></div>')


grid = ''.join(card_html(i + 1, c) for i, c in reversed(list(enumerate(cards))))

PAGE = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>oligarCH — the wall of oligarCHs</title>
<style>
 :root{{--ink:#eceaea;--dim:#9a9aa4;--gold:#c9a227}}
 *{{box-sizing:border-box}}
 body{{margin:0;color:var(--ink);
   background:#131015 radial-gradient(1100px 700px at 50% 240px,#221d26,#131015);
   font:16px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
 .wrap{{max-width:980px;margin:0 auto;padding:26px 16px 70px}}
 .kicker{{font:700 11px/1 sans-serif;letter-spacing:.18em;color:var(--gold)}}
 h1{{font:900 clamp(30px,8vw,52px)/1 sans-serif;letter-spacing:-.03em;margin:4px 0 6px}}
 .sub{{color:var(--dim);font-size:14.5px;margin:0 0 6px;max-width:640px}}
 #tally{{font:800 13px ui-monospace,monospace;color:var(--gold);margin:10px 0 4px}}
 .warn{{margin:12px 0 4px;padding:11px 13px;border:1px solid #8a6a25;border-radius:12px;
   background:#1c1712cc;color:#d8c9a4;font-size:13.5px;max-width:640px}}
 /* the wall itself: framed pictures, hung centred, rows fill in as mints arrive */
 .grid{{display:flex;flex-wrap:wrap;justify-content:center;gap:38px;padding:30px 0 10px}}
 .card{{width:min(252px,80vw);background:#26231d;padding:12px 12px 9px;
   border:9px solid #7c5d20;outline:2px solid #47360f;
   box-shadow:inset 0 0 0 3px var(--gold),0 20px 34px #000d,0 5px 10px #0009}}
 .art{{aspect-ratio:1;background:#141416;border:1px solid #0009}}
 .art img{{width:100%;height:100%;display:block}}
 .noart{{display:flex;align-items:center;justify-content:center;height:100%;
   color:#5a5a64;font:700 12px sans-serif}}
 .plq{{margin:10px auto 0;width:fit-content;max-width:100%;padding:4px 12px;border-radius:3px;
   background:linear-gradient(#e0c25a,#a8842a);color:#241c08;border:1px solid #6b5316;
   font:800 11px ui-monospace,monospace;letter-spacing:.04em;white-space:nowrap;
   overflow:hidden;text-overflow:ellipsis}}
 .plq a{{color:#241c08;text-decoration:none}}
 .cline{{text-align:center;padding:7px 4px 0;font:800 14px sans-serif;color:#d8c9a4;
   word-break:break-word}}
 .cwho{{display:flex;justify-content:space-between;gap:6px;padding:7px 2px 0;
   color:#8a8a94;font:10.5px ui-monospace,monospace}}
 .cwho a{{color:#8a8a94}} .cwho a:hover{{color:var(--gold)}}
 .fresh{{box-shadow:inset 0 0 0 3px var(--gold),0 0 0 3px var(--gold),0 20px 34px #000d}}
 .of{{color:var(--gold);font-style:italic}}
 .cta{{display:inline-block;margin-top:26px;padding:14px 22px;border-radius:12px;
   background:var(--gold);color:#141414;font:900 15px sans-serif;text-decoration:none}}
 .foot{{margin-top:26px;color:var(--dim);font-size:12.5px}}
 code{{font:11px ui-monospace,monospace;color:var(--dim);word-break:break-all}}
</style></head><body><div class="wrap">
 <div class="kicker">oligarCH &middot; PIECE 9 &middot; MINTED BY THE HOLDERS</div>
 <h1>THE WALL <span class="of">of oligarCHs</span></h1>
 <p class="sub">The ninth piece of oligarCH is not one picture — it&rsquo;s <b>yours</b>.
   Hold <b>any one</b> of the eight, make your own, and it lands on this wall automatically:
   the page reads the chain itself. Every picture lives <b>entirely inside its minting
   transaction</b> — pull the metadata apart and this exact image falls out.</p>
 <div id="tally">{len(cards)} ON THE WALL &middot; FOREVER OPEN</div>

 <p class="warn">Any one of the eight pieces is your key. They close
   <b>August 8&ndash;9, 2026</b> and can never be minted again — the ninth itself
   <b>never closes</b>.</p>

 <div class="grid" id="grid">{grid}</div>
 <a class="cta" href="../">Make yours &rarr;</a>
 <p class="foot">Reads live from Koios on every visit — a fresh mint appears here on its own.<br>
 Open source, no server: even if this site disappears, the policy lives on — anyone can clone
 the page, or hand-build the transaction, and keep minting oligarCHs forever.<br>
 <code>policy {POLICY}</code></p>

<script>
// ⚠️ api.koios.rest sends no CORS headers — a browser cannot call it directly. The BEACN
// Cloudflare worker mirrors /api/v1/* with CORS (same trick the Ledger Scrolls readers use),
// so it goes first; bare Koios stays as a fallback in case the worker ever grows CORS.
const SOURCES = ['https://koios.beacn.workers.dev/api/v1', {json.dumps(KOIOS)}];
const POLICY = {json.dumps(POLICY)};
async function kget(path, opts) {{
  let last;
  for (const s of SOURCES) {{
    try {{ const r = await fetch(s + path, opts); if (r.ok) return await r.json();
          last = new Error('http ' + r.status); }}
    catch (e) {{ last = e; }}
  }}
  throw last;
}}
const HAVE = new Set({json.dumps([c['n'] for c in cards])});
const BLOCK = new Set({json.dumps(sorted(BLOCK | {n for n in blocked}))});
let COUNT = {len(cards)};
const $ = s => document.querySelector(s);
const el = (t, cls, txt) => {{ const e = document.createElement(t);
  if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; return e; }};

// the live top-up: anything minted since the bake appears without a redeploy
(async () => {{
  try {{
    const list = await kget('/policy_asset_list?_asset_policy=' + POLICY);
    const fresh = list.map(x => x.asset_name).filter(n => !HAVE.has(n) && !BLOCK.has(n));
    if (!fresh.length) return;
    const infos = await kget('/asset_info', {{method:'POST',
      headers:{{'content-type':'application/json'}},
      body: JSON.stringify({{_asset_list: fresh.map(n => [POLICY, n])}})}});
    for (const inf of infos) {{
      const name = inf.asset_name_ascii ||
        (inf.asset_name.match(/../g)||[]).map(h=>String.fromCharCode(parseInt(h,16))).join('');
      const md = ((inf.minting_tx_metadata||{{}})['721']||{{}})[POLICY]?.[name] || {{}};
      const img = Array.isArray(md.image) ? md.image.join('') : (md.image || '');
      const card = el('div','card fresh');
      const art = el('div','art');
      if (img.startsWith('data:image/svg+xml;base64,')) {{
        const im = el('img'); im.src = img; im.alt = name; art.appendChild(im);
      }} else art.appendChild(el('div','noart','not renderable'));
      card.appendChild(art);
      const plq = el('div','plq'); COUNT += 1;
      plq.appendChild(document.createTextNode('\\u2116' + COUNT + ' \\u00b7 '));
      const nm = el('a','',name);
      nm.href = 'https://cexplorer.io/tx/' + encodeURIComponent(inf.minting_tx_hash||'');
      nm.target = '_blank'; nm.rel = 'noopener'; plq.appendChild(nm);
      card.appendChild(plq);
      if (md.Line) card.appendChild(el('div','cline','\\u201c' + md.Line + '\\u201d'));
      const t = inf.creation_time;
      const day = typeof t === 'number' ? new Date(t*1000).toISOString().slice(0,10)
                                        : String(t||'').slice(0,10);
      const who = el('div','cwho');
      who.appendChild(el('span','', 'just minted'));
      who.appendChild(el('span','', day));
      card.appendChild(who);
      $('#grid').prepend(card);
    }}
    $('#tally').textContent = COUNT + ' ON THE WALL \\u00b7 FOREVER OPEN';
  }} catch (e) {{ /* koios down -> the baked wall stands */ }}
}})();
</script></body></html>
"""

OUT = pathlib.Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_text(PAGE)
print(f'  policy   {POLICY}')
print(f'  minted   {len(assets)}   on the wall {len(cards)}   blocked {len(blocked)}')
print(f'  out      {OUT / "index.html"}  ({len((OUT / "index.html").read_bytes()):,} B)')
