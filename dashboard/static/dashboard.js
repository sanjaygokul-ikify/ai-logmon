/**
 * dashboard.js — Client-side logic for the AI LogMon Dashboard.
 *
 * Polls the Flask API every 5 seconds and updates stat cards,
 * Chart.js charts, the log feed table, and the error panel.
 */

const REFRESH_INTERVAL = 5000;

const COLORS = {
    info: "#22d3ee", warning: "#fbbf24",
    error: "#f87171", debug: "#818cf8",
    grid: "rgba(255,255,255,0.06)", text: "#94a3b8",
};

// ===================================================================
// Charts
// ===================================================================

let levelChart = null;
let errorChart = null;

function initCharts() {
    const levelCtx = document.getElementById("level-chart").getContext("2d");
    levelChart = new Chart(levelCtx, {
        type: "doughnut",
        data: {
            labels: ["Info", "Warning", "Error", "Debug"],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [COLORS.info, COLORS.warning, COLORS.error, COLORS.debug],
                borderWidth: 0, hoverOffset: 6,
            }],
        },
        options: {
            responsive: true, cutout: "65%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: COLORS.text, padding: 16, font: { family: "Inter", size: 12 } },
                },
            },
        },
    });

    const errorCtx = document.getElementById("error-chart").getContext("2d");
    errorChart = new Chart(errorCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Errors", data: [],
                borderColor: COLORS.error,
                backgroundColor: "rgba(248,113,113,0.1)",
                fill: true, tension: 0.35, pointRadius: 3,
                pointBackgroundColor: COLORS.error,
            }],
        },
        options: {
            responsive: true,
            scales: {
                x: { ticks: { color: COLORS.text, font: { family: "Inter", size: 11 }, maxTicksLimit: 8 }, grid: { color: COLORS.grid } },
                y: { beginAtZero: true, ticks: { color: COLORS.text, font: { family: "Inter", size: 11 }, stepSize: 1 }, grid: { color: COLORS.grid } },
            },
            plugins: { legend: { display: false } },
        },
    });
}

// ===================================================================
// Helpers
// ===================================================================

async function fetchJSON(url) {
    try { const r = await fetch(url); return await r.json(); }
    catch (e) { console.error("Fetch error:", url, e); return null; }
}

function animateCounter(el, target) {
    const current = parseInt(el.textContent, 10) || 0;
    if (current === target) return;
    const diff = target - current, steps = 20, inc = diff / steps;
    let step = 0;
    function tick() {
        step++;
        if (step >= steps) { el.textContent = target.toLocaleString(); return; }
        el.textContent = Math.round(current + inc * step).toLocaleString();
        requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

function formatTimestamp(iso) {
    try {
        return new Date(iso).toLocaleString([], {
            month: "short", day: "2-digit",
            hour: "2-digit", minute: "2-digit", second: "2-digit",
        });
    } catch { return iso; }
}

function badgeClass(level) { return "badge badge--" + level.toLowerCase(); }

// ===================================================================
// Update functions
// ===================================================================

async function updateStats() {
    const s = await fetchJSON("/api/stats");
    if (!s) return;
    animateCounter(document.getElementById("stat-total"), s.total_logs);
    animateCounter(document.getElementById("stat-warnings"), s.warning);
    animateCounter(document.getElementById("stat-errors"), s.total_errors);
    if (levelChart) {
        levelChart.data.datasets[0].data = [s.info, s.warning, s.error, s.debug];
        levelChart.update("none");
    }
}

const errorHistory = [];
let lastErrorCount = 0;

async function updateErrorTrend() {
    const s = await fetchJSON("/api/stats");
    if (!s) return;
    const label = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    const newErrors = lastErrorCount === 0 ? 0 : Math.max(0, s.total_errors - lastErrorCount);
    lastErrorCount = s.total_errors;
    errorHistory.push({ label, value: newErrors });
    if (errorHistory.length > 12) errorHistory.shift();
    if (errorChart) {
        errorChart.data.labels = errorHistory.map(h => h.label);
        errorChart.data.datasets[0].data = errorHistory.map(h => h.value);
        errorChart.update("none");
    }
}

// Store all logs for client-side search filtering
let allLogs = [];

async function updateLogTable() {
    const logs = await fetchJSON("/api/logs?limit=100");
    if (!logs) return;
    allLogs = logs;
    renderLogTable();
}

function renderLogTable() {
    const query = (document.getElementById("log-search").value || "").toLowerCase();
    const filtered = query
        ? allLogs.filter(l =>
            l.message.toLowerCase().includes(query) ||
            l.source.toLowerCase().includes(query) ||
            l.level.toLowerCase().includes(query))
        : allLogs;

    const tbody = document.getElementById("log-table-body");
    document.getElementById("log-count-badge").textContent = filtered.length + " entries";

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">' +
            (query ? 'No logs matching "' + query + '"' : 'No logs yet…') + '</td></tr>';
        return;
    }
    tbody.innerHTML = filtered.map(l => `
        <tr>
            <td class="col-time">${formatTimestamp(l.timestamp)}</td>
            <td class="col-level"><span class="${badgeClass(l.level)}">${l.level}</span></td>
            <td class="col-source">${l.source}</td>
            <td class="col-message">${l.message}</td>
        </tr>`).join("");
}

async function updateErrorList() {
    const errors = await fetchJSON("/api/errors?limit=30");
    if (!errors) return;
    const list = document.getElementById("error-list");
    document.getElementById("error-count-badge").textContent = errors.length + " errors";
    if (errors.length === 0) {
        list.innerHTML = '<li class="empty-state">No errors — all systems operational ✅</li>';
        return;
    }
    list.innerHTML = errors.map(e => `
        <li class="error-item">
            <span class="badge badge--${e.severity}">${e.severity.toUpperCase()}</span>
            <div class="error-item__meta">
                <span class="error-item__message">${e.message}</span>
                <span class="error-item__details">${e.source} · ${formatTimestamp(e.timestamp)}</span>
            </div>
        </li>`).join("");
}

async function checkHealth() {
    const d = await fetchJSON("/api/health");
    const dot = document.getElementById("health-dot");
    const txt = document.getElementById("health-text");
    if (d && d.status === "ok") {
        dot.style.background = "#34d399"; dot.style.boxShadow = "0 0 8px #34d399"; txt.textContent = "Healthy";
    } else {
        dot.style.background = "#f87171"; dot.style.boxShadow = "0 0 8px #f87171"; txt.textContent = "Unreachable";
    }
    document.getElementById("last-updated").textContent = "Updated " + new Date().toLocaleTimeString();
}

// ===================================================================
// Main loop
// ===================================================================

async function refresh() {
    await Promise.all([updateStats(), updateErrorTrend(), updateLogTable(), updateErrorList(), checkHealth()]);
}

document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    refresh();
    setInterval(refresh, REFRESH_INTERVAL);

    // Live search filtering — re-render table as user types
    document.getElementById("log-search").addEventListener("input", renderLogTable);
});
