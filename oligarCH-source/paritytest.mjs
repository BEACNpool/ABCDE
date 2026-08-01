// The preview must be byte-identical to what the python builder produces, or the page is
// lying about the artifact it is going to put on chain.
import puppeteer from 'puppeteer-core';
const url = process.argv[2];
const cases = JSON.parse(process.argv[3]);
const browser = await puppeteer.launch({executablePath:'/snap/bin/chromium', headless:'new',
  args:['--no-sandbox','--disable-gpu']});
const page = await browser.newPage();
const errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(url, {waitUntil:'networkidle0', timeout:60000});
const out = [];
for (const c of cases) {
  const svg = await page.evaluate(async (c) => {
    for (const [k,v] of Object.entries(c.pick)) {
      const el = document.querySelector(`.chip[data-cat="${k}"][data-val="${v}"]`);
      if (!el) return 'MISSING CHIP ' + k + '=' + v;
      el.click();
    }
    const t = document.getElementById('text');
    t.value = c.text || '';
    t.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 30));
    if (window.__svg === undefined) return 'NO __svg HOOK';
    return window.__svg;
  }, c);
  out.push(svg);
}
console.log(JSON.stringify({svgs: out, errors: errs}));
await browser.close();
