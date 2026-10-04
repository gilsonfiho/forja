// Dashboard: dispara agents via API e mostra o resultado.
(function () {
  const form = document.getElementById("run-form");
  const result = document.getElementById("result");
  const slug = document.getElementById("slug");
  const btn = document.getElementById("run-btn");

  // Clicar num card seleciona o agent no formulário.
  document.querySelectorAll(".card").forEach((card) => {
    const pick = () => {
      slug.value = card.dataset.slug;
      slug.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
    card.addEventListener("click", pick);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); }
    });
  });

  function parseParams(text) {
    const params = {};
    text.split("\n").forEach((line) => {
      const i = line.indexOf("=");
      if (i > 0) params[line.slice(0, i).trim()] = line.slice(i + 1).trim();
    });
    return params;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btn.disabled = true;
    result.textContent = "Executando…";
    const body = {
      action: document.getElementById("action").value || "default",
      prompt: document.getElementById("prompt").value || null,
      params: parseParams(document.getElementById("params").value),
      dry_run: document.getElementById("dry_run").checked,
    };
    try {
      const res = await fetch(`/api/agents/${slug.value}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      result.textContent = JSON.stringify(data, null, 2);
      result.classList.toggle("error", !res.ok || data.ok === false);
    } catch (err) {
      result.textContent = "Erro: " + err;
      result.classList.add("error");
    } finally {
      btn.disabled = false;
    }
  });
})();
