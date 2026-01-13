// ui/js/payment.js
import { searchStudent, getMe, createPaymentInit } from './api.js';

const searchForm = document.getElementById('search-form');
const studentInfo = document.getElementById('student-info');
const tuitionsTable = document.getElementById('tuitions-table');
const paymentSummary = document.getElementById('payment-summary');
const paymentForm = document.getElementById('payment-form');
const alertDiv = document.getElementById('payment-alert');
const codeInput = document.getElementById('student_code');

let currentStudent = null;
let currentUser = null;

// Load user info and balance
async function loadUserInfo() {
  try {
    const user = await getMe();
    currentUser = user;
    document.body.dataset.balance = user.balance;
    
    // Hiển thị thông tin người dùng (sử dụng full_name thay vì username)
    document.getElementById('user-name').textContent = user.full_name || user.username || 'N/A';
    document.getElementById('user-phone').textContent = user.phone_number || 'N/A';
    document.getElementById('user-email').textContent = user.email || 'N/A';
    document.getElementById('user-balance').textContent = new Intl.NumberFormat('vi-VN').format(user.balance) + ' VNĐ';
  } catch (err) {
    console.error('Lỗi load user info:', err);
    // Nếu không có token, chuyển về trang login
    if (err.message.includes('401') || err.message.includes('Unauthorized')) {
      alert('Vui lòng đăng nhập lại');
      window.location.href = 'index.html';
    }
  }
}
loadUserInfo();

// Tự động search khi nhập đủ 8 ký tự
codeInput.addEventListener('input', async (e) => {
  const code = e.target.value.trim();
  
  // Reset UI khi xóa
  if (code.length === 0) {
    studentInfo.classList.add('d-none');
    tuitionsTable.classList.add('d-none');
    hidePayment();
    return;
  }
  
  // Chỉ search khi đúng 8 ký tự
  if (code.length !== 8) {
    studentInfo.classList.add('d-none');
    tuitionsTable.classList.add('d-none');
    hidePayment();
    return;
  }
  
  // Auto search
  await performSearch(code);
});

// Bỏ submit form, chỉ giữ để prevent default
searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
});

async function performSearch(code) {
  try {
    const res = await searchStudent(code);
      const tuitionList = res.tuitions || res.all_tuitions || [];
      const studentObj = res.student || {};
      const studentCode = studentObj.student_code || studentObj.student_id || '';
      const studentName = studentObj.name || studentObj.student_name || '';
      const studentEmail = studentObj.email || studentObj.student_email || '';

      currentStudent = {
        student: {
          student_code: studentCode,
          name: studentName,
          email: studentEmail
        },
        tuitions: tuitionList
      };
    
    // Ẩn thông báo lỗi cũ
    alertDiv.classList.add('d-none');

    // Hiển thị thông tin SV
    studentInfo.innerHTML = `
      <h6 class="mb-3"><i class="fas fa-user-graduate me-2"></i>Thông tin sinh viên</h6>
      <div class="row">
        <div class="col-md-4">
            <p class="mb-2"><strong>Mã sinh viên:</strong> <span class="text-primary">${currentStudent.student.student_code}</span></p>
        </div>
        <div class="col-md-4">
            <p class="mb-2"><strong>Họ tên:</strong> ${currentStudent.student.name}</p>
        </div>
        <div class="col-md-4">
            <p class="mb-2"><strong>Email:</strong> ${currentStudent.student.email}</p>
        </div>
      </div>
    `;
    studentInfo.classList.remove('d-none');

        // Support both shapes returned by backend: `tuitions` or `all_tuitions`
      const unpaid = (currentStudent.tuitions || []).filter(t => t.status === 'unpaid');
    if (unpaid.length === 0) {
      tuitionsTable.innerHTML = '<p class="text-success text-center">Đã thanh toán hết học phí!</p>';
      tuitionsTable.classList.remove('d-none');
      hidePayment();
      return;
    }

    // Bảng học phí với styling đẹp hơn
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time để so sánh chỉ ngày
    
    // Phân loại học phí: còn hạn và quá hạn
    const validTuitions = [];
    const overdueTuitions = [];
    
    unpaid.forEach(t => {
      const dueDate = t.due_date ? new Date(t.due_date) : null;
      const isOverdue = dueDate && dueDate < today;
      
      if (isOverdue) {
        overdueTuitions.push(t);
      } else {
        validTuitions.push(t);
      }
    });
    
    // Business rule: backend marks only the oldest unpaid tuition with `canPay=true`.
    // Determine which tuitions are actually payable
    const payableTuitions = validTuitions.filter(t => t.canPay === true);
    const effectivePayables = (payableTuitions.length > 0) ? payableTuitions : validTuitions;
    
    // Compute total from the effective payables (respect backend canPay rule)
    let totalPayable = effectivePayables.reduce((s, t) => s + Number(t.fee || 0), 0);
    
    let table = `
      <h6 class="mb-3"><i class="fas fa-file-invoice-dollar me-2"></i>Danh sách học phí</h6>
      <table class="table table-striped table-hover">
        <thead class="table-primary">
          <tr>
            <th>Học kỳ</th>
            <th>Năm học</th>
            <th class="text-end">Học phí</th>
            <th class="text-center">Trạng thái</th>
          </tr>
        </thead>
        <tbody>`;
    
    // Hiển thị học phí còn hạn (có thể thanh toán)
    validTuitions.forEach(t => {
      
      const dueDate = t.due_date ? new Date(t.due_date) : null;
      const dueDateStr = dueDate 
        ? new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(dueDate)
        : 'Chưa có';
      // Highlight whether this tuition is the one allowed for payment
      const statusBadge = (t.canPay === true) ? '<span class="badge bg-primary">Có thể thanh toán</span>' : '<span class="badge bg-warning">Chưa thanh toán</span>';
      
      table += `
        <tr>
          <td>Học kỳ ${t.semester}</td>
          <td>${t.academic_year}</td>
          <td class="text-end"><strong>${new Intl.NumberFormat('vi-VN').format(t.fee)} VNĐ</strong></td>
          <td class="text-center">${statusBadge}</td>
        </tr>`;
    });
    
    // Hiển thị học phí quá hạn (KHÔNG được thanh toán qua hệ thống)
    overdueTuitions.forEach(t => {
      const dueDate = new Date(t.due_date);
      const dueDateStr = new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(dueDate);
      
      table += `
        <tr class="table-danger">
          <td>Học kỳ ${t.semester}</td>
          <td>${t.academic_year}</td>
          <td class="text-end"><strong>${new Intl.NumberFormat('vi-VN').format(t.fee)} VNĐ</strong></td>
          <td class="text-center"><span class="badge bg-danger"><i class="fas fa-ban"></i> Hết hạn nộp</span></td>
        </tr>`;
    });
    
    table += `</tbody></table>`;
    
    // Thêm cảnh báo nếu có học phí quá hạn
    if (overdueTuitions.length > 0) {
      const overdueTotal = overdueTuitions.reduce((sum, t) => sum + t.fee, 0);
      table = `<div class="alert alert-danger mb-3">
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Cảnh báo:</strong> Có ${overdueTuitions.length} học phí đã quá hạn (${new Intl.NumberFormat('vi-VN').format(overdueTotal)} VNĐ)!<br>
        <small>Các học phí quá hạn không thể thanh toán online. Vui lòng liên hệ phòng Tài chính để xử lý.</small>
      </div>` + table;
    }
    
    tuitionsTable.innerHTML = table;
    tuitionsTable.classList.remove('d-none');

    // Check if we have any payable tuitions
    if (effectivePayables.length === 0) {
      // Không có học phí nào có thể thanh toán
      paymentSummary.innerHTML = `<span class="text-danger">Không có học phí nào có thể thanh toán online.<br>Tất cả học phí đã quá hạn. Vui lòng liên hệ phòng Tài chính.</span>`;
      paymentSummary.classList.remove('d-none');
      hidePayment();
      return;
    }

    paymentSummary.innerHTML = `Tổng phải nộp: <strong>${new Intl.NumberFormat('vi-VN').format(totalPayable)} VNĐ</strong>${overdueTuitions.length > 0 ? '<br><small class="text-muted">(Không bao gồm học phí quá hạn)</small>' : ''}`;
    paymentSummary.classList.remove('d-none');
    paymentForm.classList.remove('d-none');
    paymentForm.dataset.total = totalPayable;
  } catch (err) {
    // Ẩn tất cả thông tin khi có lỗi
    studentInfo.classList.add('d-none');
    tuitionsTable.classList.add('d-none');
    hidePayment();
    
    // Hiển thị thông báo lỗi cụ thể
    if (err.message.includes('404') || err.message.includes('not found')) {
      showAlert(`<i class="fas fa-exclamation-circle me-2"></i>Không tìm thấy sinh viên với mã <strong>${code}</strong>`, 'warning');
    } else {
      showAlert(`<i class="fas fa-exclamation-triangle me-2"></i>${err.message}`, 'danger');
    }
  }
};

paymentForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!document.getElementById('agree').checked) {
    showAlert('Vui lòng đồng ý điều khoản', 'warning');
    return;
  }

  const spinner = document.getElementById('pay-spinner');
  const text = document.getElementById('pay-text');
  spinner.classList.remove('d-none');
  text.textContent = 'Đang xử lý...';

  try {
    // Validate student info exists
    const studentCode = currentStudent?.student?.student_code;
    if (!studentCode) {
      showAlert('<i class="fas fa-exclamation-circle me-2"></i>Lỗi: Thiếu thông tin sinh viên. Vui lòng tìm kiếm lại.', 'danger');
      return;
    }

    // Call payment init to create pending transaction and reserve tuitions
    const total = Number(paymentForm.dataset.total || 0);
    const initResp = await createPaymentInit(studentCode);
    
    // Backend returns: { success, transaction_id, tuition_info, message, expires_in_minutes }
    if (!initResp.success) {
      showAlert(`<i class="fas fa-exclamation-circle me-2"></i>${initResp.message || 'Không thể tạo giao dịch'}`, 'danger');
      return;
    }
    
    const ctx = {
      student_code: studentCode,
      amount: initResp.tuition_info?.amount || total,
      transaction_id: initResp.transaction_id,
      tuition_info: initResp.tuition_info,
      message: initResp.message,
      expires_in_minutes: initResp.expires_in_minutes
    };
    sessionStorage.setItem('paymentContext', JSON.stringify(ctx));
    window.location.href = '/otp.html';
  } catch (err) {
    // If server returned structured body, try to display useful info (e.g., insufficient balance)
    if (err && err.body) {
      const body = err.body;
      // FastAPI commonly wraps detail in { "detail": <object> }
      const detail = body.detail || body;
      if (detail && typeof detail === 'object') {
        // If backend sent a structured error with `error` and balance info, show it nicely
        if (detail.error) {
          let msg = `<i class="fas fa-exclamation-circle me-2"></i>${detail.error}`;
          if (detail.current_balance !== undefined && detail.required_amount !== undefined) {
            msg += `<br><small>Số dư hiện tại: <strong>${new Intl.NumberFormat('vi-VN').format(detail.current_balance)} VNĐ</strong>, cần: <strong>${new Intl.NumberFormat('vi-VN').format(detail.required_amount)} VNĐ</strong></small>`;
          }
          showAlert(msg, 'warning');
          return;
        }
        // If the error object was nested (e.g., otp errors), try to stringify a helpful part
        if (detail.otp_error) {
          showAlert(`<i class="fas fa-key me-2"></i>OTP lỗi: ${JSON.stringify(detail.otp_error)}`, 'danger');
          return;
        }
      }
    }

    // Fallback generic message
    showAlert(err.message || 'Lỗi khi tạo giao dịch', 'danger');
  } finally {
    spinner.classList.add('d-none');
    text.textContent = 'Thanh toán ngay';
  }
});

function showAlert(msg, type) {
  alertDiv.innerHTML = msg;
  alertDiv.className = `alert alert-${type} mt-3`;
  alertDiv.classList.remove('d-none');
}

function hidePayment() {
  paymentSummary.classList.add('d-none');
  paymentForm.classList.add('d-none');
}