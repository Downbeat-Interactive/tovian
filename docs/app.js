// Minimal, modular client logic for the Tovian site

(function () {
  const state = {
    entries: [], // {english, tovian, ipa, roots}
    fuseDict: null,
    highlights: [], // {id, title, summary, examples: [{tovian, english}]}
    fuseAll: null, // combined for Ask
    tableLoaded: false,
    favorites: new Set(),
    showIPA: true,
  };

  // Theme toggle
  const body = document.documentElement;
  function applyTheme(initial) {
    const saved = localStorage.getItem('theme');
    const theme = saved || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    if (theme === 'light') body.classList.add('light'); else body.classList.remove('light');
    if (!initial) localStorage.setItem('theme', theme);
  }
  applyTheme(true);
  window.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('themeToggle');
    toggle?.addEventListener('click', () => {
      const isLight = body.classList.toggle('light');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
  });

  // CSV parsing (simple, for clean CSV)
  function parseCSV(text) {
    const lines = text.split(/\r?\n/).filter(Boolean);
    const rows = lines.map((l) => l.split(','));
    const [header, ...data] = rows;
    const [englishKey, tovianKey, ipaKey, rootsKey] = header;
    return data.map((r) => ({
      english: (r[0] || '').trim(),
      tovian: (r[1] || '').trim(),
      ipa: (r[2] || '').trim(),
      roots: (r[3] || '').trim(),
    }));
  }

  // Render helpers
  function el(html) {
    const div = document.createElement('div');
    div.innerHTML = html.trim();
    return div.firstChild;
  }

  function renderCard(entry) {
    const { english, tovian, ipa, roots } = entry;
    const key = `${tovian}__${english}`;
    const isFav = state.favorites.has(key);
    return el(`
      <div class="card entry">
        <div class="title">${tovian || '<span class="muted">—</span>'} <span class="chip">${english || ''}</span></div>
        <div class="tovian">${tovian || ''}</div>
        ${state.showIPA && ipa ? `<div class="ipa">${ipa}</div>` : ''}
        ${roots ? `<div class="root">${roots}</div>` : ''}
        <div class="entry-actions">
          <button class="icon-btn copy" data-key="${key}" data-tovian="${tovian}" data-english="${english}">Copy</button>
          <button class="icon-btn star ${isFav ? 'active' : ''}" data-key="${key}">★</button>
        </div>
      </div>
    `);
  }

  function renderDictCards(list) {
    const wrap = document.getElementById('dictCards');
    wrap.innerHTML = '';
    list.slice(0, 400).forEach((e) => wrap.appendChild(renderCard(e.item || e)));
  }

  function buildTableIfNeeded() {
    if (state.tableLoaded) return;
    if (!window.CsvToTable) return;
    const csvtotable = new window.CsvToTable({ csvFile: 'dictionary.csv' });
    csvtotable.run();
    state.tableLoaded = true;
  }

  // Sorting for the legacy table view (CsvToTable headers call sortTable)
  window.sortTable = function (n) {
    const table = document.getElementById('dictionaryTable');
    if (!table) return;
    const tbody = table.tBodies[0];
    const rowsArray = Array.from(tbody.rows);
    const isNumeric = rowsArray.every((row) => !isNaN(row.cells[n].textContent.trim()));
    const currentDir = table.getAttribute('data-sort-dir-' + n) || 'asc';
    const dir = currentDir === 'asc' ? 'desc' : 'asc';
    table.setAttribute('data-sort-dir-' + n, dir);
    rowsArray.sort((a, b) => {
      const x = a.cells[n].textContent.trim();
      const y = b.cells[n].textContent.trim();
      const xv = isNumeric ? parseFloat(x) : x.toLowerCase();
      const yv = isNumeric ? parseFloat(y) : y.toLowerCase();
      if (xv < yv) return dir === 'asc' ? -1 : 1;
      if (xv > yv) return dir === 'asc' ? 1 : -1;
      return 0;
    });
    tbody.innerHTML = '';
    rowsArray.forEach((r) => tbody.appendChild(r));
  };

  // (Highlights removed) — combined search will index guide titles + dictionary

  // Load data and wire events
  async function init() {
    const isGuide = location.pathname.includes('/guide/');
    const base = isGuide ? '../' : '';
    // Load favorites
    try {
      const raw = localStorage.getItem('favorites') || '[]';
      state.favorites = new Set(JSON.parse(raw));
    } catch {}
    // Dictionary
    const csvText = await fetch(base + 'dictionary.csv').then((r) => r.text());
    state.entries = parseCSV(csvText).filter((x) => x.english && x.tovian);
    state.fuseDict = new Fuse(state.entries, { keys: ['english', 'tovian'], threshold: 0.3 });
    renderDictCards(state.entries.slice(0, 120));

    // Word of the Day (deterministic by date)
    const wotdHost = document.getElementById('wotd');
    if (wotdHost && state.entries.length) {
      const d = new Date();
      const seed = d.getFullYear() * 372 + (d.getMonth()+1) * 31 + d.getDate();
      const idx = seed % state.entries.length;
      const card = renderCard(state.entries[idx]);
      wotdHost.appendChild(card);
    }

    // Guide manifest → build list and include titles in search index
    let guideList = [];
    try {
      guideList = await fetch(base + 'guide/manifest.json').then((r) => r.json());
      // Home guide links
      const gl = document.getElementById('guideLinks');
      if (gl) {
        gl.innerHTML = '';
        guideList.forEach(p => {
          const a = document.createElement('a');
          const summary = p.summary || '';
          a.className = 'card'; a.href = `${isGuide ? '' : 'guide/'}${p.path}`; a.innerHTML = `<h3>${p.title}</h3>${summary ? `<p class="muted">${summary}</p>` : ''}`;
          gl.appendChild(a);
        });
      }
    } catch (e) {}

    // Combined search index: vocab + guide titles
    function expandEnglishVariants(phrase) {
      const tokens = phrase.split(/\s+/).filter(Boolean);
      const forms = new Set();
      tokens.forEach((t) => {
        const lower = t.toLowerCase();
        forms.add(lower);
        // simple stemming variants
        if (lower.endsWith('ing')) { forms.add(lower.slice(0, -3)); forms.add(lower.slice(0, -3) + 'e'); forms.add('to ' + lower.slice(0, -3)); }
        if (lower.endsWith('ed')) { forms.add(lower.slice(0, -2)); forms.add(lower.slice(0, -1)); }
        if (lower.endsWith('es')) { forms.add(lower.slice(0, -2)); }
        if (lower.endsWith('s')) { forms.add(lower.slice(0, -1)); }
        if (lower.startsWith('to ')) { forms.add(lower.replace(/^to\s+/, '')); }
      });
      return [...forms].join(' ');
    }
    const vocabDocs = state.entries.map((e) => ({
      type: 'vocab',
      ref: e,
      text: `${e.english} ${expandEnglishVariants(e.english)} ${e.tovian} ${e.roots} ${e.ipa}`
    }));
    const guideDocs = (guideList || []).map((g) => ({ type: 'guide', ref: g, text: `${g.title}` }));
    const all = [...vocabDocs, ...guideDocs];
    state.fuseAll = new Fuse(all, { keys: ['text'], threshold: 0.35, includeScore: true });

    // Quick search (hero) — search combined grammar + vocab
    const quick = document.getElementById('quickSearch');
    const quickOut = document.getElementById('quickResults');
    quick?.addEventListener('input', () => {
      const q = quick.value.trim();
      quickOut.innerHTML = '';
      if (!q) return;
      const hits = state.fuseAll.search(q).slice(0, 8);
      if (!hits.length) {
        quickOut.appendChild(el('<div class="muted">No results. Try another phrasing or check the guide.</div>'));
        return;
      }
      hits.forEach((res) => {
        const { type, ref } = res.item;
        if (type === 'vocab') quickOut.appendChild(renderCard(ref));
        else quickOut.appendChild(el(`<div class="list-item"><a href="${isGuide ? '' : 'guide/'}${ref.path}"><b>${ref.title}</b></a></div>`));
      });
    });

    // Dictionary filter
    const dictInput = document.getElementById('dictSearch');
    function filterTable(q) {
      const table = document.getElementById('dictionaryTable');
      if (!table) return;
      const rows = table.tBodies?.[0]?.rows || [];
      const needle = q.toLowerCase();
      Array.from(rows).forEach((row) => {
        const txt = Array.from(row.cells).map(c => c.textContent.toLowerCase()).join(' ');
        row.style.display = needle && !txt.includes(needle) ? 'none' : '';
      });
    }
    dictInput?.addEventListener('input', () => {
      const q = dictInput.value.trim();
      if (!q) {
        renderDictCards(state.entries.slice(0, 200));
        filterTable('');
        return;
      }
      const hits = state.fuseDict.search(q);
      renderDictCards(hits);
      filterTable(q);
    });

    // Toggle table (hide other view)
    const toggleBtn = document.getElementById('toggleTableBtn');
    const tableWrap = document.getElementById('tableWrap');
    const cardsWrap = document.getElementById('dictCards');
    toggleBtn?.addEventListener('click', () => {
      const nowHidden = tableWrap.classList.toggle('hidden');
      cardsWrap.style.display = nowHidden ? '' : 'none';
      if (!nowHidden) { buildTableIfNeeded(); const q = dictInput?.value?.trim() || ''; if (q) { const table = document.getElementById('dictionaryTable'); if (table) { const rows = table.tBodies?.[0]?.rows || []; const needle = q.toLowerCase(); Array.from(rows).forEach((row) => { const txt = Array.from(row.cells).map(c => c.textContent.toLowerCase()).join(' '); row.style.display = needle && !txt.includes(needle) ? 'none' : ''; }); } } }
    });

    // Favorites filter
    document.getElementById('favoritesBtn')?.addEventListener('click', () => {
      const favs = state.entries.filter(e => state.favorites.has(`${e.tovian}__${e.english}`));
      renderDictCards(favs);
    });

    // IPA toggle
    document.getElementById('toggleIpaBtn')?.addEventListener('click', () => {
      state.showIPA = !state.showIPA;
      const q = document.getElementById('dictSearch')?.value?.trim();
      if (!q) renderDictCards(state.entries.slice(0, 200));
      else renderDictCards(state.fuseDict.search(q));
    });

    // Ask
    const askInput = document.getElementById('askInput');
    askInput?.addEventListener('input', () => {
      const q = askInput.value.trim();
      if (!q) { document.getElementById('askResults').innerHTML = ''; return; }
      const hits = state.fuseAll.search(q).slice(0, 12);
      const out = document.getElementById('askResults');
      out.innerHTML = '';
      if (!hits.length) { out.appendChild(el('<div class="muted">No results.</div>')); return; }
      hits.forEach(({item}) => {
        if (item.type === 'guide') out.appendChild(el(`<div class="list-item"><a href="${isGuide ? '' : 'guide/'}${item.ref.path}"><b>${item.ref.title}</b></a></div>`));
        else out.appendChild(renderCard(item.ref));
      });
    });

    // Card actions (copy, star)
    document.getElementById('dictCards')?.addEventListener('click', async (ev) => {
      const t = ev.target;
      if (t.classList.contains('copy')) {
        const en = t.getAttribute('data-english');
        const to = t.getAttribute('data-tovian');
        try { await navigator.clipboard.writeText(`${to}`); t.textContent = 'Copied'; setTimeout(()=>t.textContent='Copy', 900);} catch {}
      }
      if (t.classList.contains('star')) {
        const key = t.getAttribute('data-key');
        if (state.favorites.has(key)) { state.favorites.delete(key); t.classList.remove('active'); }
        else { state.favorites.add(key); t.classList.add('active'); }
        localStorage.setItem('favorites', JSON.stringify([...state.favorites]));
      }
    });
  }

  window.addEventListener('DOMContentLoaded', init);
})();
