// ui/js/api.js
const API_BASE = 'http://localhost:8080';

export async function apiCall(endpoint, options = {}) {
  const config = {
    method: options.method || 'GET',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
  };
  if (options.body) config.body = options.body;

  const res = await fetch(`${API_BASE}${endpoint}`, config);
  if (!res.ok) {
    // Try parse JSON body; if parsing fails, fall back to raw text so UI can show server message
    let errBody = {};
    try {
      errBody = await res.json();
    } catch (jsonErr) {
      try {
        const txt = await res.text();
        errBody = txt ? { message: txt } : {};
      } catch (_e) {
        errBody = {};
      }
    }
    const e = new Error(errBody.error || (errBody.detail && (errBody.detail.error || JSON.stringify(errBody.detail))) || errBody.message || 'Lỗi hệ thống');
    e.status = res.status;
    e.body = errBody; // attach full parsed body for callers to inspect structured details
    throw e;
  }
  return res.json();
}

// Internal helper for simple calls
async function simpleCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${endpoint}`, options);
  if (!res.ok) {
    let errBody = {};
    try {
      errBody = await res.json();
    } catch (jsonErr) {
      try {
        const txt = await res.text();
        errBody = txt ? { message: txt } : {};
      } catch (_e) {
        errBody = {};
      }
    }
    const e = new Error(errBody.error || (errBody.detail && (errBody.detail.error || JSON.stringify(errBody.detail))) || errBody.message || 'Lỗi hệ thống');
    e.status = res.status;
    e.body = errBody;
    throw e;
  }
  return res.json();
}

// Auth
export const login = (username, password) => simpleCall('/api/auth/login', 'POST', { username, password });
export const logout = () => simpleCall('/api/auth/logout', 'POST');
export const getMe = () => simpleCall('/api/auth/me');

// Student
export const searchStudent = (code) => simpleCall('/api/students/search', 'POST', { student_code: code });

// Payment
export const createPayment = (code) => simpleCall('/api/transactions', 'POST', { student_code: code });
export const createPaymentInit = (code) => simpleCall('/api/transactions/init', 'POST', { student_code: code });
// Confirm payment: pass otp_code and student_id in body (no transactionId in URL path)
export const confirmPayment = (transactionId, otp_code, student_code) => simpleCall('/api/transactions/confirm', 'POST', { otp_code, student_id: student_code });
export const getHistory = () => simpleCall('/api/transactions/history');
export const getTransaction = (id) => simpleCall(`/api/transactions/${id}`);
export const cancelTransaction = (transactionId) => simpleCall(`/api/transactions/${transactionId}/cancel`, 'POST', null);

// OTP (Internal APIs - not used by frontend)
// Note: Frontend uses createPaymentInit which auto-issues OTP
export const verifyOtp = (otp_code) => simpleCall('/api/otp/verify', 'POST', { otp_code });
export const expireOtp = (otp_code) => simpleCall('/api/otp/expire', 'POST', { otp_code });