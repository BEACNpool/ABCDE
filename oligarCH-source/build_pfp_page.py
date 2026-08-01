#!/usr/bin/env python3
"""The oligarCH PFP creator — the page. A step-by-step wizard, built to feel like a phone app.

One trait category per screen, live preview always in view, Back/Next + swipe, per-option
thumbnails, then a review screen with the gate checklist and the mint. The browser assembles
the SAME string the python builder produces, and that exact string is what goes into the
minting transaction. What you see is what goes on chain.

THIS IS PIECE 9 OF THE COLLECTION (David, 2026-07-31). The ninth piece is not one picture —
it is every custom oligarCH, minted by the holders. Gate: hold AT LEAST ONE of the eight,
any of them. No deadline, no supply cap, the policy never dies; the page is open source and
anyone can clone it and keep minting. Policy `applied-pfp9.json` (any-of validator) — the
earlier all-eight policies 2927f7dd… (with the first real mint) and 7d6702e0… (T9 test) are
superseded and stay where they are.

  python3 build_pfp_page.py

⚠️ The preview is deliberately usable with NO WALLET. Browsing and customising is the fun part
and the reason anyone stays on the page; the gate applies at MINT, not at the door. It also
means marketing footage can show the toy without a wallet dance.

⚠️ The mouth is ONE slot worn two ways: a MOOD (expression) or a PROP (smoke/teeth) — a prop
covers the expression, so picking a prop shows over the mood and "None" hands the mouth back.
The wizard sells that honestly; the data model stays the python builder's single `mouth`.

⚠️ Test hooks the harnesses rely on — keep them: `.chip[data-cat][data-val]` buttons,
`window.__svg` (the exact assembled string), `window.__goto(i)` (jump to a step),
`window.__unsigned`, and the ids #text #mint #status #stage.
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import build_pfp as B                                                    # the catalogue

ap = argparse.ArgumentParser()
ap.add_argument('--out', default=str(HERE / 'out-pfp'))
a = ap.parse_args()

BP = json.load(open(HERE / 'applied-pfp9.json'))['validators'][0]
SCRIPT_HEX, POLICY = BP['compiledCode'], BP['hash']
COSTS = json.load(open(HERE / 'costmodel-v3.json'))

# The eight pieces. The validator wants AT LEAST ONE of these among the spent inputs.
GATE = ([('BYTTG', 'BURN YOU TO THE GROUND', '2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d'),
         ('TGM', 'THE GREAT MIGRATION', '7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5'),
         ('IVYOM', 'I VOTE YES ON ME', '5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e'),
         ('ORG', 'ORGANIC DISTRIBUTION', '80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b'),
         ('HOTEL', 'YOU CAN NEVER LEAVE', 'd91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89'),
         ('NDL', 'NO DOORS LEFT', '64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361'),
         ('DNPG', 'DO NOT PASS GO', '3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00'),
         ('SMOKE', 'DECENTRALIZED', '9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc')])

CAT = {k: d for k, d in B.CATS}
LABEL = {'bg': 'Background', 'hat': 'Headwear', 'eyes': 'Eyes', 'mouth': 'Mouth',
         'neck': 'Neck', 'mark': 'Face', 'pet': 'Accessory'}
PRETTY = {'none': 'None', 'signature': 'Signature grin', 'thug': 'Thug', 'ice': 'Iced',
          'ada': 'ADA', 'x': 'X eyes', 'dollar': 'Dollar eyes', 'teardrop2': 'Two tears',
          'grill': 'Gold grill', 'cig': 'Cigarette', 'top': 'Top hat', 'band': 'Bandana',
          'bars': 'Prison bars', 'gold': 'Gold',
          # backgrounds are the eight pieces, labelled by ticker
          'byttg': 'BYTTG', 'tgm': 'TGM', 'ivyom': 'IVYOM', 'org': 'ORG',
          'hotel': 'HOTEL', 'ndl': 'NDL', 'dnpg': 'DNPG', 'smoke': 'SMOKE',
          # the exotic african birds
          'crane': 'Crowned crane', 'roller': 'Lilac roller', 'grey': 'Grey parrot',
          'flamingo': 'Flamingo'}

# The wizard's split of the mouth slot. Editorial, so it is asserted against the catalogue:
# a new mouth trait must be filed as a mood or a prop before the page will build.
MOODS = ['signature', 'mad', 'duck', 'tongue']
PROPS = ['none', 'gold', 'diamond', 'grill', 'cigar', 'joint', 'cig']
assert set(MOODS) | set(PROPS) - {'none'} == set(B.MOUTH), \
    'every mouth trait must be classified as a mood or a prop'

STEPS = [
    dict(id='mood', cat='mood', title='The face',      sub='How is he feeling today?'),
    dict(id='eyes', cat='eyes', title='Eyes & shades', sub='What the world gets to see.'),
    dict(id='hat',  cat='hat',  title='Headwear',      sub='Crown him. Or don&rsquo;t.'),
    dict(id='neck', cat='neck', title='The chain',     sub='Weight around the neck.'),
    dict(id='prop', cat='prop', title='Smoke &amp; grillz',
         sub='Worn over the mouth — <b>None</b> keeps the face you chose.'),
    dict(id='mark', cat='mark', title='Face marks',    sub='Scars tell stories.'),
    dict(id='pet',  cat='pet',  title='Accessories',
         sub='An exotic African bird for the shoulder.'),
    dict(id='bg',   cat='bg',   title='Background',
         sub='Straight off the eight pieces — or the pen.'),
    dict(id='text', cat=None,   title='Your line',     sub='Name, ticker, handle — or a saying.'),
    dict(id='mint', cat=None,   title='Review &amp; mint', sub='Look him over. Then make him real.'),
]

HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>oligarCH — make your own</title>
<style>
 :root{{--bg:#101012;--panel:#18181c;--line:#2a2a31;--ink:#eceaea;--dim:#9a9aa4;
       --red:#ed1c24;--gold:#c9a227;--ok:#4ade80}}
 *{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
 html{{scrollbar-gutter:stable}}
 body{{margin:0;background:var(--bg);color:var(--ink);
   font:16px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
 .wrap{{max-width:520px;margin:0 auto;padding:14px 16px calc(96px + env(safe-area-inset-bottom))}}
 .kicker{{font:700 11px/1 sans-serif;letter-spacing:.18em;color:var(--gold)}}
 h1{{font:900 clamp(22px,6vw,30px)/1 sans-serif;letter-spacing:-.03em;margin:2px 0 8px}}
 .need{{margin:0 0 10px;padding:8px 11px;border:1px solid #8a6a25;border-radius:10px;
   background:#1c1712;color:#d8c9a4;font-size:12.5px;line-height:1.45}}
 .need a{{color:var(--gold)}}
 #stage{{border:1.5px solid #8a6a25;border-radius:16px;overflow:hidden;background:#141416;
   aspect-ratio:1;position:sticky;top:10px;z-index:5;width:min(100%,44vh);margin:0 auto;
   box-shadow:0 10px 30px #000a}}
 #stage svg{{width:100%;height:100%;display:block}}
 #rand{{position:absolute;top:10px;right:10px;z-index:6;width:42px;height:42px;border-radius:12px;
   border:1px solid #8a6a25;background:#141416e6;color:var(--ink);font-size:20px;cursor:pointer}}
 #size{{position:absolute;left:10px;top:14px;z-index:6;font:700 11px ui-monospace,monospace;
   color:#eceaea;background:#101012b8;padding:3px 8px;border-radius:8px}}
 .prog{{display:flex;align-items:center;gap:6px;margin:14px 2px 4px}}
 .dot{{width:9px;height:9px;border-radius:50%;background:var(--line);border:0;padding:0;
   cursor:pointer;transition:all .18s}}
 .dot.done{{background:#8a6a25}}
 .dot.cur{{background:var(--gold);transform:scale(1.45)}}
 .stepno{{margin-left:auto;color:var(--dim);font:700 12px ui-monospace,monospace}}
 .panel{{display:none;animation:in .22s ease}}
 .panel.on{{display:block}}
 @keyframes in{{from{{opacity:0;transform:translateX(26px)}}to{{opacity:1;transform:none}}}}
 .panel h2{{font:900 20px sans-serif;margin:10px 0 2px}}
 .panel .sub{{color:var(--dim);font-size:13.5px;margin:0 0 12px}}
 .cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}}
 .chip{{padding:0;border-radius:14px;border:1.5px solid var(--line);background:var(--panel);
   color:var(--ink);cursor:pointer;overflow:hidden;text-align:center}}
 .chip .th{{display:block;aspect-ratio:1;background:#141416}}
 .chip .th svg{{width:100%;height:100%;display:block}}
 .chip .lb{{display:block;font:700 12.5px sans-serif;padding:7px 4px 8px;white-space:nowrap;
   overflow:hidden;text-overflow:ellipsis}}
 .chip.on{{border-color:var(--gold);box-shadow:0 0 0 1.5px var(--gold)}}
 .chip.on .lb{{color:var(--gold)}}
 .txt{{display:flex;gap:8px;align-items:center;margin-top:8px}}
 .txt input{{flex:1;min-width:0;padding:13px;border-radius:12px;border:1.5px solid var(--line);
   background:var(--panel);color:var(--ink);font:800 17px ui-monospace,monospace;
   letter-spacing:.06em;text-transform:uppercase}}
 .txt input:focus{{outline:none;border-color:var(--gold)}}
 .txt span{{color:var(--dim);font:700 13px ui-monospace,monospace;min-width:48px;text-align:right}}
 .hint{{color:var(--dim);font-size:13px;margin:10px 0 0}}
 .forever{{margin-top:14px;padding:11px 13px;border:1px solid #8a6a25;border-radius:12px;
   background:#1c1712;color:#d8c9a4;font-size:13.5px}}
 .sum{{border:1px solid var(--line);border-radius:12px;background:var(--panel);overflow:hidden;
   margin-top:10px}}
 .sum .row{{display:flex;justify-content:space-between;gap:10px;padding:8px 12px;
   border-bottom:1px solid var(--line);font-size:13.5px}}
 .sum .row:last-child{{border-bottom:0}}
 .sum .row b{{font-weight:800}} .sum .row span{{color:var(--dim)}}
 .meta{{display:flex;justify-content:space-between;color:var(--dim);font-size:12.5px;margin-top:10px}}
 .gate{{margin-top:12px;border:1px solid var(--line);border-radius:12px;background:var(--panel);
   overflow:hidden}}
 .row2{{display:flex;align-items:center;gap:9px;padding:8px 12px;border-bottom:1px solid var(--line);
   font-size:13.5px}}
 .row2:last-child{{border-bottom:0}}
 .row2 .t{{font-weight:800;min-width:58px}} .row2 .p{{color:var(--dim);flex:1;font-size:12px}}
 .mark{{width:20px;text-align:center;font-weight:900}} .yes{{color:var(--ok)}} .no{{color:#6b6b74}}
 #mint{{width:100%;margin-top:12px;padding:16px;border-radius:14px;border:1px solid #8a6a25;
   background:var(--gold);color:#141414;font:900 17px sans-serif;cursor:pointer}}
 #mint[disabled]{{opacity:.45;cursor:not-allowed}}
 #reset{{width:100%;margin-top:10px;padding:10px;border-radius:10px;border:1px solid var(--line);
   background:none;color:var(--dim);font:700 13px sans-serif;cursor:pointer}}
 #status{{display:none;margin-top:12px;padding:11px 13px;border-radius:10px;background:var(--panel);
   border:1px solid var(--line);font-size:14px;word-break:break-word}}
 #status.on{{display:block}} #status.err{{border-color:#7a2b2b;color:#ffb4b4}}
 #status.ok{{border-color:#2b7a3f;color:#b4ffc8}}
 #status a{{color:var(--gold)}}
 .nav{{position:fixed;left:0;right:0;bottom:0;z-index:9;display:flex;gap:10px;
   padding:10px 16px calc(10px + env(safe-area-inset-bottom));
   background:linear-gradient(#10101200,#101012 34%)}}
 .nav .inner{{display:flex;gap:10px;width:100%;max-width:488px;margin:0 auto}}
 #back{{flex:1;padding:14px;border-radius:14px;border:1.5px solid var(--line);background:var(--panel);
   color:var(--ink);font:800 15px sans-serif;cursor:pointer}}
 #back[disabled]{{opacity:.35;cursor:default}}
 #next{{flex:2.2;padding:14px;border-radius:14px;border:1px solid #8a6a25;background:var(--gold);
   color:#141414;font:900 15px sans-serif;cursor:pointer}}
 code{{font:12px ui-monospace,monospace;color:var(--dim);word-break:break-all}}
</style></head><body><div class="wrap">
 <div class="kicker">oligarCH &middot; HOLDERS ONLY</div>
 <h1>Make your own</h1>
 <!-- The gate warning lives HERE, on screen one, not buried on the review step — nobody
      should dress the man for ten steps and only then learn they cannot mint (David). -->
 <div class="need">&#128273; Minting needs an oligarCH in your wallet &mdash; <b>any one of
   the eight</b> unlocks it. Don&rsquo;t hold one? <a href="../">Grab a piece first</a>.
   You can still design without one &mdash; you just can&rsquo;t mint.</div>

 <div id="stage"><button id="rand" title="Randomise">🎲</button><span id="size"></span></div>

 <div class="prog" id="prog"></div>
 <div id="panels"></div>
</div>

<div class="nav"><div class="inner">
  <button id="back">&larr; Back</button>
  <button id="next">Next &rarr;</button>
</div></div>

<script type="module">
const TRAITS = {json.dumps({k: CAT[k] for k, _ in B.CATS})};
const ORDER  = {json.dumps([k for k, _ in B.CATS])};
const LABEL  = {json.dumps(LABEL)};
const PRETTY = {json.dumps(PRETTY)};
const MOODS  = {json.dumps(MOODS)};
const PROPS  = {json.dumps(PROPS)};
const STEPS  = {json.dumps(STEPS)};
const HEAD_DEFS = {json.dumps(B.HEAD_DEFS)};
const HEAD = {json.dumps(B.HEAD)};
const GLY = {json.dumps(B.ALL_GLY)};
const GID = {json.dumps(B.GID)};
const ADV = {json.dumps(B.ADV)};
const MAXT = {B.MAX_TEXT};
const K = {json.dumps(B.K)};
const SHIRT = {json.dumps(B.SHIRT)}, DARK = {json.dumps(B.DARK)}, CREAM = {json.dumps(B.CREAM)};
const GATE = {json.dumps([{'t': t, 'ph': ph, 'p': p} for t, ph, p in GATE])};
const SCRIPT_HEX = {json.dumps(SCRIPT_HEX)};
const POLICY_EXPECT = {json.dumps(POLICY)};
const COSTS = {json.dumps(COSTS)};
const TICKER = 'PFP';
const PP = {{feeA:'44',feeB:'155381',utxoByte:'4310',maxTx:16384,maxVal:5000,
  poolDep:'500000000',keyDep:'2000000',pmN:'577',pmD:'10000',psN:'721',psD:'10000000'}};
const EX_MEM='2000000', EX_STEPS='700000000';
const CDN='https://cdn.jsdelivr.net/npm/@emurgo/cardano-serialization-lib-browser@15.0.3/';

// ⚠️ Math.round(-5.5) is -5 in JS but -6 under python's '.0f' banker's rounding. The preview
// must be byte-identical to what the python reference builds, so both use floor(v + 0.5).
const R = v => Math.floor(v + 0.5);
const $ = id => document.getElementById(id);
const hex = b => [...b].map(x=>x.toString(16).padStart(2,'0')).join('');
const unhex = s => new Uint8Array(s.match(/../g).map(x=>parseInt(x,16)));
const say = (m,k) => {{ const e=$('status'); e.className='on '+(k||''); e.innerHTML=m; }};
const nice = v => PRETTY[v] || (v[0].toUpperCase()+v.slice(1));

// ── state ─────────────────────────────────────────────────────────────────────
// The mouth is ONE slot: a prop covers the mood; 'none' hands the mouth back to the mood.
const pick = {{ mood: MOODS[0], prop: 'none' }};
ORDER.filter(k => k !== 'mouth').forEach(k => pick[k] = Object.keys(TRAITS[k])[0]);
const mouthVal = () => pick.prop !== 'none' ? pick.prop : pick.mood;
const catVal = k => k === 'mouth' ? mouthVal() : pick[k];
const optionsOf = c => c === 'mood' ? MOODS : c === 'prop' ? PROPS : Object.keys(TRAITS[c]);

// ── the text engine — MUST mirror build_pfp.band_text() byte for byte ────────
const adv = c => c === ' ' ? 12 : (ADV[c] || 22);
const widthOf = s => [...s].reduce((a,c)=>a+adv(c),0) - adv(s[s.length-1]) + 16;
function runOf(s, cx, y, sc) {{
  let x = 0; const uses = [], need = new Set();
  for (const c of s) {{
    if (c !== ' ') {{ need.add(c); uses.push(`<use href="#${{GID[c]||c}}" x="${{x}}"/>`); }}
    x += adv(c);
  }}
  const w = widthOf(s);
  return [`<g transform="translate(${{R(cx-w*sc/2)}} ${{R(y-28*sc)}}) scale(${{sc.toFixed(4)}})" `
    + `fill="none" stroke="${{CREAM}}" stroke-width="8" stroke-linecap="round" `
    + `stroke-linejoin="round">${{uses.join('')}}</g>`, need];
}}
function bandText(t) {{
  const sc1 = Math.min(3.4, 880 / widthOf(t));
  let lines = [t];
  if (sc1 < 2.0 && t.includes(' ')) {{
    let best = null, bw = null;
    for (let i = 0; i < t.length; i++) {{
      if (t[i] !== ' ') continue;
      const a = t.slice(0, i).replace(/ +$/,''), b = t.slice(i+1).replace(/^ +/,'');
      if (!a || !b) continue;
      const m = Math.max(widthOf(a), widthOf(b));
      if (bw === null || m < bw) {{ best = [a, b]; bw = m; }}
    }}
    if (best) lines = best;
  }}
  let sc, ys;
  if (lines.length === 1) {{ sc = sc1; ys = [976]; }}
  else {{ sc = Math.min(2.1, 880 / Math.max(...lines.map(widthOf))); ys = [944, 1010]; }}
  const runs = [], need = new Set();
  lines.forEach((l, i) => {{
    const [g, n] = runOf(l, 512, ys[i], sc);
    runs.push(g); n.forEach(c => need.add(c));
  }});
  const glyphs = [...need].sort().map(c=>`<path id="${{GID[c]||c}}" d="${{GLY[c]}}"/>`).join('');
  return [runs.join(''), glyphs];
}}

// ⚠️ MUST mirror build_pfp.build() exactly — this string is what goes on chain, and the
// python builder is the reference. Any divergence means the preview lies about the artifact.
function assembleFrom(st, text) {{
  const mouth = st.prop !== 'none' ? st.prop : st.mood;
  const t = (text || '').toUpperCase().trim();
  let glyphs = '', band = '';
  if (t) {{
    const [runs, g] = bandText(t);
    glyphs = g;
    band = `<rect x="0" y="884" width="1024" height="140" fill="${{DARK}}" opacity=".92"/>${{runs}}`;
  }}
  const S = 1.42;
  const inner = `<g ${{K}}><path d="M300 604q46-104 286-104t286 104v220H300z" fill="${{SHIRT}}"/></g>`
    + HEAD + TRAITS.mark[st.mark] + TRAITS.mouth[mouth]
    + TRAITS.eyes[st.eyes] + TRAITS.hat[st.hat] + TRAITS.neck[st.neck] + TRAITS.pet[st.pet];
  const face = `<g transform="translate(${{R(512-586*S)}} ${{R(456-325*S)}}) `
    + `scale(${{S}})">${{inner}}</g>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">`
    + `<defs>${{HEAD_DEFS}}${{glyphs}}</defs>${{TRAITS.bg[st.bg]}}${{face}}${{band}}</svg>`;
}}
const assemble = () => assembleFrom(pick, $('text').value);

// ── wizard scaffolding ───────────────────────────────────────────────────────
let CUR = 0;
$('prog').innerHTML = STEPS.map((s,i)=>`<button class="dot" data-step="${{i}}"></button>`).join('')
  + `<span class="stepno" id="stepno"></span>`;

$('panels').innerHTML = STEPS.map((s, i) => {{
  let body = '';
  if (s.cat) {{
    body = `<div class="cards">` + optionsOf(s.cat).map(v =>
      `<button class="chip" data-cat="${{s.cat}}" data-val="${{v}}">`
      + `<span class="th"></span><span class="lb">${{nice(v)}}</span></button>`).join('')
      + `</div>`;
  }} else if (s.id === 'text') {{
    body = `<div class="txt">
        <input id="text" maxlength="${{MAXT}}" placeholder="YOUR NAME · YOUR SAYING"
               autocomplete="off" spellcheck="false">
        <span id="count">0/${{MAXT}}</span></div>
      <p class="hint">Up to ${{MAXT}} characters — A&ndash;Z, 0&ndash;9, $ and spaces.
        A long line wraps onto two.</p>
      <div class="forever">Whatever you write is <b>permanent and public</b> — it rides inside
        the minting transaction, on chain forever, signed by your own wallet.</div>`;
  }} else {{
    body = `<div class="sum" id="sum"></div>
      <div class="meta"><span id="combo"></span><span></span></div>
      <div class="gate" id="gate"></div>
      <button id="mint">Connect wallet &amp; mint</button>
      <button id="reset">Start over</button>
      <div id="status"></div>
      <div class="forever" style="margin-top:12px">This is <b>piece 9 of oligarCH</b> — and
        it&rsquo;s yours to make. Hold <b>any one</b> of the eight and mint as many as you
        like, <b>forever</b>: no deadline, no supply cap, and the policy can never be changed
        or shut down. This page is open source — if it ever disappears, clone it and keep
        minting. The policy is the artifact, not the website.</div>
      <p class="meta" style="border:0"><code>policy ${{POLICY_EXPECT}}</code></p>`;
  }}
  return `<section class="panel" data-panel="${{i}}">
    <h2>${{s.title}}</h2><p class="sub">${{s.sub}}</p>${{body}}</section>`;
}}).join('');

function thumbs() {{
  const s = STEPS[CUR];
  if (!s.cat) return;
  document.querySelectorAll(`.panel[data-panel="${{CUR}}"] .chip`).forEach(ch => {{
    const st = Object.assign({{}}, pick);
    st[ch.dataset.cat] = ch.dataset.val;
    // no caption band on thumbnails — the card is selling the TRAIT, not the line
    ch.querySelector('.th').innerHTML = assembleFrom(st, '');
  }});
}}

let CURRENT = '';
function render() {{
  CURRENT = assemble();
  window.__svg = CURRENT;        // module scope is not global; tests read the EXACT string
                                 // rather than stage.innerHTML, which the DOM re-serialises
  $('stage').querySelectorAll('svg').forEach(e => e.remove());
  $('stage').insertAdjacentHTML('beforeend', CURRENT);
  const n = new TextEncoder().encode(CURRENT).length;
  $('size').textContent = n.toLocaleString() + ' B on chain';
  const c = $('count'); if (c) c.textContent = ($('text').value||'').length + '/' + MAXT;
  document.querySelectorAll('.chip').forEach(ch =>
    ch.classList.toggle('on', pick[ch.dataset.cat] === ch.dataset.val));
  const sum = $('sum');
  if (sum) {{
    const line = ($('text').value||'').toUpperCase().trim();
    sum.innerHTML = ORDER.map(k =>
      `<div class="row"><b>${{LABEL[k]}}</b><span>${{nice(catVal(k))}}</span></div>`).join('')
      + (line ? `<div class="row"><b>Line</b><span>${{line}}</span></div>` : '');
  }}
  thumbs();
}}

function show(i) {{
  CUR = Math.max(0, Math.min(STEPS.length - 1, i));
  document.querySelectorAll('.panel').forEach(p =>
    p.classList.toggle('on', +p.dataset.panel === CUR));
  document.querySelectorAll('.dot').forEach((d, j) => {{
    d.classList.toggle('cur', j === CUR); d.classList.toggle('done', j < CUR);
  }});
  $('stepno').textContent = (CUR + 1) + ' / ' + STEPS.length;
  $('back').disabled = CUR === 0;
  $('next').style.display = CUR === STEPS.length - 1 ? 'none' : '';
  $('next').textContent = CUR === STEPS.length - 2 ? 'Review →' : 'Next →';
  $('back').style.flex = CUR === STEPS.length - 1 ? '1' : '';
  window.scrollTo({{top: 0, behavior: 'smooth'}});
  render();
}}
window.__goto = show;

document.querySelectorAll('.dot').forEach(d => d.onclick = () => show(+d.dataset.step));
$('back').onclick = () => show(CUR - 1);
$('next').onclick = () => show(CUR + 1);
document.querySelectorAll('.chip').forEach(ch => ch.onclick = () => {{
  pick[ch.dataset.cat] = ch.dataset.val; render(); }});
$('text').oninput = e => {{
  const el = e.target, v = el.value.toUpperCase().replace(/[^A-Z0-9$ ]/g, '');
  if (v !== el.value) el.value = v;
  render();
}};
$('text').onkeydown = e => {{ if (e.key === 'Enter') {{ e.target.blur(); show(CUR + 1); }} }};
$('rand').onclick = () => {{
  pick.mood = MOODS[Math.floor(Math.random()*MOODS.length)];
  pick.prop = PROPS[Math.floor(Math.random()*PROPS.length)];
  ORDER.filter(k=>k!=='mouth').forEach(k => {{ const o = Object.keys(TRAITS[k]);
    pick[k] = o[Math.floor(Math.random()*o.length)]; }});
  render();
}};

// swipe between steps — the phone gesture; ignore swipes that start on the input
let tx0 = null, ty0 = null;
document.addEventListener('touchstart', e => {{
  if (e.target.closest('input')) {{ tx0 = null; return; }}
  tx0 = e.touches[0].clientX; ty0 = e.touches[0].clientY;
}}, {{passive: true}});
document.addEventListener('touchend', e => {{
  if (tx0 === null) return;
  const dx = e.changedTouches[0].clientX - tx0, dy = e.changedTouches[0].clientY - ty0;
  tx0 = null;
  if (Math.abs(dx) > 64 && Math.abs(dy) < 46) show(CUR + (dx < 0 ? 1 : -1));
}}, {{passive: true}});

// ── the gate + mint ──────────────────────────────────────────────────────────
function drawGate(held) {{
  const n = held ? held.filter(Boolean).length : 0;
  $('gate').innerHTML =
    `<div class="row2" style="background:#1c1712;color:#d8c9a4">`
    + `<span class="mark">&#9733;</span><b>Hold at least ONE of the eight</b>`
    + `<span class="p" style="text-align:right">${{held ? n + ' / 8 held' : 'any will do'}}</span></div>`
    + GATE.map((p,i) => {{
      const ok = held && held[i];
      return `<div class="row2"><span class="mark ${{ok?'yes':'no'}}">${{ok?'&#10003;':'&#9679;'}}</span>`
        + `<span class="t">${{p.t}}</span><span class="p">${{p.ph}}</span></div>`;
    }}).join('');
}}
drawGate(null);

$('reset').onclick = () => {{
  pick.mood = MOODS[0]; pick.prop = 'none';
  ORDER.filter(k=>k!=='mouth').forEach(k => pick[k] = Object.keys(TRAITS[k])[0]);
  $('text').value = ''; show(0);
}};
$('combo').textContent = ORDER.reduce((a,k)=>a*Object.keys(TRAITS[k]).length,1)
  .toLocaleString() + ' possible oligarCHs';

let CSL;
async function loadCSL() {{
  const bg = await import(CDN + 'cardano_serialization_lib_bg.js');
  const {{ instance }} = await WebAssembly.instantiateStreaming(
    fetch(CDN + 'cardano_serialization_lib_bg.wasm'),
    {{ './cardano_serialization_lib_bg.js': bg }});
  bg.__wbg_set_wasm(instance.exports);
  if (instance.exports.__wbindgen_start) instance.exports.__wbindgen_start();
  CSL = bg;
  const got = hex(CSL.PlutusScript.new_v3(unhex(SCRIPT_HEX)).hash().to_bytes());
  if (got !== POLICY_EXPECT) throw new Error('policy id mismatch: ' + got);
}}
function costmdls() {{
  const cm = CSL.CostModel.new();
  COSTS.forEach((v,i) => cm.set(i, v < 0
    ? CSL.Int.new_negative(CSL.BigNum.from_str(String(-v)))
    : CSL.Int.new(CSL.BigNum.from_str(String(v)))));
  const c = CSL.Costmdls.new(); c.insert(CSL.Language.new_plutus_v3(), cm); return c;
}}
function wallets() {{
  const c = window.cardano || {{}};
  return Object.keys(c).filter(k => c[k] && typeof c[k].enable === 'function' && c[k].apiVersion);
}}

$('mint').onclick = async () => {{
  $('mint').disabled = true;
  try {{
    const ws = wallets();
    if (!ws.length) throw new Error('No wallet found — open this in Vespr or Eternl.');
    say('Loading…'); if (!CSL) await loadCSL();
    const api = await window.cardano[ws[0]].enable();
    if (await api.getNetworkId() !== 1) throw new Error('Switch the wallet to mainnet.');
    const addr = CSL.Address.from_bytes(unhex(await api.getChangeAddress()));
    const utxos = (await api.getUtxos()).map(h => CSL.TransactionUnspentOutput.from_hex(h));

    const carriers = [];
    const held = GATE.map(p => {{
      const hit = utxos.find(u => {{ const ma = u.output().amount().multiasset();
        if (!ma) return false; const a = ma.get(CSL.ScriptHash.from_hex(p.p));
        return a && a.len() > 0; }});
      if (hit && !carriers.some(c => c.to_hex() === hit.to_hex())) carriers.push(hit);
      return !!hit;
    }});
    drawGate(held);
    if (!held.some(h => h)) throw new Error('You need <b>at least one</b> of the eight '
      + 'oligarCH pieces — any of them — to mint your own.');

    say('Building — your picture goes inside the transaction…');
    const cfg = CSL.TransactionBuilderConfigBuilder.new()
      .fee_algo(CSL.LinearFee.new(CSL.BigNum.from_str(PP.feeA),CSL.BigNum.from_str(PP.feeB)))
      .pool_deposit(CSL.BigNum.from_str(PP.poolDep)).key_deposit(CSL.BigNum.from_str(PP.keyDep))
      .max_value_size(PP.maxVal).max_tx_size(PP.maxTx)
      .coins_per_utxo_byte(CSL.BigNum.from_str(PP.utxoByte))
      .ex_unit_prices(CSL.ExUnitPrices.new(
        CSL.UnitInterval.new(CSL.BigNum.from_str(PP.pmN),CSL.BigNum.from_str(PP.pmD)),
        CSL.UnitInterval.new(CSL.BigNum.from_str(PP.psN),CSL.BigNum.from_str(PP.psD)))).build();
    const tb = CSL.TransactionBuilder.new(cfg);

    // ⚠️ REGRESSION FIXED 2026-07-30 (David's footage): this used to REQUIRE a pure-ada UTxO
    // and threw "Need one plain-ada UTxO to seed the name" on a wallet whose every UTxO
    // carries tokens — which is most collectors' wallets. The seed only has to be a UTxO this
    // transaction SPENDS, so the derived asset name can never repeat; it does NOT have to be
    // pure ada. Prefer pure (a tidier tx), fall back to any. The proven series page always
    // did this and the fallback was lost in the rewrite.
    const byCoin = (a,b) => Number(b.output().amount().coin().to_str())
                          - Number(a.output().amount().coin().to_str());
    const pure = utxos.filter(u => {{ const m=u.output().amount().multiasset();
      return !m || m.len()===0; }});
    const pool = (pure.length ? pure : utxos).slice().sort(byCoin);
    if (!pool.length) throw new Error('That wallet has no UTxOs — it needs a little ada.');
    const seed = pool[0];
    const nameStr = TICKER + hex(seed.input().transaction_id().to_bytes()).slice(0,8);
    const assetName = CSL.AssetName.new(new TextEncoder().encode(nameStr));
    const script = CSL.PlutusScript.new_v3(unhex(SCRIPT_HEX));
    const redeemer = CSL.Redeemer.new(CSL.RedeemerTag.new_mint(), CSL.BigNum.from_str('0'),
      CSL.PlutusData.new_empty_constr_plutus_data(CSL.BigNum.from_str('0')),
      CSL.ExUnits.new(CSL.BigNum.from_str(EX_MEM), CSL.BigNum.from_str(EX_STEPS)));
    const mb = CSL.MintBuilder.new();
    mb.add_asset(CSL.MintWitness.new_plutus_script(CSL.PlutusScriptSource.new(script), redeemer),
      assetName, CSL.Int.new_i32(1));
    tb.set_mint_builder(mb);

    // the artwork exactly as previewed, plus the traits as CIP-25 attributes so marketplaces
    // show them as real traits
    const b64 = btoa(String.fromCharCode(...new TextEncoder().encode(CURRENT)));
    const cut = s => s.match(/.{{1,64}}/g);
    const pid = hex(script.hash().to_bytes());
    const meta = {{}}; meta[pid] = {{}};
    const entry = {{ name: 'oligarCH PFP', mediaType: 'image/svg+xml',
      image: cut('data:image/svg+xml;base64,' + b64),
      description: cut('Your own oligarCH. Fully on-chain, holders only.') }};
    ORDER.forEach(k => entry[LABEL[k]] = nice(catVal(k)));
    const line = ($('text').value||'').toUpperCase().trim();
    if (line) entry['Line'] = line;
    meta[pid][nameStr] = entry;
    const aux = CSL.AuxiliaryData.new();
    const gtm = CSL.GeneralTransactionMetadata.new();
    gtm.insert(CSL.BigNum.from_str('721'), CSL.encode_json_str_to_metadatum(
      JSON.stringify(meta), CSL.MetadataJsonSchema.NoConversions));
    aux.set_metadata(gtm); tb.set_auxiliary_data(aux);

    const ma = CSL.MultiAsset.new(), as = CSL.Assets.new();
    as.insert(assetName, CSL.BigNum.from_str('1'));
    ma.insert(CSL.ScriptHash.from_bytes(script.hash().to_bytes()), as);
    const probe = CSL.Value.new(CSL.BigNum.from_str('3000000')); probe.set_multiasset(ma);
    const minAda = CSL.min_ada_for_output(CSL.TransactionOutput.new(addr, probe),
      CSL.DataCost.new_coins_per_byte(CSL.BigNum.from_str(PP.utxoByte)));
    const outV = CSL.Value.new(minAda); outV.set_multiasset(ma);
    tb.add_output(CSL.TransactionOutput.new(addr, outV));

    // ONE carrier is all the validator wants — extra pieces would only fatten the tx
    const seen = new Set();
    for (const u of [seed, ...carriers.slice(0,1), ...pool.slice(1,5)]) {{
      const k = u.to_hex(); if (seen.has(k)) continue; seen.add(k);
      tb.add_regular_input(u.output().address(), u.input(), u.output().amount());
    }}
    let col = await api.getCollateral();
    if (!col || !col.length) col = (await api.experimental?.getCollateral?.()) || [];
    if (!col.length) throw new Error('No collateral set — add some in your wallet settings.');
    const cib = CSL.TxInputsBuilder.new();
    for (const h of col) {{ const u = CSL.TransactionUnspentOutput.from_hex(h);
      cib.add_regular_input(u.output().address(), u.input(), u.output().amount()); }}
    tb.set_collateral(cib);
    tb.calc_script_data_hash(costmdls());
    tb.add_change_if_needed(addr);

    const tx = tb.build_tx();
    const unsignedHex = hex(tx.to_bytes());
    window.__unsigned = unsignedHex;
    const size = tx.to_bytes().length;
    if (size > PP.maxTx) throw new Error('Too large (' + size + ' B). Simplify a trait.');
    say('Sign to mint — tx ' + size.toLocaleString() + ' bytes.');
    const wsHex = await api.signTx(unsignedHex, true);
    // MERGE, never replace: the wallet returns only its vkeys, and assigning that whole
    // witness set over ours would wipe the plutus script and the redeemer.
    const ftx = CSL.FixedTransaction.from_hex(unsignedHex);
    const vk = CSL.TransactionWitnessSet.from_hex(wsHex).vkeys();
    if (!vk || !vk.len()) throw new Error('The wallet returned no signature.');
    for (let i=0;i<vk.len();i++) ftx.add_vkey_witness(vk.get(i));
    say('Submitting…');
    const txHash = await api.submitTx(hex(ftx.to_bytes()));
    say('<b>Minted.</b> ' + nameStr + ' is yours, picture and all, on chain forever.<br>'
      + '<a href="https://cexplorer.io/tx/' + txHash + '" target="_blank" rel="noopener">'
      + txHash + '</a><br><a href="wall/">&rarr; See yourself on THE WALL</a>', 'ok');
  }} catch (e) {{
    // CIP-30 throws {{code, info}} with no .message — never let this become "[object Object]"
    let m = '';
    if (e && typeof e === 'object') {{
      m = [e.info, e.message, e.code!==undefined?('code '+e.code):''].filter(Boolean).join(' · ');
      if (!m) {{ try {{ m = JSON.stringify(e); }} catch(_) {{ m = String(e); }} }}
    }} else m = String(e);
    say('<b>Not minted.</b> ' + m, 'err');
  }}
  $('mint').disabled = false;
}};

show(0);
</script></body></html>
"""

OUT = pathlib.Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_text(HTML)
print(f'  gate     any ONE of the eight pieces')
print(f'  policy   {POLICY}  (piece 9 — the any-of validator)')
print(f'  steps    {len(STEPS)}  ·  text cap {B.MAX_TEXT}')
print(f'  out      {OUT / "index.html"}  ({len((OUT / "index.html").read_bytes()):,} B)')
