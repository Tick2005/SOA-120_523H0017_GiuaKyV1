// ui/js/login.js
import { login } from './api.js';

const form = document.getElementById('login-form');
const alert = document.getElementById('login-alert');
const spinner = document.getElementById('login-spinner');
const text = document.querySelector('.login-text');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  alert.classList.add('d-none');
  spinner.classList.remove('d-none');
  text.textContent = 'Đang đăng nhập...';

  try {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    if (!username || !password) throw new Error('Vui lòng nhập đầy đủ thông tin');

    await login(username, password);
    window.location.href = 'payment.html';
  } catch (err) {
    alert.textContent = err.message;
    alert.classList.remove('d-none');
  } finally {
    spinner.classList.add('d-none');
    text.textContent = 'Đăng nhập';
  }
});