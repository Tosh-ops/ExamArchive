// =========================================================
// EXAM ARCHIVE — Light interactions
// =========================================================

// ---------- Toast system ----------
window.showToast = function(message, type = 'default') {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.className = 'toast';
  if (type === 'success') toast.classList.add('success');
  if (type === 'error') toast.classList.add('error');
  toast.textContent = message;

  requestAnimationFrame(() => toast.classList.add('show'));

  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
};

// ---------- Theme toggle ----------
window.toggleTheme = function () {
  const root = document.documentElement;
  const current = root.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';

  root.classList.add('theme-switching');
  root.setAttribute('data-theme', next);
  root.style.colorScheme = (next === 'dark') ? 'dark' : 'light';

  try { localStorage.setItem('theme', next); } catch (e) {}

  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      root.classList.remove('theme-switching');
    });
  });

  updateThemeIcons();
};

function updateThemeIcons() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const moon = document.getElementById('icon-moon');
  const sun = document.getElementById('icon-sun');
  if (moon && sun) {
    if (current === 'dark') {
      moon.style.display = 'none';
      sun.style.display = 'block';
    } else {
      moon.style.display = 'block';
      sun.style.display = 'none';
    }
  }
}

// ---------- Card animation + nav ----------
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.animation = `fadeInUp 0.3s ease forwards`;
    card.style.animationDelay = `${Math.min(i * 40, 300)}ms`;
  });

  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
    });
  });

  updateThemeIcons();
});

window.addEventListener('load', () => {
  document.body.classList.add('loaded');
});