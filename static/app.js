/* app.js — 파나소닉 재고관리 공통 유틸리티 */
'use strict';

console.log('Panasonic Inventory System JS Loaded - v1.0.1');

// ================================================
//  Toast 알림
// ================================================
function showToast(msg, type = 'success') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const c = document.getElementById('toast-container');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<span>${icons[type] || '📢'}</span><span>${msg}</span>`;
  c.appendChild(t);
  requestAnimationFrame(() => requestAnimationFrame(() => t.classList.add('show')));
  setTimeout(() => {
    t.classList.remove('show');
    setTimeout(() => t.remove(), 320);
  }, 3400);
}

// ================================================
//  Modal helpers
// ================================================
function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('active');
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('active');
}
function closeAllModals() {
  document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
}
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) closeAllModals();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeAllModals();
});

// ================================================
//  AJAX helper
// ================================================
async function api(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  return res.json();
}

// ================================================
//  Button loading state
// ================================================
function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn.dataset.orig = btn.textContent;
    btn.textContent  = '처리 중…';
    btn.disabled     = true;
  } else {
    btn.textContent = btn.dataset.orig || '확인';
    btn.disabled    = false;
  }
}

// ================================================
//  실시간 테이블 검색 (세션 스토리지 기반 유지 기능 탑재)
// ================================================
function initTableSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const tbody = document.querySelector(`#${tableId} tbody`);
  if (!input || !tbody) return;

  // 세션 스토리지에서 이전 검색어 복원
  const savedKw = sessionStorage.getItem('search_' + inputId);
  if (savedKw) {
    input.value = savedKw;
    const kw = savedKw.trim().toLowerCase();
    tbody.querySelectorAll('tr').forEach(row => {
      row.style.display =
        (kw === '' || row.textContent.toLowerCase().includes(kw)) ? '' : 'none';
    });
  }

  input.addEventListener('input', () => {
    const kw = input.value;
    sessionStorage.setItem('search_' + inputId, kw);
    const kwLower = kw.trim().toLowerCase();
    tbody.querySelectorAll('tr').forEach(row => {
      row.style.display =
        (kwLower === '' || row.textContent.toLowerCase().includes(kwLower)) ? '' : 'none';
    });
    updateRowCount(tableId);
  });
}

// ================================================
//  스크롤 위치 유지 및 복원
// ================================================
function initScrollRestoration() {
  const scrollKey = 'scroll_pos_' + location.pathname;
  const savedScroll = sessionStorage.getItem(scrollKey);
  
  const startScrollListening = () => {
    let scrollTimeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        sessionStorage.setItem(scrollKey, window.scrollY);
      }, 150);
    });
  };

  if (savedScroll) {
    const scrollPos = parseInt(savedScroll, 10);
    window.scrollTo(0, scrollPos);
    requestAnimationFrame(() => {
      window.scrollTo(0, scrollPos);
      setTimeout(startScrollListening, 100);
    });
  } else {
    startScrollListening();
  }
}

function updateRowCount(tableId) {
  const counter = document.getElementById(`${tableId}-count`);
  if (!counter) return;
  const visible = document.querySelectorAll(
    `#${tableId} tbody tr:not([style*="display: none"])`
  ).length;
  counter.textContent = `${visible}건`;
}

// ================================================
//  관리자 직원 관리 함수들
// ================================================
let _resetUid = null;

function openAddUserModal() {
  const f = document.getElementById('form-user');
  if (f) f.reset();
  openModal('modal-user');
}

async function submitUser() {
  const body = {
    username: document.getElementById('u-username').value.trim(),
    password: document.getElementById('u-password').value,
    name:     document.getElementById('u-name').value.trim(),
    role:     document.getElementById('u-role').value,
  };
  if (!body.username || !body.password || !body.name) {
    showToast('모든 항목을 입력해 주세요.', 'error'); return;
  }
  setLoading('btn-save-user', true);
  const res = await api('/api/admin/user', 'POST', body);
  setLoading('btn-save-user', false);
  if (res.success) {
    showToast(res.message, 'success');
    closeModal('modal-user');
    setTimeout(() => location.reload(), 700);
  } else { showToast(res.message || '오류', 'error'); }
}

async function toggleUser(uid) {
  const res = await api(`/api/admin/user/${uid}/toggle`, 'POST');
  if (res.success) { showToast(res.message, 'success'); setTimeout(() => location.reload(), 700); }
  else showToast(res.message || '오류', 'error');
}

function openResetPwModal(uid) {
  _resetUid = uid;
  const el = document.getElementById('new-password');
  if (el) el.value = '';
  openModal('modal-reset-pw');
}

async function confirmResetPw() {
  const pw = document.getElementById('new-password').value;
  if (!pw || pw.length < 4) { showToast('비밀번호는 4자 이상이어야 합니다.', 'error'); return; }
  setLoading('btn-confirm-pw', true);
  const res = await api(`/api/admin/user/${_resetUid}/password`, 'POST', { password: pw });
  setLoading('btn-confirm-pw', false);
  if (res.success) { showToast(res.message, 'success'); closeModal('modal-reset-pw'); }
  else showToast(res.message || '오류', 'error');
}

// ================================================
//  마우스 드래그로 가로 스크롤 (PC용)
// ================================================
function initDragScroll() {
  const scrolls = document.querySelectorAll('.table-scroll');
  scrolls.forEach(slider => {
    let isDown = false;
    let startX;
    let scrollLeft;

    slider.addEventListener('mousedown', (e) => {
      // 마우스 왼쪽 클릭(0)만 작동, 입력창/버튼/링크 클릭 시 제외
      if (e.button !== 0 || e.target.closest('button, input, a, select, code')) return;
      isDown = true;
      slider.style.cursor = 'grabbing';
      startX = e.pageX - slider.offsetLeft;
      scrollLeft = slider.scrollLeft;
    });

    slider.addEventListener('mouseleave', () => {
      isDown = false;
      slider.style.cursor = 'grab';
    });

    slider.addEventListener('mouseup', () => {
      isDown = false;
      slider.style.cursor = 'grab';
    });

    slider.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - slider.offsetLeft;
      const walk = (x - startX) * 1.5; // 스크롤 속도 배율
      slider.scrollLeft = scrollLeft - walk;
    });

    // 초기 마우스 커서 설정
    slider.style.cursor = 'grab';
  });
}

// ================================================
//  업무일지 (Work Logs)
// ================================================
function openWorkLogModal(id = null, date = '', today = '', tomorrow = '', memo = '') {
  document.getElementById('workLogId').value = id || '';
  
  if (!id && !date) {
    // 신규 작성 시 오늘 날짜 기본값 설정
    const tzoffset = (new Date()).getTimezoneOffset() * 60000; 
    const localISOTime = (new Date(Date.now() - tzoffset)).toISOString().slice(0, 10);
    document.getElementById('workLogDate').value = localISOTime;
    document.getElementById('workLogDate').readOnly = false;
  } else {
    document.getElementById('workLogDate').value = date;
    document.getElementById('workLogDate').readOnly = !!id;
  }
  
  const todayOld = document.getElementById('workLogToday_old');
  const tomorrowOld = document.getElementById('workLogTomorrow_old');
  const memoOld = document.getElementById('workLogMemo_old');
  
  if (id) {
    if (today) { todayOld.style.display = 'block'; todayOld.textContent = today; } else { todayOld.style.display = 'none'; todayOld.textContent = ''; }
    if (tomorrow) { tomorrowOld.style.display = 'block'; tomorrowOld.textContent = tomorrow; } else { tomorrowOld.style.display = 'none'; tomorrowOld.textContent = ''; }
    if (memo) { memoOld.style.display = 'block'; memoOld.textContent = memo; } else { memoOld.style.display = 'none'; memoOld.textContent = ''; }
    document.getElementById('workLogModalTitle').textContent = '업무일지 내용 추가';
  } else {
    todayOld.style.display = 'none'; todayOld.textContent = '';
    tomorrowOld.style.display = 'none'; tomorrowOld.textContent = '';
    memoOld.style.display = 'none'; memoOld.textContent = '';
    document.getElementById('workLogModalTitle').textContent = '업무일지 작성';
  }
  
  document.getElementById('workLogToday').value = '';
  document.getElementById('workLogTomorrow').value = '';
  document.getElementById('workLogMemo').value = '';
  
  openModal('workLogModal');
}

async function saveWorkLog() {
  const id = document.getElementById('workLogId').value;
  const date = document.getElementById('workLogDate').value;
  const today = document.getElementById('workLogToday').value.trim();
  const tomorrow = document.getElementById('workLogTomorrow').value.trim();
  const memo = document.getElementById('workLogMemo').value.trim();
  
  if (!date) {
    showToast('업무 일자를 입력해주세요.', 'error');
    return;
  }
  
  if (!today && !tomorrow && !memo) {
    showToast('업무 내용(오늘 한일, 내일 할일, 메모 중 하나)을 입력해주세요.', 'error');
    return;
  }
  
  let url = '/api/work_log';
  let method = 'POST';
  let body = { work_date: date, today_work: today, tomorrow_work: tomorrow, memo: memo };
  
  if (id) {
    url = `/api/work_log/${id}`;
    method = 'PUT';
  }
  
  const res = await api(url, method, body);
  if (res.success) {
    showToast(res.message, 'success');
    closeModal('workLogModal');
    setTimeout(() => location.reload(), 700);
  } else {
    showToast(res.message || '오류가 발생했습니다.', 'error');
  }
}

async function deleteWorkLog(id) {
  if (!confirm('정말로 이 업무일지를 삭제하시겠습니까?')) return;
  const res = await api(`/api/work_log/${id}`, 'DELETE');
  if (res.success) {
    showToast(res.message, 'success');
    setTimeout(() => location.reload(), 700);
  } else {
    showToast(res.message || '오류가 발생했습니다.', 'error');
  }
}

// ================================================
//  DOMContentLoaded
// ================================================
document.addEventListener('DOMContentLoaded', () => {
  // 일반 링크 클릭하여 화면 이동 시 세션 저장소 초기화 (새 탭 열기 제외)
  document.addEventListener('click', e => {
    if (e.button === 1 || e.ctrlKey || e.metaKey || e.shiftKey) {
      return;
    }
    const link = e.target.closest('a');
    if (link) {
      const href = link.getAttribute('href');
      if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
        const toRemove = [];
        for (let i = 0; i < sessionStorage.length; i++) {
          const key = sessionStorage.key(i);
          if (key && (key.startsWith('search_') || key.startsWith('scroll_pos_'))) {
            toRemove.push(key);
          }
        }
        toRemove.forEach(key => sessionStorage.removeItem(key));
      }
    }
  });

  ['tbl-products','tbl-history','tbl-audit','tbl-users'].forEach(id => {
    initTableSearch(`search-${id.replace('tbl-','')}`, id);
    updateRowCount(id);
  });

  initScrollRestoration();
  
  // 마우스 드래그 스크롤 기능 활성화
  initDragScroll();
});
