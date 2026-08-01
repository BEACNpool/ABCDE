// Measure the REAL piece-9 transaction and solve for the largest artwork that fits.
//
// This is not the bare-timelock shape the other eight use. Piece 9:
//   * mints under a PLUTUS policy (no native script in the witness set at all)
//   * carries the compiled validator INLINE plus a redeemer, script data hash and collateral
//   * spends the eight earlier pieces as inputs to prove control; they return as change
//   * has NO ttl, because David ruled out a deadline so secondary-market sets can still mint
//
// Usage: node measure9.js <plutus.json> [svgBytes]
//        with no svgBytes it binary-searches the maximum that fits.
const fs = require('fs');
const CSL = require('@emurgo/cardano-serialization-lib-nodejs');

const MIN_FEE_A = 44, MIN_FEE_B = 155381, MAX_TX = 16384, CPB = 4310;
// mainnet Plutus execution prices
const PRICE_MEM = 0.0577, PRICE_STEP = 0.0000721;
// measured by `aiken check` on the passing case: mem 661.9 K, cpu 191.69 M. Budgeted with
// generous headroom, because an under-budget redeemer fails at validation, not at build.
const EX_MEM = 900_000, EX_STEPS = 260_000_000;

const blueprint = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
// ⚠️ THE FOOTGUN THAT WOULD HAVE SHIPPED THE WRONG POLICY ID.
// Aiken's `compiledCode` is ALREADY a CBOR byte string (it begins 0x59 <len16>), and the true
// on-chain script hash is blake2b224(0x03 || compiledCode) — verified independently in python
// and reported identically by `aiken build`.
// Determined EMPIRICALLY against that hash, because the two plausible CSL constructors
// disagree and only one is right:
//    CSL.PlutusScript.new_v3(<wrapped bytes>)                 -> 39f7e8f0…  CORRECT
//    CSL.PlutusScript.new_v3(<inner, header stripped>)        -> 43477d47…  wrong
//    CSL.PlutusScript.from_hex_with_version(<wrapped>, v3)    -> 43477d47…  wrong (it strips
//                                                                one CBOR layer first)
// Never derive this policy id from from_hex_with_version, and never pre-strip the header.
const wrapped = blueprint.validators[0].compiledCode;
const SCRIPT_BYTES = wrapped.length / 2;

const TICKER = 'NINE';
const ADDR = (process.env.TEST_ADDR || 'addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3n0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgse35a3x');
const HELD = [
  ['2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d', 'BYTTGb454e10e'],
  ['7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5', 'TGM7eb2b9e6'],
  ['5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e', 'IVYOM53c88904'],
  ['80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b', 'ORGf6afadac'],
  ['d91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89', 'HOTEL48130e3f'],
  ['64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361', 'NDLaabbccdd'],
  ['3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00', 'DNPGc5f42353'],
  ['9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc', 'SMOKE11223344'],
];

// the Plutus script's own hash IS the policy id
const mkScript = () => CSL.PlutusScript.new_v3(Buffer.from(wrapped, 'hex'));
const POLICY = Buffer.from(mkScript().hash().to_bytes()).toString('hex');
const assetName = TICKER + 'ffffffff';
const addr = CSL.Address.from_bech32(ADDR);
const chunk = (s, n = 64) => s.match(new RegExp(`.{1,${n}}`, 'g'));

const ma = (entries) => {
  const m = CSL.MultiAsset.new();
  for (const [p, n] of entries) {
    const a = CSL.Assets.new();
    a.insert(CSL.AssetName.new(Buffer.from(n, 'utf8')), CSL.BigNum.from_str('1'));
    m.insert(CSL.ScriptHash.from_hex(p), a);
  }
  return m;
};

function build(svgBytes, opts = {}) {
  try { return build_(svgBytes, opts); }
  catch (e) { if (/Maximum transaction size/.test(String(e))) return { size: Infinity, minAda: 0 }; throw e; }
}

function build_(svgBytes, { extraInputs = 0 } = {}) {
  const svg = Buffer.alloc(svgBytes, 0x41);            // size is all that matters here
  const uri = 'data:image/svg+xml;base64,' + svg.toString('base64');
  const meta = { [POLICY]: { [assetName]: {
    name: TICKER, mediaType: 'image/svg+xml', image: chunk(uri),
    description: chunk('Fully on-chain. The ninth, gated by the other eight. Edition nine.') } } };
  const auxData = CSL.AuxiliaryData.new();
  const gtm = CSL.GeneralTransactionMetadata.new();
  gtm.insert(CSL.BigNum.from_str('721'), CSL.encode_json_str_to_metadatum(
    JSON.stringify(meta), CSL.MetadataJsonSchema.NoConversions));
  auxData.set_metadata(gtm);

  const cfg = CSL.TransactionBuilderConfigBuilder.new()
    .fee_algo(CSL.LinearFee.new(CSL.BigNum.from_str(String(MIN_FEE_A)),
                                CSL.BigNum.from_str(String(MIN_FEE_B))))
    .pool_deposit(CSL.BigNum.from_str('500000000'))
    .key_deposit(CSL.BigNum.from_str('2000000'))
    .max_value_size(5000).max_tx_size(MAX_TX)
    .coins_per_utxo_byte(CSL.BigNum.from_str(String(CPB)))
    .ex_unit_prices(CSL.ExUnitPrices.new(
      CSL.UnitInterval.new(CSL.BigNum.from_str('577'), CSL.BigNum.from_str('10000')),
      CSL.UnitInterval.new(CSL.BigNum.from_str('721'), CSL.BigNum.from_str('10000000'))))
    .build();
  const tb = CSL.TransactionBuilder.new(cfg);

  // ---- mint under the Plutus policy, script INLINE ----
  const redeemer = CSL.Redeemer.new(CSL.RedeemerTag.new_mint(), CSL.BigNum.from_str('0'),
    CSL.PlutusData.new_empty_constr_plutus_data(CSL.BigNum.from_str('0')),
    CSL.ExUnits.new(CSL.BigNum.from_str(String(EX_MEM)), CSL.BigNum.from_str(String(EX_STEPS))));
  const mb = CSL.MintBuilder.new();
  mb.add_asset(
    CSL.MintWitness.new_plutus_script(CSL.PlutusScriptSource.new(mkScript()), redeemer),
    CSL.AssetName.new(Buffer.from(assetName, 'utf8')), CSL.Int.new_i32(1));
  tb.set_mint_builder(mb);
  tb.set_auxiliary_data(auxData);
  // NO set_ttl: the ninth has no deadline.

  // the output carrying the new NFT
  const nftMa = ma([[POLICY, assetName]]);
  const probe = CSL.TransactionOutput.new(addr, (() => {
    const v = CSL.Value.new(CSL.BigNum.from_str('3000000')); v.set_multiasset(nftMa); return v; })());
  const minAda = CSL.min_ada_for_output(probe,
    CSL.DataCost.new_coins_per_byte(CSL.BigNum.from_str(String(CPB))));
  const v = CSL.Value.new(minAda); v.set_multiasset(nftMa);
  tb.add_output(CSL.TransactionOutput.new(addr, v));

  // funding input
  tb.add_regular_input(addr,
    CSL.TransactionInput.new(CSL.TransactionHash.from_hex('00'.repeat(32)), 0),
    CSL.Value.new(CSL.BigNum.from_str('30000000')));

  // the eight held pieces, spent. They come back in the change output automatically —
  // the validator deliberately does not demand a specific return output.
  HELD.forEach(([p, n], i) => {
    const val = CSL.Value.new(CSL.BigNum.from_str('1180000'));
    val.set_multiasset(ma([[p, n]]));
    tb.add_regular_input(addr,
      CSL.TransactionInput.new(CSL.TransactionHash.from_hex(String(i + 11).repeat(32).slice(0, 64)), i),
      val);
  });
  // extra pure-ada inputs, to model a fragmented wallet
  for (let i = 0; i < extraInputs; i++)
    tb.add_regular_input(addr,
      CSL.TransactionInput.new(CSL.TransactionHash.from_hex('ab'.repeat(32)), 100 + i),
      CSL.Value.new(CSL.BigNum.from_str('2000000')));

  // Plutus requires collateral and a script data hash
  const cib = CSL.TxInputsBuilder.new();
  cib.add_regular_input(addr,
    CSL.TransactionInput.new(CSL.TransactionHash.from_hex('cc'.repeat(32)), 0),
    CSL.Value.new(CSL.BigNum.from_str('5000000')));
  tb.set_collateral(cib);
  tb.set_total_collateral_and_return(CSL.BigNum.from_str('3000000'), addr);
  tb.set_script_data_hash(CSL.ScriptDataHash.from_hex('dd'.repeat(32)));

  tb.add_change_if_needed(addr);
  const body = tb.build();

  const ws = CSL.TransactionWitnessSet.new();
  const vkeys = CSL.Vkeywitnesses.new();
  vkeys.add(CSL.Vkeywitness.new(CSL.Vkey.new(CSL.PublicKey.from_bytes(Buffer.alloc(32, 1))),
    CSL.Ed25519Signature.from_bytes(Buffer.alloc(64, 1))));
  ws.set_vkeys(vkeys);
  const ps = CSL.PlutusScripts.new(); ps.add(mkScript()); ws.set_plutus_scripts(ps);
  const rs = CSL.Redeemers.new();
  rs.add(CSL.Redeemer.new(CSL.RedeemerTag.new_mint(), CSL.BigNum.from_str('0'),
    CSL.PlutusData.new_empty_constr_plutus_data(CSL.BigNum.from_str('0')),
    CSL.ExUnits.new(CSL.BigNum.from_str(String(EX_MEM)), CSL.BigNum.from_str(String(EX_STEPS)))));
  ws.set_redeemers(rs);

  const size = CSL.Transaction.new(body, ws, auxData).to_bytes().length;
  return { size, minAda: Number(minAda.to_str()) };
}

console.log(`\n  validator      ${SCRIPT_BYTES} B compiled, Plutus V3, INLINE`);
console.log(`  policy id      ${POLICY}`);
console.log(`  exUnits        mem ${EX_MEM.toLocaleString()} / steps ${EX_STEPS.toLocaleString()}`
          + `  (aiken measured 661,900 / 191,690,000)`);

const target = process.argv[3] ? Number(process.argv[3]) : null;
if (target) {
  const { size } = build(target);
  console.log(`\n  ${target.toLocaleString()} B of SVG -> ${size.toLocaleString()} B tx `
            + `(${(100 * size / MAX_TX).toFixed(1)}%)\n`);
} else {
  let lo = 1000, hi = 12000;
  while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (build(mid).size <= MAX_TX) lo = mid; else hi = mid - 1; }
  const at = build(lo);
  const fee = MIN_FEE_A * at.size + MIN_FEE_B;
  const exFee = EX_MEM * PRICE_MEM + EX_STEPS * PRICE_STEP;
  console.log(`\n  MAX ARTWORK    ${lo.toLocaleString()} B of SVG  ->  ${at.size.toLocaleString()} B tx `
            + `(${(100 * at.size / MAX_TX).toFixed(1)}%)`);
  console.log(`\n  at a 9,000 B artwork (a comfortable working target):`);
  for (const extra of [0, 5, 10, 20, 40]) {
    const r = build(9000, { extraInputs: extra });
    console.log(`    +${String(extra).padStart(2)} extra wallet inputs  ${r.size.toLocaleString().padStart(6)} B `
              + `(${(100 * r.size / MAX_TX).toFixed(1)}%)  ${r.size > MAX_TX ? 'OVER' : (MAX_TX - r.size).toLocaleString() + ' B spare'}`);
  }
  const nine = build(9000);
  const f = MIN_FEE_A * nine.size + MIN_FEE_B;
  console.log(`\n  minter pays    ${((f + exFee) / 1e6).toFixed(3)} ADA fee `
            + `(${(f / 1e6).toFixed(3)} size + ${(exFee / 1e6).toFixed(3)} execution)`);
  console.log(`                 + ${(nine.minAda / 1e6).toFixed(3)} ADA min-UTxO, which stays in their wallet`);
  console.log(`                 + a pure-ada collateral UTxO (returned; not spent unless the script fails)\n`);
}
