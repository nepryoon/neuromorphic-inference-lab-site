// /build-info.js
(async function () {
  const shaEl = document.getElementById("build-sha");
  const brEl = document.getElementById("build-branch");
  const container = document.getElementById("build-info");

  if (!container || !shaEl || !brEl) return;

  try {
    const resp = await fetch("/api/build", { cache: "no-store" });
    if (!resp.ok) throw new Error("build endpoint not available");

    const data = await resp.json();
    if (data.shaShort) shaEl.textContent = data.shaShort;
    if (data.branch) brEl.textContent = data.branch;

    // Aggiunge (una sola volta) un link al commit
    if (data.commitUrl && !document.getElementById("build-commit-link")) {
      const sep = document.createTextNode(" · ");
      const a = document.createElement("a");
      a.id = "build-commit-link";
      a.href = data.commitUrl;
      a.target = "_blank";
      a.rel = "noopener";
      a.style.textDecoration = "underline";
      a.textContent = "commit";

      container.appendChild(sep);
      container.appendChild(a);
    }
  } catch (e) {
    // fallback: lascia "unknown" senza rompere la UI
  }
})();
