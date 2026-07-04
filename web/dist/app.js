// ABCDE — A BEACN Cardano Data Explorer. Fully client-side.
import * as duckdb from 'https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@1.29.0/+esm';

const $ = (s, r = document) => r.querySelector(s);
const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
const fmtAda = n => n == null ? '' : Number(n).toLocaleString('en-US', { maximumFractionDigits: 0 }) + ' ₳';
const fmtNum = n => n == null ? '' : Number(n).toLocaleString('en-US');
const short = (a, n = 14) => !a ? '' : (a.length > n * 2 ? a.slice(0, n) + '…' + a.slice(-6) : a);
const gradeClass = g => /FACT/i.test(g) ? 'fact' : /STRONG/i.test(g) ? 'strong' : /HYPOTH/i.test(g) ? 'hyp' : 'unknown';

const j = async p => (await fetch(p)).json();

// ---------- load prebuilt data (works even if WASM never loads) ----------
let STATS, FEATURED, FINDINGS, CATALOG;
async function boot() {
  try {
    [STATS, FEATURED, FINDINGS, CATALOG] = await Promise.all([
      j('data/stats.json'), j('data/featured.json'), j('data/findings.json'), j('data/catalog.json'),
    ]);
    renderStats(); renderExplore(); renderFindings();
  } catch (e) { console.error('data load failed', e); }
  initDuck();  // separate, non-blocking
}

function renderStats() {
  const s = STATS;
  const tiles = [
    [fmtAda(s.seed_total_ada), 'genesis founder ADA tracked'],
    [fmtAda(s.component_ada), 'in one closed 115-key operation'],
    [s.tables, 'query-ready tables'],
    ['epoch ' + s.tip_epoch, 'on-chain snapshot boundary'],
  ];
  $('#stats').innerHTML = '';
  tiles.forEach(([n, l]) => {
    const t = el('div', 'stat'); t.append(el('div', 'n', n), el('div', 'l', l)); $('#stats').append(t);
  });
  const tip = `Snapshot @ block ${fmtNum(s.tip_block)}, epoch ${s.tip_epoch} (${s.tip_time} UTC) · ${s.exact_35m} wallets holding exactly 35,000,000 ₳`;
  $('#tipline').textContent = tip;
  const ft = $('#foot-tip'); if (ft) ft.textContent = `Snapshot: block ${fmtNum(s.tip_block)} · epoch ${s.tip_epoch}`;
}

// ---------- explore tabs ----------
function tableHTML(cols, rows) {
  const h = '<div class="tbl-wrap"><table><thead><tr>' + cols.map(c => `<th>${c.label}</th>`).join('') +
    '</tr></thead><tbody>' + rows.map(r => '<tr>' + cols.map(c => `<td class="${c.cls || ''}">${c.fmt ? c.fmt(r[c.k]) : (r[c.k] ?? '')}</td>`).join('') + '</tr>').join('') +
    '</tbody></table></div>';
  return h;
}
function card(title, chip, valueHTML) {
  return `<div class="card"><h3>${title}${chip ? `<span class="chip ${gradeClass(chip)}">${chip}</span>` : ''}</h3>${valueHTML}</div>`;
}
function renderExplore() {
  // seeds
  const seedRows = FEATURED.seeds.map(s => ({ ...s, ada: s.amount_ada }));
  $('#p-seeds').innerHTML =
    `<p class="sec-lede">The four founder genesis entries and the graded fourth entry — the roots every trace starts from.</p>` +
    tableHTML([
      { k: 'label', label: 'Entry' },
      { k: 'ada', label: 'Genesis ADA', fmt: fmtAda },
      { k: 'source_type', label: 'Class' },
      { k: 'grade', label: 'Grade', fmt: g => `<span class="chip ${gradeClass(g)}">${g}</span>` },
    ], seedRows);

  // whale
  const w = FEATURED.whale;
  $('#p-whale').innerHTML =
    `<div class="grid g3" style="margin-bottom:16px">
       ${card('Closed component', 'FACT', `<div class="v">${w.component_keys} keys</div><div class="sub">reachable to fixpoint via reward plumbing</div>`)}
       ${card('Exact 35M parcels', 'FACT', `<div class="v">${w.exact_35m}</div><div class="sub">of ${w.holders} holders, identical parcel size</div>`)}
       ${card('Total held', 'STRONG_INFERENCE', `<div class="v">${fmtAda(w.total_ada)}</div><div class="sub">one operation, not many owners</div>`)}
     </div>
     <p class="sec-lede">Largest current parcels — note the uniform size and the unanimous always-abstain governance posture.</p>` +
    tableHTML([
      { k: 'stake_address', label: 'Stake key', cls: 'addr', fmt: a => short(a) },
      { k: 'ada', label: 'Current ADA', fmt: fmtAda },
      { k: 'drep', label: 'DRep' },
      { k: 'withdrawals', label: 'Reward sweeps', fmt: fmtNum },
      { k: 'pattern', label: 'Custody pattern' },
    ], w.parcels);

  // hubs
  $('#p-hubs').innerHTML =
    `<p class="sec-lede">The reward plumbing funnels into four enterprise addresses. Each has received
      <b>more than the entire ADA supply</b> over its life — the structural signature of a recirculating,
      exchange-scale hot address, not an accumulation sink. <span class="chip hyp">Working hypothesis: exchange/settlement</span></p>` +
    tableHTML([
      { k: 'address', label: 'Address', cls: 'addr', fmt: a => short(a) },
      { k: 'lifetime_outputs', label: 'Lifetime outputs', fmt: fmtNum },
      { k: 'gross_received_ada', label: 'Gross received', fmt: fmtAda },
    ], FEATURED.hubs);

  // exchanges
  const ex = FEATURED.exchanges;
  $('#p-exchanges').innerHTML =
    `<p class="sec-lede">The community's exchange-tracer campaign sent NFTs to suspected deposit addresses.
      Senders labeled the deposit transactions on-chain — six exchanges are named.
      <span class="chip hyp">Self-reported — working hypothesis until corroborated</span></p>
     <div class="grid g3">` +
    ex.map(e => card(e.name, '', `<div class="v">${e.claim_txs}</div><div class="sub">on-chain deposit-claim mentions</div>`)).join('') +
    `</div>
     <p class="muted" style="font-size:13px;margin-top:16px">The tracer NFTs are FACT (they exist on-chain);
       the exchange <i>attribution</i> is the sender's claim, graded accordingly.</p>`;

  $('#tabs').addEventListener('click', e => {
    const b = e.target.closest('.tab'); if (!b) return;
    $$('.tab').forEach(t => t.classList.remove('active'));
    $$('.panel').forEach(p => p.classList.remove('active'));
    b.classList.add('active'); $('#p-' + b.dataset.p).classList.add('active');
  });
}
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

// ---------- findings ----------
function renderFindings(filter = '') {
  const q = filter.trim().toLowerCase();
  const list = FINDINGS.filter(f => !q || (f.id + f.title + f.claim + f.grade).toLowerCase().includes(q));
  $('#finds').innerHTML = list.map(f => {
    const g = (f.grade || '').split(',').pop().trim();
    return `<a class="find" href="${f.url}" target="_blank" rel="noopener">
      <div class="top"><span class="fid">${f.id}</span><span class="ft">${f.title}</span>
        <span class="chip ${gradeClass(f.grade)}">${g}</span></div>
      <p class="fc">${f.claim || ''}</p></a>`;
  }).join('') || `<p class="muted">No findings match “${filter}”.</p>`;
}

// ---------- DuckDB-WASM console ----------
let CONN = null;
async function initDuck() {
  const status = $('#qstatus'), runBtn = $('#run');
  try {
    const BUNDLES = duckdb.getJsDelivrBundles();
    const bundle = await duckdb.selectBundle(BUNDLES);
    const workerUrl = URL.createObjectURL(new Blob(
      [`importScripts("${bundle.mainWorker}");`], { type: 'text/javascript' }));
    const worker = new Worker(workerUrl);
    const db = new duckdb.AsyncDuckDB(new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING), worker);
    await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
    URL.revokeObjectURL(workerUrl);
    CONN = await db.connect();

    const manifest = await j('data/parquet/manifest.json');
    for (const name of Object.keys(manifest)) {
      const url = new URL(`data/parquet/${name}.parquet`, location.href).href;
      await db.registerFileURL(`${name}.parquet`, url, duckdb.DuckDBDataProtocol.HTTP, false);
      await CONN.query(`CREATE OR REPLACE VIEW "${name}" AS SELECT * FROM parquet_scan('${name}.parquet')`);
    }
    renderSchema(manifest);
    renderExamples();
    status.textContent = 'engine ready — run a query';
    runBtn.disabled = false;
    runBtn.addEventListener('click', runQuery);
    $('#sql').addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') runQuery(); });
  } catch (e) {
    console.error(e);
    status.classList.add('err');
    status.textContent = 'in-browser engine unavailable in this browser — clone the repo to query locally';
    $('#schema-list').innerHTML = '<span class="muted">engine unavailable</span>';
  }
}
function renderSchema(manifest) {
  const names = Object.keys(manifest).sort();
  $('#schema-count').textContent = `(${names.length})`;
  $('#schema-list').innerHTML = names.map(n =>
    `<div class="t" data-t="${n}">${n}<small>${manifest[n].rows.toLocaleString()} rows</small></div>`).join('');
  $('#schema-list').addEventListener('click', e => {
    const t = e.target.closest('.t'); if (!t) return;
    $('#sql').value = `SELECT * FROM ${t.dataset.t} LIMIT 50;`;
  });
}
function renderExamples() {
  const ex = [
    ['42 exact-35M parcels', `SELECT stake_address, current_ada, current_drep, withdrawal_count\nFROM component_control_indicators\nWHERE abs(current_ada - 35000000) < 2\nORDER BY current_ada DESC;`],
    ['Exchanges named on-chain', `SELECT metadata_json, count(*) AS mentions\nFROM tracer_deposit_claims\nWHERE metadata_json LIKE '%Deposited to%'\nGROUP BY 1 ORDER BY 2 DESC;`],
    ['Genesis seeds', `SELECT label, amount_ada, source_type, evidence_grade FROM seeds ORDER BY amount_ada DESC;`],
    ['Exchange-scale hubs', `SELECT address, lifetime_outputs, gross_received_ada FROM f11_hub_classification ORDER BY gross_received_ada DESC;`],
    ['Governance actions', `SELECT * FROM governance_actions_catalog LIMIT 25;`],
  ];
  $('#examples').innerHTML = ex.map((e, i) => `<button data-i="${i}">${e[0]}</button>`).join('');
  $('#examples').addEventListener('click', ev => {
    const b = ev.target.closest('button'); if (!b) return;
    $('#sql').value = ex[b.dataset.i][1]; runQuery();
  });
}
async function runQuery() {
  const status = $('#qstatus'), out = $('#results');
  const sql = $('#sql').value.trim(); if (!sql || !CONN) return;
  status.classList.remove('err'); status.innerHTML = '<span class="spinner"></span> running…';
  const t0 = performance.now();
  try {
    const res = await CONN.query(sql);
    const cols = res.schema.fields.map(f => f.name);
    const rows = res.toArray().map(r => r.toJSON());
    const shown = rows.slice(0, 500);
    out.innerHTML = '<table><thead><tr>' + cols.map(c => `<th>${c}</th>`).join('') +
      '</tr></thead><tbody>' + shown.map(r => '<tr>' + cols.map(c => {
        let v = r[c]; if (typeof v === 'bigint') v = v.toString();
        return `<td>${v === null || v === undefined ? '' : String(v)}</td>`;
      }).join('') + '</tr>').join('') + '</tbody></table>';
    const ms = (performance.now() - t0).toFixed(0);
    status.textContent = `${rows.length.toLocaleString()} rows in ${ms} ms` + (rows.length > 500 ? ' (showing 500)' : '');
  } catch (e) {
    status.classList.add('err'); status.textContent = String(e.message || e);
    out.innerHTML = '';
  }
}

$('#find-search')?.addEventListener('input', e => renderFindings(e.target.value));
boot();
