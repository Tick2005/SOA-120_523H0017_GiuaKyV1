// ui/js/success.js
import { getMe } from './api.js';

const txnCodeEl = document.getElementById('txn-code');
const studentCodeEl = document.getElementById('student-code');
const amountEl = document.getElementById('amount');
const newBalanceEl = document.getElementById('new-balance');
const createdAtEl = document.getElementById('created-at');
const countdownEl = document.getElementById('countdown');

let countdown = 30;
let timerId = null;

async function init() {
  // Load transaction data from sessionStorage
  const rawData = sessionStorage.getItem('paymentSuccess');
  if (!rawData) {
    // No success data, redirect to payment page
    window.location.replace('/payment.html');
    return;
  }

  try {
    const data = JSON.parse(rawData);
    
    // Display transaction details
    txnCodeEl.textContent = data.transaction_code || 'N/A';
    studentCodeEl.textContent = data.student_code || 'N/A';
    amountEl.textContent = new Intl.NumberFormat('vi-VN').format(data.amount || 0) + ' VNĐ';
    newBalanceEl.textContent = new Intl.NumberFormat('vi-VN').format(data.new_balance || 0) + ' VNĐ';
    
    if (data.created_at) {
      const date = new Date(data.created_at);
      createdAtEl.textContent = new Intl.DateTimeFormat('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } else {
      createdAtEl.textContent = 'N/A';
    }

    // Clear sessionStorage after display
    sessionStorage.removeItem('paymentSuccess');
    sessionStorage.removeItem('paymentContext');

    // Start countdown timer
    startCountdown();
  } catch (err) {
    console.error('Failed to parse success data:', err);
    window.location.replace('/payment.html');
  }
}

function startCountdown() {
  countdownEl.textContent = countdown.toString();
  timerId = setInterval(() => {
    countdown -= 1;
    countdownEl.textContent = countdown.toString();
    if (countdown <= 0) {
      clearInterval(timerId);
      window.location.replace('/payment.html');
    }
  }, 1000);
}

init();
