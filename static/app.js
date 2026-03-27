function initTextViewer() {
  const root = document.querySelector("[data-text-viewer]");
  if (!root) return;

  const toolId = root.dataset.toolId || "text_viewer";
  const tabsWrap = root.querySelector(".text-viewer-tabs-wrap");
  const panel = root.querySelector(".text-viewer-panel");
  const refreshBtn = root.querySelector(".text-viewer-refresh");
  const filterInput = root.querySelector(".text-viewer-filter");

  let files = [];
  let activeFile = null;

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function getFiltered() {
    const q = (filterInput.value || "").trim().toLowerCase();
    if (!q) return files;
    return files.filter((f) => f.toLowerCase().includes(q));
  }

  function renderTabs() {
    const filtered = getFiltered();
    tabsWrap.innerHTML = "";
    filtered.forEach((name) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "text-viewer-tab" + (name === activeFile ? " is-active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-selected", name === activeFile ? "true" : "false");
      btn.dataset.file = name;
      btn.textContent = name;
      tabsWrap.appendChild(btn);
    });
  }

  function setPlaceholder(html) {
    panel.innerHTML = html;
  }

  async function fetchList() {
    setPlaceholder('<p class="text-viewer-placeholder">正在加载列表…</p>');
    tabsWrap.innerHTML = "";
    try {
      const res = await fetch(`/api/tools/${toolId}/list`);
      const data = await res.json();
      if (!data.ok) {
        setPlaceholder(`<p class="text-viewer-error">${escapeHtml(data.error || "加载失败")}</p>`);
        return;
      }
      files = data.files || [];
      if (!files.length) {
        activeFile = null;
        const extra = data.hint ? `<span class="text-viewer-dir-hint">${escapeHtml(data.hint)}</span>` : "";
        setPlaceholder(
          `<p class="text-viewer-placeholder">暂无可用文本文件。请将文件放入目录后点击「刷新列表」。${extra}</p>`
        );
        return;
      }
      if (!activeFile || !files.includes(activeFile)) {
        activeFile = files[0];
      }
      renderTabs();
      await loadContent(activeFile);
    } catch (err) {
      setPlaceholder(`<p class="text-viewer-error">${escapeHtml("请求失败: " + err.message)}</p>`);
    }
  }

  async function loadContent(name) {
    if (!name) return;
    activeFile = name;
    renderTabs();
    setPlaceholder('<p class="text-viewer-placeholder">正在加载正文…</p>');
    try {
      const u = `/api/tools/${encodeURIComponent(toolId)}/content?file=${encodeURIComponent(name)}`;
      const res = await fetch(u);
      const data = await res.json();
      if (!data.ok) {
        setPlaceholder(`<p class="text-viewer-error">${escapeHtml(data.error || "读取失败")}</p>`);
        return;
      }
      setPlaceholder(`<pre class="text-viewer-pre"><code>${escapeHtml(data.content)}</code></pre>`);
    } catch (err) {
      setPlaceholder(`<p class="text-viewer-error">${escapeHtml("请求失败: " + err.message)}</p>`);
    }
  }

  tabsWrap.addEventListener("click", (e) => {
    const tab = e.target.closest(".text-viewer-tab");
    if (!tab || !root.contains(tab)) return;
    const f = tab.dataset.file;
    if (f) loadContent(f);
  });

  refreshBtn.addEventListener("click", () => fetchList());

  let debounce;
  filterInput.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      const filtered = getFiltered();
      renderTabs();
      if (!filtered.length) {
        setPlaceholder(
          '<p class="text-viewer-placeholder" data-text-viewer-filter-empty>没有匹配的页签。</p>'
        );
        return;
      }
      if (!filtered.includes(activeFile)) {
        loadContent(filtered[0]);
      } else if (panel.querySelector("[data-text-viewer-filter-empty]")) {
        loadContent(activeFile);
      }
    }, 120);
  });

  fetchList();
}

function initMediaShelf() {
  const root = document.querySelector("[data-media-shelf]");
  if (!root) return;

  const toolId = root.dataset.toolId || "media_shelf";
  const refreshBtn = root.querySelector(".media-shelf-refresh");
  const searchInput = root.querySelector(".media-shelf-search");
  const categorySel = root.querySelector(".media-shelf-filter-category");
  const statusSel = root.querySelector(".media-shelf-filter-status");
  const sourceSel = root.querySelector(".media-shelf-filter-source");
  const summaryEl = root.querySelector(".media-shelf-summary");
  const listWrap = root.querySelector(".media-shelf-list-wrap");

  let files = [];
  let items = [];

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s ?? "";
    return d.innerHTML;
  }

  function renderSourceOptions() {
    const current = sourceSel.value || "all";
    sourceSel.innerHTML = '<option value="all">全部文件</option>';
    files.forEach((f) => {
      const op = document.createElement("option");
      op.value = f;
      op.textContent = f;
      sourceSel.appendChild(op);
    });
    sourceSel.value = files.includes(current) ? current : "all";
  }

  function statusLabel(status) {
    return status === "watched" ? "看过" : (status === "unwatched" ? "没看过" : "未标注");
  }

  function categoryLabel(category) {
    if (category === "movie") return "电影";
    if (category === "tv") return "电视剧";
    if (category === "anime") return "动漫";
    return "未分类";
  }

  function filteredItems() {
    const q = (searchInput.value || "").trim().toLowerCase();
    const c = categorySel.value || "all";
    const s = statusSel.value || "all";
    const source = sourceSel.value || "all";
    const filtered = items.filter((x) => {
      if (c !== "all" && x.category !== c) return false;
      if (s !== "all" && x.status !== s) return false;
      if (source !== "all" && x.source !== source) return false;
      if (!q) return true;
      const hay = `${x.title || ""} ${x.note || ""}`.toLowerCase();
      return hay.includes(q);
    });
    const statusRank = { unwatched: 0, watched: 1 };
    filtered.sort((a, b) => {
      const ra = statusRank[a.status] ?? 2;
      const rb = statusRank[b.status] ?? 2;
      if (ra !== rb) return ra - rb;
      return (a.title || "").localeCompare((b.title || ""), "zh-Hans-CN", { sensitivity: "base" });
    });
    return filtered;
  }

  function renderSummary(list) {
    const watched = list.filter((x) => x.status === "watched").length;
    const unwatched = list.filter((x) => x.status === "unwatched").length;
    const movie = list.filter((x) => x.category === "movie").length;
    const tv = list.filter((x) => x.category === "tv").length;
    const anime = list.filter((x) => x.category === "anime").length;
    summaryEl.innerHTML = `
      <span class="media-pill">共 ${list.length} 条</span>
      <span class="media-pill">电影 ${movie}</span>
      <span class="media-pill">电视剧 ${tv}</span>
      <span class="media-pill">动漫 ${anime}</span>
      <span class="media-pill is-watched">看过 ${watched}</span>
      <span class="media-pill is-unwatched">没看过 ${unwatched}</span>
    `;
  }

  function renderList() {
    const list = filteredItems();
    renderSummary(list);
    if (!list.length) {
      listWrap.innerHTML = '<p class="media-shelf-placeholder">没有匹配的影视条目。</p>';
      return;
    }
    const rows = list.map((x) => {
      const note = x.note ? `<p class="media-item-note">${esc(x.note)}</p>` : "";
      return `
        <article class="media-item-card">
          <h3 class="media-item-title">${esc(x.title)}</h3>
          <div class="media-item-meta">
            <span class="media-badge category">${esc(categoryLabel(x.category))}</span>
            <span class="media-badge ${x.status === "watched" ? "watched" : (x.status === "unwatched" ? "unwatched" : "unknown")}">${esc(statusLabel(x.status))}</span>
            <span class="media-badge source">${esc(x.source || "未知来源")}</span>
          </div>
          ${note}
        </article>
      `;
    });
    listWrap.innerHTML = `<div class="media-item-grid">${rows.join("")}</div>`;
  }

  async function fetchItems() {
    listWrap.innerHTML = '<p class="media-shelf-placeholder">正在加载影视列表…</p>';
    try {
      const source = sourceSel.value && sourceSel.value !== "all" ? sourceSel.value : "";
      const url = source
        ? `/api/tools/${encodeURIComponent(toolId)}/items?source=${encodeURIComponent(source)}`
        : `/api/tools/${encodeURIComponent(toolId)}/items`;
      const res = await fetch(url);
      const data = await res.json();
      if (!data.ok) {
        listWrap.innerHTML = `<p class="media-shelf-error">${esc(data.error || "加载失败")}</p>`;
        return;
      }
      files = data.files || [];
      items = data.items || [];
      renderSourceOptions();
      renderList();
    } catch (err) {
      listWrap.innerHTML = `<p class="media-shelf-error">${esc("请求失败: " + err.message)}</p>`;
    }
  }

  refreshBtn.addEventListener("click", () => {
    sourceSel.value = "all";
    fetchItems();
  });
  searchInput.addEventListener("input", renderList);
  categorySel.addEventListener("change", renderList);
  statusSel.addEventListener("change", renderList);
  sourceSel.addEventListener("change", fetchItems);

  fetchItems();
}

function initBodyWeight() {
  const root = document.querySelector("[data-body-weight]");
  if (!root) return;

  const toolId = root.dataset.toolId || "body_weight";
  let dashboardChart = null;
  let trendChart = null;

  // 标签切换
  root.querySelectorAll(".body-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const targetPanel = tab.dataset.tab;
      root.querySelectorAll(".body-tab").forEach(t => t.classList.remove("active"));
      root.querySelectorAll(".body-panel").forEach(p => p.style.display = "none");
      tab.classList.add("active");
      const panel = root.querySelector(`[data-panel="${targetPanel}"]`);
      if (panel) panel.style.display = "block";
      
      // 加载对应数据
      if (targetPanel === "dashboard") loadDashboard();
      else if (targetPanel === "daily") initDailyForm();
      else if (targetPanel === "trend") loadTrend();
      else if (targetPanel === "strategy") loadStrategy();
    });
  });

  // 仪表盘
  async function loadDashboard() {
    try {
      const res = await fetch(`/api/tools/${toolId}/dashboard`);
      const data = await res.json();
      if (!data.ok) {
        console.error("加载仪表盘失败:", data.error);
        return;
      }

      document.getElementById("current-weight").textContent = data.current_weight ? `${data.current_weight} kg` : "--";
      document.getElementById("ma7-weight").textContent = data.ma7 ? `${data.ma7} kg` : "--";
      
      const phaseEl = document.getElementById("current-phase");
      const phaseMap = {
        building: "建立期",
        plateau: "平台期",
        accelerating: "加速期",
        unstable: "失控期"
      };
      phaseEl.textContent = phaseMap[data.phase?.phase] || "--";
      phaseEl.className = `dash-value phase-badge phase-${data.phase?.phase || "unknown"}`;
      document.getElementById("phase-reason").textContent = data.phase?.reason || "--";
      
      document.getElementById("week-compliance").textContent = data.compliance ? `${(data.compliance * 100).toFixed(0)}%` : "--";
      document.getElementById("week-binge").textContent = data.binge_count || 0;
      
      document.getElementById("current-strategy").textContent = data.strategy?.name || "未设置";
      document.getElementById("strategy-days").textContent = data.strategy ? `运行 ${data.strategy.days} 天` : "--";

      // 绘制图表
      renderDashboardChart(data.chart);
    } catch (err) {
      console.error("加载仪表盘失败:", err);
    }
  }

  function renderDashboardChart(chartData) {
    const canvas = document.getElementById("dashboard-chart");
    if (!canvas) return;
    
    if (dashboardChart) dashboardChart.destroy();
    
    const ctx = canvas.getContext("2d");
    dashboardChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: chartData.dates,
        datasets: [{
          label: "体重 (kg)",
          data: chartData.weights,
          borderColor: "#58a6ff",
          backgroundColor: "rgba(88, 166, 255, 0.1)",
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, labels: { color: "#e6edf3" } }
        },
        scales: {
          x: { ticks: { color: "#8b949e" }, grid: { color: "#2d3a4d" } },
          y: { ticks: { color: "#8b949e" }, grid: { color: "#2d3a4d" } }
        }
      }
    });
  }

  // 每日记录
  function initDailyForm() {
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("log-date").value = today;
    
    // 范围滑块实时显示
    ["energy", "hunger", "mood"].forEach(type => {
      const slider = document.getElementById(`log-${type}`);
      const display = document.getElementById(`${type}-val`);
      slider.addEventListener("input", () => {
        display.textContent = slider.value;
      });
    });
  }

  document.getElementById("load-date")?.addEventListener("click", async () => {
    const dateVal = document.getElementById("log-date").value;
    if (!dateVal) return;
    
    try {
      const res = await fetch(`/api/tools/${toolId}/daily-log?date=${dateVal}`);
      const data = await res.json();
      if (data.ok && data.log) {
        const log = data.log;
        document.getElementById("log-weight").value = log.weight || "";
        document.getElementById("log-sleep").value = log.sleep_hours || "";
        document.getElementById("log-steps").value = log.steps || "";
        document.getElementById("log-exercise").value = log.exercise_minutes || "";
        document.getElementById("log-fasting").checked = log.fasting_168 === 1;
        document.getElementById("log-sugar-free").checked = log.sugar_free === 1;
        document.getElementById("log-binge").checked = log.binge === 1;
        document.getElementById("log-energy").value = log.energy_level || 5;
        document.getElementById("energy-val").textContent = log.energy_level || 5;
        document.getElementById("log-hunger").value = log.hunger_level || 5;
        document.getElementById("hunger-val").textContent = log.hunger_level || 5;
        document.getElementById("log-mood").value = log.mood_level || 5;
        document.getElementById("mood-val").textContent = log.mood_level || 5;
        document.getElementById("log-notes").value = log.notes || "";
      }
    } catch (err) {
      console.error("加载记录失败:", err);
    }
  });

  document.getElementById("copy-yesterday")?.addEventListener("click", async () => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split("T")[0];
    
    try {
      const res = await fetch(`/api/tools/${toolId}/daily-log?date=${yesterdayStr}`);
      const data = await res.json();
      if (data.ok && data.log) {
        const log = data.log;
        document.getElementById("log-weight").value = log.weight || "";
        document.getElementById("log-sleep").value = log.sleep_hours || "";
        document.getElementById("log-steps").value = log.steps || "";
        document.getElementById("log-exercise").value = log.exercise_minutes || "";
        document.getElementById("log-fasting").checked = log.fasting_168 === 1;
        document.getElementById("log-sugar-free").checked = log.sugar_free === 1;
        document.getElementById("log-binge").checked = false;
        document.getElementById("log-energy").value = log.energy_level || 5;
        document.getElementById("energy-val").textContent = log.energy_level || 5;
        document.getElementById("log-hunger").value = log.hunger_level || 5;
        document.getElementById("hunger-val").textContent = log.hunger_level || 5;
        document.getElementById("log-mood").value = log.mood_level || 5;
        document.getElementById("mood-val").textContent = log.mood_level || 5;
        document.getElementById("log-notes").value = "";
      }
    } catch (err) {
      console.error("复制昨日数据失败:", err);
    }
  });

  document.getElementById("save-log")?.addEventListener("click", async () => {
    const resultEl = document.getElementById("daily-result");
    const logData = {
      date: document.getElementById("log-date").value,
      weight: document.getElementById("log-weight").value,
      sleep_hours: document.getElementById("log-sleep").value,
      steps: document.getElementById("log-steps").value,
      exercise_minutes: document.getElementById("log-exercise").value,
      fasting_168: document.getElementById("log-fasting").checked,
      sugar_free: document.getElementById("log-sugar-free").checked,
      binge: document.getElementById("log-binge").checked,
      energy_level: document.getElementById("log-energy").value,
      hunger_level: document.getElementById("log-hunger").value,
      mood_level: document.getElementById("log-mood").value,
      notes: document.getElementById("log-notes").value
    };

    try {
      const res = await fetch(`/api/tools/${toolId}/daily-log`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(logData)
      });
      const data = await res.json();
      
      if (data.ok) {
        resultEl.textContent = "✓ " + data.message;
        resultEl.className = "result-msg success";
      } else {
        resultEl.textContent = "✗ " + data.error;
        resultEl.className = "result-msg error";
      }
    } catch (err) {
      resultEl.textContent = "✗ 保存失败: " + err.message;
      resultEl.className = "result-msg error";
    }
  });

  document.getElementById("clear-form")?.addEventListener("click", () => {
    document.getElementById("log-weight").value = "";
    document.getElementById("log-sleep").value = "";
    document.getElementById("log-steps").value = "";
    document.getElementById("log-exercise").value = "";
    document.getElementById("log-fasting").checked = false;
    document.getElementById("log-sugar-free").checked = false;
    document.getElementById("log-binge").checked = false;
    document.getElementById("log-energy").value = 5;
    document.getElementById("energy-val").textContent = 5;
    document.getElementById("log-hunger").value = 5;
    document.getElementById("hunger-val").textContent = 5;
    document.getElementById("log-mood").value = 5;
    document.getElementById("mood-val").textContent = 5;
    document.getElementById("log-notes").value = "";
  });

  // 趋势图表
  async function loadTrend() {
    const days = document.getElementById("trend-range")?.value || 30;
    
    try {
      const res = await fetch(`/api/tools/${toolId}/trend?days=${days}`);
      const data = await res.json();
      if (!data.ok) {
        console.error("加载趋势失败:", data.error);
        return;
      }

      renderTrendChart(data);
    } catch (err) {
      console.error("加载趋势失败:", err);
    }
  }

  function renderTrendChart(data) {
    const canvas = document.getElementById("trend-chart");
    if (!canvas) return;
    
    if (trendChart) trendChart.destroy();
    
    const ctx = canvas.getContext("2d");
    trendChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.dates,
        datasets: [
          {
            label: "体重 (kg)",
            data: data.weights,
            borderColor: "#58a6ff",
            backgroundColor: "rgba(88, 166, 255, 0.1)",
            tension: 0.2,
            pointRadius: 3
          },
          {
            label: "7日均线",
            data: data.ma7,
            borderColor: "#f85149",
            backgroundColor: "transparent",
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, labels: { color: "#e6edf3" } }
        },
        scales: {
          x: { ticks: { color: "#8b949e" }, grid: { color: "#2d3a4d" } },
          y: { ticks: { color: "#8b949e" }, grid: { color: "#2d3a4d" } }
        }
      }
    });
  }

  document.getElementById("refresh-trend")?.addEventListener("click", loadTrend);
  document.getElementById("trend-range")?.addEventListener("change", loadTrend);

  // 策略管理
  async function loadStrategy() {
    try {
      const [currentRes, historyRes] = await Promise.all([
        fetch(`/api/tools/${toolId}/strategy/current`),
        fetch(`/api/tools/${toolId}/strategy/history`)
      ]);
      
      const currentData = await currentRes.json();
      const historyData = await historyRes.json();
      
      // 显示当前策略
      const currentEl = document.getElementById("current-strategy-detail");
      if (currentData.ok && currentData.strategy) {
        const s = currentData.strategy;
        currentEl.innerHTML = `
          <div class="strategy-card">
            <h4>${s.version_name}</h4>
            <p><strong>开始日期：</strong>${s.start_date}</p>
            <p><strong>核心策略：</strong>${s.core_strategy}</p>
            <p><strong>变更变量：</strong>${s.variables_changed}</p>
            <p><strong>预期效果：</strong>${s.expected_effect}</p>
          </div>
        `;
      } else {
        currentEl.innerHTML = "<p>暂无活跃策略</p>";
      }
      
      // 显示历史版本
      const listEl = document.getElementById("strategy-list");
      if (historyData.ok && historyData.strategies && historyData.strategies.length) {
        listEl.innerHTML = historyData.strategies.map(s => `
          <div class="strategy-card ${s.active ? 'active' : 'inactive'}">
            <h4>${s.version_name} ${s.active ? '<span class="badge-active">当前</span>' : ''}</h4>
            <p><strong>时间：</strong>${s.start_date} ${s.end_date ? '至 ' + s.end_date : '至今'}</p>
            <p><strong>核心策略：</strong>${s.core_strategy}</p>
          </div>
        `).join("");
      } else {
        listEl.innerHTML = "<p>暂无历史版本</p>";
      }
      
      // 设置默认开始日期为今天
      document.getElementById("strategy-start").value = new Date().toISOString().split("T")[0];
    } catch (err) {
      console.error("加载策略失败:", err);
    }
  }

  document.getElementById("create-strategy")?.addEventListener("click", async () => {
    const resultEl = document.getElementById("strategy-result");
    const strategyData = {
      version_name: document.getElementById("strategy-name").value,
      start_date: document.getElementById("strategy-start").value,
      core_strategy: document.getElementById("strategy-core").value,
      variables_changed: document.getElementById("strategy-vars").value,
      expected_effect: document.getElementById("strategy-effect").value
    };

    if (!strategyData.version_name || !strategyData.start_date || !strategyData.core_strategy) {
      resultEl.textContent = "✗ 请填写必填字段";
      resultEl.className = "result-msg error";
      return;
    }

    try {
      const res = await fetch(`/api/tools/${toolId}/strategy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(strategyData)
      });
      const data = await res.json();
      
      if (data.ok) {
        resultEl.textContent = "✓ " + data.message;
        resultEl.className = "result-msg success";
        // 清空表单
        document.getElementById("strategy-name").value = "";
        document.getElementById("strategy-core").value = "";
        document.getElementById("strategy-vars").value = "";
        document.getElementById("strategy-effect").value = "";
        // 重新加载
        setTimeout(loadStrategy, 1000);
      } else {
        resultEl.textContent = "✗ " + data.error;
        resultEl.className = "result-msg error";
      }
    } catch (err) {
      resultEl.textContent = "✗ 创建失败: " + err.message;
      resultEl.className = "result-msg error";
    }
  });

  // 数据导出
  document.getElementById("export-data")?.addEventListener("click", async () => {
    try {
      const res = await fetch(`/api/tools/${toolId}/export`);
      const data = await res.json();
      
      if (data.ok) {
        document.getElementById("export-json").value = JSON.stringify(data.data, null, 2);
      } else {
        document.getElementById("export-json").value = "导出失败: " + data.error;
      }
    } catch (err) {
      document.getElementById("export-json").value = "导出失败: " + err.message;
    }
  });

  document.getElementById("copy-export")?.addEventListener("click", () => {
    const textarea = document.getElementById("export-json");
    textarea.select();
    document.execCommand("copy");
    alert("已复制到剪贴板");
  });

  // 初始化：加载仪表盘
  loadDashboard();
}

document.addEventListener("DOMContentLoaded", () => {
  initTextViewer();
  initMediaShelf();
  initBodyWeight();

  document.body.addEventListener("click", async (e) => {
    const runBtn = e.target.closest(".btn-run");
    if (!runBtn) return;

    const toolId = runBtn.dataset.tool;
    const form = runBtn.closest(".tool-form");
    const resultEl = form?.querySelector(".result");
    if (!resultEl) return;

    resultEl.textContent = "执行中...";
    resultEl.className = "result";

    const payload = {};
    form.querySelectorAll("[data-param]").forEach((el) => {
      const val = el.type === "checkbox" ? (el.checked ? "1" : "0") : (el.value || "").trim();
      payload[el.dataset.param] = val;
    });

    try {
      const res = await fetch(`/api/tools/${toolId}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.ok) {
        resultEl.className = "result success";
        let msg;
        if (data.skipped !== undefined) {
          msg = `已重命名 ${(data.renamed || []).length} 个文件`;
          if (data.renamed?.length) msg += "\n" + data.renamed.map(([a, b]) => `${a} → ${b}`).join("\n");
          if (data.skipped.length) msg += `\n未找到 ${data.skipped.length} 个: ${data.skipped.join(", ")}`;
          if (data.errors?.length) msg += "\n错误: " + data.errors.join("; ");
        } else if (data.lines_written !== undefined) {
          msg = `已写入 ${data.lines_written} 行到 ${data.output}`;
          if (data.errors?.length) msg += "\n错误: " + data.errors.join("; ");
        } else if (data.moved !== undefined) {
          msg = `完成。移动了 ${data.moved.length} 个文件`;
          if (data.renamed?.length) msg += `\n重命名: ${data.renamed.map(([a, b]) => `${a} → ${b}`).join(", ")}`;
          if (data.errors?.length) msg += `\n错误: ${data.errors.join("; ")}`;
        } else {
          msg = "完成。";
        }
        resultEl.textContent = msg;
      } else {
        resultEl.className = "result error";
        resultEl.textContent = data.error || "未知错误";
      }
    } catch (err) {
      resultEl.className = "result error";
      resultEl.textContent = "请求失败: " + err.message;
    }
  });
});
