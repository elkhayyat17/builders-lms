/**
 * Builders LMS — Language Toggle
 * Handles language switching for both logged-in and guest users.
 */

(function () {
  'use strict';

  // Wait for DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    injectLanguageToggle();
  });

  function injectLanguageToggle() {
    // Find the navbar actions area
    const navbar = document.querySelector('.navbar-nav, .nav-right, [data-nav-actions]');
    if (!navbar) return;

    const currentLang = document.documentElement.lang || 'ar';
    const toggleText = currentLang === 'ar' ? 'EN' : 'ع';

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'builders-lang-toggle';
    toggleBtn.textContent = toggleText;
    toggleBtn.title = currentLang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية';
    toggleBtn.style.cssText = `
      padding: 4px 12px;
      margin: 0 8px;
      border: 1px solid rgba(255,255,255,0.3);
      border-radius: 4px;
      background: transparent;
      color: inherit;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    `;

    toggleBtn.addEventListener('mouseenter', function () {
      this.style.background = 'rgba(255,255,255,0.1)';
    });
    toggleBtn.addEventListener('mouseleave', function () {
      this.style.background = 'transparent';
    });

    toggleBtn.addEventListener('click', function () {
      const newLang = currentLang === 'ar' ? 'en' : 'ar';

      function applyAndReload() {
        document.cookie =
          'preferred_language=' +
          newLang +
          ';path=/;max-age=31536000;SameSite=Lax';
        document.documentElement.lang = newLang;
        document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
        window.location.reload();
      }

      // Check if user is logged in
      if (window.__session && window.__session.user && window.__session.user !== 'Guest') {
        // For logged-in users — update their user profile
        fetch('/api/method/frappe.client.set_value', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || '',
          },
          body: JSON.stringify({
            doctype: 'User',
            name: window.__session.user,
            fieldname: 'language',
            value: newLang,
          }),
        }).then(function () {
          applyAndReload();
        }).catch(function () {
          applyAndReload();
        });
      } else {
        applyAndReload();
      }
    });

    navbar.appendChild(toggleBtn);
  }
})();
