// ui/js/auth-check.js
// Prevent authenticated pages from being accessed after logout via back button

import { getMe } from './api.js';

export async function requireAuth() {
  try {
    // Try to get current user
    await getMe();
    // If successful, user is authenticated - allow access
    return true;
  } catch (err) {
    // If failed, user is not authenticated - redirect to login
    console.warn('Authentication required, redirecting to login');
    window.location.replace('/');
    return false;
  }
}

// Prevent page from being cached
if (window.performance && performance.navigation.type === 2) {
  // Page was accessed via back/forward button
  console.log('Page accessed via back button, revalidating auth...');
  window.location.replace('/');
}
