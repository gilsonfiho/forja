// WorkG dashboard — formulário dinâmico por agent + renderização rica do resultado.
(function () {
  const specs = window.WORKG_SPECS || [];
  const bySlug = Object.fromEntries(specs.map((s) => [s.slug, s]));

  const $ = (id) => document.getElementById(id);
  const form = $("run-form");
  const slugSel = $("slug");
  const actionSel = $("action");
  const actionDesc = $("action-desc");
  const dynParams = $("dynamic-params");
  const promptWrap = $("prompt-wrap");
  const btn = $("run-btn");

  // Campo principal a renderizar como markdown, por prioridade.
  const PRIMARY_KEYS = ["answer", "analysis", "output", "markdown", "report", "instructions"];

  // ---------- Markdown ----------
  function renderMarkdown(el, md) {
    const html = window.marked ? marked.parse(md || "") : (md || "");
    el.innerHTML = window.DOMPurify ? DOMPurify.sanitize(html) : html;
    if (window.hljs) el.querySelectorAll("pre code").forEach((b) => hljs.highlightElement(b));
  }

  // ---------- Formulário dinâmico ----------
  function currentAction() {
    const spec = bySlug[slugSel.value];
    return (spec && spec.actions || []).find((a) => a.name === actionSel.value);
  }

  function buildActions() {
    const spec = bySlug[slugSel.value];
    actionSel.innerHTML = "";
    const actions = (spec && spec.actions) || [];
    if (actions.length === 0) {
      actionSel.innerHTML = '<option value="default">default</option>';
    } else {
      actions.forEach((a, i) => {
        const o = document.createElement("option");
        o.value = a.name;
        o.textContent = a.name + (i === 0 ? " (default)" : "");
        actionSel.appendChild(o);
      });
    }
    buildParams();
  }

  function buildParams() {
    const action = currentAction();
    actionDesc.textContent = action ? action.description || "" : "";
    dynParams.innerHTML = "";
    const params = (action && action.params) || [];
    params.forEach((p) => {
      const label = document.createElement("label");
      const req = p.required ? ' <span class="req">*</span>' : "";
      label.innerHTML = `${p.name}${req}` + (p.help ? ` <small>${p.help}</small>` : "");
      const input = document.createElement("input");
      input.dataset.param = p.name;
      input.placeholder = p.placeholder || "";
      if (p.required) input.required = true;
      label.appendChild(input);
      dynParams.appendChild(label);
    });
    promptWrap.style.display = (!action || action.accepts_prompt !== false) ? "" : "none";
  }

  function collectParams() {
    const params = {};
    dynParams.querySelectorAll("input[data-param]").forEach((i) => {
      if (i.value.trim()) params[i.dataset.param] = i.value.trim();
    });
    ($("params").value || "").split("\n").forEach((line) => {
      const k = line.indexOf("=");
      if (k > 0) params[line.slice(0, k).trim()] = line.slice(k + 1).trim();
    });
    return params;
  }

  slugSel.addEventListener("change", buildActions);
  actionSel.addEventListener("change", buildParams);

  document.querySelectorAll(".card").forEach((card) => {
    const pick = () => {
      slugSel.value = card.dataset.slug;
      buildActions();
      slugSel.scrollIntoView({ behavior: "smooth", block: "center" });
    };
    card.addEventListener("click", pick);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); }
    });
  });

  // ---------- Render de dados estruturados ----------
  function isPlainObject(v) { return v && typeof v === "object" && !Array.isArray(v); }

  function tableFromArray(arr) {
    if (arr.length && isPlainObject(arr[0])) {
      const cols = [...new Set(arr.flatMap((o) => Object.keys(o)))];
      const head = cols.map((c) => `<th>${c}</th>`).join("");
      const rows = arr.map((o) =>
        "<tr>" + cols.map((c) => `<td>${fmtScalar(o[c])}</td>`).join("") + "</tr>").join("");
      return `<table class="dtable"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>`;
    }
    return `<ul class="dlist">${arr.map((v) => `<li>${fmtScalar(v)}</li>`).join("")}</ul>`;
  }

  function fmtScalar(v) {
    if (v === null || v === undefined) return '<span class="muted">—</span>';
    if (typeof v === "object") return `<code>${escapeHtml(JSON.stringify(v))}</code>`;
    return escapeHtml(String(v));
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function renderData(container, data) {
    container.innerHTML = "";
    const entries = Object.entries(data || {});
    if (!entries.length) { container.innerHTML = '<p class="muted">Sem dados estruturados.</p>'; return; }
    entries.forEach(([key, val]) => {
      const block = document.createElement("div");
      block.className = "data-block";
      let body;
      if (Array.isArray(val)) body = tableFromArray(val);
      else if (isPlainObject(val)) body = tableFromArray([val]);
      else body = `<div class="data-scalar">${fmtScalar(val)}</div>`;
      block.innerHTML = `<h4>${escapeHtml(key)}</h4>${body}`;
      container.appendChild(block);
    });
  }

  // ---------- Artefatos ----------
  function renderArtifacts(container, artifacts) {
    container.innerHTML = "";
    if (!artifacts || !artifacts.length) {
      container.innerHTML = '<p class="muted">Nenhum artefato gerado.</p>'; return;
    }
    artifacts.forEach((path) => {
      const card = document.createElement("div");
      card.className = "artifact";
      const name = path.split(/[\\/]/).pop();
      card.innerHTML =
        `<div class="artifact-head"><span>📄 ${escapeHtml(name)}</span>
         <button class="ghost" type="button">pré-visualizar</button></div>
         <div class="artifact-body markdown hidden"></div>`;
      const body = card.querySelector(".artifact-body");
      card.querySelector("button").addEventListener("click", async () => {
        body.classList.toggle("hidden");
        if (body.dataset.loaded) return;
        body.textContent = "carregando…";
        try {
          const res = await fetch(`/api/artifact?path=${encodeURIComponent(path)}`);
          const d = await res.json();
          if (!res.ok) { body.textContent = d.detail || "erro"; return; }
          if (d.kind === "markdown") renderMarkdown(body, d.content);
          else body.innerHTML = `<pre class="code"><code>${escapeHtml(d.content)}</code></pre>`;
          if (window.hljs) body.querySelectorAll("pre code").forEach((b) => hljs.highlightElement(b));
          body.dataset.loaded = "1";
        } catch (e) { body.textContent = "erro: " + e; }
      });
      container.appendChild(card);
    });
  }

  async function loadArtifactInto(el, path) {
    try {
      const res = await fetch(`/api/artifact?path=${encodeURIComponent(path)}`);
      const d = await res.json();
      if (!res.ok) { el.innerHTML = `<p class="muted">${escapeHtml(d.detail || "erro")}</p>`; return; }
      if (d.kind === "markdown") renderMarkdown(el, d.content);
      else { el.innerHTML = `<pre class="code"><code>${escapeHtml(d.content)}</code></pre>`;
        if (window.hljs) el.querySelectorAll("pre code").forEach((b) => hljs.highlightElement(b)); }
    } catch (e) { el.innerHTML = `<p class="muted">erro: ${escapeHtml(String(e))}</p>`; }
  }

  // ---------- Render principal ----------
  function duration(a, b) {
    if (!a || !b) return "";
    const ms = new Date(b) - new Date(a);
    return ms >= 0 ? `${ms} ms` : "";
  }

  function renderResult(data) {
    $("result-section").classList.remove("hidden");
    const chip = $("status-chip");
    chip.textContent = data.ok ? "OK" : "ERRO";
    chip.className = "chip " + (data.ok ? "ok" : "err");
    $("result-title").textContent = `${data.agent} · ${data.action}`;
    $("result-time").textContent = duration(data.started_at, data.finished_at);
    $("result-summary").textContent = data.summary || "";
    $("json-view").textContent = JSON.stringify(data, null, 2);

    const d = data.data || {};
    const key = PRIMARY_KEYS.find((k) => typeof d[k] === "string" && d[k].trim());
    const rendered = $("rendered");
    const mdArtifact = (data.artifacts || []).find((p) => p.toLowerCase().endsWith(".md"));
    if (key) {
      renderMarkdown(rendered, d[key]);
    } else if (mdArtifact) {
      rendered.innerHTML = '<p class="muted">Renderizando artefato…</p>';
      loadArtifactInto(rendered, mdArtifact);
    } else if (data.error) {
      rendered.innerHTML = `<div class="callout err">${escapeHtml(data.error)}</div>`;
    } else {
      rendered.innerHTML = `<p class="muted">Sem conteúdo textual — veja as abas Dados / Artefatos.</p>`;
    }
    renderArtifacts($("artifacts"), data.artifacts);
    renderData($("data-view"), d);
    switchTab("rendered");
    $("result-section").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function switchTab(name) {
    document.querySelectorAll(".tab").forEach((t) =>
      t.classList.toggle("active", t.dataset.tab === name));
    document.querySelectorAll(".tab-panel").forEach((p) =>
      p.classList.toggle("active", p.id === "panel-" + name));
  }
  document.querySelectorAll(".tab").forEach((t) =>
    t.addEventListener("click", () => switchTab(t.dataset.tab)));

  $("copy-btn").addEventListener("click", () => {
    navigator.clipboard.writeText($("json-view").textContent || "");
  });

  // ---------- Submit ----------
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true; btn.textContent = "Executando…";
    const action = actionSel.value || "default";
    const acceptsPrompt = promptWrap.style.display !== "none";
    const body = {
      action,
      prompt: acceptsPrompt ? ($("prompt").value || null) : null,
      params: collectParams(),
      dry_run: $("dry_run").checked,
    };
    try {
      const res = await fetch(`/api/agents/${slugSel.value}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok && !data.agent) {
        renderResult({ agent: slugSel.value, action, ok: false,
          summary: data.detail || "erro", data: {}, artifacts: [], error: data.detail });
      } else {
        renderResult(data);
      }
    } catch (err) {
      renderResult({ agent: slugSel.value, action, ok: false,
        summary: "falha de rede", data: {}, artifacts: [], error: String(err) });
    } finally {
      btn.disabled = false; btn.textContent = "▶ Executar";
    }
  });

  buildActions();
})();
