// Build the REAL gated transaction from a REAL on-chain wallet and have a node evaluate the
// Plutus script — without signing and without submitting. This is the only test that proves
// the validator actually runs on mainnet: aiken proves the logic, the stub harness proves the
// transaction assembles, and this proves the ledger accepts and executes it.
//
//   node evaluate.mjs [--seven]
//
// --seven drops one piece from the inputs. It MUST come back as a script failure; if it
// evaluates fine, the gate is not gating anything.
import fs from 'fs';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const CSL = require('@emurgo/cardano-serialization-lib-nodejs');

const SEVEN = process.argv.includes('--seven');
const PROJ = fs.readFileSync(process.env.BLOCKFROST_PROJECT_ID_FILE || (process.env.HOME + '/.blockfrost_project_id'), 'utf8').trim();
const BF = 'https://cardano-mainnet.blockfrost.io/api/v0';
const bp = JSON.parse(fs.readFileSync('applied-test.json', 'utf8')).validators[0];
const SCRIPT_HEX = bp.compiledCode, POLICY = bp.hash;
const COSTS = JSON.parse(fs.readFileSync('costmodel-v3.json', 'utf8'));
const SVG = fs.readFileSync(process.env.HOME + '/Desktop/2026-07-28_byttg-mint/icy.svg');
const HOLDER = JSON.parse(fs.readFileSync('holder.json', 'utf8'));
const TICKER = 'T9';
const REQUIRED = ['2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d',
  '7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5',
  '5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e',
  '80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b',
  'd91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89',
  '64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361',
  '3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00',
  '9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc'];

const hex = b => Buffer.from(b).toString('hex');
const bf = async (p, opts) => {
  const r = await fetch(BF + p, { ...opts, headers: { project_id: PROJ, ...(opts?.headers || {}) } });
  const t = await r.text();
  return { status: r.status, body: (() => { try { return JSON.parse(t); } catch { return t; } })() };
};

const addrB = HOLDER.addr;
const addr = CSL.Address.from_bech32(addrB);
const { body: utxos } = await bf(`/addresses/${addrB}/utxos?count=100`);
if (!Array.isArray(utxos)) { console.error('utxo fetch failed:', utxos); process.exit(1); }
console.log(`\n  wallet   ${addrB.slice(0, 24)}…   ${utxos.length} UTxOs`);

// turn a Blockfrost utxo into a CSL TransactionUnspentOutput
function toCsl(u) {
  const ma = CSL.MultiAsset.new();
  let lovelace = '0';
  for (const a of u.amount) {
    if (a.unit === 'lovelace') { lovelace = a.quantity; continue; }
    const pol = a.unit.slice(0, 56), nameHex = a.unit.slice(56);
    const as = CSL.Assets.new();
    as.insert(CSL.AssetName.new(Buffer.from(nameHex, 'hex')), CSL.BigNum.from_str(a.quantity));
    ma.insert(CSL.ScriptHash.from_hex(pol), as);
  }
  const v = CSL.Value.new(CSL.BigNum.from_str(lovelace));
  if (ma.len()) v.set_multiasset(ma);
  return CSL.TransactionUnspentOutput.new(
    CSL.TransactionInput.new(CSL.TransactionHash.from_hex(u.tx_hash), u.output_index),
    CSL.TransactionOutput.new(addr, v));
}
const all = utxos.map(toCsl);
const policiesOf = u => {
  const m = u.output().amount().multiasset(); const out = [];
  if (!m) return out;
  for (let i = 0; i < m.keys().len(); i++) out.push(hex(m.keys().get(i).to_bytes()));
  return out;
};

const need = SEVEN ? REQUIRED.slice(0, 7) : REQUIRED;
const carriers = [];
for (const p of need) {
  const hit = all.find(u => policiesOf(u).includes(p));
  if (!hit) { console.error('  wallet is missing policy', p); process.exit(1); }
  if (!carriers.some(c => c.to_hex() === hit.to_hex())) carriers.push(hit);
}
const pure = all.filter(u => policiesOf(u).length === 0)
  .sort((a, b) => Number(b.output().amount().coin().to_str()) - Number(a.output().amount().coin().to_str()));
if (!pure.length) { console.error('  no pure-ada UTxO to seed the name'); process.exit(1); }
console.log(`  carriers ${carriers.length}   pure-ada ${pure.length}`);

const cfg = CSL.TransactionBuilderConfigBuilder.new()
  .fee_algo(CSL.LinearFee.new(CSL.BigNum.from_str('44'), CSL.BigNum.from_str('155381')))
  .pool_deposit(CSL.BigNum.from_str('500000000')).key_deposit(CSL.BigNum.from_str('2000000'))
  .max_value_size(5000).max_tx_size(16384)
  .coins_per_utxo_byte(CSL.BigNum.from_str('4310'))
  .ex_unit_prices(CSL.ExUnitPrices.new(
    CSL.UnitInterval.new(CSL.BigNum.from_str('577'), CSL.BigNum.from_str('10000')),
    CSL.UnitInterval.new(CSL.BigNum.from_str('721'), CSL.BigNum.from_str('10000000'))))
  .build();
const tb = CSL.TransactionBuilder.new(cfg);

const seed = pure[0];
const nameStr = TICKER + hex(seed.input().transaction_id().to_bytes()).slice(0, 8);
const assetName = CSL.AssetName.new(Buffer.from(nameStr, 'utf8'));
const script = CSL.PlutusScript.new_v3(Buffer.from(SCRIPT_HEX, 'hex'));
if (hex(script.hash().to_bytes()) !== POLICY) throw new Error('policy mismatch');

const redeemer = CSL.Redeemer.new(CSL.RedeemerTag.new_mint(), CSL.BigNum.from_str('0'),
  CSL.PlutusData.new_empty_constr_plutus_data(CSL.BigNum.from_str('0')),
  CSL.ExUnits.new(CSL.BigNum.from_str('2000000'), CSL.BigNum.from_str('700000000')));
const mb = CSL.MintBuilder.new();
mb.add_asset(CSL.MintWitness.new_plutus_script(CSL.PlutusScriptSource.new(script), redeemer),
  assetName, CSL.Int.new_i32(1));
tb.set_mint_builder(mb);

const cut = s => s.match(/.{1,64}/g);
const uri = 'data:image/svg+xml;base64,' + SVG.toString('base64');
const meta = {}; meta[POLICY] = {};
meta[POLICY][nameStr] = { name: TICKER, mediaType: 'image/svg+xml', image: cut(uri),
  description: cut('The ninth. Gated by the other eight. Fully on-chain.') };
const aux = CSL.AuxiliaryData.new();
const gtm = CSL.GeneralTransactionMetadata.new();
gtm.insert(CSL.BigNum.from_str('721'), CSL.encode_json_str_to_metadatum(
  JSON.stringify(meta), CSL.MetadataJsonSchema.NoConversions));
aux.set_metadata(gtm);
tb.set_auxiliary_data(aux);

const ma = CSL.MultiAsset.new(); const as = CSL.Assets.new();
as.insert(assetName, CSL.BigNum.from_str('1'));
ma.insert(CSL.ScriptHash.from_bytes(script.hash().to_bytes()), as);
const probe = CSL.Value.new(CSL.BigNum.from_str('3000000')); probe.set_multiasset(ma);
const minAda = CSL.min_ada_for_output(CSL.TransactionOutput.new(addr, probe),
  CSL.DataCost.new_coins_per_byte(CSL.BigNum.from_str('4310')));
const outV = CSL.Value.new(minAda); outV.set_multiasset(ma);
tb.add_output(CSL.TransactionOutput.new(addr, outV));

const added = new Set();
for (const u of [seed, ...carriers, ...pure.slice(1, 5)]) {
  const k = u.to_hex(); if (added.has(k)) continue; added.add(k);
  tb.add_regular_input(u.output().address(), u.input(), u.output().amount());
}
const cib = CSL.TxInputsBuilder.new();
const col = pure[pure.length - 1];
cib.add_regular_input(col.output().address(), col.input(), col.output().amount());
tb.set_collateral(cib);

const cm = CSL.CostModel.new();
COSTS.forEach((v, i) => cm.set(i, v < 0
  ? CSL.Int.new_negative(CSL.BigNum.from_str(String(-v)))
  : CSL.Int.new(CSL.BigNum.from_str(String(v)))));
const cms = CSL.Costmdls.new(); cms.insert(CSL.Language.new_plutus_v3(), cm);
tb.calc_script_data_hash(cms);
tb.add_change_if_needed(addr);

const tx = tb.build_tx();
const cbor = hex(tx.to_bytes());
console.log(`  tx       ${(cbor.length / 2).toLocaleString()} B   asset ${nameStr}`);
console.log(`  mode     ${SEVEN ? 'SEVEN of eight (MUST FAIL)' : 'EIGHT of eight (must pass)'}`);

const res = await bf('/utils/txs/evaluate', {
  method: 'POST', headers: { 'Content-Type': 'application/cbor' }, body: cbor });
console.log('\n  evaluate ->', res.status);
console.log(JSON.stringify(res.body, null, 1).split('\n').slice(0, 26).map(l => '  ' + l).join('\n'));

const r = res.body?.result ?? res.body;
const okShape = r && (r.EvaluationResult || (typeof r === 'object' && Object.values(r).some(v => v && v.memory)));
if (SEVEN) {
  console.log(okShape ? '\n  *** FAIL: seven of eight EVALUATED — the gate is not gating ***\n'
                      : '\n  PASS: seven of eight is rejected by the script\n');
  process.exit(okShape ? 1 : 0);
} else {
  console.log(okShape ? '\n  PASS: the script executed on chain data\n'
                      : '\n  *** FAIL: eight of eight did not evaluate ***\n');
  process.exit(okShape ? 0 : 1);
}
