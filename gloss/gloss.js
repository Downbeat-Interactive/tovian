// Simple glosser and draft translator using the site dictionary
(function(){
  const BASE = (window.__BASE || '/');

  function el(html){ const d=document.createElement('div'); d.innerHTML=html.trim(); return d.firstChild; }

  function tokenizeTovian(text){
    // Keep letters, apostrophes, hyphens; split on whitespace/punct but keep tokens
    const raw = text.split(/\s+/).filter(Boolean);
    const tokens = [];
    raw.forEach(r => {
      const parts = r.match(/[A-Za-z’'\-]+|[^A-Za-z’'\-]+/g) || [r];
      parts.forEach(p => { if (/^[A-Za-z’'\-]+$/.test(p)) tokens.push(p); });
    });
    return tokens;
  }

  function normalizeTovian(s){ return (s || '').toLowerCase().replace(/[’']/g, "'"); }
  function normalizeEnglish(s){ return (s || '').toLowerCase(); }

  async function loadDict(){
    const csv = await fetch(BASE + 'dictionary.csv').then(r=>r.text());
    const lines = csv.split(/\r?\n/).filter(Boolean);
    const [header, ...rows] = lines;
    return rows.map(l => {
      const [en, to, ipa, roots] = l.split(',');
      return { english:(en||'').trim(), tovian:(to||'').trim(), ipa:(ipa||'').trim(), roots:(roots||'').trim() };
    }).filter(e => e.english && e.tovian && !/\(obsolete\)/i.test(e.english));
  }

  function bestMatchToken(dict, token){
    const t = normalizeTovian(token);
    // exact match by Tovian
    let hit = dict.find(e => normalizeTovian(e.tovian) === t);
    if (hit) return hit;
    // try stripping hyphens/apostrophes
    const t2 = t.replace(/[-']/g,'');
    hit = dict.find(e => normalizeTovian(e.tovian).replace(/[-']/g,'') === t2);
    if (hit) return hit;
    // try startsWith for compounds
    hit = dict.find(e => t.startsWith(normalizeTovian(e.tovian)));
    return hit || null;
  }

  function glossTable(tokens, rows){
    const head = `<thead><tr><th>Token</th><th>Segments</th><th>Gloss</th><th>IPA</th><th>Roots</th></tr></thead>`;
    const body = tokens.map(tok => {
      const segs = tok.split('-');
      const parts = segs.map(s => ({ s, m: bestMatchToken(rows, s) }));
      if (parts.length > 1) {
        const segText = parts.map(p => `<span class="tovian">${p.s}</span>`).join('‑');
        const gloss = parts.map(p => p.m ? p.m.english : '(?)').join(' + ');
        const ipa = parts.map(p => p.m ? p.m.ipa : '').filter(Boolean).join(' ');
        const roots = parts.map(p => p.m ? p.m.roots : '').filter(Boolean).join(' | ');
        return `<tr><td>${tok}</td><td>${segText}</td><td>${gloss}</td><td>${ipa}</td><td>${roots}</td></tr>`;
      }
      const m = bestMatchToken(rows, tok);
      if (!m) return `<tr><td>${tok}</td><td class="muted" colspan="4">(no match)</td></tr>`;
      return `<tr><td>${tok}</td><td class="tovian">${m.tovian}</td><td>${m.english}</td><td>${m.ipa}</td><td>${m.roots}</td></tr>`;
    }).join('');
    return `<table>${head}<tbody>${body}</tbody></table>`;
  }

  function choosePersonSuffix(words){
    const w0 = (words[0]||'').toLowerCase();
    if (w0 === 'i' || w0 === 'we') return 'i'; // 1st
    if (w0 === 'you') return 'o'; // 2nd
    return 'a'; // 3rd default
  }

  function buildCaseObject(rows, tokens){
    // Simple PP detection with determiners: in/at/with/for/from/to/towards/together with
    // Returns { phrase, consumed } where phrase is the Tovian case-marked object and consumed is indices removed
    const lower = tokens.map(t => t.toLowerCase());
    const detWords = new Set(['the','a','an']);
    const caseMap = {
      'in': 'ti-', 'at': 'ti-', 'on': 'ti-',
      'with': 'si-', 'by': 'si-',
      'for': 'lhu-',
      'from': 'di-', 'away': 'di-',
      'to': 'su-', 'towards': 'su-',
      'together': 'yi-'
    };
    for (let i=0; i<lower.length; i++) {
      const w = lower[i];
      if (w in caseMap || caseMap[w]) {
        let j = i + 1;
        if (detWords.has(lower[j])) j++;
        const head = tokens[j];
        if (!head) continue;
        // Lookup noun
        const norm = normalizeEnglish(head.replace(/[.,!?;:]+$/,''));
        let hit = rows.find(e => normalizeEnglish(e.english) === norm);
        if (!hit) hit = rows.find(e => normalizeEnglish(e.english).startsWith(norm));
        if (!hit) continue;
        // Build: definiteness 'a-' or 'o-' for non-subject
        const def = (j-1 >= 0 && detWords.has(lower[j-1]) && lower[j-1] === 'a') ? 'o-' : 'a-';
        const casePref = caseMap[w] || 'ti-';
        const noun = hit.tovian; // includes class prefix
        const phrase = `${def}${casePref}${noun}`;
        // consumed indices: i, (i+1 if det), j
        const consumed = new Set([i]);
        if (detWords.has(lower[i+1])) consumed.add(i+1);
        consumed.add(j);
        return { phrase, consumed };
      }
    }
    return null;
  }

  function draftTranslateENtoTovian(rows, text){
    const words = text.split(/\s+/).filter(Boolean);
    const out = [];
    // Determine tense from English hints
    const joined = words.join(' ').toLowerCase();
    let aux = 'fa';
    if (/\b(will|tomorrow)\b/.test(joined)) aux = 'fo';
    else if (/(ed\b|yesterday|ago)\b/.test(joined)) aux = 'fe';
    // Determine person suffix for main verb (heuristic)
    const first = (words[0]||'').toLowerCase();
    let personSuf = 'a'; // default aligns with example; adjust per grammar
    if (first === 'you') personSuf = 'o';
    const subjPron = first === 'i' ? 'na' : (first === 'you' ? 'wa' : '');
    // Map words to Tovian and mark verbs
    const verbSet = new Set(['see','speak','go','walk','be','have','do','eat','sleep','love','know','want','give','take','come','make','say','think','hear','look']);
    const mapped = words.map(w => {
      const raw = w.replace(/[.,!?;:]+$/,'');
      const norm = normalizeEnglish(raw);
      let hit = rows.find(e => normalizeEnglish(e.english) === norm);
      if (!hit) hit = rows.find(e => normalizeEnglish(e.english).startsWith(norm));
      const isVerb = !!(hit && verbSet.has(normalizeEnglish(hit.english).split(/\s+/)[0]));
      return { en: raw, to: hit ? hit.tovian : raw, ipa: hit ? hit.ipa : '', isVerb };
    });
    // Case-marked object phrase detection
    const cpp = buildCaseObject(rows, words);
    // Find first verb and move AUX+VERB to sentence end (SOV)
    const vi = mapped.findIndex(m => m.isVerb);
    if (vi !== -1) {
      const verb = mapped[vi];
      // person suffix on main verb
      let main = verb.to + (personSuf || '');
      main = main.replace(/([aeiou])\1+$/,'$1');
      const pre = mapped.slice(0, vi);
      const post = mapped.slice(vi + 1);
      // Remove consumed tokens from rest if any
      let rest = [...pre, ...post].map(m => m.to).filter(Boolean);
      if (cpp && cpp.consumed) {
        // Remove consumed tokens by original word indices: rebuild rest from words
        rest = words
          .map((w, idx) => ({ idx, w }))
          .filter(x => !cpp.consumed.has(x.idx) && x.idx !== vi)
          .map(x => {
            const raw = x.w.replace(/[.,!?;:]+$/,'');
            const norm = normalizeEnglish(raw);
            let hit = rows.find(e => normalizeEnglish(e.english) === norm);
            if (!hit) hit = rows.find(e => normalizeEnglish(e.english).startsWith(norm));
            return hit ? hit.tovian : raw;
          });
      }
      const parts = [];
      if (subjPron) parts.push(subjPron);
      if (cpp && cpp.phrase) parts.push(cpp.phrase);
      parts.push(aux, main);
      return parts.filter(Boolean).join(' ');
    }
    // Fallback: just prefix aux
    return [subjPron, aux, ...mapped.map(m => m.to)].filter(Boolean).join(' ');
  }

  window.addEventListener('DOMContentLoaded', async () => {
    let dict = [];
    try { dict = await loadDict(); } catch {}
    const glossIn = document.getElementById('glossInput');
    const glossBtn = document.getElementById('glossBtn');
    const glossOut = document.getElementById('glossOut');
    const clearGloss = document.getElementById('clearGloss');
    const tranIn = document.getElementById('tranInput');
    const tranBtn = document.getElementById('tranBtn');
    const tranOut = document.getElementById('tranOut');
    const clearTran = document.getElementById('clearTran');

    glossBtn?.addEventListener('click', () => {
      const text = (glossIn?.value || '').trim();
      if (!text) { glossOut.innerHTML = ''; return; }
      const tokens = tokenizeTovian(text);
      glossOut.innerHTML = glossTable(tokens, dict);
    });
    clearGloss?.addEventListener('click', () => { if (glossIn) glossIn.value=''; glossOut.innerHTML=''; });

    tranBtn?.addEventListener('click', () => {
      const text = (tranIn?.value || '').trim();
      if (!text) { tranOut.innerHTML = ''; return; }
      const draft = draftTranslateENtoTovian(dict, text);
      tranOut.innerHTML = '';
      // Line 1: Tovian (with .tovian)
      tranOut.appendChild(el(`<div class="card"><div class="tovian" style="font-size:22px">${draft}</div></div>`));
      // Line 2: Romanization (same text, no .tovian)
      tranOut.appendChild(el(`<div class="card"><div style="font-size:18px">${draft}</div></div>`));
      // Line 3: IPA (best-effort per-token)
      const ipa = draft.split(/\s+/).map(tok => {
        const m = bestMatchToken(dict, tok);
        return m && m.ipa ? m.ipa.replace(/\s+/g, '') : tok;
      }).join(' ');
      tranOut.appendChild(el(`<div class="card"><div class="ipa" style="font-size:14px">${ipa}</div></div>`));
    });
    clearTran?.addEventListener('click', () => { if (tranIn) tranIn.value=''; tranOut.innerHTML=''; });
  });
})();
