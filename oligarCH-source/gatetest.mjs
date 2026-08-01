// Drive the REAL gate page with a stubbed CIP-30 wallet, and check both halves:
//   * holding all EIGHT -> a valid gated transaction is built and submitted
//   * holding only SEVEN -> the page refuses and names the missing piece
// A gate that only proves it lets people in has proved nothing.
//
//   node gatetest.mjs <url> <svgPath> <ticker> <expectedPolicyId> [--seven]
import puppeteer from 'puppeteer-core';
import fs from 'fs';
import { createRequire } from 'module';
const CSL = createRequire(import.meta.url)('@emurgo/cardano-serialization-lib-nodejs');

const [url, svgPath, TICKER, EXPECT_POLICY] = process.argv.slice(2);
const SEVEN = process.argv.includes('--seven');
// --nopure reproduces David's failing wallet: EVERY UTxO carries a token, so there is no
// pure-ada UTxO to seed the name. The mint must still work.
const NOPURE = process.argv.includes('--nopure');
const svgBytes = fs.readFileSync(svgPath);
const hex = b => Buffer.from(b).toString('hex');

const ADDR = CSL.Address.from_bech32(
  (process.env.TEST_ADDR || 'addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3n0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgse35a3x'));

const HELD = [
  ['2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d', 'BYTTGb454e10e'],
  ['7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5', 'TGM7eb2b9e6'],
  ['5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e', 'IVYOM53c88904'],
  ['80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b', 'ORGf6afadac'],
  ['d91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89', 'HOTEL48130e3f'],
  ['64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361', 'NDLaabbccdd'],
  ['3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00', 'DNPGc5f42353'],
  ['9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc', 'SMOKE11223344'],
].slice(0, SEVEN ? 7 : 8);

const nftUtxo = (policy, name, ix) => {
  const ma = CSL.MultiAsset.new(), as = CSL.Assets.new();
  as.insert(CSL.AssetName.new(Buffer.from(name, 'utf8')), CSL.BigNum.from_str('1'));
  ma.insert(CSL.ScriptHash.from_hex(policy), as);
  const v = CSL.Value.new(CSL.BigNum.from_str('1180000')); v.set_multiasset(ma);
  return CSL.TransactionUnspentOutput.new(
    CSL.TransactionInput.new(CSL.TransactionHash.from_hex(String(ix + 11).repeat(32).slice(0, 64)), ix),
    CSL.TransactionOutput.new(ADDR, v)).to_hex();
};
const adaUtxo = (lovelace, seedByte, ix) => CSL.TransactionUnspentOutput.new(
  CSL.TransactionInput.new(CSL.TransactionHash.from_hex(seedByte.repeat(32)), ix),
  CSL.TransactionOutput.new(ADDR, CSL.Value.new(CSL.BigNum.from_str(String(lovelace))))).to_hex();

const ws = CSL.TransactionWitnessSet.new();
const vks = CSL.Vkeywitnesses.new();
vks.add(CSL.Vkeywitness.new(CSL.Vkey.new(CSL.PublicKey.from_bytes(Buffer.alloc(32, 7))),
  CSL.Ed25519Signature.from_bytes(Buffer.alloc(64, 9))));
ws.set_vkeys(vks);

const fixtures = {
  addr: hex(ADDR.to_bytes()),
  utxos: [NOPURE ? nftUtxo('11'.repeat(28), 'JUNKTOKEN', 90) : adaUtxo(40_000_000, '9c', 3),
          ...HELD.map(([p, n], i) => nftUtxo(p, n, i))],
  collateral: [adaUtxo(5_000_000, 'cc', 0)],
  wits: ws.to_hex(),
};

const browser = await puppeteer.launch({
  executablePath: '/snap/bin/chromium', headless: 'new',
  args: ['--no-sandbox', '--disable-gpu'],
});
const page = await browser.newPage();
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error' && !/favicon|404/.test(m.text())) errors.push('console: ' + m.text()); });
page.on('response', r => { if (r.status() >= 400 && !/favicon/.test(r.url())) errors.push(r.status() + ' ' + r.url()); });

await page.evaluateOnNewDocument(f => {
  const api = {
    getNetworkId: async () => 1,
    getChangeAddress: async () => f.addr,
    getUtxos: async () => f.utxos,
    getBalance: async () => '1a02faf080',
    getUsedAddresses: async () => [f.addr],
    getUnusedAddresses: async () => [],
    getRewardAddresses: async () => [],
    getCollateral: async () => f.collateral,
    signTx: async (txHex) => { window.__unsigned = txHex; return f.wits; },
    submitTx: async (txHex) => { window.__submitted = txHex; return 'ab'.repeat(32); },
  };
  window.cardano = { stubwallet: {
    apiVersion: '0.1.0', name: 'StubWallet', icon: '',
    enable: async () => api, isEnabled: async () => true } };
}, fixtures);

await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });
await page.waitForSelector('#pick button[data-w]', { timeout: 20000 });
await page.click('#pick button[data-w]');

const pass = [], fail = [];
const ok = (c, label, extra = '') => (c ? pass : fail).push(`${c ? 'PASS' : 'FAIL'}  ${label}${extra ? '  ' + extra : ''}`);

if (SEVEN) {
  await page.waitForFunction(() => document.getElementById('status')?.className.includes('err'),
    { timeout: 40000 }).catch(() => {});
  const msg = await page.$eval('#status', e => e.textContent);
  const tally = await page.$eval('#tally', e => e.textContent);
  const submitted = await page.evaluate(() => window.__submitted || null);
  ok(/incomplete/i.test(msg), 'seven of eight is refused', JSON.stringify(msg.slice(0, 60)));
  ok(/SMOKE/.test(msg), 'the refusal names the missing piece');
  ok(/7 of 8/.test(tally), 'tally reads 7 of 8', JSON.stringify(tally));
  ok(submitted === null, 'nothing was signed or submitted');
} else {
  await page.waitForFunction(() => window.__submitted, { timeout: 60000 });
  const submitted = await page.evaluate(() => window.__submitted);
  const tally = await page.$eval('#tally', e => e.textContent);
  const tx = CSL.Transaction.from_hex(submitted);
  const body = tx.body(), size = Buffer.from(tx.to_bytes()).length;

  ok(/8 of 8/.test(tally), 'tally reads 8 of 8', JSON.stringify(tally));
  ok(size <= 16384, 'signed tx within the 16,384 B limit', `${size.toLocaleString()} B (${(100*size/16384).toFixed(1)}%)`);

  const mint = body.mint();
  ok(mint.keys().len() === 1, 'exactly one policy minted');
  const pid = hex(mint.keys().get(0).to_bytes());
  ok(pid === EXPECT_POLICY, 'minted policy is the gate policy', pid);
  const assets = mint.get(mint.keys().get(0)).get(0);
  ok(assets.len() === 1, 'exactly one asset minted');
  const an = Buffer.from(assets.keys().get(0).name()).toString('utf8');
  ok(an.startsWith(TICKER) && an.length === TICKER.length + 8,
     'asset name is TICKER + 8 hex of the seed UTxO', an);
  if (NOPURE) ok(true, 'minted with NO pure-ada UTxO in the wallet', an);
  ok(assets.get(assets.keys().get(0)).to_str() === '1', 'quantity is exactly 1');

  // every one of the eight must actually be spent — that is the proof of control
  const ins = new Set();
  for (let i = 0; i < body.inputs().len(); i++)
    ins.add(hex(body.inputs().get(i).transaction_id().to_bytes()) + '#' + body.inputs().get(i).index());
  const spentAll = HELD.every((_, i) => ins.has(String(i + 11).repeat(32).slice(0, 64) + '#' + i));
  ok(spentAll, 'all eight pieces are SPENT as inputs', `${ins.size} inputs`);

  ok(!!body.collateral() && body.collateral().len() > 0, 'collateral is attached');
  ok(!!body.script_data_hash(), 'script data hash is set',
     body.script_data_hash() ? hex(body.script_data_hash().to_bytes()).slice(0, 16) + '…' : '');
  ok(body.ttl() === undefined || body.ttl() === null, 'no ttl — the ninth has no deadline');

  const wits = tx.witness_set();
  ok(!!wits.plutus_scripts() && wits.plutus_scripts().len() === 1, 'the plutus script rides inline');
  ok(!!wits.redeemers() && wits.redeemers().len() === 1, 'a mint redeemer is present');

  // the picture must come back out of the metadata byte-identical
  const md = tx.auxiliary_data().metadata().get(CSL.BigNum.from_str('721'));
  const json = JSON.parse(CSL.decode_metadatum_to_json_str(md, CSL.MetadataJsonSchema.NoConversions));
  const uri = json[pid][an].image.join('');
  const recovered = Buffer.from(uri.replace(/^data:image\/svg\+xml;base64,/, ''), 'base64');
  ok(recovered.equals(svgBytes), 'image round-trips out of the tx byte-identical',
     `${recovered.length.toLocaleString()} B`);
  ok(json[pid][an].image.every(c => Buffer.byteLength(c) <= 64), 'every metadata chunk within 64 B');
}

ok(errors.length === 0, 'no page errors', errors.slice(0, 2).join(' | '));
console.log('\n' + [...pass, ...fail].map(l => '  ' + l).join('\n'));
console.log(fail.length ? `\n  ${fail.length} FAILED\n` : '\n  all checks passed\n');
await browser.close();
process.exit(fail.length ? 1 : 0);
