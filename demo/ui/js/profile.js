// ui/js/profile.js
import { getMe, apiCall } from './api.js';

let currentUser = null;

async function loadProfile() {
  try {
    currentUser = await getMe();
    document.getElementById('view-username').textContent = currentUser.username;
    document.getElementById('view-fullname').textContent = currentUser.full_name || 'N/A';
    document.getElementById('view-phone').textContent = currentUser.phone_number || 'N/A';
    document.getElementById('view-email').textContent = currentUser.email;
    document.getElementById('view-balance').textContent = currentUser.balance.toLocaleString() + '₫';
    document.getElementById('view-id').textContent = '#' + currentUser.id;
    
    // Pre-fill form with current values
    document.getElementById('new-username').placeholder = `Hiện tại: ${currentUser.username}`;
    document.getElementById('new-email').placeholder = `Hiện tại: ${currentUser.email}`;
    document.getElementById('new-fullname').placeholder = `Hiện tại: ${currentUser.full_name || 'N/A'}`;
    document.getElementById('new-phone').placeholder = `Hiện tại: ${currentUser.phone_number || 'N/A'}`;
  } catch (err) {
    showAlert('danger', 'Lỗi: ' + err.message);
  }
}

function showAlert(type, message) {
  const alertDiv = document.getElementById('update-alert');
  if (!alertDiv) {
    console.error('Alert div not found');
    return;
  }
  alertDiv.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  </div>`;
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initProfile);
} else {
  initProfile();
}

function initProfile() {
  const updateForm = document.getElementById('update-form');
  if (!updateForm) {
    console.error('Update form not found');
    return;
  }

  updateForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newUsername = document.getElementById('new-username').value.trim();
    const newEmail = document.getElementById('new-email').value.trim();
    const newFullname = document.getElementById('new-fullname').value.trim();
    const newPhone = document.getElementById('new-phone').value.trim();
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Validation
    if (!newUsername && !newEmail && !newFullname && !newPhone && !newPassword) {
      showAlert('warning', 'Vui lòng nhập ít nhất một trường cần thay đổi');
      return;
    }
    
    if (newPassword) {
      if (!currentPassword) {
        showAlert('warning', 'Vui lòng nhập mật khẩu hiện tại để đổi mật khẩu');
        return;
      }
      if (newPassword.length < 6) {
        showAlert('warning', 'Mật khẩu mới phải có ít nhất 6 ký tự');
        return;
      }
      if (newPassword !== confirmPassword) {
        showAlert('warning', 'Mật khẩu mới và xác nhận không khớp');
        return;
      }
    }
    
    try {
      const updateData = {};
      if (newUsername) updateData.username = newUsername;
      if (newEmail) updateData.email = newEmail;
      if (newFullname) updateData.full_name = newFullname;
      if (newPhone) updateData.phone_number = newPhone;
      if (newPassword) {
        updateData.current_password = currentPassword;
        updateData.new_password = newPassword;
      }
      
      const response = await apiCall('/api/auth/profile', {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });
      
      showAlert('success', response.message || 'Cập nhật thông tin thành công!');
      
      // Clear password fields
      document.getElementById('current-password').value = '';
      document.getElementById('new-password').value = '';
      document.getElementById('confirm-password').value = '';
      
      // Clear other fields
      document.getElementById('new-username').value = '';
      document.getElementById('new-email').value = '';
      document.getElementById('new-fullname').value = '';
      document.getElementById('new-phone').value = '';
      
      // Reload profile
      await loadProfile();
      
    } catch (err) {
      showAlert('danger', 'Lỗi: ' + err.message);
    }
  });

  // Load profile data
  loadProfile();
}