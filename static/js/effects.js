/* ============================================================
   НЕФК effects.js v2 — Clean effects panel + 10 animations
   Кнопка фіксована ліворуч знизу
   ============================================================ */

const FX_KEY = 'nemk-fx';

const FX_LIST = [
  { id:'off',       icon:'○',  name:'Вимкнено',        nameEn:'Off',           desc:'Без ефектів',                  descEn:'No effects' },
  { id:'particles', icon:'◉',  name:'Частинки',         nameEn:'Particles',     desc:'З\'єднані точки у фоні',       descEn:'Connected dots background' },
  { id:'stars',     icon:'✦',  name:'Зірки',            nameEn:'Stars',         desc:'Мерехтливі зірки',             descEn:'Twinkling starfield' },
  { id:'snow',      icon:'*',  name:'Сніг',             nameEn:'Snow',          desc:'Падаючі сніжинки',             descEn:'Falling snowflakes' },
  { id:'matrix',    icon:'▓',  name:'Матриця',          nameEn:'Matrix',        desc:'Символи НЕФК падають',         descEn:'NEFC symbols falling' },
  { id:'neon',      icon:'◈',  name:'Неон',             nameEn:'Neon',          desc:'Пульсуюче підсвічення карток', descEn:'Pulsing card glow' },
  { id:'bubbles',   icon:'◎',  name:'Бульбашки',        nameEn:'Bubbles',       desc:'Прозорі кулі вгору',           descEn:'Transparent bubbles rising' },
  { id:'aurora',    icon:'≋',  name:'Аврора',           nameEn:'Aurora',        desc:'Переливний градієнт фону',     descEn:'Shifting gradient background' },
  { id:'cursor',    icon:'⊕',  name:'Слід',             nameEn:'Trail',         desc:'Хвіст за курсором',            descEn:'Cursor trail effect' },
  { id:'glitch',    icon:'⚡',  name:'Глітч',            nameEn:'Glitch',        desc:'Помехи на картках',            descEn:'Glitch effect on cards' },
  { id:'fire',      icon:'▲',  name:'Феєрверк',         nameEn:'Fireworks',     desc:'Вибухи по кліку',              descEn:'Fireworks on click' },
];

let _cur = localStorage.getItem(FX_KEY) || 'off';
let _cleanup = null;
let _open = false;

document.addEventListener('DOMContentLoaded', () => {
  _css();
  _buildBtn();
  _buildPanel();
  if (_cur !== 'off') {
    const fx = FX_LIST.find(f => f.id === _cur);
    if (fx) setTimeout(() => _apply(fx), 700);
  }
});

/* ── Кнопка ─────────────────────────────────────────────────── */
function _buildBtn() {
  const btn = document.createElement('button');
  btn.id = 'fx-btn';
  btn.setAttribute('aria-label', 'Ефекти сайту');
  btn.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="fx-btn-ico">
      <circle cx="8" cy="8" r="3" fill="currentColor"/>
      <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M3.05 12.95l1.41-1.41M11.54 4.46l1.41-1.41" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    <span class="fx-btn-lbl">Ефекти</span>
  `;
  btn.onclick = _toggle;
  document.body.appendChild(btn);
}

/* ── Панель ──────────────────────────────────────────────────── */
function _buildPanel() {
  const p = document.createElement('div');
  p.id = 'fx-panel';
  p.setAttribute('role', 'dialog');
  p.setAttribute('aria-label', 'Вибір ефектів');

  p.innerHTML = `
    <div class="fx-ph">
      <div class="fx-pt">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style="opacity:.7">
          <circle cx="8" cy="8" r="3" fill="currentColor"/>
          <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M3.05 12.95l1.41-1.41M11.54 4.46l1.41-1.41" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Ефекти сайту
      </div>
      <button class="fx-close" onclick="_toggle()" aria-label="Закрити">
        <svg width="10" height="10" viewBox="0 0 10 10"><path d="M1 1l8 8M9 1L1 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      </button>
    </div>
    <div class="fx-grid" id="fx-grid"></div>
    <div class="fx-pf">
      <span class="fx-pf-dot" id="fx-dot"></span>
      <span id="fx-lbl">${_getLbl(_cur)}</span>
    </div>
  `;

  const grid = p.querySelector('#fx-grid');
  FX_LIST.forEach(fx => {
    const card = document.createElement('button');
    card.className = 'fx-card' + (fx.id === _cur ? ' _fxa' : '');
    card.dataset.id = fx.id;
    card.innerHTML = `<span class="fx-ci">${fx.icon}</span><span class="fx-cn">${fx.name}</span>`;
    card.title = fx.desc;
    card.onclick = () => _select(fx.id);
    grid.appendChild(card);
  });

  document.body.appendChild(p);
}

function _getLbl(id) {
  const fx = FX_LIST.find(f => f.id === id);
  return fx ? fx.name : 'Вимкнено';
}

function _toggle() {
  _open = !_open;
  document.getElementById('fx-panel')?.classList.toggle('_fxo', _open);
  document.getElementById('fx-btn')?.classList.toggle('_fxba', _open);
}

function _select(id) {
  _stop();
  _cur = id;
  localStorage.setItem(FX_KEY, id);
  document.querySelectorAll('.fx-card').forEach(c => c.classList.toggle('_fxa', c.dataset.id === id));
  const lbl = document.getElementById('fx-lbl');
  if (lbl) lbl.textContent = _getLbl(id);
  const fx = FX_LIST.find(f => f.id === id);
  if (fx) _apply(fx);
  setTimeout(_toggle, 250);
}

function _apply(fx) {
  const fns = { off:_off, particles:_particles, stars:_stars, snow:_snow, matrix:_matrix, neon:_neon, bubbles:_bubbles, aurora:_aurora, cursor:_cursor, glitch:_glitch, fire:_fire };
  (fns[fx.id] || _off)();
}

/* ── Stop ────────────────────────────────────────────────────── */
function _stop() {
  if (typeof _cleanup === 'function') { _cleanup(); _cleanup = null; }
  ['#_fx_cv','#_fx_sn','#_fx_bb','#_fx_ns','#_fx_gl','#_fx_au','#_fx_cs'].forEach(sel => {
    document.querySelector(sel)?.remove();
  });
  document.removeEventListener('mousemove', _cursorMove);
  document.removeEventListener('click', _fireClick);
  document.body.style.filter = '';
}

/* ──────────────────── EFFECTS ────────────────────────────────── */

function _off() { /* nothing */ }

/* 1. Particles — canvas з точками і лініями */
function _particles() {
  const cv = _canvas('_fx_cv', -1, .9);
  const ctx = cv.getContext('2d');
  let w = cv.width = innerWidth, h = cv.height = innerHeight;
  const pts = Array.from({length:70}, () => ({
    x:Math.random()*w, y:Math.random()*h,
    vx:(Math.random()-.5)*.5, vy:(Math.random()-.5)*.5,
    r:1+Math.random()*2.5, op:.15+Math.random()*.35
  }));
  const loop = () => {
    ctx.clearRect(0,0,w,h);
    for (let i=0;i<pts.length;i++) {
      const p=pts[i]; p.x+=p.vx; p.y+=p.vy;
      if(p.x<0||p.x>w) p.vx*=-1; if(p.y<0||p.y>h) p.vy*=-1;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(59,130,246,${p.op})`; ctx.fill();
      for (let j=i+1;j<pts.length;j++) {
        const q=pts[j], d=Math.hypot(p.x-q.x,p.y-q.y);
        if(d<110){ ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
          ctx.strokeStyle=`rgba(59,130,246,${.1*(1-d/110)})`; ctx.lineWidth=.7; ctx.stroke(); }
      }
    }
  };
  const tid = setInterval(loop,30);
  const onR = () => { w=cv.width=innerWidth; h=cv.height=innerHeight; };
  addEventListener('resize',onR);
  _cleanup = () => { clearInterval(tid); removeEventListener('resize',onR); };
}

/* 2. Stars — мерехтливі зірки */
function _stars() {
  const cv = _canvas('_fx_cv', -1);
  const ctx = cv.getContext('2d');
  let w=cv.width=innerWidth, h=cv.height=innerHeight;
  const ss = Array.from({length:180}, () => ({
    x:Math.random()*w, y:Math.random()*h,
    r:.4+Math.random()*1.6, op:Math.random(), d:(Math.random()-.5)*.025
  }));
  const loop = () => {
    ctx.clearRect(0,0,w,h);
    ss.forEach(s => {
      s.op+=s.d; if(s.op<=0||s.op>=.9) s.d*=-1;
      ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(147,197,253,${s.op})`; ctx.fill();
    });
  };
  const tid=setInterval(loop,55);
  const onR=()=>{w=cv.width=innerWidth;h=cv.height=innerHeight;};
  addEventListener('resize',onR);
  _cleanup=()=>{clearInterval(tid);removeEventListener('resize',onR);};
}

/* 3. Snow — DOM сніжинки */
function _snow() {
  const wrap = document.createElement('div');
  wrap.id='_fx_sn';
  wrap.style.cssText='position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:9990;';
  document.body.appendChild(wrap);
  const inj=_styleOnce('_fx_sn_kf',`@keyframes _sfx_sn{0%{transform:translateY(-20px) translateX(0) rotate(0);opacity:.85}100%{transform:translateY(110vh) translateX(var(--sx)) rotate(360deg);opacity:0}}`);
  for (let i=0;i<55;i++){
    const el=document.createElement('div');
    const sz=3+Math.random()*8, dur=5+Math.random()*7, delay=Math.random()*9, sx=(Math.random()-.5)*80;
    el.style.cssText=`position:absolute;left:${Math.random()*100}%;top:-16px;width:${sz}px;height:${sz}px;border-radius:50%;background:rgba(219,234,254,.8);--sx:${sx}px;animation:_sfx_sn ${dur}s linear ${delay}s infinite;`;
    wrap.appendChild(el);
  }
  _cleanup=()=>{wrap.remove();inj?.remove();};
}

/* 4. Matrix — canvas символи */
function _matrix() {
  const cv=_canvas('_fx_cv',-1,.15);
  const ctx=cv.getContext('2d');
  let w=cv.width=innerWidth,h=cv.height=innerHeight;
  const cols=Math.floor(w/15), drops=Array(cols).fill(1);
  const chars='НЕФК01NEFC01ABCDE';
  const loop=()=>{
    ctx.fillStyle='rgba(0,0,0,.05)'; ctx.fillRect(0,0,w,h);
    ctx.fillStyle='#22c55e'; ctx.font='13px monospace';
    drops.forEach((y,i)=>{
      ctx.fillText(chars[Math.floor(Math.random()*chars.length)],i*15,y*15);
      if(y*15>h&&Math.random()>.975) drops[i]=0; drops[i]++;
    });
  };
  const tid=setInterval(loop,50);
  const onR=()=>{w=cv.width=innerWidth;h=cv.height=innerHeight;};
  addEventListener('resize',onR);
  _cleanup=()=>{clearInterval(tid);removeEventListener('resize',onR);};
}

/* 5. Neon — CSS pulse */
function _neon() {
  const st=_styleOnce('_fx_ns',`
    .post-card,.post-card-gl,.page-glass-card,.sidebar-widget {
      animation:_sfx_neon 3s ease-in-out infinite !important;
    }
    @keyframes _sfx_neon {
      0%,100%{box-shadow:0 0 4px rgba(37,99,235,.2)}
      50%    {box-shadow:0 0 16px rgba(37,99,235,.5),0 0 32px rgba(14,165,233,.25)}
    }
  `);
  _cleanup=()=>st?.remove();
}

/* 6. Bubbles — DOM бульбашки */
function _bubbles() {
  const wrap=document.createElement('div');
  wrap.id='_fx_bb';
  wrap.style.cssText='position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:9990;';
  document.body.appendChild(wrap);
  const inj=_styleOnce('_fx_bb_kf',`@keyframes _sfx_bb{0%{transform:translateY(0) scale(1);opacity:.6}100%{transform:translateY(-110vh) scale(1.15);opacity:0}}`);
  const tid=setInterval(()=>{
    const b=document.createElement('div');
    const sz=6+Math.random()*22, dur=6+Math.random()*8;
    b.style.cssText=`position:absolute;left:${Math.random()*100}%;bottom:-30px;width:${sz}px;height:${sz}px;border-radius:50%;border:1px solid rgba(147,197,253,.3);background:rgba(59,130,246,.04);animation:_sfx_bb ${dur}s ease-in forwards;`;
    wrap.appendChild(b);
    setTimeout(()=>b.remove(),(dur+.5)*1000);
  },400);
  _cleanup=()=>{clearInterval(tid);wrap.remove();inj?.remove();};
}

/* 7. Aurora — shifting gradient */
function _aurora() {
  const st=_styleOnce('_fx_au',`
    body.nemk-body{animation:_sfx_au 10s linear infinite !important}
    @keyframes _sfx_au{
      0%  {filter:hue-rotate(0deg)  saturate(1)}
      50% {filter:hue-rotate(30deg) saturate(1.15)}
      100%{filter:hue-rotate(0deg)  saturate(1)}
    }
  `);
  _cleanup=()=>{st?.remove();document.body.style.filter='';};
}

/* 8. Cursor trail */
let _cursorMove=null;
function _cursor(){
  const inj=_styleOnce('_fx_cs',`@keyframes _sfx_tr{from{opacity:.8;transform:translate(-50%,-50%) scale(1)}to{opacity:0;transform:translate(-50%,-50%) scale(.05)}}`);
  _cursorMove=e=>{
    const d=document.createElement('div');
    const colors=['#3b82f6','#60a5fa','#93c5fd'];
    d.style.cssText=`position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:7px;height:7px;border-radius:50%;background:${colors[Math.floor(Math.random()*colors.length)]};pointer-events:none;z-index:99995;animation:_sfx_tr .5s ease forwards;`;
    document.body.appendChild(d);
    setTimeout(()=>d.remove(),550);
  };
  document.addEventListener('mousemove',_cursorMove);
  _cleanup=()=>{document.removeEventListener('mousemove',_cursorMove);inj?.remove();};
}

/* 9. Glitch */
function _glitch(){
  const st=_styleOnce('_fx_gl',`
    .post-card,.post-card-gl,.page-glass-card{animation:_sfx_gl 7s ease-in-out infinite !important}
    @keyframes _sfx_gl{
      0%,90%,100%{transform:none;filter:none}
      92%{transform:translateX(-2px);filter:hue-rotate(80deg) brightness(1.15)}
      93%{transform:translateX(2px); filter:hue-rotate(-40deg)}
      94%{transform:none;           filter:brightness(.9)}
      96%{transform:translateX(1px);filter:saturate(2.5)}
      97%{transform:none;           filter:none}
    }
  `);
  _cleanup=()=>st?.remove();
}

/* 10. Fireworks on click */
let _fireClick=null;
function _fire(){
  const inj=_styleOnce('_fx_cs',`
    body *{cursor:crosshair !important}
    @keyframes _sfx_fw{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(var(--fdx),var(--fdy)) scale(.1);opacity:0}}
  `);
  _fireClick=e=>{
    const cols=['#2563eb','#3b82f6','#60a5fa','#f59e0b','#22c55e','#f87171','#fff'];
    for(let i=0;i<20;i++){
      const p=document.createElement('div');
      const a=(i/20)*Math.PI*2, d=35+Math.random()*70;
      const sz=3+Math.random()*6;
      p.style.cssText=`position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:${sz}px;height:${sz}px;border-radius:50%;background:${cols[i%cols.length]};pointer-events:none;z-index:99996;--fdx:${Math.cos(a)*d}px;--fdy:${Math.sin(a)*d}px;animation:_sfx_fw .7s ease forwards;`;
      document.body.appendChild(p);
      setTimeout(()=>p.remove(),800);
    }
  };
  document.addEventListener('click',_fireClick);
  _cleanup=()=>{document.removeEventListener('click',_fireClick);inj?.remove();document.body.style.cursor='';};
}

/* ── Helpers ─────────────────────────────────────────────────── */
function _canvas(id, zIndex=-1, opacity=1){
  const cv=document.createElement('canvas');
  cv.id=id;
  cv.style.cssText=`position:fixed;inset:0;z-index:${zIndex};pointer-events:none;opacity:${opacity};`;
  document.body.appendChild(cv);
  return cv;
}
function _styleOnce(id, css){
  if(document.getElementById(id)) return null;
  const s=document.createElement('style'); s.id=id; s.textContent=css;
  document.head.appendChild(s); return s;
}

/* ── CSS ─────────────────────────────────────────────────────── */
function _css(){
  if(document.getElementById('_fx_css')) return;
  const s=document.createElement('style'); s.id='_fx_css';
  s.textContent=`
    /* Кнопка */
    #fx-btn{
      position:fixed;bottom:1.5rem;left:1.5rem;
      display:flex;align-items:center;gap:.4rem;
      padding:.38rem .85rem;
      background:var(--card);
      backdrop-filter:blur(20px);
      border:1px solid var(--divider);
      border-radius:50px;
      color:var(--text2);font-size:.76rem;font-weight:700;
      cursor:pointer;z-index:9980;
      box-shadow:var(--shadow);
      transition:background .15s,color .15s,border-color .15s,transform .15s;
      -webkit-tap-highlight-color:transparent;
    }
    #fx-btn:hover{background:var(--hover-bg);color:var(--p);border-color:rgba(37,99,235,.2);transform:translateY(-1px);}
    #fx-btn._fxba{background:var(--p);color:#fff;border-color:transparent;}
    .fx-btn-ico{flex-shrink:0;color:currentColor;}
    .fx-btn-lbl{letter-spacing:.02em;}

    /* Панель */
    #fx-panel{
      position:fixed;bottom:4rem;left:1.5rem;
      width:310px;
      background:var(--card);
      backdrop-filter:blur(28px) saturate(180%);
      border:1px solid var(--divider);
      border-radius:18px;
      box-shadow:var(--shadow-lg);
      z-index:9979;
      transform:scale(.9) translateY(10px);
      opacity:0;pointer-events:none;
      transition:transform .3s cubic-bezier(.34,1.56,.64,1),opacity .2s;
      overflow:hidden;
    }
    #fx-panel._fxo{transform:scale(1) translateY(0);opacity:1;pointer-events:all;}

    /* Header */
    .fx-ph{
      display:flex;align-items:center;justify-content:space-between;
      padding:.7rem .9rem;
      border-bottom:1px solid var(--divider);
    }
    .fx-pt{display:flex;align-items:center;gap:.4rem;font-size:.82rem;font-weight:700;color:var(--text);}
    .fx-close{
      width:22px;height:22px;border-radius:50%;
      background:var(--hover-bg);border:1px solid var(--divider);
      color:var(--muted);cursor:pointer;
      display:flex;align-items:center;justify-content:center;
      transition:background .12s,color .12s;
    }
    .fx-close:hover{background:var(--red);color:#fff;border-color:transparent;}

    /* Grid */
    .fx-grid{
      display:grid;grid-template-columns:repeat(3,1fr);
      gap:.35rem;padding:.65rem;
    }
    .fx-card{
      display:flex;flex-direction:column;align-items:center;
      gap:.28rem;padding:.6rem .4rem;
      border-radius:11px;
      background:var(--bg3);
      border:1.5px solid transparent;
      cursor:pointer;
      transition:background .15s,border-color .15s,transform .15s;
      -webkit-tap-highlight-color:transparent;
    }
    .fx-card:hover{background:var(--hover-bg);transform:translateY(-2px);}
    .fx-card._fxa{
      border-color:var(--p);
      background:rgba(37,99,235,.08);
    }
    .fx-ci{font-size:1.35rem;line-height:1;}
    .fx-cn{font-size:.7rem;font-weight:700;color:var(--text);text-align:center;}

    /* Footer */
    .fx-pf{
      display:flex;align-items:center;gap:.5rem;
      padding:.5rem .9rem;
      border-top:1px solid var(--divider);
      font-size:.75rem;color:var(--muted);
    }
    .fx-pf-dot{
      width:6px;height:6px;border-radius:50%;background:var(--green);
      box-shadow:0 0 6px var(--green);flex-shrink:0;
    }

    /* Mobile */
    @media(max-width:480px){
      #fx-btn{bottom:1.2rem;left:1.2rem;padding:.32rem .7rem;}
      #fx-panel{width:calc(100vw - 1.5rem);left:.75rem;bottom:3.8rem;}
    }
  `;
  document.head.appendChild(s);
}
