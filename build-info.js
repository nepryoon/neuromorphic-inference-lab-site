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
      var sha = data.sha || data.commit || data.COMMIT || data.gitCommit || "";
      var shaShort = data.shaShort || (sha ? String(sha).slice(0, 7) : "");
      var builtAt = data.built || data.builtAt || data.time || data.timestamp || "";
      var commitUrl = data.commitUrl || "";

      branchEl.textContent = "branch: " + (branch || "unavailable");
      
      // Make commit a clickable link if commitUrl is available
      if (commitUrl && shaShort) {
        commitEl.innerHTML = "commit: <a href=\"" + commitUrl + "\" target=\"_blank\" rel=\"noopener\" style=\"color: inherit; text-decoration: underline;\">" + shaShort + "</a>";
      } else {
        commitEl.textContent = "commit: " + (shaShort || "unavailable");
      }
      
      // Use shaShort as fallback when builtAt is empty
      timeEl.textContent = builtAt ? ("built: " + builtAt) : (shaShort ? ("built: " + shaShort) : "built: unavailable");
    } catch (e) {
      branchEl.textContent = "branch: local";
      commitEl.textContent = "commit: unavailable";
      timeEl.textContent = "built: unavailable";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    setActiveNav();
    loadBuildProvenance();
  });
})();
