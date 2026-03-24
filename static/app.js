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
    return items.filter((x) => {
      if (c !== "all" && x.category !== c) return false;
      if (s !== "all" && x.status !== s) return false;
      if (source !== "all" && x.source !== source) return false;
      if (!q) return true;
      const hay = `${x.title || ""} ${x.note || ""}`.toLowerCase();
      return hay.includes(q);
    });
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

document.addEventListener("DOMContentLoaded", () => {
  initTextViewer();
  initMediaShelf();

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
