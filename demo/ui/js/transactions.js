// ui/js/transactions.js
import { getHistory } from './api.js';

const tableDiv = document.getElementById('history-table');
const noData = document.getElementById('no-data');
const statsDiv = document.getElementById('stats');
const dateFromInput = document.getElementById('date-from');
const dateToInput = document.getElementById('date-to');
const sortBySelect = document.getElementById('sort-by');
const btnFilter = document.getElementById('btn-filter');
const btnReset = document.getElementById('btn-reset');

let allTransactions = [];

// Load dữ liệu ban đầu
async function loadData() {
  try {
    const res = await getHistory();
    if (!res.transactions?.length) {
      noData.classList.remove('d-none');
      tableDiv.innerHTML = '';
      statsDiv.classList.add('d-none');
      return;
    }
    
    allTransactions = res.transactions;
    renderTransactions(allTransactions);
  } catch (err) {
    tableDiv.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>${err.message}</div>`;
    if (err.message.includes('401') || err.message.includes('Unauthorized')) {
      setTimeout(() => window.location.href = 'index.html', 2000);
    }
  }
}

// Render bảng giao dịch
function renderTransactions(transactions) {
  if (!transactions || transactions.length === 0) {
    noData.classList.remove('d-none');
    tableDiv.innerHTML = '';
    statsDiv.classList.add('d-none');
    return;
  }
  
  noData.classList.add('d-none');
  statsDiv.classList.remove('d-none');
  
  // Tính thống kê
  const totalCount = transactions.length;
  const totalAmount = transactions.reduce((sum, t) => sum + t.amount, 0);
  const avgAmount = totalAmount / totalCount;
  
  document.getElementById('total-count').textContent = totalCount;
  document.getElementById('total-amount').textContent = new Intl.NumberFormat('vi-VN').format(totalAmount) + ' VNĐ';
  document.getElementById('avg-amount').textContent = new Intl.NumberFormat('vi-VN').format(avgAmount) + ' VNĐ';
  
  // Render bảng
  let html = `
    <table class="table table-hover table-striped">
      <thead class="table-primary">
        <tr>
          <th style="width: 15%">Mã GD</th>
          <th style="width: 15%">Mã học phí</th>
          <th style="width: 20%" class="text-end">Số tiền</th>
          <th style="width: 25%">Thời gian</th>
          <th style="width: 25%">Trạng thái</th>
        </tr>
      </thead>
      <tbody>`;
  
  transactions.forEach(t => {
    const date = new Date(t.created_at);
    // Format as HH:MM:SS - DD/MM/YYYY
    const pad = (n) => String(n).padStart(2, '0');
    const hh = pad(date.getHours());
    const mm = pad(date.getMinutes());
    const ss = pad(date.getSeconds());
    const dd = pad(date.getDate());
    const MM = pad(date.getMonth() + 1);
    const YYYY = date.getFullYear();
    const dateStr = `${hh}:${mm}:${ss} - ${dd}/${MM}/${YYYY}`;
    
    // Generate transaction_code from id (backend doesn't return transaction_code)
    const transaction_code = `TXN${String(t.id).padStart(8, '0')}`;
    
    // tuition_id as display value (backend doesn't return student_code)
    const tuition_display = `#${t.tuition_id}`;
    
    // Map status to badge/color
    const status = (t.status || '').toLowerCase();
    let badgeHtml = '';
    let amountClass = 'text-body';
    if (status === 'completed') {
      badgeHtml = '<span class="badge bg-success">Thành công</span>';
      amountClass = 'text-success';
    } else if (status === 'pending') {
      badgeHtml = '<span class="badge bg-warning">Đang chờ</span>';
      amountClass = 'text-warning';
    } else if (status === 'cancelled') {
      badgeHtml = '<span class="badge bg-secondary">Đã hủy</span>';
      amountClass = 'text-muted';
    } else if (status === 'failed') {
      badgeHtml = '<span class="badge bg-danger">Thất bại</span>';
      amountClass = 'text-danger';
    } else {
      badgeHtml = `<span class="badge bg-secondary">${status || 'unknown'}</span>`;
    }

    html += `
      <tr>
        <td><code class="text-primary">${transaction_code}</code></td>
        <td><strong>${tuition_display}</strong></td>
        <td class="text-end"><strong class="${amountClass}">${new Intl.NumberFormat('vi-VN').format(t.amount)} VNĐ</strong></td>
        <td><i class="far fa-clock me-1"></i>${dateStr}</td>
        <td>${badgeHtml}</td>
      </tr>`;
  });
  
  html += `</tbody></table>`;
  tableDiv.innerHTML = html;
}

// Filter giao dịch theo ngày
function filterByDate(transactions) {
  const dateFrom = dateFromInput.value ? new Date(dateFromInput.value) : null;
  const dateTo = dateToInput.value ? new Date(dateToInput.value) : null;
  
  if (dateTo) {
    dateTo.setHours(23, 59, 59, 999); // Set to end of day
  }
  
  // Be defensive: if transactions is undefined, return empty array
  return (transactions || []).filter(t => {
    const tDate = new Date(t.created_at);
    
    if (dateFrom && tDate < dateFrom) return false;
    if (dateTo && tDate > dateTo) return false;
    
    return true;
  });
}

// Sort giao dịch
function sortTransactions(transactions, sortBy) {
  const sorted = [...transactions];
  
  switch(sortBy) {
    case 'date-desc':
      sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      break;
    case 'date-asc':
      sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      break;
    case 'amount-desc':
      sorted.sort((a, b) => b.amount - a.amount);
      break;
    case 'amount-asc':
      sorted.sort((a, b) => a.amount - b.amount);
      break;
    case 'tuition-asc':
      sorted.sort((a, b) => a.tuition_id - b.tuition_id);
      break;
    case 'tuition-desc':
      sorted.sort((a, b) => b.tuition_id - a.tuition_id);
      break;
  }
  
  return sorted;
}

// Apply filter và sort
function applyFiltersAndSort() {
  let filtered = filterByDate(allTransactions);
  let sorted = sortTransactions(filtered, sortBySelect.value);
  renderTransactions(sorted);
}

// Event listeners
btnFilter.addEventListener('click', applyFiltersAndSort);
btnReset.addEventListener('click', () => {
  dateFromInput.value = '';
  dateToInput.value = '';
  sortBySelect.value = 'date-desc';
  renderTransactions(allTransactions);
});

sortBySelect.addEventListener('change', applyFiltersAndSort);

// Load data on page load
loadData();