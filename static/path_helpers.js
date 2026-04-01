/**
 * 路径辅助：选择文件夹（调用本机 API）、粘贴 Windows 路径并转为 WSL、常用路径预设。
 * 需配合 input/textarea 上的 data-wsl-path-input；多行目录用 data-path-mode="append"。
 */
function winPathToWsl(s) {
  if (!s) return "";
  let t = String(s).trim().replace(/^["']|["']$/g, "");
  t = t.replace(/\\/g, "/");
  const unc = /^\/\/wsl(?:\.localhost)?\//i.test(t);
  if (unc) {
    const parts = t.split("/").filter(Boolean);
    if (parts.length >= 2 && /^wsl/i.test(parts[0])) {
      const rest = parts.slice(2).join("/");
      return rest ? "/" + rest : "/";
    }
  }
  const m = /^([a-zA-Z]):(\/.*)?$/.exec(t);
  if (m) {
    const drive = m[1].toLowerCase();
    const rest = (m[2] || "").replace(/^\/+/, "");
    return "/mnt/" + drive + (rest ? "/" + rest : "");
  }
  return t;
}

function injectPathToolbar(input) {
  if (input.dataset.pathToolbarInjected) return;
  input.dataset.pathToolbarInjected = "1";

  const toolbar = document.createElement("div");
  toolbar.className = "path-toolbar";

  const btnPick = document.createElement("button");
  btnPick.type = "button";
  btnPick.className = "btn-path";
  btnPick.textContent = "选择文件夹…";
  btnPick.title = "调用本机对话框（WSL 下通常为 Windows 文件夹选择器）";

  const btnPaste = document.createElement("button");
  btnPaste.type = "button";
  btnPaste.className = "btn-path";
  btnPaste.textContent = "粘贴 Windows 路径";
  btnPaste.title = "从剪贴板读取 C:\\... 并转为 /mnt/c/...";

  btnPick.addEventListener("click", async () => {
    btnPick.disabled = true;
    try {
      const res = await fetch("/api/pick-folder", { method: "POST" });
      const data = await res.json();
      if (data.ok && data.path) {
        applyPath(input, data.path);
      } else {
        alert(data.error || "未获取路径");
      }
    } catch (e) {
      alert("请求失败: " + e.message);
    } finally {
      btnPick.disabled = false;
    }
  });

  btnPaste.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      const wsl = winPathToWsl(text);
      if (!wsl) {
        alert("剪贴板为空或无法识别");
        return;
      }
      applyPath(input, wsl);
    } catch (e) {
      alert("读取剪贴板失败（部分浏览器需 HTTPS 或权限）: " + e.message);
    }
  });

  toolbar.appendChild(btnPick);
  toolbar.appendChild(btnPaste);
  input.insertAdjacentElement("afterend", toolbar);
}

function applyPath(input, path) {
  const mode = input.getAttribute("data-path-mode") || "replace";
  if (mode === "append") {
    const cur = (input.value || "").trim();
    input.value = cur ? cur + "\n" + path : path;
  } else {
    input.value = path;
  }
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

async function injectPresets() {
  const forms = document.querySelectorAll(".tool-form");
  if (!forms.length) return;

  let data;
  try {
    const res = await fetch("/api/path-presets");
    data = await res.json();
  } catch {
    return;
  }
  const presets = data.presets || [];
  if (!presets.length) return;

  forms.forEach((form) => {
    if (form.querySelector(".path-presets")) return;
    const bar = document.createElement("div");
    bar.className = "path-presets";
    const label = document.createElement("span");
    label.className = "path-presets-label";
    label.textContent = "常用路径";
    bar.appendChild(label);

    presets.forEach((p) => {
      if (!p || !p.path) return;
      const b = document.createElement("button");
      b.type = "button";
      b.className = "path-preset-chip";
      b.textContent = p.label || p.path;
      b.title = p.path;
      b.addEventListener("click", () => {
        const targets = form.querySelectorAll("[data-wsl-path-input]");
        const first = targets[0];
        if (first) applyPath(first, p.path);
      });
      bar.appendChild(b);
    });

    const first = form.querySelector(".desc, .tool-form > .field");
    if (first) {
      first.insertAdjacentElement("beforebegin", bar);
    } else {
      form.insertBefore(bar, form.firstChild);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-wsl-path-input]").forEach(injectPathToolbar);
  injectPresets();
});
