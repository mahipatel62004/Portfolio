const API_BASE_URL = window.PORTFOLIO_API_BASE_URL || "http://localhost:5000/api";

let adminKey = sessionStorage.getItem("adminKey") || "";
let state = { search: "", status: "ALL", sort: "latest", page: 1, pageSize: 15 };
let currentInquiryId = null;

const keyGate = document.getElementById("key-gate");
const adminShell = document.getElementById("admin-shell");

function showToast(message, type = "success") {
  const stack = document.getElementById("toast-stack");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", "X-Admin-Key": adminKey, ...(options.headers || {}) },
  });
  if (res.status === 401) {
    sessionStorage.removeItem("adminKey");
    adminKey = "";
    keyGate.style.display = "block";
    adminShell.style.display = "none";
    throw new Error("Unauthorized");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false) throw new Error(data.message || "Request failed");
  return data;
}

// --- Admin key gate ---------------------------------------------------------
document.getElementById("admin-key-submit").addEventListener("click", unlockDashboard);
document.getElementById("admin-key-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") unlockDashboard();
});

async function unlockDashboard() {
  const val = document.getElementById("admin-key-input").value.trim();
  if (!val) return;
  adminKey = val;
  try {
    await apiFetch("/inquiries?page=1&pageSize=1");
    sessionStorage.setItem("adminKey", adminKey);
    keyGate.style.display = "none";
    adminShell.style.display = "block";
    loadInquiries();
  } catch (err) {
    showToast("Invalid admin key.", "error");
  }
}

if (adminKey) {
  keyGate.style.display = "none";
  adminShell.style.display = "block";
  loadInquiries();
}

// --- Toolbar -----------------------------------------------------------------
let searchTimer;
document.getElementById("search-input").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.search = e.target.value.trim();
    state.page = 1;
    loadInquiries();
  }, 350);
});

document.getElementById("status-filter").addEventListener("change", (e) => {
  state.status = e.target.value;
  state.page = 1;
  loadInquiries();
});

document.getElementById("sort-select").addEventListener("change", (e) => {
  state.sort = e.target.value;
  state.page = 1;
  loadInquiries();
});

document.getElementById("prev-page").addEventListener("click", () => {
  if (state.page > 1) { state.page -= 1; loadInquiries(); }
});
document.getElementById("next-page").addEventListener("click", () => {
  state.page += 1;
  loadInquiries();
});

// --- Load + render table ------------------------------------------------------
async function loadInquiries() {
  const wrap = document.getElementById("table-wrap");
  wrap.innerHTML = `<div class="loading-state">Loading inquiries…</div>`;

  const params = new URLSearchParams({
    search: state.search,
    status: state.status,
    sort: state.sort,
    page: state.page,
    pageSize: state.pageSize,
  });

  try {
    const { data, pagination } = await apiFetch(`/inquiries?${params.toString()}`);
    renderTable(data);
    renderPagination(pagination);
  } catch (err) {
    if (err.message !== "Unauthorized") {
      wrap.innerHTML = `<div class="error-state">Couldn't load inquiries. ${err.message}</div>`;
    }
  }
}

function renderTable(items) {
  const wrap = document.getElementById("table-wrap");
  if (!items.length) {
    wrap.innerHTML = `<div class="empty-state">No inquiries match your filters yet.</div>`;
    return;
  }

  const rows = items
    .map(
      (item) => `
      <tr class="row-clickable" data-id="${item.id}">
        <td>
          <div class="cell-name">${escapeHtml(item.fullName)}</div>
          <div class="cell-sub">${escapeHtml(item.email)}</div>
        </td>
        <td>${escapeHtml(item.subject)}</td>
        <td><span class="status-badge status-${item.status}">${item.status}</span></td>
        <td class="cell-sub">${formatDate(item.createdAt)}</td>
      </tr>`
    )
    .join("");

  wrap.innerHTML = `
    <table class="inquiry-table">
      <thead><tr><th>From</th><th>Subject</th><th>Status</th><th>Received</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;

  wrap.querySelectorAll("tr.row-clickable").forEach((row) => {
    row.addEventListener("click", () => openInquiry(row.dataset.id));
  });
}

function renderPagination(pagination) {
  const el = document.getElementById("pagination");
  if (!pagination || pagination.totalPages <= 1) {
    el.style.display = "none";
    return;
  }
  el.style.display = "flex";
  document.getElementById("page-label").textContent = `Page ${pagination.page} of ${pagination.totalPages}`;
  document.getElementById("prev-page").disabled = pagination.page <= 1;
  document.getElementById("next-page").disabled = pagination.page >= pagination.totalPages;
}

// --- Detail modal ---------------------------------------------------------
const modalOverlay = document.getElementById("modal-overlay");

async function openInquiry(id) {
  try {
    const { data } = await apiFetch(`/inquiries/${id}`);
    currentInquiryId = id;
    document.getElementById("modal-subject").textContent = data.subject;
    document.getElementById("modal-from").textContent = `${data.fullName} · ${data.email}`;
    document.getElementById("modal-company").textContent = data.company || "—";
    document.getElementById("modal-date").textContent = formatDate(data.createdAt);
    document.getElementById("modal-message").textContent = data.message;
    modalOverlay.classList.add("open");

    // Auto mark-as-read the first time it's opened
    if (data.status === "NEW") {
      await apiFetch(`/inquiries/${id}/status`, { method: "PATCH", body: JSON.stringify({ status: "READ" }) });
      loadInquiries();
    }
  } catch (err) {
    if (err.message !== "Unauthorized") showToast(err.message, "error");
  }
}

document.getElementById("modal-close").addEventListener("click", () => modalOverlay.classList.remove("open"));
modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) modalOverlay.classList.remove("open"); });

document.getElementById("mark-read").addEventListener("click", () => setStatus("READ"));
document.getElementById("mark-replied").addEventListener("click", () => setStatus("REPLIED"));

async function setStatus(status) {
  try {
    await apiFetch(`/inquiries/${currentInquiryId}/status`, { method: "PATCH", body: JSON.stringify({ status }) });
    showToast(`Marked as ${status.toLowerCase()}.`, "success");
    modalOverlay.classList.remove("open");
    loadInquiries();
  } catch (err) {
    showToast(err.message, "error");
  }
}

document.getElementById("delete-inquiry").addEventListener("click", async () => {
  if (!confirm("Delete this inquiry permanently? This cannot be undone.")) return;
  try {
    await apiFetch(`/inquiries/${currentInquiryId}`, { method: "DELETE" });
    showToast("Inquiry deleted.", "success");
    modalOverlay.classList.remove("open");
    loadInquiries();
  } catch (err) {
    showToast(err.message, "error");
  }
});

// --- Helpers ---------------------------------------------------------------
function formatDate(iso) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
