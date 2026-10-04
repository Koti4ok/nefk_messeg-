/* ============================================================
   НЕФК effects.js — кнопка вибору анімацій + 10 ефектів
   Кнопка "🎨" фіксована в лівому нижньому куті
   ============================================================ */

const FX_KEY = 'nemk-fx';

const EFFECTS = [
  {
    id: 'none',
    name: 'Вимкнено',
    icon: '⛔',
    desc: 'Без ефектів',
    apply: () => _fxStop(),
  },
  {
    id: 'matrix',
    name: 'Матриця',
    icon: '🟢',
    desc: 'Зелені символи падають',
    apply: () => _fxMatrix(),
  },
  {
    id: 'snow',
    name: 'Сніг',
    icon: '❄️',
    desc: 'Падаючі сніжинки',
    apply: () => _fxSnow(),
  },
  {
    id: 'neon',
    name: 'Неон',
    icon: '💜',
    desc: 'Неонове свічення карток',
    apply: () => _fxNeon(),
  },
  {
    id: 'particles',
    name: 'Частинки',
    icon: '✨',
    desc: 'Плаваючі частинки',
    apply: () => _fxParticles(),
  },
  {
    id: 'rainbow',
    name: 'Веселка',
    icon: '🌈',
    desc: 'Веселковий градієнт фону',
    apply: () => _fxRainbow(),
  },
  {
    id: 'glitch',
    name: 'Глітч',
    icon: '📺',
    desc: 'Глітч-ефект на картках',
    apply: () => _fxGlitch(),
  },
  {
    id: 'bubbles',
    name: 'Бульбашки',
    icon: '🫧',
    desc: 'Бульбашки пливуть вгору',
    apply: () => _fxBubbles(),
  },
  {
    id: 'stars',
    name: 'Зоряне небо',
    icon: '🌌',
    desc: 'Мерехтливі зірки',
    apply: () => _fxStarfield(),
  },
  {
    id: 'cursor',
    name: 'Хвіст курсора',
    icon: '🖱️',
    desc: 'Слід за курсором',
    apply: () => _fxCursorTrail(),
  },
  {
    id: 'fireworks',
    name: 'Феєрверк',
    icon: '🎆',
    desc: 'Феєрверки по кліку',
    apply: () => _fxFireworks(),
  },
];

let _currentFx = localStorage.getItem(FX_KEY) || 'none';
let _fxCleanup = null;  // функція очищення поточного ефекту
let _panelOpen = false;

/* ── Ін'єкція UI при DOMContentLoaded ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  _injectFxStyles();
  _buildFxBtn();
  _buildFxPanel();
  // Відновити збережений ефект
  if (_currentFx !== 'none') {
    const fx = EFFECTS.find(e => e.id === _currentFx);
    if (fx) setTimeout(() => fx.apply(), 600);
  }
});

/* ── Кнопка 🎨 ─────────────────────────────────────────────── */
function _buildFxBtn() {
  const btn = document.createElement('button');
  btn.id = 'fx-btn';
  btn.title = 'Вибір анімацій';
  btn.innerHTML = '<span class="fx-btn-icon">🎨</span><span class="fx-btn-label">Ефекти</span>';
  btn.onclick = _toggleFxPanel;
  document.body.appendChild(btn);
}

/* ── Панель вибору ─────────────────────────────────────────── */
function _buildFxPanel() {
  const panel = document.createElement('div');
  panel.id = 'fx-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Вибір анімацій сайту');

  const header = document.createElement('div');
  header.className = 'fx-panel-header';
  header.innerHTML = `
    <div class="fx-panel-title">
      <span>🎨</span> Анімації сайту
    </div>
    <button class="fx-panel-close" onclick="_toggleFxPanel()" aria-label="Закрити">✕</button>
  `;

  const grid = document.createElement('div');
  grid.className = 'fx-panel-grid';

  EFFECTS.forEach(fx => {
    const card = document.createElement('button');
    card.className = 'fx-card' + (fx.id === _currentFx ? ' fx-active' : '');
    card.dataset.fxId = fx.id;
    card.innerHTML = `
      <span class="fx-card-icon">${fx.icon}</span>
      <span class="fx-card-name">${fx.name}</span>
      <span class="fx-card-desc">${fx.desc}</span>
    `;
    card.onclick = () => _selectFx(fx.id);
    grid.appendChild(card);
  });

  const footer = document.createElement('div');
  footer.className = 'fx-panel-footer';
  footer.innerHTML = `<span id="fx-active-label">Активно: <b>${_getLabelById(_currentFx)}</b></span>`;

  panel.appendChild(header);
  panel.appendChild(grid);
  panel.appendChild(footer);
  document.body.appendChild(panel);
}

function _getLabelById(id) {
  const fx = EFFECTS.find(e => e.id === id);
  return fx ? `${fx.icon} ${fx.name}` : '⛔ Вимкнено';
}

function _toggleFxPanel() {
  _panelOpen = !_panelOpen;
  const panel = document.getElementById('fx-panel');
  const btn   = document.getElementById('fx-btn');
  if (panel) panel.classList.toggle('fx-panel-open', _panelOpen);
  if (btn)   btn.classList.toggle('fx-btn-active', _panelOpen);
}

function _selectFx(id) {
  // Зупинити поточний
  _fxStop();

  _currentFx = id;
  localStorage.setItem(FX_KEY, id);

  // Оновити активну карту
  document.querySelectorAll('.fx-card').forEach(c => {
    c.classList.toggle('fx-active', c.dataset.fxId === id);
  });

  // Оновити footer
  const lbl = document.getElementById('fx-active-label');
  if (lbl) lbl.innerHTML = `Активно: <b>${_getLabelById(id)}</b>`;

  // Запустити новий
  const fx = EFFECTS.find(e => e.id === id);
  if (fx) fx.apply();

  // Закрити панель
  setTimeout(_toggleFxPanel, 300);
}

/* ── Зупинити поточний ефект ──────────────────────────────── */
function _fxStop() {
  if (typeof _fxCleanup === 'function') {
    _fxCleanup();
    _fxCleanup = null;
  }
  // Прибрати залишки
  ['#fx-canvas','#fx-rain','#fx-bubbles','#fx-stars',
   '#fx-neon-style','#fx-rainbow-style','#fx-glitch-style',
   '#fx-cursor-style'].forEach(sel => {
    document.querySelector(sel)?.remove();
  });
  document.removeEventListener('click', _fireworkClick);
  document.removeEventListener('mousemove', _cursorMove);
  document.body.style.backgroundImage = '';
  document.body.style.animation = '';
}

/* ══════════════════════════════════════════════════════════════
   ЕФЕКТИ
══════════════════════════════════════════════════════════════ */

/* 1. MATRIX — зелені символи ──────────────────────────────── */
function _fxMatrix() {
  const canvas = document.createElement('canvas');
  canvas.id = 'fx-canvas';
  canvas.style.cssText = `
    position:fixed;inset:0;z-index:-1;pointer-events:none;
    opacity:.18;
  `;
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let w = canvas.width = window.innerWidth;
  let h = canvas.height = window.innerHeight;
  const cols = Math.floor(w / 16);
  const drops = Array(cols).fill(1);
  const chars = 'НЕФК0101ABCDEFGHIJKLM01АБВГДЕ01NEFC';

  const draw = () => {
    ctx.fillStyle = 'rgba(0,0,0,.05)';
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = '#22c55e';
    ctx.font = '14px monospace';
    drops.forEach((y, i) => {
      ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * 16, y * 16);
      if (y * 16 > h && Math.random() > .975) drops[i] = 0;
      drops[i]++;
    });
  };

  const tid = setInterval(draw, 50);
  const onResize = () => { w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; };
  window.addEventListener('resize', onResize);
  _fxCleanup = () => { clearInterval(tid); window.removeEventListener('resize', onResize); };
}

/* 2. SNOW ──────────────────────────────────────────────────── */
function _fxSnow() {
  const cnt = 60;
  const container = document.createElement('div');
  container.id = 'fx-rain';
  container.style.cssText = 'position:fixed;inset:0;z-index:9990;pointer-events:none;overflow:hidden;';

  for (let i = 0; i < cnt; i++) {
    const s = document.createElement('div');
    const sz = 4 + Math.random() * 10;
    const dur = 4 + Math.random() * 6;
    const delay = Math.random() * 8;
    const left = Math.random() * 100;
    s.style.cssText = `
      position:absolute;
      left:${left}%;top:-20px;
      width:${sz}px;height:${sz}px;
      border-radius:50%;
      background:rgba(147,197,253,.85);
      animation:_snowFall ${dur}s linear ${delay}s infinite;
      filter:blur(.5px);
    `;
    container.appendChild(s);
  }
  document.body.appendChild(container);
  _fxCleanup = () => container.remove();
}

/* 3. NEON ──────────────────────────────────────────────────── */
function _fxNeon() {
  const st = document.createElement('style');
  st.id = 'fx-neon-style';
  st.textContent = `
    .post-card, .post-card-gl, .page-glass-card, .sidebar-widget, .gl-card, .h-card {
      animation: _neonPulse 2.5s ease-in-out infinite !important;
    }
    @keyframes _neonPulse {
      0%,100%{ box-shadow: 0 0 8px rgba(37,99,235,.3), 0 0 20px rgba(37,99,235,.15); }
      50%    { box-shadow: 0 0 20px rgba(14,165,233,.6), 0 0 40px rgba(14,165,233,.3),
                           0 0 60px rgba(59,130,246,.2); }
    }
  `;
  document.head.appendChild(st);
  _fxCleanup = () => st.remove();
}

/* 4. PARTICLES ─────────────────────────────────────────────── */
function _fxParticles() {
  const canvas = document.createElement('canvas');
  canvas.id = 'fx-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;z-index:-1;pointer-events:none;';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let w = canvas.width = window.innerWidth;
  let h = canvas.height = window.innerHeight;

  const pts = Array.from({length: 80}, () => ({
    x: Math.random()*w, y: Math.random()*h,
    vx: (Math.random()-.5)*.6, vy: (Math.random()-.5)*.6,
    r: 1.5+Math.random()*3,
    op: .2+Math.random()*.5,
  }));

  const draw = () => {
    ctx.clearRect(0, 0, w, h);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if(p.x<0||p.x>w) p.vx*=-1;
      if(p.y<0||p.y>h) p.vy*=-1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(59,130,246,${p.op})`;
      ctx.fill();
    });
    // З'єднуємо близькі частинки
    for(let i=0;i<pts.length;i++){
      for(let j=i+1;j<pts.length;j++){
        const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y;
        const dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<120){
          ctx.beginPath();
          ctx.moveTo(pts[i].x,pts[i].y);
          ctx.lineTo(pts[j].x,pts[j].y);
          ctx.strokeStyle=`rgba(59,130,246,${.12*(1-dist/120)})`;
          ctx.lineWidth=.8;
          ctx.stroke();
        }
      }
    }
  };

  const tid = setInterval(draw, 30);
  const onR = () => { w=canvas.width=window.innerWidth; h=canvas.height=window.innerHeight; };
  window.addEventListener('resize',onR);
  _fxCleanup = () => { clearInterval(tid); window.removeEventListener('resize',onR); };
}

/* 5. RAINBOW ───────────────────────────────────────────────── */
function _fxRainbow() {
  const st = document.createElement('style');
  st.id = 'fx-rainbow-style';
  st.textContent = `
    body.nemk-body {
      background-image: none !important;
      animation: _rainbowBg 8s linear infinite !important;
    }
    @keyframes _rainbowBg {
      0%   { filter: hue-rotate(0deg); }
      100% { filter: hue-rotate(360deg); }
    }
  `;
  document.head.appendChild(st);
  _fxCleanup = () => { st.remove(); document.body.style.filter=''; };
}

/* 6. GLITCH ────────────────────────────────────────────────── */
function _fxGlitch() {
  const st = document.createElement('style');
  st.id = 'fx-glitch-style';
  st.textContent = `
    .navbar, .post-card, .post-card-gl, .page-glass-card {
      animation: _glitchShake 6s ease-in-out infinite !important;
    }
    @keyframes _glitchShake {
      0%,92%,100%{ transform:translate(0,0); filter:none; }
      93%{ transform:translate(-3px,1px); filter:hue-rotate(90deg) brightness(1.2); }
      94%{ transform:translate(3px,-1px); filter:hue-rotate(-60deg); }
      95%{ transform:translate(-2px,2px); filter:brightness(.85) contrast(1.5); }
      96%{ transform:translate(0,0);     filter:none; }
      97%{ transform:translate(2px,-2px);filter:saturate(3); }
      98%{ transform:translate(-1px,1px);filter:invert(.1); }
      99%{ transform:translate(0,0);     filter:none; }
    }
  `;
  document.head.appendChild(st);
  _fxCleanup = () => st.remove();
}

/* 7. BUBBLES ───────────────────────────────────────────────── */
function _fxBubbles() {
  const container = document.createElement('div');
  container.id = 'fx-bubbles';
  container.style.cssText = 'position:fixed;inset:0;z-index:9990;pointer-events:none;overflow:hidden;';

  const spawnBubble = () => {
    const b = document.createElement('div');
    const sz = 8 + Math.random() * 28;
    const left = Math.random() * 100;
    const dur = 5 + Math.random() * 8;
    b.style.cssText = `
      position:absolute;
      left:${left}%;bottom:-40px;
      width:${sz}px;height:${sz}px;
      border-radius:50%;
      border:1.5px solid rgba(147,197,253,.45);
      background:rgba(59,130,246,.06);
      animation:_bubbleRise ${dur}s ease-in forwards;
    `;
    container.appendChild(b);
    setTimeout(() => b.remove(), dur * 1000 + 200);
  };

  const tid = setInterval(spawnBubble, 350);
  document.body.appendChild(container);
  _fxCleanup = () => { clearInterval(tid); container.remove(); };
}

/* 8. STARFIELD ─────────────────────────────────────────────── */
function _fxStarfield() {
  const canvas = document.createElement('canvas');
  canvas.id = 'fx-canvas';
  canvas.style.cssText = 'position:fixed;inset:0;z-index:-1;pointer-events:none;';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let w = canvas.width = window.innerWidth;
  let h = canvas.height = window.innerHeight;

  const stars = Array.from({length:200}, () => ({
    x: Math.random()*w, y: Math.random()*h,
    r: .5+Math.random()*1.8,
    op: Math.random(),
    dop: (Math.random()-.5)*.03,
  }));

  const draw = () => {
    ctx.clearRect(0,0,w,h);
    stars.forEach(s => {
      s.op += s.dop;
      if(s.op<=0||s.op>=1) s.dop *= -1;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(147,197,253,${s.op})`;
      ctx.fill();
    });
  };

  const tid = setInterval(draw, 50);
  const onR = () => { w=canvas.width=window.innerWidth; h=canvas.height=window.innerHeight; };
  window.addEventListener('resize',onR);
  _fxCleanup = () => { clearInterval(tid); window.removeEventListener('resize',onR); };
}

/* 9. CURSOR TRAIL ──────────────────────────────────────────── */
let _cursorTrails = [];
function _cursorMove(e) {
  const d = document.createElement('div');
  const colors = ['#2563eb','#0ea5e9','#38bdf8','#60a5fa'];
  d.style.cssText = `
    position:fixed;left:${e.clientX}px;top:${e.clientY}px;
    width:8px;height:8px;border-radius:50%;
    background:${colors[Math.floor(Math.random()*colors.length)]};
    pointer-events:none;z-index:99995;
    transform:translate(-50%,-50%);
    animation:_trailFade .6s ease forwards;
  `;
  document.body.appendChild(d);
  _cursorTrails.push(d);
  setTimeout(() => { d.remove(); _cursorTrails = _cursorTrails.filter(x=>x!==d); }, 650);
}

function _fxCursorTrail() {
  const st = document.createElement('style');
  st.id = 'fx-cursor-style';
  st.textContent = `@keyframes _trailFade {
    from{opacity:.9;transform:translate(-50%,-50%) scale(1)}
    to  {opacity:0;transform:translate(-50%,-50%) scale(.1)}
  }`;
  document.head.appendChild(st);
  document.addEventListener('mousemove', _cursorMove);
  _fxCleanup = () => {
    st.remove();
    document.removeEventListener('mousemove', _cursorMove);
    _cursorTrails.forEach(d => d.remove());
    _cursorTrails = [];
  };
}

/* 10. FIREWORKS (по кліку) ─────────────────────────────────── */
function _fireworkClick(e) {
  const colors = ['#2563eb','#0ea5e9','#38bdf8','#f59e0b','#f472b6','#22c55e','#fff'];
  const bursts = 24;
  for (let i = 0; i < bursts; i++) {
    const p = document.createElement('div');
    const ang = (i / bursts) * Math.PI * 2;
    const dist = 40 + Math.random() * 80;
    const dx = Math.cos(ang) * dist;
    const dy = Math.sin(ang) * dist;
    const sz = 4 + Math.random() * 7;
    p.style.cssText = `
      position:fixed;
      left:${e.clientX}px;top:${e.clientY}px;
      width:${sz}px;height:${sz}px;
      border-radius:50%;
      background:${colors[i % colors.length]};
      pointer-events:none;z-index:99996;
      animation:_fwBurst .8s ease forwards;
      --fdx:${dx}px;--fdy:${dy}px;
    `;
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 900);
  }
}

function _fxFireworks() {
  const st = document.createElement('style');
  st.id = 'fx-cursor-style';
  st.textContent = `
    body * { cursor: crosshair !important; }
    @keyframes _fwBurst {
      0%  {transform:translate(0,0) scale(1);opacity:1}
      100%{transform:translate(var(--fdx),var(--fdy)) scale(.1);opacity:0}
    }
  `;
  document.head.appendChild(st);
  document.addEventListener('click', _fireworkClick);
  _fxCleanup = () => {
    st.remove();
    document.removeEventListener('click', _fireworkClick);
  };
}

/* ── Inject styles ──────────────────────────────────────────── */
function _injectFxStyles() {
  if (document.getElementById('_fx_styles')) return;
  const s = document.createElement('style');
  s.id = '_fx_styles';
  s.textContent = `
    /* ── FX Button ── */
    #fx-btn {
      position:fixed;
      bottom:1.75rem;left:1.75rem;
      display:flex;align-items:center;gap:.45rem;
      padding:.55rem 1rem;
      border-radius:50px;
      background:var(--card);
      backdrop-filter:blur(24px) saturate(180%);
      border:1px solid var(--border);
      color:var(--text);
      font-size:.8rem;font-weight:700;
      cursor:pointer;z-index:9990;
      box-shadow:var(--shadow);
      transition:transform .2s,box-shadow .2s,background .2s;
      overflow:hidden;
    }
    #fx-btn::before {
      content:'';position:absolute;inset:0;
      background:linear-gradient(90deg,
        transparent,rgba(37,99,235,.25),transparent);
      background-size:200% 100%;
      animation:_btnShimmer 2.5s linear infinite;
    }
    #fx-btn:hover {
      transform:translateY(-3px) scale(1.04);
      box-shadow:var(--shadow-lg);
      background:linear-gradient(135deg,var(--p),var(--accent));
      color:#fff;border-color:transparent;
    }
    #fx-btn:hover::before{display:none;}
    #fx-btn.fx-btn-active {
      background:linear-gradient(135deg,var(--p),var(--accent));
      color:#fff;border-color:transparent;
    }
    .fx-btn-icon { font-size:1.1rem; }
    .fx-btn-label { letter-spacing:.03em; }

    /* ── FX Panel ── */
    #fx-panel {
      position:fixed;
      bottom:5rem;left:1.75rem;
      width:340px;
      background:var(--card);
      backdrop-filter:blur(32px) saturate(200%);
      border:1px solid var(--border);
      border-radius:24px;
      box-shadow:0 20px 60px rgba(0,0,0,.18),inset 0 1px 0 rgba(255,255,255,.1);
      z-index:9989;
      transform:scale(.88) translateY(16px);
      opacity:0;pointer-events:none;
      transition:transform .35s cubic-bezier(.34,1.56,.64,1),opacity .25s;
      overflow:hidden;
    }
    #fx-panel.fx-panel-open {
      transform:scale(1) translateY(0);
      opacity:1;pointer-events:all;
    }
    .fx-panel-header {
      display:flex;align-items:center;justify-content:space-between;
      padding:.9rem 1.1rem;
      background:linear-gradient(135deg,rgba(37,99,235,.15),rgba(14,165,233,.1));
      border-bottom:1px solid var(--divider);
    }
    .fx-panel-title {
      font-size:.95rem;font-weight:800;color:var(--text);
      display:flex;align-items:center;gap:.5rem;
    }
    .fx-panel-close {
      width:26px;height:26px;border-radius:50%;
      background:var(--hover-bg);border:1px solid var(--border);
      color:var(--muted);font-size:.75rem;cursor:pointer;
      display:flex;align-items:center;justify-content:center;
      transition:background .15s,color .15s;
    }
    .fx-panel-close:hover{background:var(--red);color:#fff;border-color:transparent;}

    /* Grid */
    .fx-panel-grid {
      display:grid;grid-template-columns:repeat(3,1fr);
      gap:.5rem;padding:.85rem;
      max-height:300px;overflow-y:auto;
      scrollbar-width:thin;
    }
    .fx-card {
      display:flex;flex-direction:column;align-items:center;
      gap:.3rem;padding:.65rem .4rem;
      border-radius:14px;
      background:var(--bg3);
      border:1.5px solid transparent;
      cursor:pointer;
      transition:transform .18s,box-shadow .18s,background .18s,border-color .18s;
      position:relative;overflow:hidden;
    }
    .fx-card::after {
      content:'';position:absolute;inset:0;border-radius:inherit;
      background:linear-gradient(135deg,rgba(37,99,235,.15),rgba(14,165,233,.1));
      opacity:0;transition:opacity .2s;
    }
    .fx-card:hover { transform:translateY(-3px) scale(1.04); box-shadow:var(--shadow); }
    .fx-card:hover::after { opacity:1; }
    .fx-active {
      border-color:var(--p)!important;
      background:rgba(37,99,235,.12)!important;
      box-shadow:0 0 0 2px rgba(37,99,235,.2)!important;
    }
    .fx-active::after{opacity:1!important;}
    .fx-card-icon  { font-size:1.5rem; }
    .fx-card-name  { font-size:.74rem;font-weight:700;color:var(--text); }
    .fx-card-desc  { font-size:.65rem;color:var(--muted);text-align:center;line-height:1.3; }

    .fx-panel-footer {
      padding:.6rem 1.1rem;
      border-top:1px solid var(--divider);
      font-size:.78rem;color:var(--muted);
      background:var(--card);
    }
    .fx-panel-footer b { color:var(--p); }

    /* Keyframes for effects */
    @keyframes _snowFall {
      0%  {transform:translateY(0) translateX(0) rotate(0deg);opacity:.85}
      100%{transform:translateY(110vh) translateX(${Math.floor(Math.random()*80-40)}px) rotate(360deg);opacity:0}
    }
    @keyframes _bubbleRise {
      0%  {transform:translateY(0)     scale(1);   opacity:.7}
      100%{transform:translateY(-110vh) scale(1.2); opacity:0}
    }
    @keyframes _btnShimmer {
      0%  {background-position:200% 0}
      100%{background-position:-200% 0}
    }

    /* Mobile */
    @media(max-width:480px){
      #fx-btn   { bottom:1.25rem;left:1.25rem;padding:.45rem .8rem;font-size:.74rem; }
      #fx-panel { width:calc(100vw - 2rem);left:1rem;bottom:4.5rem; }
    }
  `;
  document.head.appendChild(s);
}
