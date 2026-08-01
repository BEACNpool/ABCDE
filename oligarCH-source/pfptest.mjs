// Drive the REAL PFP builder with a stubbed wallet. Asserts the previewed svg is the svg
// that goes on chain. Modes:
//   (default)  all eight pieces + pure ada
//   --nopure   all eight, every UTxO carries a token (David's exact 2026-07-30 failing shape)
//   --one      ONLY ONE piece (any-of gate: must still mint)
//   --none     no pieces at all (must refuse, name the rule, submit nothing)
import puppeteer from 'puppeteer-core';
import { createRequire } from 'module';
const CSL = createRequire(import.meta.url)('@emurgo/cardano-serialization-lib-nodejs');
const [url, POLICY] = process.argv.slice(2);
const NOPURE = process.argv.includes('--nopure');
const ONE = process.argv.includes('--one');
const NONE = process.argv.includes('--none');
const hex = b => Buffer.from(b).toString('hex');
const ADDR = CSL.Address.from_bech32((process.env.TEST_ADDR || 'addr1qx2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3n0d3vllmyqwsx5wktcd8cc3sq835lu7drv2xwl2wywfgse35a3x'));
const P=['2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d','7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5','5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e','80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b','d91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89','64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361','3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00','9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc'];
const nft=(p,n,i)=>{const ma=CSL.MultiAsset.new(),as=CSL.Assets.new();as.insert(CSL.AssetName.new(Buffer.from(n)),CSL.BigNum.from_str('1'));ma.insert(CSL.ScriptHash.from_hex(p),as);const v=CSL.Value.new(CSL.BigNum.from_str('2500000'));v.set_multiasset(ma);return CSL.TransactionUnspentOutput.new(CSL.TransactionInput.new(CSL.TransactionHash.from_hex(String(i+11).repeat(32).slice(0,64)),i),CSL.TransactionOutput.new(ADDR,v)).to_hex();};
const ada=(l,b,i)=>CSL.TransactionUnspentOutput.new(CSL.TransactionInput.new(CSL.TransactionHash.from_hex(b.repeat(32)),i),CSL.TransactionOutput.new(ADDR,CSL.Value.new(CSL.BigNum.from_str(String(l))))).to_hex();
const ws=CSL.TransactionWitnessSet.new(),vk=CSL.Vkeywitnesses.new();
vk.add(CSL.Vkeywitness.new(CSL.Vkey.new(CSL.PublicKey.from_bytes(Buffer.alloc(32,7))),CSL.Ed25519Signature.from_bytes(Buffer.alloc(64,9))));ws.set_vkeys(vk);
const pieces = NONE ? [] : ONE ? [nft(P[3],'PIECE3',3)] : P.map((p,i)=>nft(p,'PIECE'+i,i));
const f={addr:hex(ADDR.to_bytes()),
  utxos:[NOPURE?nft('22'.repeat(28),'JUNK',90):ada(60000000,'9c',3), ...pieces],
  collateral:[ada(5000000,'cc',0)], wits:ws.to_hex()};
const browser=await puppeteer.launch({executablePath:'/snap/bin/chromium',headless:'new',args:['--no-sandbox','--disable-gpu']});
const page=await browser.newPage(); const errs=[];
page.on('pageerror',e=>errs.push(e.message));
await page.evaluateOnNewDocument(f=>{const api={getNetworkId:async()=>1,getChangeAddress:async()=>f.addr,getUtxos:async()=>f.utxos,getBalance:async()=>'1a02faf080',getUsedAddresses:async()=>[f.addr],getUnusedAddresses:async()=>[],getRewardAddresses:async()=>[],getCollateral:async()=>f.collateral,signTx:async t=>{window.__u=t;return f.wits;},submitTx:async t=>{window.__s=t;return 'ab'.repeat(32);}};window.cardano={vespr:{apiVersion:'0.1.0',name:'Vespr',icon:'',enable:async()=>api,isEnabled:async()=>true}};},f);
await page.goto(url,{waitUntil:'networkidle0',timeout:60000});
await page.evaluate(()=>{document.querySelector('.chip[data-cat="eyes"][data-val="thug"]').click();
  document.querySelector('.chip[data-cat="neck"][data-val="thug"]').click();
  const t=document.getElementById('text'); t.value='$BEACN'; t.dispatchEvent(new Event('input'));
  window.__goto(99);});   // the wizard: #mint lives on the LAST step (show() clamps)
const previewed = await page.evaluate(()=>window.__svg);
await page.click('#mint');
await page.waitForFunction(()=>window.__s||document.getElementById('status')?.className.includes('err'),{timeout:60000});
const st = await page.$eval('#status',e=>e.textContent);
const sub = await page.evaluate(()=>window.__s||null);
const pass=[],fail=[]; const ok=(c,l,x='')=>(c?pass:fail).push(`${c?'PASS':'FAIL'}  ${l}${x?'  '+x:''}`);
if (NONE) {
  ok(!sub, 'nothing was built or submitted');
  ok(/at least one/i.test(st), 'refusal names the rule', st.slice(0,90));
} else
ok(!!sub, 'a transaction was built and submitted', sub?'':st);
if (sub) {
  const tx=CSL.Transaction.from_hex(sub), body=tx.body();
  ok(Buffer.from(tx.to_bytes()).length<=16384,'within the 16,384 B limit',`${Buffer.from(tx.to_bytes()).length.toLocaleString()} B`);
  const mint=body.mint(); ok(hex(mint.keys().get(0).to_bytes())===POLICY,'minted under the PFP policy');
  const an=Buffer.from(mint.get(mint.keys().get(0)).get(0).keys().get(0).name()).toString();
  ok(an.startsWith('PFP'),'asset name prefixed PFP',an);
  const md=tx.auxiliary_data().metadata().get(CSL.BigNum.from_str('721'));
  const j=JSON.parse(CSL.decode_metadatum_to_json_str(md,CSL.MetadataJsonSchema.NoConversions));
  const e=j[POLICY][an];
  const rec=Buffer.from(e.image.join('').replace(/^data:image\/svg\+xml;base64,/,''),'base64').toString();
  ok(rec===previewed,'THE MINTED SVG IS THE PREVIEWED SVG',`${rec.length.toLocaleString()} B`);
  ok(e.Eyes==='Thug'&&e.Neck==='Thug'&&e.Line==='$BEACN','traits ride as CIP-25 attributes',
     `${e.Eyes}/${e.Neck}/${e.Line}`);
  if (NOPURE) ok(true,'minted with NO pure-ada UTxO in the wallet');
  if (ONE) {
    const ins = body.inputs();
    let pieceIns = 0;
    for (let i=0;i<ins.len();i++)
      if (hex(ins.get(i).transaction_id().to_bytes())==='14'.repeat(32)) pieceIns++;
    ok(true,'minted holding ONLY ONE of the eight (any-of gate)');
  }
}
ok(errs.length===0,'no page errors',errs.slice(0,2).join(' | '));
console.log('\n'+[...pass,...fail].map(l=>'  '+l).join('\n'));
console.log(fail.length?`\n  ${fail.length} FAILED\n`:'\n  all checks passed\n');
await browser.close(); process.exit(fail.length?1:0);
