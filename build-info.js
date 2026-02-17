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

      // Extract values
      var branch = data.branch || "unknown";
      var sha = data.sha || "";
      var shaShort = (sha || "unknown").substring(0, 7);
      var builtAt = data.builtAt || data.deployedAt || new Date().toISOString().split("T")[0];

      branchEl.textContent = "branch: " + branch;
      commitEl.textContent = "commit: " + shaShort;
      timeEl.textContent = "built: " + builtAt;
    } catch (e) {
      branchEl.textContent = "branch: local";
      commitEl.textContent = "commit: dev";
      timeEl.textContent = "built: —";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    setActiveNav();
    loadBuildProvenance();
  });
})();
