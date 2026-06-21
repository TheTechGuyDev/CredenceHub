// ─────────────────────────────────────────
// CREDENCEHUB — MAIN JAVASCRIPT
// Full mobile responsive support
// ─────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {

  // ── Initialize Lucide Icons ──
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // ── Theme Management ──
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');
  const html = document.documentElement;

  const savedTheme = localStorage.getItem('ch_theme') || 'light';
  html.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const current = html.getAttribute('data-theme');
      const next = current === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('ch_theme', next);
      updateThemeIcon(next);
      if (typeof lucide !== 'undefined') lucide.createIcons();
    });
  }

  function updateThemeIcon(theme) {
    if (!themeIcon) return;
    themeIcon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  // ── Sidebar Toggle (Desktop) ──
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mainContent = document.getElementById('mainContent');

  // Only apply collapsed state on non-mobile
  if (window.innerWidth > 768) {
    const sidebarCollapsed = localStorage.getItem('ch_sidebar_collapsed') === 'true';
    if (sidebarCollapsed && sidebar) {
      sidebar.classList.add('collapsed');
      if (mainContent) mainContent.classList.add('sidebar-collapsed');
    }
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      if (!sidebar || window.innerWidth <= 768) return;
      const isCollapsed = sidebar.classList.toggle('collapsed');
      if (mainContent) mainContent.classList.toggle('sidebar-collapsed', isCollapsed);
      localStorage.setItem('ch_sidebar_collapsed', isCollapsed);
      if (typeof lucide !== 'undefined') lucide.createIcons();
    });
  }

  // ── Mobile Sidebar ──
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileOverlay = document.getElementById('mobileOverlay');

  window.openMobileSidebar = function () {
    if (sidebar) sidebar.classList.add('mobile-open');
    if (mobileOverlay) mobileOverlay.classList.add('show');
    document.body.style.overflow = 'hidden';
  };

  window.closeMobileSidebar = function () {
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (mobileOverlay) mobileOverlay.classList.remove('show');
    document.body.style.overflow = '';
  };

  function checkMobile() {
    if (!mobileMenuBtn) return;
    if (window.innerWidth <= 768) {
      mobileMenuBtn.style.display = 'flex';
      // Ensure sidebar is hidden on mobile unless opened
      if (sidebar && !sidebar.classList.contains('mobile-open')) {
        sidebar.style.transform = 'translateX(-100%)';
      }
    } else {
      mobileMenuBtn.style.display = 'none';
      // Ensure overlay is closed on desktop
      closeMobileSidebar();
      if (sidebar) sidebar.style.transform = '';
    }
  }

  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', openMobileSidebar);
  }

  // Close mobile sidebar on overlay click
  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', closeMobileSidebar);
  }

  // Close mobile sidebar on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeMobileSidebar();
      // Also close modals
      document.querySelectorAll('.modal-overlay.show').forEach(function (overlay) {
        overlay.classList.remove('show');
        document.body.style.overflow = '';
      });
    }
  });

  window.addEventListener('resize', checkMobile);
  checkMobile();

  // ── User Menu Dropdown ──
  const userMenuBtn = document.getElementById('userMenuBtn');
  const userMenu = document.getElementById('userMenu');

  if (userMenuBtn && userMenu) {
    userMenuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      userMenu.classList.toggle('show');
    });
  }

  // ── Close all dropdowns on outside click ──
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.dropdown-menu.show').forEach(function (menu) {
      if (!menu.contains(e.target) && !menu.previousElementSibling.contains(e.target)) {
        menu.classList.remove('show');
      }
    });
  });

  // ── Generic Dropdown Toggle ──
  document.querySelectorAll('[data-dropdown]').forEach(function (trigger) {
    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      const targetId = this.getAttribute('data-dropdown');
      const menu = document.getElementById(targetId);
      if (menu) menu.classList.toggle('show');
    });
  });

  // ── Modal Management ──
  window.openModal = function (modalId) {
    const overlay = document.getElementById(modalId);
    if (overlay) {
      overlay.classList.add('show');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = function (modalId) {
    const overlay = document.getElementById(modalId);
    if (overlay) {
      overlay.classList.remove('show');
      document.body.style.overflow = '';
    }
  };

  // Close modal on overlay click
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        overlay.classList.remove('show');
        document.body.style.overflow = '';
      }
    });
  });

  // ── Toast Notifications ──
  window.showToast = function (message, type) {
    type = type || 'info';
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const icons = {
      success: 'check-circle',
      danger: 'x-circle',
      warning: 'alert-triangle',
      info: 'info'
    };

    const colors = {
      success: 'var(--success)',
      danger: 'var(--danger)',
      warning: 'var(--warning)',
      info: 'var(--info)'
    };

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
      <span class="toast-icon">
        <i data-lucide="${icons[type] || 'info'}"
           style="color:${colors[type] || colors.info}; width:16px; height:16px;"></i>
      </span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.closest('.toast').remove()">
        <i data-lucide="x" style="width:14px; height:14px;"></i>
      </button>
    `;

    container.appendChild(toast);
    if (typeof lucide !== 'undefined') lucide.createIcons();

    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(function () { toast.remove(); }, 300);
    }, 5000);
  };

  // ── Number Formatting ──
  window.formatCurrency = function (value, currency) {
    currency = currency || 'USD';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value || 0);
  };

  window.formatNumber = function (value, decimals) {
    decimals = decimals !== undefined ? decimals : 0;
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value || 0);
  };

  window.formatPercent = function (value, decimals) {
    decimals = decimals !== undefined ? decimals : 1;
    return (value || 0).toFixed(decimals) + '%';
  };

  // ── Confirm Delete ──
  window.confirmDelete = function (message, callback) {
    message = message || 'Are you sure you want to delete this item?';
    if (confirm(message)) {
      if (typeof callback === 'function') callback();
    }
  };

  // ── Form Validation ──
  window.validateForm = function (formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    let valid = true;
    form.querySelectorAll('[required]').forEach(function (field) {
      if (!field.value.trim()) {
        field.style.borderColor = 'var(--danger)';
        valid = false;
      } else {
        field.style.borderColor = '';
      }
    });
    return valid;
  };

  // ── Table Sort ──
  document.querySelectorAll('th[data-sort]').forEach(function (th) {
    th.style.cursor = 'pointer';
    th.addEventListener('click', function () {
      const table = this.closest('table');
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const col = Array.from(this.parentElement.children).indexOf(this);
      const asc = this.getAttribute('data-order') !== 'asc';

      rows.sort(function (a, b) {
        const aVal = a.children[col] ? a.children[col].textContent.trim() : '';
        const bVal = b.children[col] ? b.children[col].textContent.trim() : '';
        const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
          return asc ? aNum - bNum : bNum - aNum;
        }
        return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      });

      rows.forEach(function (row) { tbody.appendChild(row); });
      th.setAttribute('data-order', asc ? 'asc' : 'desc');
    });
  });

  // ── Search Filter ──
  window.filterTable = function (inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;

    input.addEventListener('keyup', function () {
      const filter = this.value.toLowerCase();
      table.querySelectorAll('tbody tr').forEach(function (row) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  };

  // ── Copy to Clipboard ──
  window.copyToClipboard = function (text, btnEl) {
    navigator.clipboard.writeText(text).then(function () {
      showToast('Copied to clipboard!', 'success');
      if (btnEl) {
        const original = btnEl.innerHTML;
        btnEl.innerHTML = '<i data-lucide="check" style="width:14px;height:14px;"></i>';
        if (typeof lucide !== 'undefined') lucide.createIcons();
        setTimeout(function () {
          btnEl.innerHTML = original;
          if (typeof lucide !== 'undefined') lucide.createIcons();
        }, 2000);
      }
    });
  };

  // ── Tabs ──
  document.querySelectorAll('[data-tab-group]').forEach(function (tabGroup) {
    const groupName = tabGroup.getAttribute('data-tab-group');
    const tabs = document.querySelectorAll(`[data-tab="${groupName}"]`);
    const panels = document.querySelectorAll(`[data-tab-panel="${groupName}"]`);

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        const target = this.getAttribute('data-tab-target');
        tabs.forEach(function (t) { t.classList.remove('active'); });
        panels.forEach(function (p) { p.style.display = 'none'; });
        this.classList.add('active');
        const panel = document.getElementById(target);
        if (panel) panel.style.display = 'block';
      });
    });

    if (tabs.length > 0) tabs[0].click();
  });

  // ── Smooth scroll ──
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Auto dismiss toasts ──
  document.querySelectorAll('.toast').forEach(function (toast) {
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(function () { toast.remove(); }, 300);
    }, 5000);
  });

});