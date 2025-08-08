// Guide scaffolding: sidebar, prev/next, and page ToC
(async function(){
  const manifestUrl = 'manifest.json';
  const resp = await fetch(manifestUrl);
  const manifest = await resp.json();

  // Determine current page by filename
  const parts = location.pathname.split('/');
  const file = parts[parts.length - 1] || 'index.html';
  const currentIndex = manifest.findIndex(p => p.path === file);

  // Build sidebar
  const sidebar = document.getElementById('guideSidebar');
  if (sidebar) {
    const nav = document.createElement('nav');
    manifest.forEach((p, idx) => {
      const a = document.createElement('a');
      a.href = p.path;
      a.textContent = p.title;
      if (idx === currentIndex) a.classList.add('active');
      nav.appendChild(a);
    });
    sidebar.innerHTML = '<div class="section-title">Guide</div>';
    sidebar.appendChild(nav);

    // Page ToC
    const toc = document.createElement('div');
    toc.className = 'guide-toc';
    const h2s = document.querySelectorAll('.guide-content h2, .guide-content h3');
    if (h2s.length) {
      const title = document.createElement('div');
      title.className = 'section-title';
      title.textContent = 'On this page';
      toc.appendChild(title);
      h2s.forEach((h, i) => {
        if (!h.id) h.id = 's' + (i+1);
        const link = document.createElement('a');
        link.href = '#' + h.id;
        link.textContent = h.textContent;
        toc.appendChild(link);
      });
      sidebar.appendChild(toc);
    }
  }

  // Prev/Next
  const navWrap = document.getElementById('guideNav');
  if (navWrap) {
    navWrap.innerHTML = '';
    const prev = manifest[currentIndex - 1];
    const next = manifest[currentIndex + 1];
    const left = document.createElement('div');
    const right = document.createElement('div');
    if (prev) left.innerHTML = `<a class="btn" href="${prev.path}">← ${prev.title}</a>`;
    if (next) right.innerHTML = `<a class="btn" href="${next.path}">${next.title} →</a>`;
    navWrap.appendChild(left);
    navWrap.appendChild(right);
  }

  // Markdown loader: render md/<basename>.md into #mdHost
  const mdHost = document.getElementById('mdHost');
  if (mdHost && window.marked) {
    const base = file || 'index.html';
    const mdPath = 'md/' + base.replace('.html', '.md');
    try {
      const md = await fetch(mdPath).then(r => r.text());
      mdHost.innerHTML = window.marked.parse(md);
    } catch (e) {
      mdHost.innerHTML = '<p class="muted">This section is not yet available.</p>';
    }
  }
})();
