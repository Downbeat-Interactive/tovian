// Guide scaffolding: sidebar, prev/next, and page ToC
(function(){
  window.addEventListener('DOMContentLoaded', async () => {
    try {
      const base = location.pathname.includes('/guide/') ? '' : 'guide/';
      const pages = await fetch(base + 'manifest.json').then(r => r.json());
      // Normalize current path to '/guide/<file>.html' regardless of site base
      const match = location.pathname.match(/\/guide\/[^?#]*/);
      const currentPath = match ? match[0] : location.pathname; // e.g., '/guide/verbs.html'

      // Sidebar
      const aside = document.getElementById('guideSidebar');
      if (aside && Array.isArray(pages)) {
        const nav = document.createElement('nav');
        pages.forEach(p => {
          const a = document.createElement('a');
          a.href = p.path; a.textContent = p.title;
          if (p.path === currentPath) a.classList.add('active');
          nav.appendChild(a);
        });
        aside.innerHTML = '<div class="section-title">Guide</div>';
        aside.appendChild(nav);

        // Page ToC
        const toc = document.createElement('div');
        toc.className = 'guide-toc';
        const headings = document.querySelectorAll('.guide-content h2, .guide-content h3');
        if (headings.length) {
          const title = document.createElement('div');
          title.className = 'section-title';
          title.textContent = 'On this page';
          toc.appendChild(title);
          headings.forEach((h, i) => {
            if (!h.id) h.id = 's' + (i+1);
            const link = document.createElement('a');
            link.href = '#' + h.id;
            link.textContent = h.textContent;
            toc.appendChild(link);
          });
          aside.appendChild(toc);
        }
      }

      // Prev/Next
      let idx = pages.findIndex(p => p.path === currentPath);
      if (idx === -1) {
        // Fallback: compare by filename only
        const file = currentPath.split('/').pop();
        idx = pages.findIndex(p => (p.path || '').endsWith('/' + file));
      }
      const prev = idx > 0 ? pages[idx - 1] : null;
      const next = idx >= 0 && idx < pages.length - 1 ? pages[idx + 1] : null;
      const navHost = document.getElementById('guideNav');
      if (navHost) {
        navHost.innerHTML = '';
        if (prev) {
          const a = document.createElement('a');
          a.className = 'btn'; a.href = prev.path; a.textContent = '← ' + prev.title;
          navHost.appendChild(a);
        }
        if (next) {
          const a = document.createElement('a');
          a.className = 'btn'; a.href = next.path; a.textContent = next.title + ' →';
          navHost.appendChild(a);
        }
      }
    } catch (e) {
      // silent
    }
  });
})();
