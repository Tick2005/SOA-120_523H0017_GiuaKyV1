// ui/js/logout.js
import { logout } from './api.js';

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLogout);
} else {
  initLogout();
}

function initLogout() {
  const logoutBtn = document.getElementById('logout-btn');
  if (!logoutBtn) {
    console.warn('Logout button not found');
    return;
  }

  logoutBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    
    try {
      await logout();
      // Force reload to root and prevent back button from cached authenticated state
      window.location.replace('/');
    } catch (err) {
      console.error('Logout error:', err);
      alert('Lỗi đăng xuất: ' + err.message);
    }
  });
}
