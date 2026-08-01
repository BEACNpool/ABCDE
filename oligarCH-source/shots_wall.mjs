import puppeteer from 'puppeteer-core';
const [url, out] = process.argv.slice(2);
const b = await puppeteer.launch({executablePath:'/snap/bin/chromium', headless:'new',
  args:['--no-sandbox','--disable-gpu']});
const p = await b.newPage();
await p.setViewport({width:390, height:844, deviceScaleFactor:2});
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.goto(url,{waitUntil:'networkidle0',timeout:60000});
await new Promise(r=>setTimeout(r,2500));   // let the live Koios top-up run
await p.screenshot({path:out+'/wall-mobile.png'});
await p.setViewport({width:1280, height:900, deviceScaleFactor:1});
await new Promise(r=>setTimeout(r,400));
await p.screenshot({path:out+'/wall-desktop.png'});
const tally = await p.$eval('#tally', e=>e.textContent);
console.log('tally:', tally, errs.length?('ERRORS: '+errs.join('|')):'· no page errors');
await b.close();
