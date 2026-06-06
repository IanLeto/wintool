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
    return status === "watched" ? "已完成" : (status === "unwatched" ? "未完成" : "未标注");
  }

  function categoryLabel(category) {
    if (category === "movie") return "电影";
    if (category === "tv") return "电视剧";
    if (category === "anime") return "动漫";
    if (category === "game") return "游戏";
    if (category === "book") return "书籍";
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
    const game = list.filter((x) => x.category === "game").length;
    const book = list.filter((x) => x.category === "book").length;
    
    let pills = [`共 ${list.length} 条`];
    if (movie > 0) pills.push(`电影 ${movie}`);
    if (tv > 0) pills.push(`电视剧 ${tv}`);
    if (anime > 0) pills.push(`动漫 ${anime}`);
    if (game > 0) pills.push(`游戏 ${game}`);
    if (book > 0) pills.push(`书籍 ${book}`);
    pills.push(`<span class="is-watched">已完成 ${watched}</span>`);
    pills.push(`<span class="is-unwatched">未完成 ${unwatched}</span>`);
    
    summaryEl.innerHTML = pills.map(p => `<span class="media-pill">${p}</span>`).join('');
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

function promptBankSuggestFilename() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `新提示词-${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}.md`;
}

function initPromptBank() {
  const root = document.querySelector("[data-prompt-bank]");
  if (!root) return;

  const toolId = root.dataset.toolId || "prompt_bank";
  const refreshBtn = root.querySelector(".prompt-bank-refresh");
  const filterInput = root.querySelector(".prompt-bank-filter");
  const listWrap = root.querySelector(".prompt-bank-list-wrap");
  const newNameInput = root.querySelector(".prompt-bank-new-name");
  const newBtn = root.querySelector(".prompt-bank-new");
  const currentEl = root.querySelector("[data-prompt-current]");
  const bodyEl = root.querySelector(".prompt-bank-body");
  const saveBtn = root.querySelector(".prompt-bank-save");
  const deleteBtn = root.querySelector(".prompt-bank-delete");
  const statusEl = root.querySelector(".prompt-bank-status");

  let files = [];
  /** @type {string | null} */
  let activeFile = null;
  /** @type {string | null} */
  let lastSavedSnapshot = null;

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s ?? "";
    return d.innerHTML;
  }

  function setStatus(msg, isErr) {
    statusEl.textContent = msg || "";
    statusEl.style.color = isErr ? "var(--danger)" : "var(--muted)";
  }

  function isDirty() {
    if (!activeFile) return (bodyEl.value || "").trim().length > 0;
    return bodyEl.value !== lastSavedSnapshot;
  }

  function filteredFiles() {
    const q = (filterInput.value || "").trim().toLowerCase();
    if (!q) return files;
    return files.filter((f) => f.toLowerCase().includes(q));
  }

  function renderList() {
    const list = filteredFiles();
    if (!list.length) {
      listWrap.innerHTML =
        '<p class="text-viewer-placeholder" style="margin:0.5rem">暂无匹配文件。</p>';
      return;
    }
    listWrap.innerHTML = list
      .map((f) => {
        const active = f === activeFile ? " is-active" : "";
        const enc = encodeURIComponent(f);
        return `<button type="button" class="prompt-bank-file-btn${active}" data-file="${enc}">${esc(f)}</button>`;
      })
      .join("");
  }

  async function loadList(selectName) {
    setStatus("加载列表…");
    try {
      const res = await fetch(`/api/tools/${encodeURIComponent(toolId)}/list`);
      const data = await res.json();
      if (!data.ok) {
        setStatus(data.error || "列表失败", true);
        return;
      }
      files = data.files || [];
      renderList();
      const pick =
        selectName && files.includes(selectName)
          ? selectName
          : activeFile && files.includes(activeFile)
            ? activeFile
            : null;
      if (pick) await openFile(pick, true);
      else if (files.length) await openFile(files[0], true);
      else {
        activeFile = null;
        currentEl.textContent = "（未选择）";
        bodyEl.value = "";
        lastSavedSnapshot = "";
        setStatus("目录为空，可在左侧填写新文件名后保存");
      }
    } catch (err) {
      setStatus("请求失败: " + err.message, true);
    }
  }

  async function openFile(name, force) {
    if (!force && isDirty()) {
      // eslint-disable-next-line no-alert
      if (!window.confirm("当前内容未保存，确定切换文件？")) return;
    }
    setStatus("读取…");
    try {
      const res = await fetch(
        `/api/tools/${encodeURIComponent(toolId)}/content?file=${encodeURIComponent(name)}`
      );
      const data = await res.json();
      if (!data.ok) {
        setStatus(data.error || "读取失败", true);
        return;
      }
      activeFile = data.file;
      bodyEl.value = data.content ?? "";
      lastSavedSnapshot = bodyEl.value;
      currentEl.textContent = activeFile;
      renderList();
      setStatus("");
    } catch (err) {
      setStatus("请求失败: " + err.message, true);
    }
  }

  async function saveCurrent() {
    let name = activeFile || (newNameInput.value || "").trim();
    if (!name) {
      name = promptBankSuggestFilename();
      newNameInput.value = name;
    }
    setStatus("保存中…");
    try {
      const res = await fetch(`/api/tools/${encodeURIComponent(toolId)}/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file: name, content: bodyEl.value }),
      });
      const data = await res.json();
      if (!data.ok) {
        setStatus(data.error || "保存失败", true);
        return;
      }
      activeFile = data.file;
      currentEl.textContent = activeFile;
      lastSavedSnapshot = bodyEl.value;
      newNameInput.value = "";
      await loadList(activeFile);
      setStatus("已保存");
    } catch (err) {
      setStatus("请求失败: " + err.message, true);
    }
  }

  async function deleteCurrent() {
    if (!activeFile) {
      setStatus("没有选中的文件", true);
      return;
    }
    // eslint-disable-next-line no-alert
    if (!window.confirm(`确定删除文件「${activeFile}」？不可恢复。`)) return;
    setStatus("删除中…");
    try {
      const res = await fetch(`/api/tools/${encodeURIComponent(toolId)}/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file: activeFile }),
      });
      const data = await res.json();
      if (!data.ok) {
        setStatus(data.error || "删除失败", true);
        return;
      }
      activeFile = null;
      bodyEl.value = "";
      lastSavedSnapshot = "";
      currentEl.textContent = "（未选择）";
      await loadList(null);
      setStatus("已删除");
    } catch (err) {
      setStatus("请求失败: " + err.message, true);
    }
  }

  function createNew() {
    if (isDirty()) {
      // eslint-disable-next-line no-alert
      if (!window.confirm("当前编辑未保存，确定新建？")) return;
    }
    activeFile = null;
    bodyEl.value = "";
    lastSavedSnapshot = "";
    newNameInput.value = promptBankSuggestFilename();
    newNameInput.placeholder = "可改文件名；留空则保存时自动生成";
    currentEl.textContent = `将保存为：${newNameInput.value}`;
    setStatus("已填入默认文件名，可直接在右侧粘贴内容后点「保存」");
    renderList();
  }

  refreshBtn.addEventListener("click", () => loadList(activeFile));
  filterInput.addEventListener("input", renderList);
  listWrap.addEventListener("click", (e) => {
    const btn = e.target.closest(".prompt-bank-file-btn");
    const raw = btn?.getAttribute("data-file");
    if (!btn || raw == null || raw === "") return;
    let name;
    try {
      name = decodeURIComponent(raw);
    } catch {
      return;
    }
    openFile(name, false);
  });
  saveBtn.addEventListener("click", () => saveCurrent());
  deleteBtn.addEventListener("click", () => deleteCurrent());
  newBtn.addEventListener("click", () => createNew());

  loadList(null);
}

function initExportDirStructure() {
  const root = document.querySelector("[data-export-dir-structure]");
  if (!root) return;

  const toolId = root.dataset.toolId || "export_dir_structure";
  const dirsEl = root.querySelector("[data-export-dirs]");
  const shallowEl = root.querySelector("[data-export-shallow]");
  const depthEl = root.querySelector("[data-export-depth]");
  const treeEl = root.querySelector("[data-export-tree]");
  const statsEl = root.querySelector("[data-export-stats]");
  const preEl = root.querySelector("[data-export-preview-text]");
  const metaEl = root.querySelector("[data-export-meta]");
  const msgEl = root.querySelector("[data-export-msg]");
  const copyBtn = root.querySelector("[data-export-copy]");
  const previewBtn = root.querySelector("[data-export-preview]");
  const saveBtn = root.querySelector("[data-export-save]");
  const outputEl = root.querySelector("[data-export-output]");

  let lastText = "";

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s ?? "";
    return d.innerHTML;
  }

  function setMsg(text, kind) {
    msgEl.textContent = text || "";
    msgEl.classList.remove("is-error", "is-ok", "is-info");
    if (kind === "error") msgEl.classList.add("is-error");
    if (kind === "ok") msgEl.classList.add("is-ok");
    if (kind === "info") msgEl.classList.add("is-info");
  }

  function setMeta(data) {
    if (!data) {
      metaEl.textContent = "等待生成...";
      return;
    }
    const stats = data.stats || {};
    const parts = [];
    if (data.lines != null) parts.push(`${data.lines} 行`);
    if (stats.total_dirs != null) parts.push(`${stats.total_dirs} 个文件夹`);
    if (stats.total_files != null) parts.push(`${stats.total_files} 个文件`);
    if (data.errors?.length) parts.push(`⚠️ ${data.errors.length} 个错误`);
    metaEl.textContent = parts.join(" · ") || "已生成";
  }

  async function doPreview() {
    setMsg("");
    preEl.textContent = "正在生成目录结构...";
    copyBtn.disabled = true;
    lastText = "";
    setMeta(null);
    previewBtn.disabled = true;
    
    try {
      const maxDepth = shallowEl.checked ? 1 : (parseInt(depthEl.value) || 5);
      
      const res = await fetch(`/api/tools/${encodeURIComponent(toolId)}/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dirs: dirsEl.value || "",
          shallow: shallowEl.checked ? "1" : "0",
          max_depth: maxDepth,
          tree_format: treeEl.checked ? "1" : "0",
          show_stats: statsEl.checked ? "1" : "0",
        }),
      });
      
      const data = await res.json();
      
      if (!data.ok) {
        preEl.textContent = "❌ 生成失败";
        const errorMsg = data.error || "生成失败";
        const details = data.details ? "\n详情: " + data.details.join("; ") : "";
        setMsg(errorMsg + details, "error");
        setMeta(null);
        return;
      }
      
      lastText = data.text ?? "";
      preEl.textContent = lastText || "（空结果）";
      copyBtn.disabled = !lastText;
      setMeta(data);
      
      // 显示转换信息
      let messages = [];
      if (data.conversions?.length) {
        messages.push("✓ 路径已转换: " + data.conversions.length + " 个");
      }
      if (data.errors?.length) {
        messages.push("⚠️ " + data.errors.join("; "));
      }
      if (!messages.length) {
        messages.push("✓ 生成成功！可复制或保存到文件");
      }
      
      setMsg(messages.join(" | "), data.errors?.length ? "error" : "ok");
      
    } catch (err) {
      preEl.textContent = "❌ 请求失败";
      setMsg("请求失败: " + err.message, "error");
      setMeta(null);
    } finally {
      previewBtn.disabled = false;
    }
  }

  previewBtn.addEventListener("click", () => doPreview());

  copyBtn.addEventListener("click", async () => {
    if (!lastText) return;
    try {
      await navigator.clipboard.writeText(lastText);
      setMsg("✓ 已复制到剪贴板", "ok");
      setTimeout(() => setMsg(""), 2000);
    } catch (e) {
      setMsg("复制失败: " + e.message, "error");
    }
  });

  saveBtn.addEventListener("click", async () => {
    const output = (outputEl.value || "").trim();
    if (!output) {
      setMsg("请先填写输出文件路径", "error");
      return;
    }
    
    setMsg("正在写入文件...", "info");
    saveBtn.disabled = true;
    
    try {
      const maxDepth = shallowEl.checked ? 1 : (parseInt(depthEl.value) || 5);
      
      const res = await fetch(`/api/tools/${encodeURIComponent(toolId)}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dirs: dirsEl.value || "",
          shallow: shallowEl.checked ? "1" : "0",
          max_depth: maxDepth,
          tree_format: treeEl.checked ? "1" : "0",
          show_stats: statsEl.checked ? "1" : "0",
          output,
        }),
      });
      
      const data = await res.json();
      
      if (!data.ok) {
        setMsg(data.error || "写入失败", "error");
        return;
      }
      
      lastText = data.text ?? lastText;
      if (lastText) {
        preEl.textContent = lastText;
        copyBtn.disabled = false;
      }
      
      setMeta(data);
      
      let msg = `✓ 已写入 ${data.lines_written ?? 0} 行 → ${data.output}`;
      if (data.errors?.length) {
        msg += " | ⚠️ " + data.errors.join("; ");
      }
      setMsg(msg, data.errors?.length ? "error" : "ok");
      
    } catch (err) {
      setMsg("请求失败: " + err.message, "error");
    } finally {
      saveBtn.disabled = false;
    }
  });

  // 浅层模式切换时禁用深度输入
  shallowEl.addEventListener("change", () => {
    if (depthEl) {
      depthEl.disabled = shallowEl.checked;
    }
  });
}

function initAiLibrary() {
  const root = document.querySelector("[data-ai-library]");
  if (!root) return;

  const toolId = root.dataset.toolId || "ai_library";
  const refreshBtn = root.querySelector(".ai-library-refresh");
  const groupSel = root.querySelector(".ai-library-group");
  const filterInput = root.querySelector(".ai-library-filter");
  const metaEl = root.querySelector(".ai-library-meta");
  const fileListEl = root.querySelector(".ai-library-filelist");
  const mainEl = root.querySelector(".ai-library-main");

  let files = [];
  let activeFile = null;

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s ?? "";
    return d.innerHTML;
  }

  function filteredFiles() {
    const q = (filterInput.value || "").trim().toLowerCase();
    if (!q) return files;
    return files.filter((x) => x.toLowerCase().includes(q));
  }

  function renderFileList() {
    const list = filteredFiles();
    fileListEl.innerHTML = "";
    if (!list.length) {
      fileListEl.innerHTML = '<p class="ai-library-empty">没有匹配文件</p>';
      return;
    }
    list.forEach((name) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "ai-library-file" + (name === activeFile ? " is-active" : "");
      btn.dataset.file = name;
      btn.textContent = name;
      fileListEl.appendChild(btn);
    });
  }

  async function loadContent(name) {
    if (!name) return;
    activeFile = name;
    renderFileList();
    mainEl.innerHTML = '<p class="ai-library-placeholder">正在加载正文…</p>';
    try {
      const group = groupSel.value || "answers";
      const u = `/api/tools/${encodeURIComponent(toolId)}/content?group=${encodeURIComponent(group)}&file=${encodeURIComponent(name)}`;
      const res = await fetch(u);
      const data = await res.json();
      if (!data.ok) {
        mainEl.innerHTML = `<p class="ai-library-error">${esc(data.error || "读取失败")}</p>`;
        return;
      }
      mainEl.innerHTML = `<pre class="ai-library-pre"><code>${esc(data.content || "")}</code></pre>`;
    } catch (err) {
      mainEl.innerHTML = `<p class="ai-library-error">${esc("请求失败: " + err.message)}</p>`;
    }
  }

  async function fetchList() {
    fileListEl.innerHTML = "";
    mainEl.innerHTML = '<p class="ai-library-placeholder">正在加载列表…</p>';
    metaEl.textContent = "";
    try {
      const group = groupSel.value || "answers";
      const u = `/api/tools/${encodeURIComponent(toolId)}/list?group=${encodeURIComponent(group)}`;
      const res = await fetch(u);
      const data = await res.json();
      if (!data.ok) {
        mainEl.innerHTML = `<p class="ai-library-error">${esc(data.error || "加载失败")}</p>`;
        return;
      }
      files = data.files || [];
      metaEl.innerHTML = `
        <span class="ai-library-pill">${esc(data.group_label || group)}</span>
        <span class="ai-library-pill">${files.length} 个文件</span>
        <span class="ai-library-dir">${esc(data.dir || "")}</span>
      `;

      if (!files.length) {
        activeFile = null;
        const hint = data.hint ? `<span class="ai-library-hint">${esc(data.hint)}</span>` : "";
        mainEl.innerHTML = `<p class="ai-library-placeholder">当前目录暂无可展示文件。${hint}</p>`;
        renderFileList();
        return;
      }
      if (!activeFile || !files.includes(activeFile)) {
        activeFile = files[0];
      }
      renderFileList();
      await loadContent(activeFile);
    } catch (err) {
      mainEl.innerHTML = `<p class="ai-library-error">${esc("请求失败: " + err.message)}</p>`;
    }
  }

  fileListEl.addEventListener("click", (e) => {
    const btn = e.target.closest(".ai-library-file");
    if (!btn || !root.contains(btn)) return;
    const name = btn.dataset.file;
    if (name) loadContent(name);
  });

  refreshBtn.addEventListener("click", () => fetchList());
  groupSel.addEventListener("change", () => {
    activeFile = null;
    fetchList();
  });
  filterInput.addEventListener("input", () => {
    const list = filteredFiles();
    renderFileList();
    if (!list.length) {
      mainEl.innerHTML = '<p class="ai-library-placeholder">没有匹配文件。</p>';
      return;
    }
    if (!list.includes(activeFile)) {
      loadContent(list[0]);
    }
  });

  fetchList();
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
  initPromptBank();
  initExportDirStructure();
  initAiLibrary();
  initBodyWeight();
  initBatchExtract7z();

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
        } else if (Array.isArray(data.unzipped)) {
          const seven = data.seven_found ? "已检测到 7z" : "未检测到 7z（部分格式依赖 7z）";
          msg = `${seven}\n成功 ${data.unzipped.length} 个（已删原压缩包）`;
          if (data.unzipped.length) {
            msg +=
              "\n" +
              data.unzipped.map((x) => `${x.file} [${x.method}]`).join("\n");
          }
          if (data.skipped?.length) {
            msg +=
              "\n跳过 " +
              data.skipped.length +
              " 个:\n" +
              data.skipped.map((x) => `${x.file}\n  → ${x.reason}`).join("\n");
          }
          if (data.errors?.length) msg += "\n错误: " + data.errors.join("; ");
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

// ==================== 批量7z解压工具 ====================
function initBatchExtract7z() {
  const root = document.querySelector("[data-batch-extract-7z]");
  if (!root) return;

  const toolId = root.dataset.toolId || "batch_extract_7z";
  
  // 表单元素
  const sourceInput = root.querySelector("[data-batch-7z-source]");
  const passwordInput = root.querySelector("[data-batch-7z-password]");
  const depthInput = root.querySelector("[data-batch-7z-depth]");
  const deleteCheckbox = root.querySelector("[data-batch-7z-delete]");
  const skipCheckbox = root.querySelector("[data-batch-7z-skip]");
  
  // 按钮
  const scanBtn = root.querySelector("[data-batch-7z-scan]");
  const startBtn = root.querySelector("[data-batch-7z-start]");
  const stopBtn = root.querySelector("[data-batch-7z-stop]");
  
  // 显示区域
  const scanResult = root.querySelector("[data-batch-7z-scan-result]");
  const scanInfo = root.querySelector("[data-batch-7z-scan-info]");
  const statsEl = root.querySelector("[data-batch-7z-stats]");
  const currentFileEl = root.querySelector("[data-current-file]");
  const currentStageEl = root.querySelector("[data-current-stage]");
  const progressFill = root.querySelector("[data-batch-7z-progress-fill]");
  const progressText = root.querySelector("[data-batch-7z-progress-text]");
  const logsEl = root.querySelector("[data-batch-7z-logs]");
  
  let progressInterval = null;
  
  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }
  
  function addLog(message, level = "info") {
    const logItem = document.createElement("div");
    logItem.className = `batch-7z-log-item batch-7z-log-${level}`;
    logItem.textContent = message;
    logsEl.appendChild(logItem);
    logsEl.scrollTop = logsEl.scrollHeight;
    
    // 只保留最近50条
    while (logsEl.children.length > 50) {
      logsEl.removeChild(logsEl.firstChild);
    }
  }
  
  function updateStats(data) {
    root.querySelector("[data-stat-total]").textContent = data.total || 0;
    root.querySelector("[data-stat-success]").textContent = data.success || 0;
    root.querySelector("[data-stat-skipped]").textContent = data.skipped || 0;
    root.querySelector("[data-stat-failed]").textContent = data.failed || 0;
    
    currentFileEl.textContent = data.current_file || "等待开始...";
    currentStageEl.textContent = data.stage || "-";
    
    // 更新进度条
    const percent = data.total > 0 ? Math.round((data.processed / data.total) * 100) : 0;
    progressFill.style.width = percent + "%";
    progressText.textContent = percent + "%";
    
    // 显示日志
    if (data.logs && data.logs.length > 0) {
      data.logs.forEach(log => {
        const time = log.time || "";
        const msg = `[${time}] ${log.message}`;
        addLog(msg, log.level || "info");
      });
    }
  }
  
  function startProgressPolling() {
    if (progressInterval) return;
    
    progressInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/tools/${toolId}/progress`);
        const data = await res.json();
        
        updateStats(data);
        
        if (!data.running) {
          stopProgressPolling();
          startBtn.disabled = false;
          stopBtn.disabled = true;
          scanBtn.disabled = false;
        }
      } catch (err) {
        console.error("获取进度失败:", err);
      }
    }, 1000);
  }
  
  function stopProgressPolling() {
    if (progressInterval) {
      clearInterval(progressInterval);
      progressInterval = null;
    }
  }
  
  // 扫描文件
  scanBtn.addEventListener("click", async () => {
    const source = sourceInput.value.trim();
    if (!source) {
      alert("请填写源目录");
      return;
    }
    
    scanBtn.disabled = true;
    scanInfo.innerHTML = '<p class="batch-7z-loading">正在扫描...</p>';
    scanResult.style.display = "block";
    
    try {
      const res = await fetch(`/api/tools/${toolId}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source })
      });
      
      const data = await res.json();
      
      if (data.ok) {
        let html = `<p class="batch-7z-success">✓ 找到 ${data.total} 个.7z文件</p>`;
        
        if (data.files && data.files.length > 0) {
          html += '<ul class="batch-7z-file-list">';
          data.files.forEach(f => {
            html += `<li>${escapeHtml(f)}</li>`;
          });
          html += '</ul>';
        }
        
        if (data.existing_dirs && data.existing_dirs.length > 0) {
          html += `<p class="batch-7z-warning">⚠️ 已存在 ${data.existing_dirs.length} 个目录（将跳过）</p>`;
        }
        
        scanInfo.innerHTML = html;
        startBtn.disabled = data.total === 0;
      } else {
        scanInfo.innerHTML = `<p class="batch-7z-error">✗ ${escapeHtml(data.error)}</p>`;
        startBtn.disabled = true;
      }
    } catch (err) {
      scanInfo.innerHTML = `<p class="batch-7z-error">✗ 请求失败: ${escapeHtml(err.message)}</p>`;
      startBtn.disabled = true;
    } finally {
      scanBtn.disabled = false;
    }
  });
  
  // 开始解压
  startBtn.addEventListener("click", async () => {
    const source = sourceInput.value.trim();
    const password = passwordInput.value.trim();
    const maxDepth = parseInt(depthInput.value) || 3;
    const deleteOriginal = deleteCheckbox.checked;
    const skipExisting = skipCheckbox.checked;
    
    if (!source) {
      alert("请填写源目录");
      return;
    }
    
    if (!confirm("确定要开始批量解压吗？这可能需要较长时间。")) {
      return;
    }
    
    startBtn.disabled = true;
    stopBtn.disabled = false;
    scanBtn.disabled = true;
    
    // 清空日志
    logsEl.innerHTML = '<div class="batch-7z-log-item batch-7z-log-info">开始解压任务...</div>';
    
    try {
      const res = await fetch(`/api/tools/${toolId}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source,
          password,
          max_depth: maxDepth,
          delete_original: deleteOriginal,
          skip_existing: skipExisting
        })
      });
      
      const data = await res.json();
      
      if (data.ok) {
        addLog("✓ 任务已启动", "success");
        startProgressPolling();
      } else {
        addLog(`✗ 启动失败: ${data.error}`, "error");
        startBtn.disabled = false;
        stopBtn.disabled = true;
        scanBtn.disabled = false;
      }
    } catch (err) {
      addLog(`✗ 请求失败: ${err.message}`, "error");
      startBtn.disabled = false;
      stopBtn.disabled = true;
      scanBtn.disabled = false;
    }
  });
  
  // 停止解压
  stopBtn.addEventListener("click", async () => {
    if (!confirm("确定要停止解压吗？")) {
      return;
    }
    
    try {
      const res = await fetch(`/api/tools/${toolId}/stop`, {
        method: "POST"
      });
      
      const data = await res.json();
      
      if (data.ok) {
        addLog("⏹️ 正在停止...", "warning");
      } else {
        addLog(`✗ 停止失败: ${data.error}`, "error");
      }
    } catch (err) {
      addLog(`✗ 请求失败: ${err.message}`, "error");
    }
  });
  
  // 页面卸载时停止轮询
  window.addEventListener("beforeunload", () => {
    stopProgressPolling();
  });
}
