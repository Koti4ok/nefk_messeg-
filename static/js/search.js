/**
 * НЕФК Суспільство — live AJAX пошук з fuzzy підтримкою
 * Dropdown в navbar: юзери + пости + групи
 */
(function () {
  'use strict';

  const input    = document.getElementById('nav-search-input');
  const dropdown = document.getElementById('search-dropdown');
  const body     = document.getElementById('search-dropdown-body');
  const allLink  = document.getElementById('search-all-link');
  if (!input || !dropdown) return;

  let timer = null;

  function esc(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderDropdown(data) {
    let html = '';
    const q = data.query || '';

    if (data.users && data.users.length) {
      html += `<div class="srch-section-label">👤 Люди</div>`;
      data.users.forEach(u => {
        html += `
          <a href="${esc(u.url)}" class="srch-item">
            <img src="${esc(u.avatar)}" class="srch-avatar" alt="">
            <div class="srch-info">
              <div class="srch-name">${esc(u.full_name)}</div>
              <div class="srch-sub">@${esc(u.username)}</div>
            </div>
          </a>`;
      });
    }

    if (data.posts && data.posts.length) {
      html += `<div class="srch-section-label">📝 Пости</div>`;
      data.posts.forEach(p => {
        html += `
          <a href="${esc(p.url)}" class="srch-item">
            <img src="${esc(p.author_avatar)}" class="srch-avatar srch-avatar-sm" alt="">
            <div class="srch-info">
              <div class="srch-name srch-post-text">${esc(p.content)}</div>
              <div class="srch-sub">${esc(p.author)}</div>
            </div>
          </a>`;
      });
    }

    if (data.groups && data.groups.length) {
      html += `<div class="srch-section-label">👥 Групи</div>`;
      data.groups.forEach(g => {
        html += `
          <a href="${esc(g.url)}" class="srch-item">
            <img src="${esc(g.avatar)}" class="srch-avatar" alt="">
            <div class="srch-info">
              <div class="srch-name">${esc(g.name)}</div>
              <div class="srch-sub">${g.members} учасників</div>
            </div>
          </a>`;
      });
    }

    const total = (data.users || []).length +
                  (data.posts || []).length +
                  (data.groups || []).length;
    if (total === 0) {
      html = `<div class="srch-empty">Нічого не знайдено 🤷</div>`;
    }

    body.innerHTML = html;
    if (allLink) allLink.href = `/search/?q=${encodeURIComponent(q)}`;
    dropdown.style.display = 'block';
  }

  function hideDropdown() {
    dropdown.style.display = 'none';
  }

  // Live пошук з debounce 280мс
  input.addEventListener('input', function () {
    clearTimeout(timer);
    const q = this.value.trim();
    if (q.length < 2) { hideDropdown(); return; }
    timer = setTimeout(() => {
      fetch(`/api/search/?q=${encodeURIComponent(q)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      })
        .then(r => r.json())
        .then(renderDropdown)
        .catch(() => {});
    }, 280);
  });

  // Закрити при кліку поза dropdown
  document.addEventListener('click', function (e) {
    const wrapper = document.getElementById('search-wrapper');
    if (wrapper && !wrapper.contains(e.target)) hideDropdown();
  });

  // Закрити при Escape
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { hideDropdown(); this.blur(); }
  });

  // При фокусі — показати якщо вже є текст і результати
  input.addEventListener('focus', function () {
    if (this.value.trim().length >= 2 && body && body.innerHTML.trim()) {
      dropdown.style.display = 'block';
    }
  });
})();
