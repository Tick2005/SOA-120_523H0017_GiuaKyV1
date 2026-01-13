// ui/js/otp.js
import { getMe, verifyOtp, expireOtp, confirmPayment, cancelTransaction, createPaymentInit } from './api.js';

const alertDiv = document.getElementById('otp-alert');
const verifyBtn = document.getElementById('verify-btn');
const verifySpinner = document.getElementById('verify-spinner');
const resendBtn = document.getElementById('resend-btn');
const resendTimer = document.getElementById('resend-timer');
const otpInput = document.getElementById('otp-code');
const devOtpHint = document.getElementById('dev-otp-hint');
const instructions = document.getElementById('otp-instructions');

let context = null;
let countdown = 60;
let timerId = null;
let lastSentOtp = null;

function showAlert(msg, type = 'info') {
  alertDiv.innerHTML = msg;
  alertDiv.className = `alert alert-${type}`;
  alertDiv.classList.remove('d-none');
}

function maskEmail(email) {
  if (!email || !email.includes('@')) return email || '';
  const [user, domain] = email.split('@');
  const visible = user.slice(0, 2);
  return `${visible}${'*'.repeat(Math.max(0, user.length - 2))}@${domain}`;
}

function startTimer() {
  resendBtn.disabled = true;
  countdown = 60;
  resendTimer.textContent = countdown.toString();
  clearInterval(timerId);
  timerId = setInterval(() => {
    countdown -= 1;
    resendTimer.textContent = countdown.toString();
    if (countdown <= 0) {
      clearInterval(timerId);
      resendBtn.disabled = false;
    }
  }, 1000);
}

async function init() {
  // 1) Load payment context
  const raw = sessionStorage.getItem('paymentContext');
  if (!raw) {
    window.location.replace('/payment.html');
    return;
  }
  try {
    context = JSON.parse(raw);
  } catch {
    window.location.replace('/payment.html');
    return;
  }
  if (!context?.student_code) {
    window.location.replace('/payment.html');
    return;
  }

  // 2) Load user for display
  try {
    const me = await getMe();
    instructions.textContent = `Vui lòng nhập mã OTP gồm 6 chữ số được gửi đến email ${maskEmail(me?.email)}.`;
  } catch (e) {
    // if unauthorized, auth-check will redirect anyway
  }

  // 3) Show success message from context (OTP already sent during payment init)
  if (context.message) {
    showAlert(`<i class="fas fa-paper-plane me-2"></i>${context.message}`, 'success');
  } else {
    showAlert('<i class="fas fa-paper-plane me-2"></i>OTP đã được gửi đến email của bạn.', 'success');
  }
  
  // Start timer for resend
  startTimer();
}

async function sendOtpNow() {
  try {
    // Resend OTP: Call /api/transactions/init again with same student_code
    // Backend will automatically expire old OTP and create new one
    // This maintains the same transaction but generates fresh OTP
    const res = await createPaymentInit(context?.student_code);
    
    // Update transaction_id in case it changed (though it should be same)
    if (res?.transaction_id) {
      context.transaction_id = res.transaction_id;
      sessionStorage.setItem('paymentContext', JSON.stringify(context));
    }
    
    // Backend may return otp_code in dev mode for testing
    lastSentOtp = res?.otp_code || null;
    if (devOtpHint && lastSentOtp) {
      devOtpHint.style.display = 'block';
      devOtpHint.textContent = `Mã OTP (dev): ${lastSentOtp}`;
    }
    
    showAlert('<i class="fas fa-paper-plane me-2"></i>OTP mới đã được gửi đến email của bạn.', 'success');
    startTimer();
  } catch (err) {
    showAlert(`<i class="fas fa-exclamation-triangle me-2"></i>${err.message}`, 'danger');
  }
}

async function onVerify() {
  const code = (otpInput.value || '').trim();
  if (!code || code.length !== 6) {
    showAlert('Vui lòng nhập đủ 6 chữ số OTP.', 'warning');
    return;
  }
  
  // Validate numeric only
  if (!/^\d{6}$/.test(code)) {
    showAlert('OTP chỉ được chứa số. Vui lòng nhập lại.', 'warning');
    return;
  }
  
  verifyBtn.disabled = true;
  verifySpinner.classList.remove('d-none');

  try {
    console.log('[otp] Submitting confirm for code=', code, 'devHint=', lastSentOtp);
    // Instead of verifying OTP on the client (which would mark it used),
    // call the server-side confirm endpoint which will perform the single
    // authoritative OTP verification and then complete the payment atomically.
    // This avoids the double-verify race where frontend consumes the OTP and
    // the payment service cannot verify it again.
    const result = await confirmPayment(context.transaction_id, code, context.student_code);

  // 4) Store success data and redirect to success page
    sessionStorage.removeItem('paymentContext');
    
    // Backend returns: { success, message, transaction: { id, customer_id, tuition_id, amount, status, created_at }, new_balance }
    // Generate transaction_code from id (backend uses TXN{id:08d} format)
    const transactionCode = `TXN${String(result.transaction.id).padStart(8, '0')}`;
    
    sessionStorage.setItem('paymentSuccess', JSON.stringify({
      transaction_code: transactionCode,
      student_code: context.student_code,
      amount: result.transaction.amount,
      new_balance: result.new_balance,
      created_at: result.transaction.created_at
    }));
    window.location.replace('/success.html');
    
  } catch (err) {
    // Handle OTP verification errors
    console.error('OTP Verify Error:', err.message);
    if (err && err.body) console.error('OTP Confirm Error body:', err.body);
    
    // Show error message directly from backend
    const errMessage = err.message || 'Lỗi khi xác thực OTP';
    showAlert(`<i class="fas fa-exclamation-triangle me-2"></i>${errMessage}`, 'danger');
    
    // Clear input for retry
    otpInput.value = '';
    otpInput.focus();
  } finally {
    verifyBtn.disabled = false;
    verifySpinner.classList.add('d-none');
  }
}

// Events
verifyBtn.addEventListener('click', onVerify);
resendBtn.addEventListener('click', async () => {
  await sendOtpNow();
});

// Intercept "Back to payment" link to cancel pending transaction first
const backLink = document.querySelector('a[href="/payment.html"]');
if (backLink) {
  backLink.addEventListener('click', async (e) => {
    e.preventDefault();
    try {
      if (context?.transaction_id) {
        await cancelTransaction(context.transaction_id);
      }
    } catch (err) {
      console.warn('Failed to cancel transaction on back:', err.message || err);
    }
    window.location.href = '/payment.html';
  });
}

// Try to cancel pending transaction on page unload (best-effort)
window.addEventListener('beforeunload', (e) => {
  try {
    if (context?.transaction_id) {
      // best-effort synchronous-ish request
      navigator.sendBeacon(`${window.location.origin}/api/transactions/${context.transaction_id}/cancel`);
    }
  } catch (_) {
    // ignore
  }
});

// Auto-focus input and init
otpInput?.focus();
init();
