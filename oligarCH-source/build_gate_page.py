#!/usr/bin/env python3
"""Build the piece-9 gated mint page.

  python3 build_gate_page.py            -> TEST build   (policy 7d6702e0…, prefix T9)
  python3 build_gate_page.py --prod     -> PROD build   (policy 2ff84522…, prefix ICY)

⚠️ DEFAULTS TO THE TEST BUILD ON PURPOSE. The two scripts are byte-for-byte the same logic;
only the applied `prefix` parameter differs, which changes the policy id. So a full end-to-end
mint can be done on mainnet with a real wallet and real ada, and it CANNOT land under the real
piece-9 policy. Nothing about the gate is stubbed — the test proves the production path.

⚠️ This page does NOT belong on the public site. It has no link from anywhere, and the series
build (`build_page.py` in the byttg-mint tree) knows nothing about it.
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).parent
ART = pathlib.Path.home() / 'Desktop/2026-07-28_byttg-mint/icy.svg'

ap = argparse.ArgumentParser()
ap.add_argument('--prod', action='store_true', help='build against the real piece-9 policy')
ap.add_argument('--out', default=str(HERE / 'out'))
args = ap.parse_args()

BP = json.load(open(HERE / ('applied-prod.json' if args.prod else 'applied-test.json')))
V = BP['validators'][0]
SCRIPT_HEX, POLICY = V['compiledCode'], V['hash']
TICKER = 'ICY' if args.prod else 'T9'

# The eight, in release order. Names are illustrative only — the gate matches on POLICY,
# because every minter's copy carries a different seed-derived asset name.
PIECES = [
    ('BYTTG', 'BURN YOU TO THE GROUND', '2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d'),
    ('TGM',   'THE GREAT MIGRATION',    '7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5'),
    ('IVYOM', 'I VOTE YES ON ME',       '5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e'),
    ('ORG',   'ORGANIC DISTRIBUTION',   '80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b'),
    ('HOTEL', 'YOU CAN NEVER LEAVE',    'd91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89'),
    ('NDL',   'NO DOORS LEFT',          '64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361'),
    ('DNPG',  'DO NOT PASS GO',         '3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00'),
    ('SMOKE', 'DECENTRALIZED',          '9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc'),
]

# mainnet PlutusV3 cost model, epoch 646. The script data hash is computed over this, and a
# wrong model produces a hash the node rejects — it is not optional and it is not guessable.
COSTS = json.load(open(HERE / 'costmodel-v3.json'))
assert len(COSTS) == 350, len(COSTS)

SVG = ART.read_text().strip()
assert '</script' not in SVG.lower()

HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>oligarCH — the ninth{'' if args.prod else ' (TEST)'}</title>
<style>
 :root{{--bg:#101012;--panel:#18181c;--line:#2a2a31;--ink:#eceaea;--dim:#9a9aa4;
       --red:#ed1c24;--gold:#c9a227;--ok:#4ade80}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--bg);color:var(--ink);
      font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
 .wrap{{max-width:560px;margin:0 auto;padding:26px 18px 64px}}
 h1{{font:900 clamp(30px,8vw,46px)/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:-.03em;margin:0}}
 .kicker{{font:700 12px/1 sans-serif;letter-spacing:.18em;color:var(--gold);margin-bottom:9px}}
 .sub{{color:var(--dim);margin:8px 0 18px;font-size:15px}}
 .banner{{background:#3a1d1d;border:1px solid #7a2b2b;color:#ffb4b4;border-radius:10px;
         padding:10px 12px;font-size:13px;margin-bottom:16px}}
 .veil{{position:relative;border:1.5px solid #8a6a25;border-radius:14px;overflow:hidden;
       background:#141416;aspect-ratio:1;display:grid;place-items:center}}
 .veil img{{width:100%;display:block}}
 .q{{font:900 clamp(52px,18vw,120px)/1 sans-serif;color:#f4f4f4;text-shadow:0 2px 14px #000}}
 .gate{{margin:18px 0 8px;border:1px solid var(--line);border-radius:12px;background:var(--panel)}}
 .row{{display:flex;align-items:center;gap:10px;padding:9px 13px;border-bottom:1px solid var(--line);
      font-size:14px}}
 .row:last-child{{border-bottom:0}}
 .row .t{{font-weight:800;min-width:62px}}
 .row .p{{color:var(--dim);flex:1;font-size:12.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
 .mark{{width:22px;text-align:center;font-weight:900}}
 .yes{{color:var(--ok)}} .no{{color:#6b6b74}}
 .tally{{text-align:center;color:var(--dim);font-size:13px;margin:10px 0 16px}}
 button{{width:100%;padding:14px;border-radius:11px;border:1px solid #8a6a25;background:var(--gold);
        color:#141414;font:800 16px sans-serif;cursor:pointer}}
 button.ghost{{background:transparent;color:var(--ink);border-color:var(--line)}}
 button[disabled]{{opacity:.4;cursor:not-allowed}}
 .stack{{display:grid;gap:9px}}
 #status{{display:none;margin-top:14px;padding:11px 13px;border-radius:10px;background:var(--panel);
         border:1px solid var(--line);font-size:14px;word-break:break-word}}
 #status.on{{display:block}} #status.err{{border-color:#7a2b2b;color:#ffb4b4}}
 #status.ok{{border-color:#2b7a3f;color:#b4ffc8}}
 code{{font:12px ui-monospace,monospace;color:var(--dim);word-break:break-all}}
 footer{{margin-top:26px;color:var(--dim);font-size:12px;text-align:center}}
</style></head><body><div class="wrap">
 <div class="kicker">OLIGARCH &middot; NINE OF NINE</div>
 <h1>The ninth</h1>
 <p class="sub">Not an open mint. The policy will only mint for a transaction that spends all
    eight earlier pieces — proof, on chain, that they are yours.</p>
 {'' if args.prod else '<div class="banner"><b>TEST BUILD.</b> Policy <code>' + POLICY + '</code> — a throwaway with identical logic. Nothing minted here can ever be the real piece nine.</div>'}

 <div class="veil" id="veil"><div class="q">?</div></div>

 <div class="gate" id="gate"></div>
 <p class="tally" id="tally">Connect a wallet to check the set.</p>

 <div class="stack" id="pick"></div>
 <div id="status"></div>
 <footer>The picture lives entirely inside the minting transaction.<br>
   policy <code>{POLICY}</code></footer>
</div>

<script id="art" type="image/svg+xml">{SVG}</script>
<script type="module">
const SCRIPT_HEX = {json.dumps(SCRIPT_HEX)};
const POLICY_EXPECT = {json.dumps(POLICY)};
const TICKER = {json.dumps(TICKER)};
const PIECES = {json.dumps([{'t': t, 'ph': ph, 'p': p} for t, ph, p in PIECES])};
const COSTS = {json.dumps(COSTS)};
const PP = {{feeA:'44', feeB:'155381', utxoByte:'4310', maxTx:16384, maxVal:5000,
            poolDep:'500000000', keyDep:'2000000', priceMemN:'577', priceMemD:'10000',
            priceStepN:'721', priceStepD:'10000000'}};
// MEASURED on mainnet via ogmios EvaluateTx against a real 8-piece wallet (34 UTxOs):
// memory 548,351 / steps 163,345,402. Budgeted ~3.6x/4.3x above that on purpose — the script
// folds over the transaction's inputs, so a wallet with many more UTxOs does more work, and an
// UNDER-budget redeemer is a hard validation failure while the overage costs ~0.02 ADA.
const EX_MEM = '2000000', EX_STEPS = '700000000';
const CDN = 'https://cdn.jsdelivr.net/npm/@emurgo/cardano-serialization-lib-browser@15.0.3/';

const $ = id => document.getElementById(id);
const hex = b => [...b].map(x => x.toString(16).padStart(2,'0')).join('');
const unhex = s => new Uint8Array(s.match(/../g).map(x => parseInt(x,16)));
const B64 = btoa(String.fromCharCode(...new TextEncoder().encode($('art').textContent.trim())));
const say = (m,k) => {{ const e=$('status'); e.className='on '+(k||''); e.innerHTML=m; }};

// the checklist renders before any wallet is connected, so the ask is legible up front
function drawGate(held) {{
  $('gate').innerHTML = PIECES.map((p,i) => {{
    const ok = held && held[i];
    return `<div class="row"><span class="mark ${{ok?'yes':'no'}}">${{ok?'&#10003;':'&#9679;'}}</span>`
         + `<span class="t">${{p.t}}</span><span class="p">${{p.ph}}</span></div>`;
  }}).join('');
}}
drawGate(null);

let CSL;
async function loadCSL() {{
  const bg = await import(CDN + 'cardano_serialization_lib_bg.js');
  const {{ instance }} = await WebAssembly.instantiateStreaming(
    fetch(CDN + 'cardano_serialization_lib_bg.wasm'),
    {{ './cardano_serialization_lib_bg.js': bg }});
  bg.__wbg_set_wasm(instance.exports);
  if (instance.exports.__wbindgen_start) instance.exports.__wbindgen_start();
  CSL = bg;
  // ⚠️ new_v3 takes the ALREADY cbor-wrapped compiledCode. from_hex_with_version strips a
  // layer first and yields a different, wrong policy id.
  const s = CSL.PlutusScript.new_v3(unhex(SCRIPT_HEX));
  const got = hex(s.hash().to_bytes());
  if (got !== POLICY_EXPECT) throw new Error('policy id mismatch: ' + got);
}}

function listWallets() {{
  const c = window.cardano || {{}};
  const keys = Object.keys(c).filter(k => c[k] && typeof c[k].enable === 'function' && c[k].apiVersion);
  $('pick').innerHTML = keys.length
    ? keys.map(k => `<button data-w="${{k}}">Connect ${{c[k].name || k}}</button>`).join('')
    : '<button class="ghost" disabled>No wallet detected — open this in Vespr or Eternl</button>';
  keys.forEach(k => $('pick').querySelector(`[data-w="${{k}}"]`).onclick = () => run(k));
}}
setTimeout(listWallets, 400); setTimeout(listWallets, 1400);

// ⚠️ FOUR of the 350 PlutusV3 costs are NEGATIVE. CostModel.set takes a CSL.Int, and Int.new
// only accepts a magnitude — a negative must go through Int.new_negative or it silently flips
// sign, giving a cost model that hashes to a script data hash the node rejects. That failure
// arrives as an opaque submit error, so it has to be right here.
function costmdls() {{
  const cm = CSL.CostModel.new();
  COSTS.forEach((v,i) => cm.set(i, v < 0
    ? CSL.Int.new_negative(CSL.BigNum.from_str(String(-v)))
    : CSL.Int.new(CSL.BigNum.from_str(String(v)))));
  const c = CSL.Costmdls.new();
  c.insert(CSL.Language.new_plutus_v3(), cm);
  return c;
}}

async function run(key) {{
  $('pick').querySelectorAll('button').forEach(b => b.disabled = true);
  try {{
    say('Loading the serialization library…');
    if (!CSL) await loadCSL();
    say('Connecting to your wallet…');
    const api = await window.cardano[key].enable();
    if (await api.getNetworkId() !== 1) throw new Error('Switch the wallet to mainnet.');

    const addr = CSL.Address.from_bytes(unhex(await api.getChangeAddress()));
    const raw = await api.getUtxos();
    if (!raw || !raw.length) throw new Error('That wallet has no UTxOs.');
    const utxos = raw.map(h => CSL.TransactionUnspentOutput.from_hex(h));

    // ---- the gate check, client side. The chain enforces it again at submit. ----
    const carriers = [];            // one UTxO per required policy
    const held = PIECES.map(p => {{
      const hit = utxos.find(u => {{
        const ma = u.output().amount().multiasset();
        if (!ma) return false;
        const a = ma.get(CSL.ScriptHash.from_hex(p.p));
        return a && a.len() > 0;
      }});
      if (hit && !carriers.some(c => c.to_hex() === hit.to_hex())) carriers.push(hit);
      return !!hit;
    }});
    drawGate(held);
    const have = held.filter(Boolean).length;
    $('tally').textContent = have + ' of 8 held';
    if (have < 8) {{
      const missing = PIECES.filter((_,i) => !held[i]).map(p => p.t).join(', ');
      throw new Error('The set is incomplete — missing <b>' + missing + '</b>. '
                    + 'The policy will refuse this transaction.');
    }}

    say('Building the transaction — the whole picture goes inside it…');
    const cfg = CSL.TransactionBuilderConfigBuilder.new()
      .fee_algo(CSL.LinearFee.new(CSL.BigNum.from_str(PP.feeA), CSL.BigNum.from_str(PP.feeB)))
      .pool_deposit(CSL.BigNum.from_str(PP.poolDep)).key_deposit(CSL.BigNum.from_str(PP.keyDep))
      .max_value_size(PP.maxVal).max_tx_size(PP.maxTx)
      .coins_per_utxo_byte(CSL.BigNum.from_str(PP.utxoByte))
      .ex_unit_prices(CSL.ExUnitPrices.new(
        CSL.UnitInterval.new(CSL.BigNum.from_str(PP.priceMemN), CSL.BigNum.from_str(PP.priceMemD)),
        CSL.UnitInterval.new(CSL.BigNum.from_str(PP.priceStepN), CSL.BigNum.from_str(PP.priceStepD))))
      .build();
    const tb = CSL.TransactionBuilder.new(cfg);

    // seed: a pure-ada UTxO, consumed by this tx, so the derived name can never repeat
    // ⚠️ REGRESSION FIXED 2026-07-30 (David's footage): this used to REQUIRE a pure-ada UTxO
    // and threw "Need one plain-ada UTxO to seed the name" on a wallet whose every UTxO
    // carries tokens — which is most collectors' wallets. The seed only has to be a UTxO this
    // transaction SPENDS, so the derived asset name can never repeat; it does NOT have to be
    // pure ada. Prefer pure (a tidier tx), fall back to any. The proven series page always
    // did this and the fallback was lost in the rewrite.
    const pure = utxos.filter(u => {{ const m = u.output().amount().multiasset();
                                     return !m || m.len() === 0; }});
    const pool = (pure.length ? pure : utxos).slice().sort((a,b) =>
      Number(b.output().amount().coin().to_str()) - Number(a.output().amount().coin().to_str()));
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

    const cut = s => s.match(/.{{1,64}}/g);
    const uri = 'data:image/svg+xml;base64,' + B64;
    const policyHex = hex(script.hash().to_bytes());
    const meta = {{}}; meta[policyHex] = {{}};
    meta[policyHex][nameStr] = {{ name: TICKER, mediaType: 'image/svg+xml', image: cut(uri),
      description: cut('The ninth. Gated by the other eight. Fully on-chain.') }};
    const aux = CSL.AuxiliaryData.new();
    const gtm = CSL.GeneralTransactionMetadata.new();
    gtm.insert(CSL.BigNum.from_str('721'), CSL.encode_json_str_to_metadatum(
      JSON.stringify(meta), CSL.MetadataJsonSchema.NoConversions));
    aux.set_metadata(gtm);
    tb.set_auxiliary_data(aux);

    // the NFT output
    const ma = CSL.MultiAsset.new(); const as = CSL.Assets.new();
    as.insert(assetName, CSL.BigNum.from_str('1'));
    ma.insert(CSL.ScriptHash.from_bytes(script.hash().to_bytes()), as);
    const probe = CSL.Value.new(CSL.BigNum.from_str('3000000')); probe.set_multiasset(ma);
    const minAda = CSL.min_ada_for_output(CSL.TransactionOutput.new(addr, probe),
      CSL.DataCost.new_coins_per_byte(CSL.BigNum.from_str(PP.utxoByte)));
    const outV = CSL.Value.new(minAda); outV.set_multiasset(ma);
    tb.add_output(CSL.TransactionOutput.new(addr, outV));

    // inputs: the seed, plus the eight carriers. THE EIGHT ARE THE PROOF — spending them is
    // what requires the owner's signature. They return automatically in the change output.
    const added = new Set();
    for (const u of [seed, ...carriers]) {{
      const k = u.to_hex(); if (added.has(k)) continue; added.add(k);
      tb.add_regular_input(u.output().address(), u.input(), u.output().amount());
    }}
    // a little more ada if the fee needs it
    for (const u of pool.slice(1, 6)) {{
      const k = u.to_hex(); if (added.has(k)) continue; added.add(k);
      tb.add_regular_input(u.output().address(), u.input(), u.output().amount());
    }}

    // collateral — required for any Plutus script
    let col = await api.getCollateral();
    if (!col || !col.length) col = (await api.experimental?.getCollateral?.()) || [];
    if (!col.length) throw new Error('The wallet returned no collateral. Set some in the '
      + 'wallet settings (5 ADA is plenty) and try again.');
    const cib = CSL.TxInputsBuilder.new();
    for (const h of col) {{
      const u = CSL.TransactionUnspentOutput.from_hex(h);
      cib.add_regular_input(u.output().address(), u.input(), u.output().amount());
    }}
    tb.set_collateral(cib);

    tb.calc_script_data_hash(costmdls());
    tb.add_change_if_needed(addr);

    // build_tx() assembles the witness set too — the inline plutus script and the mint
    // redeemer live there. build() alone returns only a body, and signing a bodyless-witness
    // transaction means the wallet never sees the script it is authorising.
    const tx = tb.build_tx();
    const unsignedHex = hex(tx.to_bytes());
    window.__unsigned = unsignedHex;
    const size = tx.to_bytes().length;
    if (size > PP.maxTx) throw new Error('Transaction too large (' + size + ' B).');

    say('Sign to mint <b>' + nameStr + '</b>.<br>tx ' + size.toLocaleString()
      + ' / ' + PP.maxTx.toLocaleString() + ' bytes.');
    const wsHex = await api.signTx(unsignedHex, true);

    // ⚠️ MERGE, NEVER REPLACE. A CIP-30 wallet returns only the witnesses it added — its
    // vkeys. Assigning that whole witness set over ours wipes the plutus script and the
    // redeemer, and the node then rejects the transaction as missing its script. Take the
    // vkeys out and add them to a FixedTransaction, which also preserves the ORIGINAL body
    // bytes so the signature stays valid.
    const ftx = CSL.FixedTransaction.from_hex(unsignedHex);
    const vk = CSL.TransactionWitnessSet.from_hex(wsHex).vkeys();
    if (!vk || !vk.len()) throw new Error('The wallet returned no signature.');
    for (let i = 0; i < vk.len(); i++) ftx.add_vkey_witness(vk.get(i));

    say('Submitting…');
    const txHash = await api.submitTx(hex(ftx.to_bytes()));

    $('veil').innerHTML = '<img src="' + uri + '" alt="the ninth">';
    say('<b>Minted.</b> ' + nameStr + ' is yours, picture and all, on chain forever.<br>'
      + '<code>' + txHash + '</code>', 'ok');
  }} catch (e) {{
    // ⚠️ CIP-30 throws PLAIN OBJECTS: {{code, info}}. They have no .message, so the obvious
    // `e.message || String(e)` renders "[object Object]" and the real reason is lost — which
    // is exactly what happened on the first live attempt. Dig out every shape.
    let m = '';
    if (e && typeof e === 'object') {{
      m = [e.info, e.message, (e.code !== undefined ? 'code ' + e.code : '')]
            .filter(Boolean).join(' &middot; ');
      if (!m) {{ try {{ m = JSON.stringify(e); }} catch (_) {{ m = String(e); }} }}
    }} else m = String(e);
    // and hand over the exact bytes, so a failure can be evaluated off-page instead of guessed
    const diag = window.__unsigned
      ? '<details style="margin-top:9px"><summary>diagnostic — send this to Clawd</summary>'
        + '<code style="display:block;margin-top:6px;max-height:150px;overflow:auto">'
        + window.__unsigned + '</code></details>'
      : '';
    say('<b>Not minted.</b> ' + m + diag, 'err');
    $('pick').querySelectorAll('button').forEach(b => b.disabled = false);
  }}
}}
</script></body></html>
"""

OUT = pathlib.Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'index.html').write_text(HTML)
print(f'  {"PROD" if args.prod else "TEST"} build')
print(f'  policy   {POLICY}')
print(f'  ticker   {TICKER}')
print(f'  script   {len(SCRIPT_HEX)//2} B   artwork {len(SVG.encode()):,} B')
print(f'  out      {OUT / "index.html"}  ({len((OUT / "index.html").read_bytes()):,} B)')
