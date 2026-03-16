// ═══════════════════════════════════════
// CINEMATIC PAGE TRANSITION
// Three panels slam down on leave,
// content fades+slides in on arrive.
// ═══════════════════════════════════════

const overlay = document.getElementById('page-transition');

function buildPanels() {
  if (!overlay) return;
  overlay.innerHTML = '';
  for (let i = 0; i < 3; i++) {
    const p = document.createElement('div');
    p.className = 'pt-panel';
    overlay.appendChild(p);
  }
}

function transitionOut(href) {
  if (!overlay) { window.location.href = href; return; }
  overlay.classList.add('leaving');
  // Wait for panels to fully cover screen, then navigate
  setTimeout(() => { window.location.href = href; }, 680);
}

document.addEventListener('DOMContentLoaded', () => {
  buildPanels();

  // Intercept internal link clicks
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (!href
      || href.startsWith('#')
      || href.startsWith('http')
      || href.startsWith('mailto')
      || link.getAttribute('onclick')
      || link.getAttribute('target') === '_blank'
    ) return;

    link.addEventListener('click', e => {
      const target = link.getAttribute('href');
      if (!target || target.startsWith('#')) return;
      e.preventDefault();
      transitionOut(target);
    });
  });

  // Forms — transition out before submit
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      if (overlay) overlay.classList.add('leaving');
    });
  });

  // Init everything else
  initAlerts();
  initSearch();
  initFilters();
  initReveal();
  animateCounters();

  const typeEl = document.getElementById('hero-type');
  if (typeEl) {
    typeWriter(typeEl, [
      'Developer APIs',
      'REST Endpoints',
      'API Keys',
      'Webhooks',
      'Public APIs'
    ]);
  }
});


// ═══════════════════════════════════════
// COPY UTILITY
// ═══════════════════════════════════════
function copyText(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = '✓ Copied';
    btn.style.color = 'var(--green)';
    btn.style.borderColor = 'rgba(52,211,153,0.4)';
    setTimeout(() => {
      btn.textContent = orig;
      btn.style.color = '';
      btn.style.borderColor = '';
    }, 2000);
  });
}

function copyKey() {
  const el  = document.getElementById('key-value');
  const btn = document.getElementById('copy-key-btn');
  if (el && btn) copyText(el.textContent.trim(), btn);
}


// ═══════════════════════════════════════
// LIVE SEARCH
// ═══════════════════════════════════════
function initSearch() {
  const input   = document.getElementById('api-search');
  const cards   = document.querySelectorAll('.api-card-item');
  const countEl = document.getElementById('api-count');
  const emptyEl = document.getElementById('search-empty');
  if (!input || !cards.length) return;

  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    let visible = 0;
    cards.forEach(card => {
      const match = !q || card.textContent.toLowerCase().includes(q);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    if (countEl) countEl.textContent = `${visible} result${visible !== 1 ? 's' : ''}`;
    if (emptyEl) emptyEl.style.display = visible === 0 ? '' : 'none';
  });
}


// ═══════════════════════════════════════
// CATEGORY FILTER
// ═══════════════════════════════════════
function initFilters() {
  const tabs  = document.querySelectorAll('.filter-tab');
  const cards = document.querySelectorAll('.api-card-item');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const cat = tab.dataset.cat;
      cards.forEach(card => {
        card.style.display = (cat === 'all' || card.dataset.cat === cat) ? '' : 'none';
      });
    });
  });
}


// ═══════════════════════════════════════
// TYPING ANIMATION
// ═══════════════════════════════════════
function typeWriter(el, words, speed = 95, pause = 1600) {
  let wi = 0, ci = 0, deleting = false;
  function tick() {
    const word = words[wi];
    el.textContent = deleting
      ? word.substring(0, ci--)
      : word.substring(0, ci++);
    if (!deleting && ci > word.length) {
      deleting = true;
      setTimeout(tick, pause);
      return;
    }
    if (deleting && ci < 0) {
      deleting = false;
      wi = (wi + 1) % words.length;
      ci = 0;
    }
    setTimeout(tick, deleting ? speed / 2 : speed);
  }
  tick();
}


// ═══════════════════════════════════════
// AUTO-DISMISS ALERTS
// ═══════════════════════════════════════
function initAlerts() {
  document.querySelectorAll('.alert').forEach(a => {
    setTimeout(() => {
      a.style.transition = 'opacity 0.5s, transform 0.5s';
      a.style.opacity    = '0';
      a.style.transform  = 'translateY(-5px)';
      setTimeout(() => a.remove(), 500);
    }, 4000);
  });
}


// ═══════════════════════════════════════
// SCROLL REVEAL
// ═══════════════════════════════════════
function initReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity   = '1';
        entry.target.style.transform = 'translateY(0)';
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.reveal').forEach(el => {
    el.style.opacity    = '0';
    el.style.transform  = 'translateY(18px)';
    el.style.transition = 'opacity 0.6s cubic-bezier(0.16,1,0.3,1), transform 0.6s cubic-bezier(0.16,1,0.3,1)';
    obs.observe(el);
  });
}


// ═══════════════════════════════════════
// COUNTER ANIMATION
// ═══════════════════════════════════════
function animateCounters() {
  document.querySelectorAll('.stat-num[data-val]').forEach(el => {
    const target = parseInt(el.dataset.val) || 0;
    if (target === 0) { el.textContent = '0'; return; }
    let current = 0;
    const step  = Math.max(1, Math.ceil(target / 45));
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 28);
  });
}