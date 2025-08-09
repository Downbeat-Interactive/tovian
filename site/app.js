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
  
    // Base prefix for path (from Eleventy pathPrefix)
    const BASE = (window.__BASE || '/');

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
      // Scroll reveal
      try {
        const startReveal = () => {
          const io = new IntersectionObserver((entries) => {
            entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } });
          }, { threshold: 0.05 });
          requestAnimationFrame(() => {
            document.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));
          });
        };
        if (document.fonts && document.fonts.ready) {
          document.fonts.ready.then(startReveal);
        } else {
          startReveal();
        }
      } catch {}
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
      if (!wrap) return; // No dictionary grid on this page
      wrap.innerHTML = '';
      list.slice(0, 400).forEach((e) => wrap.appendChild(renderCard(e.item || e)));
    }
  
    function buildTableIfNeeded() {
      if (state.tableLoaded) return;
      if (!window.CsvToTable) return;
      const csvtotable = new window.CsvToTable({ csvFile: 'dictionary.csv' });
      csvtotable.run();
      state.tableLoaded = true;
      setTimeout(() => {
        addRomanizationColumnToDictionary();
        applyIpaVisibilityToTable();
        makeGuideTablesSortable();
      }, 0);
    }

    // Apply IPA show/hide to dictionary table
    function applyIpaVisibilityToTable() {
      const table = document.getElementById('dictionaryTable');
      if (!table) return;
      const show = !!state.showIPA;
      const headers = Array.from(table.querySelectorAll('thead th'));
      const ipaIndex = headers.findIndex(th => /\bipa\b/i.test(th.textContent));
      if (ipaIndex !== -1) {
        headers[ipaIndex].style.display = show ? '' : 'none';
        const rows = table.tBodies?.[0]?.rows || [];
        Array.from(rows).forEach(row => {
          const cell = row.cells[ipaIndex];
          if (cell) cell.style.display = show ? '' : 'none';
        });
      }
    }

    // Build consonants table for Phonology page from ipa_map.csv
    async function buildPhonologyConsonants() {
      const host = document.getElementById('consonantsAuto');
      if (!host) return;
      try {
        const base = location.pathname.includes('/guide/') ? '../' : '';
        const mapCsv = await fetch(base + 'ipa_map.csv').then(r => r.text());
        const rows = mapCsv.split(/\r?\n/).filter(Boolean);
        const header = rows.shift();
        const map = rows.map(line => {
          const [g, ipa] = line.split(',');
          return { g: (g||'').trim(), ipa: (ipa||'').trim() };
        }).filter(x => x.g && x.ipa);
        // Find an example for each grapheme
        const example = {};
        state.entries.forEach(e => {
          const w = (e.tovian || '').toLowerCase();
          map.forEach(({g}) => {
            const needle = g.toLowerCase();
            if (!example[g] && w.replace(/['-]/g,'').includes(needle)) example[g] = e.tovian;
          });
        });
        const body = map.map(({g, ipa}) => `<tr><td>${g}</td><td class=\"tovian\">${g}</td><td>/${ipa}/</td><td>${example[g]||''}</td></tr>`).join('');
        host.innerHTML = `<table><thead><tr><th>Romanization</th><th>Tovian</th><th>IPA</th><th>Example</th></tr></thead><tbody>${body}</tbody></table>`;
      } catch (e) {}
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
      const base = (window.__BASE || '/');
      // Load favorites
      try {
        const raw = localStorage.getItem('favorites') || '[]';
        state.favorites = new Set(JSON.parse(raw));
      } catch {}
      // Dictionary
      const csvText = await fetch(base + 'dictionary.csv').then((r) => r.text());
      state.entries = parseCSV(csvText).filter((x) => x.english && x.tovian && !/\(obsolete\)/i.test(x.english));
      state.fuseDict = new Fuse(state.entries, { keys: ['english', 'tovian'], threshold: 0.3 });
      renderDictCards(state.entries.slice(0, 400));
      // Handle hash scrolling after dynamic content affects layout
      function scrollToHashIfAny() {
        if (!location.hash) return;
        const el = document.querySelector(location.hash);
        if (!el) return;
        const header = document.querySelector('.site-header');
        const offset = header ? header.getBoundingClientRect().height + 8 : 0;
        const top = el.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
      requestAnimationFrame(scrollToHashIfAny);
      setTimeout(scrollToHashIfAny, 250);
      window.addEventListener('hashchange', () => setTimeout(scrollToHashIfAny, 50));
  
      // Word of the Day (deterministic by date)
      const wotdHost = document.getElementById('wotd');
      if (wotdHost && state.entries.length) {
        const d = new Date();
        // ignore calendar/date-like entries for WOTD
        const months = ['january','february','march','april','may','june','july','august','september','october','november','december'];
        const seasons = ['spring','summer','autumn','winter'];
        const nonCalendar = state.entries.filter(e => {
          const en = (e.english || '').toLowerCase();
          if (/^\d+\s+of\s+(spring|summer|autumn|winter)$/.test(en)) return false;
          if (months.some(m => new RegExp('^'+m+'\\s+\\d+$').test(en))) return false;
          return true;
        });
        const pool = nonCalendar.length ? nonCalendar : state.entries;
        const seed = d.getFullYear() * 372 + (d.getMonth()+1) * 31 + d.getDate();
        const idx = seed % pool.length;
        const card = renderCard(pool[idx]);
        wotdHost.appendChild(card);
        // Also show today's named date if present (e.g., "January 20")
        try {
          const dateKey = `${months[d.getMonth()]} ${d.getDate()}`;
          const match = state.entries.find(e => e.english.toLowerCase() === dateKey);
          if (match) {
            const head = document.createElement('div');
            head.className = 'muted';
            head.textContent = 'Today in Tovian calendar:';
            wotdHost.appendChild(head);
            wotdHost.appendChild(renderCard(match));
          }
        } catch {}
        // CountUp dictionary stats
        const stat = document.getElementById('dictStats');
        if (stat) {
          stat.innerHTML = `Dictionary entries: <b id="dictCount">0</b>`;
          const target = document.getElementById('dictCount');
          countUp(target, state.entries.length, 800);
        }
        const badge = document.getElementById('dictBadge');
        if (badge) {
          badge.textContent = '0';
          countUp(badge, state.entries.length, 800);
        }
        // Chip with today label next to WOTD heading
        const chip = document.getElementById('wotdChip');
        if (chip) {
          try { chip.textContent = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }); } catch { chip.textContent = `${d.getMonth()+1}/${d.getDate()}`; }
        }
      }
  
      // Guide manifest → build list and include titles in search index
      let guideList = [];
      try {
        guideList = await fetch(base + 'guide/manifest.json').then((r) => r.json());
        const resolveGuideHref = (p) => {
          if (!p) return '';
          if (p.startsWith('/')) return (BASE + p.replace(/^\//, ''));
          // Ensure we always include '/guide/' from the site root when linking from home
          return (isGuide ? '' : (BASE + 'guide/')) + p;
        };
        // Home guide links
        const gl = document.getElementById('guideLinks');
        if (gl) {
          gl.innerHTML = '';
          guideList.forEach(p => {
            const a = document.createElement('a');
            const summary = p.summary || '';
            const ICONS = { 'overview':'📘', 'phonology':'🔤', 'nouns':'📦', 'pronouns':'🗣️', 'verbs':'⚙️', 'mood-voice':'🎛️', 'questions':'❓', 'adjectives':'🏷️', 'syntax':'🧭', 'introductions':'👋', 'memory-dreams':'💭', 'numbers':'🔢', 'calendar':'📅', 'examples':'🧪' };
            const icon = ICONS[p.id] || '📄';
            a.className = 'card';
            a.href = resolveGuideHref(p.path);
            a.innerHTML = `<h3><span style="margin-right:6px">${icon}</span>${p.title}</h3>${summary ? `<p class="muted">${summary}</p>` : ''}`;
            gl.appendChild(a);
          });
        }
      } catch (e) {}
  
      // Populate numbers/ordinals/months/dates if placeholders exist
      buildNumbersAndCalendar();
      // Build consonants table on Phonology page
      buildPhonologyConsonants();
      // Make any guide tables sortable (static + injected)
      makeGuideTablesSortable();

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
      function hideQuick() { if (quickOut) { quickOut.innerHTML = ''; quickOut.classList.remove('open'); } }
      function showQuick() { if (quickOut) quickOut.classList.add('open'); }
      quick?.addEventListener('input', () => {
        const q = quick.value.trim();
        if (!quickOut) return;
        quickOut.innerHTML = '';
        if (!q) { hideQuick(); return; }
        const hits = state.fuseAll.search(q).slice(0, 8);
        if (!hits.length) {
          quickOut.appendChild(el('<div class="muted">No results. Try another phrasing or check the guide.</div>'));
          showQuick();
          return;
        }
        hits.forEach((res) => {
          const { type, ref } = res.item;
          if (type === 'vocab') quickOut.appendChild(renderCard(ref));
          else {
            const ICONS = { 'overview':'📘', 'phonology':'🔤', 'nouns-cases':'📦', 'pronouns':'🗣️', 'verbs':'⚙️', 'mood-voice':'🎛️', 'questions':'❓', 'adjectives':'🏷️', 'syntax':'🧭', 'introductions':'👋', 'memory-dreams':'💭', 'numbers':'🔢', 'calendar':'📅', 'examples':'🧪' };
            const icon = ICONS[ref.id] || '📄';
            const href = ref.path && ref.path.startsWith('/') ? (BASE + ref.path.replace(/^\//, '')) : (isGuide ? '' : 'guide/') + (ref.path || '');
            quickOut.appendChild(el(`<div class="list-item"><a href="${href}"><b><span style="margin-right:6px">${icon}</span>${ref.title}</b></a></div>`));
          }
        });
        showQuick();
      });
      // Hide on click-away
      document.addEventListener('click', (e) => {
        const header = document.querySelector('.site-header');
        if (!header) return;
        if (!header.contains(e.target)) hideQuick();
      });
      // Hide on Escape
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideQuick(); });

      // (legacy hook removed) numbers/calendar now built generically

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
          renderDictCards(state.entries);
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
        toggleBtn.setAttribute('aria-pressed', nowHidden ? 'false' : 'true');
        cardsWrap.style.display = nowHidden ? '' : 'none';
        const more = document.getElementById('loadMoreBtn');
        if (more) more.style.display = nowHidden ? (state.cardsShown < (document.getElementById('dictSearch')?.value?.trim() ? state.fuseDict.search(document.getElementById('dictSearch').value.trim()).length : state.entries.length) ? '' : 'none') : 'none';
        if (!nowHidden) { buildTableIfNeeded(); const q = dictInput?.value?.trim() || ''; if (q) { const table = document.getElementById('dictionaryTable'); if (table) { const rows = table.tBodies?.[0]?.rows || []; const needle = q.toLowerCase(); Array.from(rows).forEach((row) => { const txt = Array.from(row.cells).map(c => c.textContent.toLowerCase()).join(' '); row.style.display = needle && !txt.includes(needle) ? 'none' : ''; }); } } setTimeout(applyIpaVisibilityToTable, 0); }
      });

      // Load more button
      document.getElementById('loadMoreBtn')?.addEventListener('click', () => {
        const q = document.getElementById('dictSearch')?.value?.trim();
        const list = q ? state.fuseDict.search(q) : state.entries;
        appendMoreCards(list);
      });
  
      // Favorites toggle
      const favBtn = document.getElementById('favoritesBtn');
      if (favBtn) {
        favBtn.setAttribute('aria-pressed', 'false');
        favBtn.addEventListener('click', () => {
          const pressed = favBtn.getAttribute('aria-pressed') === 'true';
          favBtn.setAttribute('aria-pressed', pressed ? 'false' : 'true');
          if (pressed) {
            const q = document.getElementById('dictSearch')?.value?.trim();
            if (!q) renderDictCards(state.entries.slice(0, 400));
            else renderDictCards(state.fuseDict.search(q));
          } else {
            const favs = state.entries.filter(e => state.favorites.has(`${e.tovian}__${e.english}`));
            renderDictCards(favs);
          }
        });
      }
  
      // IPA toggle
      const ipaBtn = document.getElementById('toggleIpaBtn');
      if (ipaBtn) ipaBtn.setAttribute('aria-pressed', state.showIPA ? 'true' : 'false');
      ipaBtn?.addEventListener('click', () => {
        state.showIPA = !state.showIPA;
        ipaBtn.setAttribute('aria-pressed', state.showIPA ? 'true' : 'false');
        const q = document.getElementById('dictSearch')?.value?.trim();
        if (!q) renderDictCards(state.entries.slice(0, 200));
        else renderDictCards(state.fuseDict.search(q));
        applyIpaVisibilityToTable();
      });
  
      // Ask
      const askInput = document.getElementById('askInput');
      const askOut = document.getElementById('askResults');
      function hideAsk(){ if (askOut){ askOut.innerHTML=''; askOut.classList.remove('open'); } }
      function showAsk(){ if (askOut){ askOut.classList.add('open'); } }
      askInput?.addEventListener('input', () => {
        const q = askInput.value.trim();
        if (!q) { hideAsk(); return; }
        const hits = state.fuseAll.search(q).slice(0, 12);
        askOut.innerHTML = '';
        if (!hits.length) { askOut.appendChild(el('<div class="muted">No results.</div>')); showAsk(); return; }
        hits.forEach(({item}) => {
          if (item.type === 'guide') {
            const ICONS = { 'overview':'📘', 'nouns-cases':'📦', 'pronouns':'🗣️', 'verbs':'⚙️', 'mood-voice':'🎛️', 'questions':'❓', 'adjectives':'🏷️', 'syntax':'🧭', 'introductions':'👋', 'memory-dreams':'💭', 'numbers':'🔢', 'calendar':'📅', 'examples':'🧪' };
            const icon = ICONS[item.ref.id] || '📄';
            const href = item.ref.path && item.ref.path.startsWith('/') ? (BASE + item.ref.path.replace(/^\//, '')) : (isGuide ? '' : 'guide/') + (item.ref.path || '');
            askOut.appendChild(el(`<div class="list-item"><a href="${href}"><b><span style="margin-right:6px">${icon}</span>${item.ref.title}</b></a></div>`));
          } else {
            askOut.appendChild(renderCard(item.ref));
          }
        });
        showAsk();
      });
      document.addEventListener('click', (e) => {
        const qa = document.querySelector('.qa');
        if (!qa) return;
        if (!qa.contains(e.target)) hideAsk();
      });
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideAsk(); });
  
      // Card actions (copy, star) across all contexts (dictionary, quick search, ask)
      document.addEventListener('click', async (ev) => {
        const btn = ev.target.closest('button.icon-btn');
        if (!btn) return;
        if (btn.classList.contains('copy')) {
          const to = btn.getAttribute('data-tovian');
          try { await navigator.clipboard.writeText(`${to||''}`); btn.textContent = 'Copied'; setTimeout(()=>btn.textContent='Copy', 900);} catch {}
          return;
        }
        if (btn.classList.contains('star')) {
          const key = btn.getAttribute('data-key');
          if (!key) return;
          if (state.favorites.has(key)) { state.favorites.delete(key); btn.classList.remove('active'); }
          else { state.favorites.add(key); btn.classList.add('active'); }
          localStorage.setItem('favorites', JSON.stringify([...state.favorites]));
          return;
        }
      });
    }

    // Simple CountUp
    function countUp(el, to, duration=600) {
      const start = performance.now();
      const from = 0;
      function tick(t) {
        const p = Math.min(1, (t - start) / duration);
        const eased = p < 0.5 ? 2*p*p : -1 + (4 - 2*p) * p; // easeInOutQuad
        const val = Math.floor(from + (to - from) * eased);
        el.textContent = val.toLocaleString();
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    // Insert Romanization column into dictionary table (after Tovian column)
    function addRomanizationColumnToDictionary() {
      const table = document.getElementById('dictionaryTable');
      if (!table) return;
      const theadRow = table.tHead?.rows?.[0];
      if (!theadRow) return;
      const headers = Array.from(theadRow.cells).map(th => th.textContent.trim().toLowerCase());
      const tovIdx = headers.indexOf('tovian');
      if (tovIdx === -1) return;
      if (headers.includes('romanization')) return; // already added
      const th = document.createElement('th');
      th.textContent = 'Romanization';
      th.style.cursor = 'pointer';
      th.addEventListener('click', () => sortArbitraryTable(table, tovIdx + 1));
      if (theadRow.cells.length > tovIdx + 1) theadRow.insertBefore(th, theadRow.cells[tovIdx + 1]);
      else theadRow.appendChild(th);
      const rows = table.tBodies?.[0]?.rows || [];
      Array.from(rows).forEach(row => {
        const td = document.createElement('td');
        td.textContent = row.cells[tovIdx]?.textContent || '';
        if (row.cells.length > tovIdx + 1) row.insertBefore(td, row.cells[tovIdx + 1]);
        else row.appendChild(td);
      });
    }

    // Generic sorter used by injected headers
    function sortArbitraryTable(table, colIndex) {
      const tbody = table.tBodies?.[0];
      if (!tbody) return;
      const rowsArray = Array.from(tbody.rows);
      const currentDir = table.getAttribute('data-sort-dir-' + colIndex) || 'asc';
      const dir = currentDir === 'asc' ? 'desc' : 'asc';
      table.setAttribute('data-sort-dir-' + colIndex, dir);
      rowsArray.sort((a, b) => {
        const x = (a.cells[colIndex]?.textContent || '').trim().toLowerCase();
        const y = (b.cells[colIndex]?.textContent || '').trim().toLowerCase();
        if (x < y) return dir === 'asc' ? -1 : 1;
        if (x > y) return dir === 'asc' ? 1 : -1;
        return 0;
      });
      tbody.innerHTML = '';
      rowsArray.forEach((r) => tbody.appendChild(r));
    }

    // Make all guide tables sortable (static and dynamically injected)
    function makeGuideTablesSortable() {
      const scope = document.querySelector('.guide-content') || document;
      const attach = (table) => {
        if (!table || table.__sortable) return;
        table.__sortable = true;
        const thead = table.tHead; if (!thead) return;
        Array.from(thead.rows[0].cells).forEach((th, idx) => {
          th.style.cursor = 'pointer';
          th.addEventListener('click', () => sortArbitraryTable(table, idx));
        });
      };
      scope.querySelectorAll('table').forEach(attach);
      const mo = new MutationObserver(() => {
        scope.querySelectorAll('table').forEach(attach);
      });
      mo.observe(scope, { childList: true, subtree: true });
    }

    // Build numbers/ordinals and calendar tables from dictionary.csv
    function buildNumbersAndCalendar() {
      const numsHost = document.getElementById('numbersAuto');
      const ordHost = document.getElementById('ordinalsAuto');
      const monthsHost = document.getElementById('monthsAuto');
      const datesHost = document.getElementById('datesAuto');
      if (!numsHost && !ordHost && !monthsHost && !datesHost) return;
      const months = ['january','february','march','april','may','june','july','august','september','october','november','december'];
      const parts = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety','hundred','thousand'];
      const ords = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth','sixteenth','seventeenth','eighteenth','nineteenth','twentieth'];
    const isNumberWord = (s) => {
      const w = s.toLowerCase();
      if (w.includes('of')) return false; // no spaces or irrelevant words
      if (/^\d+/.test(w)) return true;
      if (parts.some(p => w.split(/\s+/).includes(p))) return true; // match whole words only
      return false;
    };

    function tableFor(list, caption, sorter) {
      const rows = list
        .slice()
        .sort(sorter)
        .map(e => `<tr><td>${e.english}</td><td class="tovian">${e.tovian}</td><td>${e.tovian}</td><td class="ipa">${e.ipa}</td><td>${e.roots}</td></tr>`)
        .join('');
      return `<table><thead><tr><th>${caption}</th><th>Tovian</th><th>Romanization</th><th>IPA</th><th>Roots</th></tr></thead><tbody>${rows}</tbody></table>`;
    }
      const isOrdinalWord = (s) => ords.some(o=>s.toLowerCase().startsWith(o));
      const isMonthOnly = (s) => months.some(m => s.toLowerCase() === m);
      const isDateName = (s) => months.some(m => s.toLowerCase().startsWith(m + ' '));
      const nums = state.entries.filter(e => isNumberWord(e.english) && !isOrdinalWord(e.english));
      const ordList = state.entries.filter(e => isOrdinalWord(e.english));
      const mons = state.entries.filter(e => isMonthOnly(e.english));
      const dates = state.entries.filter(e => isDateName(e.english));

      function monthSorter(a, b) {
        const ma = months.findIndex(m => a.english.toLowerCase() === m);
        const mb = months.findIndex(m => b.english.toLowerCase() === m);
        return ma - mb;
      }
      function dateSorter(a, b) {
        const getDay = (s) => {
          const m = s.toLowerCase().split(' ')[0];
          const d = s.toLowerCase().split(' ')[1];
          const monthIdx = months.findIndex(mm => mm === m);
          let dayNum = 0;
          if (d) {
            const parts = d.split(/[^a-z0-9]+/).filter(Boolean);
            if (parts.length) {
              const first = parts[0];
              if (/^\d+$/.test(first)) dayNum = parseInt(first, 10);
              else {
                const ordIdx = ords.findIndex(o => first.startsWith(o));
                if (ordIdx !== -1) dayNum = ordIdx + 1;
              }
            }
          }
          return monthIdx * 31 + (dayNum || 0); // rough ordering
        };
        return getDay(a.english) - getDay(b.english);
      }
      function numberSorter(a, b) {
        const aNum = parseInt(a.english.split(/\s+/)[0], 10);
        const bNum = parseInt(b.english.split(/\s+/)[0], 10);
        if (!isNaN(aNum) && !isNaN(bNum)) return aNum - bNum;
        if (!isNaN(aNum)) return -1;
        if (!isNaN(bNum)) return 1;
        return a.english.localeCompare(b.english);
      }
      function tableFor(list, caption, sorter) {
        const rows = list
          .slice()
          .sort(sorter)
          .map(e => `<tr><td>${e.english}</td><td class="tovian">${e.tovian}</td><td>${e.tovian}</td><td class="ipa">${e.ipa}</td><td>${e.roots}</td></tr>`)
          .join('');
        return `<table><thead><tr><th>${caption}</th><th>Tovian</th><th>Romanization</th><th>IPA</th><th>Roots</th></tr></thead><tbody>${rows}</tbody></table>`;
      }
      if (numsHost) numsHost.innerHTML = tableFor(nums, 'Number (EN)', numberSorter);
      if (ordHost) ordHost.innerHTML = tableFor(ordList, 'Ordinal (EN)', numberSorter);
      if (monthsHost) monthsHost.innerHTML = tableFor(mons, 'Month', monthSorter);
      if (datesHost) datesHost.innerHTML = tableFor(dates, 'Named Date', dateSorter);
    }

    window.addEventListener('DOMContentLoaded', init);
  })();
  
