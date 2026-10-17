/* ============================================================
   НЕФК translate.js v4 — Clean DOM-scan UA↔EN
   ============================================================ */

const LANG_KEY = 'nemk-lang';
let _lang = localStorage.getItem(LANG_KEY) || 'uk';
let _busy = false;

const SKIP_TAGS = new Set([
  'SCRIPT','STYLE','TEXTAREA','CODE','PRE','NOSCRIPT','SVG','MATH','CANVAS','INPUT'
]);

/* ── Init ─────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  _injectStyles();
  _syncBtns(_lang);
  if (_lang === 'en') {
    _fetchPairs('en').then(p => { _walk(p); _syncBtns('en'); }).catch(() => {});
  }
});

/* ── Public toggle ────────────────────────────────────────────── */
function toggleLang() {
  if (_busy) return;
  _run(_lang === 'uk' ? 'en' : 'uk');
}

/* ── Main ─────────────────────────────────────────────────────── */
async function _run(lang) {
  _busy = true;
  _animBtns();
  _ripple();
  try {
    const pairs = await _fetchPairs(lang);
    await _fade(true);
    _walk(pairs);
    _lang = lang;
    localStorage.setItem(LANG_KEY, lang);
    await _fade(false);
    _syncBtns(lang);
    _toast(lang);
  } catch(e) {
    console.error('[translate]', e);
    await _fade(false);
  } finally { _busy = false; }
}

/* ── AJAX ─────────────────────────────────────────────────────── */
async function _fetchPairs(lang) {
  const r = await fetch(`/api/translate/?lang=${lang}`, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return (await r.json()).pairs || [];
}

/* ── DOM walk ─────────────────────────────────────────────────── */
function _walk(pairs) {
  if (!pairs.length) return;

  function node(n) {
    if (n.nodeType === 3) {           // text node
      let t = n.textContent;
      if (!t.trim()) return;
      let ok = false;
      for (const [f, to] of pairs) {
        if (t.includes(f)) { t = t.split(f).join(to); ok = true; }
      }
      if (ok) {
        n.textContent = t;
        _flash(n.parentElement);
      }
      return;
    }
    if (n.nodeType !== 1) return;
    if (SKIP_TAGS.has(n.tagName)) return;
    // attrs
    for (const a of ['placeholder','title','aria-label','alt']) {
      const v = n.getAttribute(a);
      if (!v) continue;
      let nv = v;
      for (const [f, to] of pairs) nv = nv.split(f).join(to);
      if (nv !== v) n.setAttribute(a, nv);
    }
    n.childNodes.forEach(node);
  }
  node(document.body);
}

/* ── Flash on changed element ─────────────────────────────────── */
function _flash(el) {
  if (!el || !el.classList) return;
  el.classList.remove('_tl_f');
  void el.offsetWidth;
  el.classList.add('_tl_f');
  setTimeout(() => el.classList.remove('_tl_f'), 500);
}

/* ── Fade main content ────────────────────────────────────────── */
function _fade(on) {
  return new Promise(res => {
    const m = document.querySelector('main') || document.body;
    m.style.transition = 'opacity .2s, filter .2s';
    m.style.opacity = on ? '0.08' : '1';
    m.style.filter  = on ? 'blur(2px)' : 'blur(0)';
    setTimeout(() => { if (!on) { m.style.transition = m.style.opacity = m.style.filter = ''; } res(); }, 220);
  });
}

/* ── Sync all lang buttons ────────────────────────────────────── */
function _syncBtns(lang) {
  const label = lang === 'en' ? 'UA' : 'EN';
  const flag  = lang === 'en' ? '🇺🇦' : '🇬🇧';
  document.querySelectorAll('.lang-toggle-btn').forEach(btn => {
    const sp = btn.querySelector('.lang-btn-label');
    if (sp) sp.textContent = label;
    const fl = btn.querySelector('.lang-btn-flag');
    if (fl) fl.textContent = flag;
    btn.classList.toggle('_lang-active', lang === 'en');
    btn.setAttribute('title', lang === 'en' ? 'Switch to Ukrainian' : 'Switch to English');
  });
}

/* ── Button spin animation ────────────────────────────────────── */
function _animBtns() {
  document.querySelectorAll('.lang-toggle-btn').forEach(b => {
    b.style.animation = 'none'; void b.offsetWidth;
    b.style.animation = '_tl_spin .45s cubic-bezier(.34,1.56,.64,1)';
    setTimeout(() => b.style.animation = '', 500);
  });
}

/* ── Ripple effect from button ────────────────────────────────── */
function _ripple() {
  const btn = document.querySelector('.lang-toggle-btn');
  let x = window.innerWidth / 2, y = 60;
  if (btn) { const r = btn.getBoundingClientRect(); x = r.left + r.width/2; y = r.top + r.height/2; }
  const d = document.createElement('div');
  d.style.cssText = `
    position:fixed;left:${x}px;top:${y}px;
    width:8px;height:8px;border-radius:50%;
    background:rgba(37,99,235,.2);
    pointer-events:none;z-index:99990;
    transform:translate(-50%,-50%);
    animation:_tl_ripple .7s ease forwards;
  `;
  document.body.appendChild(d);
  setTimeout(() => d.remove(), 750);

  // small confetti
  for (let i = 0; i < 20; i++) {
    setTimeout(() => {
      const p = document.createElement('div');
      const a = Math.random() * Math.PI * 2;
      const dist = 40 + Math.random() * 100;
      const sz = 3 + Math.random() * 6;
      const colors = ['#2563eb','#3b82f6','#60a5fa','#93c5fd'];
      p.style.cssText = `
        position:fixed;left:${x}px;top:${y}px;
        width:${sz}px;height:${sz}px;
        border-radius:${Math.random()>.5?'50%':'2px'};
        background:${colors[i%colors.length]};
        pointer-events:none;z-index:99991;
        animation:_tl_dot .6s ease forwards;
        --dx:${Math.cos(a)*dist}px;--dy:${Math.sin(a)*dist}px;
      `;
      document.body.appendChild(p);
      setTimeout(() => p.remove(), 700);
    }, i * 20);
  }
}

/* ── Toast ────────────────────────────────────────────────────── */
function _toast(lang) {
  document.getElementById('_tl_toast')?.remove();
  const t = document.createElement('div');
  t.id = '_tl_toast';
  t.style.cssText = `
    position:fixed;bottom:5.5rem;left:50%;transform:translateX(-50%);
    background:var(--card);backdrop-filter:blur(20px);
    border:1px solid var(--divider);border-radius:50px;
    padding:.45rem 1.2rem;font-size:.82rem;font-weight:700;
    color:var(--text);box-shadow:var(--shadow-lg);
    z-index:99999;white-space:nowrap;
    animation:_tl_toast .35s cubic-bezier(.34,1.56,.64,1) both;
  `;
  t.textContent = lang === 'en' ? '🇬🇧 Switched to English' : '🇺🇦 Перемкнуто на українську';
  document.body.appendChild(t);
  setTimeout(() => {
    t.style.transition = 'opacity .25s,transform .25s';
    t.style.opacity = '0'; t.style.transform = 'translateX(-50%) translateY(10px)';
    setTimeout(() => t.remove(), 280);
  }, 2500);
}

/* ── Inject styles once ───────────────────────────────────────── */
function _injectStyles() {
  if (document.getElementById('_tl_css')) return;
  const s = document.createElement('style');
  s.id = '_tl_css';
  s.textContent = `
    /* Lang button — clean pill */
    .lang-toggle-btn {
      display:inline-flex;align-items:center;gap:.3rem;
      padding:.28rem .7rem;border-radius:20px;
      background:var(--hover-bg);
      border:1px solid var(--divider);
      color:var(--text2);font-size:.76rem;font-weight:700;
      cursor:pointer;white-space:nowrap;letter-spacing:.02em;
      position:relative;overflow:hidden;
      transition:background .15s,color .15s,border-color .15s,transform .15s;
      -webkit-tap-highlight-color:transparent;
    }
    .lang-toggle-btn:hover, .lang-toggle-btn._lang-active {
      background:var(--p);color:#fff;border-color:transparent;
      transform:translateY(-1px);
    }
    .lang-btn-flag { font-size:.9rem; }
    .lang-btn-label { font-size:.73rem; font-weight:800; }

    /* Translated element flash */
    ._tl_f { animation:_tl_flash .45s ease forwards !important; }

    /* Keyframes */
    @keyframes _tl_spin {
      0%  { transform:rotateY(0)    scale(1) }
      40% { transform:rotateY(180deg) scale(1.12) }
      100%{ transform:rotateY(360deg) scale(1) }
    }
    @keyframes _tl_ripple {
      from{ transform:translate(-50%,-50%) scale(0); opacity:.8 }
      to  { transform:translate(-50%,-50%) scale(120); opacity:0 }
    }
    @keyframes _tl_dot {
      0%  { transform:translate(0,0) scale(1); opacity:1 }
      100%{ transform:translate(var(--dx),var(--dy)) scale(.1); opacity:0 }
    }
    @keyframes _tl_toast {
      from{ opacity:0;transform:translate(-50%,12px) scale(.9) }
      to  { opacity:1;transform:translate(-50%,0)    scale(1) }
    }
    @keyframes _tl_flash {
      0%  { opacity:.3;filter:brightness(1.4) }
      60% { opacity:1;filter:brightness(1.1) }
      100%{ opacity:1;filter:brightness(1) }
    }
  `;
  document.head.appendChild(s);
}
