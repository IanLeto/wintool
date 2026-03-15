document.addEventListener("DOMContentLoaded", () => {
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
