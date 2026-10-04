/* ============================================================
   НЕМК Суспільство v5 — main.js
   Theme switching · AJAX likes · Notifications · AI chatbot
   ============================================================ */

// ══ THEME ══════════════════════════════════════════════════════
const THEME_KEY = 'nemk-theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  _updateThemeButtons(theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

function setTheme(theme) {
  applyTheme(theme);
}

function _updateThemeButtons(theme) {
  const btnLight = document.getElementById('btn-light-theme');
  const btnDark  = document.getElementById('btn-dark-theme');
  if (btnLight) {
    btnLight.style.opacity    = theme === 'light' ? '1'   : '.5';
    btnLight.style.fontWeight = theme === 'light' ? '700' : '400';
  }
  if (btnDark) {
    btnDark.style.opacity    = theme === 'dark' ? '1'   : '.5';
    btnDark.style.fontWeight = theme === 'dark' ? '700' : '400';
  }
}

// Init theme immediately (before DOMContentLoaded to avoid flash)
(function initTheme() {
  const saved       = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme       = saved || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
})();

// ══ DOM READY ══════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', function () {

  // Apply full theme (buttons etc.)
  const currentTheme = localStorage.getItem(THEME_KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(currentTheme);

  // ── CSRF helper ─────────────────────────────────────────────
  function getCsrf() {
    const c = document.cookie.split(';').find(x => x.trim().startsWith('csrftoken='));
    return c ? decodeURIComponent(c.split('=')[1]) : '';
  }
  // Expose globally so AI chatbot (outside DOMContentLoaded) can use it
  window.getCsrf = getCsrf;

  // ── AJAX Like ────────────────────────────────────────────────
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.dataset.url;
      if (!url) return;

      const icon      = this;
      const counter   = this.querySelector('.like-count');
      const wasLiked  = icon.classList.contains('liked');

      // Optimistic UI
      icon.classList.toggle('liked');
      icon.style.transform = 'scale(1.5)';
      setTimeout(() => { icon.style.transform = ''; }, 300);

      if (counter) {
        const n = parseInt(counter.textContent, 10) || 0;
        counter.textContent = wasLiked ? n - 1 : n + 1;
      }

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrf(),
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
        .then(r => r.json())
        .then(data => {
          if (counter) counter.textContent = data.count;
          icon.classList.toggle('liked', !!data.liked);
        })
        .catch(() => {
          // Revert on error
          icon.classList.toggle('liked');
          if (counter) {
            const n = parseInt(counter.textContent, 10) || 0;
            counter.textContent = wasLiked ? n + 1 : n - 1;
          }
        });
    });
  });

  // ── Notification badge polling ───────────────────────────────
  const badge = document.getElementById('notif-badge');
  if (badge) {
    function updateBadge() {
      fetch('/notifications/unread/')
        .then(r => r.json())
        .then(data => {
          if (data.count > 0) {
            badge.textContent = data.count > 99 ? '99+' : data.count;
            badge.classList.remove('d-none');
          } else {
            badge.classList.add('d-none');
          }
        })
        .catch(() => {});
    }
    updateBadge();
    setInterval(updateBadge, 15000);
  }

  // ── Auto-dismiss flash alerts ────────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('#flash-container .alert-dismissible').forEach(el => {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(-8px)';
      setTimeout(() => el.remove(), 400);
    });
  }, 4000);

  // ── Scroll reveal ────────────────────────────────────────────
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
          // Animate rating bars
          entry.target.querySelectorAll('.rating-bar-fill').forEach(bar => {
            const w = bar.getAttribute('data-width') || bar.style.width;
            bar.setAttribute('data-width', w);
            bar.style.width = '0';
            requestAnimationFrame(() => { bar.style.width = w; });
          });
        }, i * 70);
        revealObs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => revealObs.observe(el));

  // ── Hero particles ───────────────────────────────────────────
  const pc = document.getElementById('hero-particles');
  if (pc) {
    for (let i = 0; i < 55; i++) {
      const s  = document.createElement('div');
      const sz = Math.random() * 4 + 1.5;
      s.className = 'particle';
      s.style.cssText = `
        left: ${Math.random() * 100}%;
        width: ${sz}px; height: ${sz}px;
        background: rgba(255,255,255,${(Math.random() * .5 + .1).toFixed(2)});
        animation-duration: ${(Math.random() * 14 + 8).toFixed(1)}s;
        animation-delay: ${(Math.random() * 10).toFixed(1)}s;
      `;
      pc.appendChild(s);
    }
  }

  // ── Smooth scroll ────────────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
  });

  // ── Star rating (home page reviews) ─────────────────────────
  let _selectedStars = 0;
  document.querySelectorAll('.star-opt').forEach(star => {
    star.addEventListener('mouseover', function () {
      const v = +this.dataset.v;
      document.querySelectorAll('.star-opt').forEach((s, i) => {
        s.style.color = i < v ? '#ffd60a' : '#ddd';
      });
    });
    star.addEventListener('mouseout', () => {
      document.querySelectorAll('.star-opt').forEach((s, i) => {
        s.style.color = i < _selectedStars ? '#ffd60a' : '#ddd';
      });
    });
    star.addEventListener('click', function () {
      _selectedStars = +this.dataset.v;
      document.querySelectorAll('.star-opt').forEach((s, i) => {
        s.style.color = i < _selectedStars ? '#ffd60a' : '#ddd';
      });
    });
  });
  window.selectedStars = () => _selectedStars;

  // ── Theme buttons sync ───────────────────────────────────────
  _updateThemeButtons(currentTheme);

}); // end DOMContentLoaded

// ══ AI CHATBOT ════════════════════════════════════════════════
let _aiOpen = false;

function toggleAiChat() {
  _aiOpen = !_aiOpen;
  const win  = document.getElementById('ai-chat-window');
  const icon = document.getElementById('fab-icon');
  if (win) win.classList.toggle('open', _aiOpen);
  if (icon) icon.textContent = _aiOpen ? '✕' : '🤖';
  if (_aiOpen) {
    const inp = document.getElementById('ai-input');
    if (inp) setTimeout(() => inp.focus(), 400);
    // Прокрутити до кінця повідомлень
    const box = document.getElementById('ai-messages');
    if (box) setTimeout(() => { box.scrollTop = box.scrollHeight; }, 450);
  }
}

function appendAiMsg(text, isUser) {
  const box = document.getElementById('ai-messages');
  if (!box) return;
  const d = document.createElement('div');
  d.className = `ai-msg ${isUser ? 'user' : 'bot'}`;

  const now = new Date();
  const time = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');

  // Convert markdown-like **bold** and newlines
  let html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');

  d.innerHTML = `
    <div class="ai-msg-inner">${html}</div>
    <div class="ai-msg-time">${time}</div>`;
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}

function _showAiTyping() {
  const box = document.getElementById('ai-messages');
  if (!box) return;
  const d = document.createElement('div');
  d.className = 'ai-msg bot';
  d.id = 'ai-typing';
  d.innerHTML = '<div class="ai-msg-inner"><span class="typing-dots"><span></span><span></span><span></span></span></div>';
  box.appendChild(d);
  box.scrollTop = box.scrollHeight;
}

function _removeAiTyping() {
  const el = document.getElementById('ai-typing');
  if (el) el.remove();
}

function sendAiMsg() {
  const inp = document.getElementById('ai-input');
  if (!inp) return;
  const msg = inp.value.trim();
  if (!msg) return;
  inp.value = '';
  askBot(msg);
}

function askBot(msg) {
  if (!_aiOpen) toggleAiChat();
  appendAiMsg(msg, true);
  _showAiTyping();

  fetch('/api/chatbot/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': (window.getCsrf ? window.getCsrf() : ''),
    },
    body: JSON.stringify({ message: msg }),
  })
    .then(r => r.json())
    .then(data => {
      _removeAiTyping();
      appendAiMsg(data.answer || 'Немає відповіді.', false);
    })
    .catch(() => {
      _removeAiTyping();
      appendAiMsg('😕 Помилка. Спробуй ще раз.', false);
    });
}
