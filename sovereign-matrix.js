import {
  DEFAULT_SOVEREIGN_MATRIX_URL,
  resolveSovereignMatrixUrl
} from "/config/sovereign-matrix-config.js";

const links = document.querySelectorAll("[data-sovereign-matrix-link]");

function updateLinks(destination) {
  links.forEach((link) => link.setAttribute("href", destination));
}

// Make the direct production destination available immediately. The API then
// applies a validated Cloudflare Pages environment override when configured.
updateLinks(DEFAULT_SOVEREIGN_MATRIX_URL);

fetch("/api/site-config", { headers: { accept: "application/json" } })
  .then((response) => (response.ok ? response.json() : null))
  .then((config) => {
    if (config?.sovereignMatrixUrl) {
      updateLinks(resolveSovereignMatrixUrl(config.sovereignMatrixUrl));
    }
  })
  .catch(() => {
    // Keep the safe production default; configuration must never block navigation.
  });
