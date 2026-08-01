import puppeteer from 'puppeteer-core';
const url = process.argv[2], outdir = process.argv[3];
const browser = await puppeteer.launch({executablePath:'/snap/bin/chromium', headless:'new',
  args:['--no-sandbox','--disable-gpu']});
const page = await browser.newPage();
await page.setViewport({width:390, height:844, deviceScaleFactor:2});
const errs=[]; page.on('pageerror',e=>errs.push(e.message));
await page.goto(url,{waitUntil:'networkidle0',timeout:60000});
// dress him up a bit so the steps aren't all defaults
await page.evaluate(()=>{
  document.querySelector('.chip[data-cat="mood"][data-val="mad"]').click();
  document.querySelector('.chip[data-cat="eyes"][data-val="thug"]').click();
  document.querySelector('.chip[data-cat="hat"][data-val="crown"]').click();
  document.querySelector('.chip[data-cat="neck"][data-val="thug"]').click();
  const t=document.getElementById('text'); t.value='SOMETIMES YOU DEAL WITH OLIGARCH';
  t.dispatchEvent(new Event('input'));
});
const nsteps = await page.evaluate(()=>document.querySelectorAll('.panel').length);
for (let i=0;i<nsteps;i++){
  await page.evaluate(i=>window.__goto(i), i);
  await new Promise(r=>setTimeout(r,350));
  await page.screenshot({path:`${outdir}/step${i}.png`});
}
console.log(errs.length?('ERRORS: '+errs.join(' | ')):'no page errors');
await browser.close();
