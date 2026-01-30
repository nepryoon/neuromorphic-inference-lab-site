(function () {
  function setActiveNav() {
    var path = (window.location.pathname || "/").replace(/\/+$/, "") || "/";
    var links = document.querySelectorAll("[data-nav]");
    for (var i = 0; i < links.length; i++) {
      var href = links[i].getAttribute("href") || "";
      var normalised = href.replace(/\/+$/, "") || "/";
      if (normalised === path) links[i].classList.add("active");
    }
  }

  async function loadBuildProvenance() {
    var branchEl = document.getElementById("build-branch");
    var commitEl = document.getElementById("build-commit");
    var timeEl = document.getElementById("build-time");

    if (!branchEl || !commitEl || !timeEl) return;

    try {
      var res = await fetch("/api/build", { cache: "no-store" });
      if (!res.ok) throw new Error("build endpoint not ok");
      var data = await res.json();

      // Accept a few likely key names to be resilient.
      var branch = data.branch || data.BRANCH || data.gitBranch || "unknown";
      var commit = data.commit || data.COMMIT || data.gitCommit || "unknown";
      var builtAt = data.builtAt || data.time || data.timestamp || "";

      branchEl.textContent = "branch: " + branch;
      commitEl.textContent = "commit: " + String(commit).slice(0, 12);
      timeEl.textContent = builtAt ? ("built: " + builtAt) : "built: unknown";
    } catch (e) {
      branchEl.textContent = "branch: unknown";
      commitEl.textContent = "commit: unknown";
      timeEl.textContent = "built: unknown";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    setActiveNav();
    loadBuildProvenance();
  });
})();
