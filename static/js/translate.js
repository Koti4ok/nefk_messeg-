/* ============================================================
   НЕФК translate.js v3 — повний DOM-scan переклад UA↔EN
   Не потребує data-атрибутів, замінює ВЕСЬ текст на сторінці
   ============================================================ */

const LANG_KEY = 'nemk-lang';
let _lang = localStorage.getItem(LANG_KEY) || 'uk';
let _busy = false;

// Теги, де текст НЕ чіпаємо
const SKIP_TAGS = new Set([
  'SCRIPT','STYLE','TEXTAREA','CODE','PRE',
  'NOSCRIPT','SVG','MATH','CANVAS'
]);

/* ── Ініціалізація ─────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  _injectBaseStyles();
  _syncBtn(_lang);
  if (_lang === 'en') {
    _fetchPairs('en').then(pairs => {
      _domReplace(pairs);
      _syncBtn('en');
    }).catch(() => {});
  }
});

/* ── Публічна кнопка ───────────────────────────────────────── */
function toggleLang() {
  if (_busy) return;
  _doTranslate(_lang === 'uk' ? 'en' : 'uk');
}

/* ── Головна процедура ─────────────────────────────────────── */
async function _doTranslate(lang) {
  _busy = true;
  try {
    _animBtnFlip();
    _fxWave();
    _fxBurst();
    _fxFlash();
    _fxBodyPulse();

    const pairs = await _fetchPairs(lang);

    // Плавне розмиття
    await _pageBlur(true);
    _domReplace(pairs);
    _lang = lang;
    localStorage.setItem(LANG_KEY, lang);
    await _pageBlur(false);

    _syncBtn(lang);
    _fxToast(lang);
    _fxStars();
  } catch(e) {
    console.error('[translate]', e);
    await _pageBlur(false);
  } finally {
    _busy = false;
  }
}

/* ── AJAX ──────────────────────────────────────────────────── */
async function _fetchPairs(lang) {
  const r = await fetch(`/api/translate/?lang=${lang}`,{
    headers:{'X-Requested-With':'XMLHttpRequest'}
  });
  if(!r.ok) throw new Error('HTTP '+r.status);
  const j = await r.json();
  return j.pairs || [];
}

/* ── DOM replace — обхід усіх текстових вузлів ─────────────── */
function _domReplace(pairs) {
  if(!pairs.length) return;

  function walk(node) {
    // Текстовий вузол
    if(node.nodeType === 3) {
      let t = node.textContent;
      if(!t.trim()) return;
      let changed = false;
      for(const [from, to] of pairs) {
        if(t.includes(from)) {
          t = t.split(from).join(to);
          changed = true;
        }
      }
      if(changed) {
        node.textContent = t;
        _shimmerEl(node.parentElement);
      }
      return;
    }

    // Елемент
    if(node.nodeType === 1) {
      const tag = node.tagName;
      if(SKIP_TAGS.has(tag)) return;

      // Атрибути
      _replaceAttr(node, 'placeholder', pairs);
      _replaceAttr(node, 'title', pairs);
      _replaceAttr(node, 'aria-label', pairs);
      _replaceAttr(node, 'alt', pairs);
      _replaceAttr(node, 'value', pairs, ['BUTTON','SUBMIT']);

      node.childNodes.forEach(walk);
    }
  }

  walk(document.body);
}

function _replaceAttr(el, attr, pairs, tags) {
  if(tags && !tags.includes(el.tagName)) return;
  const v = el.getAttribute(attr);
  if(!v) return;
  let nv = v;
  for(const [f,t] of pairs) nv = nv.split(f).join(t);
  if(nv !== v) el.setAttribute(attr, nv);
}

/* ── Shimmer анімація на елементі ──────────────────────────── */
function _shimmerEl(el) {
  if(!el || !el.classList) return;
  el.classList.remove('_i18n_sh');
  void el.offsetWidth;
  el.classList.add('_i18n_sh');
  setTimeout(() => el.classList.remove('_i18n_sh'), 700);
}

/* ── Blur сторінки ─────────────────────────────────────────── */
function _pageBlur(on) {
  return new Promise(res => {
    const main = document.querySelector('main') || document.body;
    main.style.transition = 'opacity .22s, filter .22s';
    main.style.opacity    = on ? '0.1' : '1';
    main.style.filter     = on ? 'blur(3px)' : 'blur(0)';
    setTimeout(() => {
      if(!on){ main.style.transition=''; main.style.opacity=''; main.style.filter=''; }
      res();
    }, 240);
  });
}

/* ── Синхронізація кнопок ──────────────────────────────────── */
function _syncBtn(lang) {
  const label = lang==='en' ? '🇺🇦 UA' : '🇬🇧 EN';
  document.querySelectorAll('.lang-toggle-btn').forEach(btn => {
    const sp = btn.querySelector('.lang-btn-label') || btn;
    sp.textContent = label;
    btn.classList.toggle('lang-en', lang==='en');
  });
}

/* ── 3D flip кнопки ────────────────────────────────────────── */
function _animBtnFlip() {
  document.querySelectorAll('.lang-toggle-btn').forEach(btn => {
    btn.style.animation = 'none';
    void btn.offsetWidth;
    btn.style.animation = '_langFlip .55s cubic-bezier(.34,1.56,.64,1)';
    setTimeout(() => btn.style.animation='', 600);
  });
}

/* ── FX: Хвиля ─────────────────────────────────────────────── */
function _fxWave() {
  const d = document.createElement('div');
  d.style.cssText = `
    position:fixed;inset:0;z-index:99990;pointer-events:none;
    display:flex;align-items:center;justify-content:center;overflow:hidden;
  `;
  const c = document.createElement('div');
  c.style.cssText = `
    width:20px;height:20px;border-radius:50%;
    background:radial-gradient(circle,rgba(37,99,235,.22),rgba(14,165,233,.1) 50%,transparent 70%);
    animation:_waveX .85s cubic-bezier(.22,1,.36,1) forwards;
  `;
  d.appendChild(c);
  document.body.appendChild(d);
  setTimeout(() => d.remove(), 950);
}

/* ── FX: Burst конфеті ──────────────────────────────────────── */
function _fxBurst() {
  const colors = ['#2563eb','#0ea5e9','#38bdf8','#60a5fa','#93c5fd','#ffffff'];
  const btn = document.querySelector('.lang-toggle-btn');
  let ox = window.innerWidth/2, oy = 64;
  if(btn){ const r=btn.getBoundingClientRect(); ox=r.left+r.width/2; oy=r.top+r.height/2; }
  for(let i=0;i<36;i++){
    setTimeout(()=>{
      const p = document.createElement('div');
      const ang = Math.random()*Math.PI*2;
      const dist = 60+Math.random()*180;
      const dx = Math.cos(ang)*dist, dy = Math.sin(ang)*dist;
      const sz = 3+Math.random()*9;
      p.style.cssText = `
        position:fixed;left:${ox}px;top:${oy}px;
        width:${sz}px;height:${sz}px;
        border-radius:${Math.random()>.5?'50%':'3px'};
        background:${colors[i%colors.length]};
        pointer-events:none;z-index:99998;
        transform:translate(0,0);
        animation:_fly${i%3} ${.5+Math.random()*.5}s ease forwards;
      `;
      document.body.appendChild(p);
      setTimeout(()=>p.remove(),1100);
    }, i*18);
  }
}

/* ── FX: Flash ──────────────────────────────────────────────── */
function _fxFlash() {
  const d = document.createElement('div');
  d.style.cssText = `
    position:fixed;inset:0;z-index:99989;pointer-events:none;
    background:linear-gradient(135deg,rgba(37,99,235,.08),rgba(14,165,233,.05));
    animation:_flashX .5s ease forwards;
  `;
  document.body.appendChild(d);
  setTimeout(()=>d.remove(), 550);
}

/* ── FX: Body pulse ─────────────────────────────────────────── */
function _fxBodyPulse() {
  document.body.style.transition='filter .12s';
  document.body.style.filter='brightness(1.04) hue-rotate(8deg)';
  setTimeout(()=>{
    document.body.style.filter='brightness(.98) hue-rotate(-3deg)';
    setTimeout(()=>{document.body.style.filter='';document.body.style.transition='';},150);
  },120);
}

/* ── FX: Зірки ──────────────────────────────────────────────── */
function _fxStars() {
  const em = ['✨','🌟','💫','⭐','🎉','🚀','💙','🌊'];
  for(let i=0;i<8;i++){
    setTimeout(()=>{
      const d = document.createElement('div');
      const dy = -(60+Math.random()*100);
      d.style.cssText = `
        position:fixed;left:${5+Math.random()*90}vw;
        bottom:${8+Math.random()*15}vh;
        font-size:${1+Math.random()*.8}rem;
        pointer-events:none;z-index:99997;
        animation:_starX .9s ease forwards;
        --dy:${dy}px;--dx:${(Math.random()-.5)*50}px;
      `;
      d.textContent = em[i%em.length];
      document.body.appendChild(d);
      setTimeout(()=>d.remove(),1000);
    }, i*80);
  }
}

/* ── FX: Toast ──────────────────────────────────────────────── */
function _fxToast(lang) {
  document.getElementById('_tl_toast')?.remove();
  const t = document.createElement('div');
  t.id = '_tl_toast';
  t.style.cssText = `
    position:fixed;bottom:6rem;left:50%;
    transform:translateX(-50%);
    background:var(--card);
    backdrop-filter:blur(24px) saturate(180%);
    border:1px solid var(--border);
    border-radius:50px;padding:.5rem 1.4rem;
    font-size:.85rem;font-weight:700;
    color:var(--text);box-shadow:var(--shadow-lg);
    z-index:99999;white-space:nowrap;
    animation:_toastX .4s cubic-bezier(.34,1.56,.64,1) both;
  `;
  t.textContent = lang==='en' ? '🇬🇧 Switched to English!' : '🇺🇦 Перемкнуто на українську!';
  document.body.appendChild(t);
  setTimeout(()=>{
    t.style.transition='opacity .3s,transform .3s';
    t.style.opacity='0';
    t.style.transform='translateX(-50%) translateY(12px)';
    setTimeout(()=>t.remove(),350);
  }, 2800);
}

/* ── Inject base styles ─────────────────────────────────────── */
function _injectBaseStyles() {
  if(document.getElementById('_tl_styles')) return;
  const s = document.createElement('style');
  s.id = '_tl_styles';
  s.textContent = `
    /* Lang button — shimmer */
    .lang-toggle-btn {
      display:inline-flex;align-items:center;gap:.35rem;
      padding:.3rem .85rem;border-radius:22px;
      border:1.5px solid rgba(37,99,235,.25);
      background:rgba(37,99,235,.07);
      color:var(--p);font-size:.78rem;font-weight:800;
      cursor:pointer;white-space:nowrap;letter-spacing:.03em;
      position:relative;overflow:hidden;
      transition:box-shadow .2s,transform .15s,background .2s;
    }
    .lang-toggle-btn::before {
      content:'';position:absolute;inset:0;
      background:linear-gradient(90deg,
        transparent 0%,rgba(59,130,246,.5) 50%,transparent 100%);
      background-size:200% 100%;
      animation:_btnShimmer 2s linear infinite;
      pointer-events:none;
    }
    .lang-toggle-btn:hover {
      background:linear-gradient(135deg,#2563eb,#0ea5e9);
      color:#fff;border-color:transparent;
      box-shadow:0 4px 16px rgba(37,99,235,.45);
      transform:translateY(-2px);
    }
    .lang-toggle-btn:hover::before{display:none;}
    .lang-en {
      background:linear-gradient(135deg,#2563eb,#0ea5e9)!important;
      color:#fff!important;border-color:transparent!important;
      box-shadow:0 4px 16px rgba(37,99,235,.4)!important;
    }
    .lang-en::before{display:none;}

    /* Shimmer on translated text */
    ._i18n_sh {
      animation:_shimEl .6s ease forwards!important;
    }

    /* Keyframes */
    @keyframes _btnShimmer {
      0%  {background-position:200% 0}
      100%{background-position:-200% 0}
    }
    @keyframes _langFlip {
      0%  {transform:rotateY(0)   scale(1)}
      40% {transform:rotateY(180deg) scale(1.15)}
      100%{transform:rotateY(360deg) scale(1)}
    }
    @keyframes _waveX {
      from{transform:scale(0);opacity:1}
      to  {transform:scale(280);opacity:0}
    }
    @keyframes _flashX {
      0%{opacity:0}20%{opacity:1}100%{opacity:0}
    }
    @keyframes _fly0 {
      to{transform:translate(var(--dx,60px),var(--dy,-80px)) scale(.1);opacity:0}
    }
    @keyframes _fly1 {
      to{transform:translate(var(--dx,-40px),var(--dy,-120px)) scale(.15);opacity:0}
    }
    @keyframes _fly2 {
      to{transform:translate(var(--dx,90px),var(--dy,-50px)) scale(.05);opacity:0}
    }
    @keyframes _starX {
      0%  {transform:translate(0,0) scale(1);opacity:1}
      100%{transform:translate(var(--dx,0),var(--dy,-80px)) scale(.3);opacity:0}
    }
    @keyframes _toastX {
      from{opacity:0;transform:translate(-50%,16px) scale(.9)}
      to  {opacity:1;transform:translate(-50%,0)    scale(1)}
    }
    @keyframes _shimEl {
      0%  {opacity:.3;color:#60a5fa;filter:blur(.5px)}
      50% {opacity:1;color:#2563eb;filter:blur(0)}
      100%{opacity:1;color:inherit;filter:blur(0)}
    }
  `;
  document.head.appendChild(s);
}
