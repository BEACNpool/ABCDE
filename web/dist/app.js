// ABCDE — A BEACN Cardano Data Explorer. Static onboarding launchpad.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
const fmtAda = n => n == null ? '' : Number(n).toLocaleString('en-US', { maximumFractionDigits: 0 }) + ' ₳';
const fmtNum = n => n == null ? '' : Number(n).toLocaleString('en-US');
const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const gradeClass = g => /FACT/i.test(g) ? 'fact' : /STRONG/i.test(g) ? 'strong' : /HYPOTH/i.test(g) ? 'hyp' : 'unknown';
const j = async p => (await fetch(p)).json();

let STATS, FAMILIES, QUESTIONS, FINDINGS, HOOKS;
let MODEL = 'code', OS = 'mac';

(async function boot() {
  try {
    [STATS, FAMILIES, QUESTIONS, FINDINGS, HOOKS] = await Promise.all(
      ['stats', 'families', 'questions', 'findings', 'hooks'].map(n => j(`data/${n}.json`)));
    renderStats(); renderHooks(); renderFamilies(); renderQuestions(); renderFindings();
  } catch (e) { console.error('data load failed', e); }
  wirePickers(); renderSteps(); renderAsk();
})();

const SITE = 'https://beacnpool.github.io/ABCDE';
function shareUrl(h) {
  const text = `${h.headline}  (on-chain, graded, verify it yourself 👇)`;
  const url = `${SITE}/r/${h.slug}.html`;
  return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
}
function renderHooks() {
  $('#hooks').innerHTML = HOOKS.map((h, i) => `
    <div class="hook">
      <div class="hook-top"><span class="hook-kicker">${esc(h.kicker)}</span>
        <span class="chip ${gradeClass(h.grade)}">${esc(h.grade)}</span></div>
      <h3 class="hook-h">${esc(h.headline)}</h3>
      <p class="hook-sub">${esc(h.sub)}</p>
      <div class="hook-actions">
        <button class="hook-verify" data-i="${i}">Verify it yourself →</button>
        <a class="hook-share" href="${shareUrl(h)}" target="_blank" rel="noopener" title="Share on X">↗ Share</a>
      </div>
    </div>`).join('');
  $$('#hooks .hook-verify').forEach(b => b.addEventListener('click', () => {
    const ask = HOOKS[+b.dataset.i].ask;
    navigator.clipboard.writeText(ask).catch(() => {});
    location.hash = '#start';
    b.textContent = 'Question copied — set up below, then paste ✓';
    setTimeout(() => { b.textContent = 'Verify it yourself →'; }, 2600);
  }));
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
  tiles.forEach(([n, l]) => { const t = el('div', 'stat'); t.append(el('div', 'n', n), el('div', 'l', l)); $('#stats').append(t); });
  $('#tipline').textContent = `Snapshot @ block ${fmtNum(s.tip_block)}, epoch ${s.tip_epoch} (${s.tip_time} UTC) · ${s.exact_35m} wallets holding exactly 35,000,000 ₳`;
  const tc = $('#tblcount'); if (tc) tc.textContent = s.tables;
  const ft = $('#foot-tip'); if (ft) ft.textContent = `Snapshot: block ${fmtNum(s.tip_block)} · epoch ${s.tip_epoch}`;
}

// ---------------- get started: pickers + command blocks ----------------
const REPO = 'https://github.com/BEACNpool/ABCDE.git';
function installStep(os) {
  if (os === 'win') return {
    title: 'Clone & set up (PowerShell)', lang: 'powershell',
    code: `git clone ${REPO}; cd ABCDE\npy -3 -m venv .venv; .\\.venv\\Scripts\\Activate.ps1\npy -3 -m pip install -r requirements/base.txt`,
  };
  return {
    title: 'Clone & set up', lang: 'bash',
    code: `git clone ${REPO} && cd ABCDE\npython3 -m venv .venv && source .venv/bin/activate\npip install -r requirements/base.txt`,
  };
}
function connectStep(model, os) {
  const win = os === 'win';
  if (model === 'code') {
    return win ? {
      title: 'Connect it to Claude Code', lang: 'powershell',
      code: `claude mcp add abcde-genesis -- "$($PWD.Path)\\.venv\\Scripts\\python.exe" "$($PWD.Path)\\mcp_server\\server.py"`,
    } : {
      title: 'Connect it to Claude Code', lang: 'bash',
      code: `claude mcp add abcde-genesis -- "$PWD/.venv/bin/python" "$PWD/mcp_server/server.py"`,
    };
  }
  if (model === 'codex') {
    return win ? {
      title: 'Connect it to Codex', lang: 'powershell',
      code: `if (!(Test-Path ~/.codex)) { New-Item -ItemType Directory ~/.codex | Out-Null }\n$p = $PWD.Path -replace '\\\\','/'\n@"\n\n[mcp_servers.abcde-genesis]\ncommand = "$p/.venv/Scripts/python.exe"\nargs = ["$p/mcp_server/server.py"]\n"@ | Add-Content ~/.codex/config.toml`,
    } : {
      title: 'Connect it to Codex', lang: 'bash',
      code: `mkdir -p ~/.codex && cat >> ~/.codex/config.toml <<EOF\n\n[mcp_servers.abcde-genesis]\ncommand = "$PWD/.venv/bin/python"\nargs = ["$PWD/mcp_server/server.py"]\nEOF`,
    };
  }
  // claude desktop — print the JSON to paste into the GUI config
  return win ? {
    title: 'Connect it to Claude Desktop', lang: 'powershell',
    note: 'This prints the config with your real path. Copy the JSON block it outputs into Claude Desktop → Settings → Developer → Edit Config, then restart Claude Desktop.',
    code: `$p = $PWD.Path -replace '\\\\','/'\n@"\n{\n  "mcpServers": {\n    "abcde-genesis": {\n      "command": "$p/.venv/Scripts/python.exe",\n      "args": ["$p/mcp_server/server.py"]\n    }\n  }\n}\n"@`,
  } : {
    title: 'Connect it to Claude Desktop', lang: 'bash',
    note: 'This prints the config with your real path. Copy the JSON it outputs into Claude Desktop → Settings → Developer → Edit Config, then restart Claude Desktop.',
    code: `cat <<EOF\n{\n  "mcpServers": {\n    "abcde-genesis": {\n      "command": "$PWD/.venv/bin/python",\n      "args": ["$PWD/mcp_server/server.py"]\n    }\n  }\n}\nEOF`,
  };
}
function runStep(model) {
  if (model === 'code') return { title: 'Start & ask', lang: 'bash', code: `claude`, note: 'Run this inside the ABCDE folder, then type your question — e.g. “Using abcde-genesis, where did EMURGO’s genesis ADA go?”' };
  if (model === 'codex') return { title: 'Start & ask', lang: 'bash', code: `codex`, note: 'Then ask your question. Codex loads the abcde-genesis tools from the config you just wrote.' };
  return { title: 'Start & ask', code: '', note: 'Restart Claude Desktop and open a new chat — the abcde-genesis tools are now available. Ask away.' };
}
function renderSteps() {
  const steps = [installStep(OS), connectStep(MODEL, OS), runStep(MODEL)];
  $('#steps-flow').innerHTML = steps.map((s, i) => `
    <div class="step-card">
      <div class="step-head"><span class="step-n">${i + 1}</span><h3>${s.title}</h3>
        ${s.code ? `<button class="copy-btn" data-i="${i}">Copy</button>` : ''}</div>
      ${s.code ? `<pre class="code-block"><code>${esc(s.code)}</code></pre>` : ''}
      ${s.note ? `<p class="step-note">${s.note}</p>` : ''}
    </div>`).join('');
  $$('#steps-flow .copy-btn').forEach(b => b.addEventListener('click', () => {
    navigator.clipboard.writeText(steps[+b.dataset.i].code).then(() => {
      b.textContent = 'Copied ✓'; setTimeout(() => b.textContent = 'Copy', 1400);
    });
  }));
}
function wirePickers() {
  $('#pick-model').addEventListener('click', e => { const p = e.target.closest('.pill'); if (!p) return; MODEL = p.dataset.v; setActive('#pick-model', p); renderSteps(); });
  $('#pick-os').addEventListener('click', e => { const p = e.target.closest('.pill'); if (!p) return; OS = p.dataset.v; setActive('#pick-os', p); renderSteps(); });
}
function setActive(sel, btn) { $$(sel + ' .pill').forEach(x => x.classList.remove('active')); btn.classList.add('active'); }

function renderAsk() {
  const ex = [
    'Using abcde-genesis, where did EMURGO’s genesis ADA end up — which pools and DReps does the trace reach?',
    'How much genesis-descended ADA sits with stake keys whose rewards were never withdrawn?',
    'Which DReps hold the most genesis-traced stake, and what is the evidence grade?',
  ];
  $('#ask-examples').innerHTML = ex.map(q => `<button class="ask-q">${esc(q)}</button>`).join('');
  $$('#ask-examples .ask-q').forEach(b => b.addEventListener('click', () => {
    navigator.clipboard.writeText(b.textContent).then(() => { b.classList.add('copied'); setTimeout(() => b.classList.remove('copied'), 1200); });
  }));
}

// ---------------- data map ----------------
function renderFamilies() {
  $('#families').innerHTML = FAMILIES.map(f => `
    <div class="fam">
      <div class="fam-top"><h3>${esc(f.family)}</h3><span class="fam-n">${f.table_count} tables</span></div>
      <div class="fam-rows">${fmtNum(f.total_rows)} rows</div>
      <div class="fam-tables">${f.tables.slice(0, 6).map(t => `<code>${esc(t.table)}</code>`).join(' ')}${f.tables.length > 6 ? ` <span class="muted">+${f.tables.length - 6} more</span>` : ''}</div>
    </div>`).join('');
}
function renderQuestions() {
  $('#questions').innerHTML = QUESTIONS.map(g => `
    <div class="q-group"><h4>${esc(g.theme)}</h4>
      ${g.qs.map(q => `<button class="q-item">${esc(q)}</button>`).join('')}</div>`).join('');
  $$('#questions .q-item').forEach(b => b.addEventListener('click', () => {
    navigator.clipboard.writeText(b.textContent).then(() => { b.classList.add('copied'); setTimeout(() => b.classList.remove('copied'), 1200); });
  }));
}

// ---------------- findings ----------------
function renderFindings(filter = '') {
  const q = filter.trim().toLowerCase();
  const list = FINDINGS.filter(f => !q || (f.id + f.title + f.claim + f.grade).toLowerCase().includes(q));
  $('#finds').innerHTML = list.map(f => {
    const g = (f.grade || '').split(',').pop().trim();
    return `<a class="find" href="${f.url}" target="_blank" rel="noopener">
      <div class="top"><span class="fid">${f.id}</span><span class="ft">${esc(f.title)}</span>
        <span class="chip ${gradeClass(f.grade)}">${esc(g)}</span></div>
      <p class="fc">${esc(f.claim || '')}</p></a>`;
  }).join('') || `<p class="muted">No findings match “${esc(filter)}”.</p>`;
}
$('#find-search')?.addEventListener('input', e => renderFindings(e.target.value));
