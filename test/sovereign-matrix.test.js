import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  DEFAULT_SOVEREIGN_MATRIX_URL,
  resolveSovereignMatrixUrl
} from "../config/sovereign-matrix-config.js";
import { onRequestGet as getSiteConfig } from "../functions/api/site-config.js";

const home = await readFile(new URL("../index.html", import.meta.url), "utf8");
const demos = await readFile(new URL("../demos/index.html", import.meta.url), "utf8");

test("configuration uses the production default and accepts safe HTTPS overrides", async () => {
  assert.equal(DEFAULT_SOVEREIGN_MATRIX_URL, "https://matrix.neuromorphicinference.com");
  assert.equal(resolveSovereignMatrixUrl("http://unsafe.example"), DEFAULT_SOVEREIGN_MATRIX_URL);
  assert.equal(resolveSovereignMatrixUrl("https://preview.example/demo/"), "https://preview.example/demo");

  const response = getSiteConfig({ env: { NEXT_PUBLIC_SOVEREIGN_MATRIX_URL: "https://staging.example/matrix" } });
  assert.deepEqual(await response.json(), { sovereignMatrixUrl: "https://staging.example/matrix" });
});

test("homepage renders an accessible hero CTA and responsive navigation entry", () => {
  assert.match(home, />Launch Sovereign AI Demo/);
  assert.match(home, /<nav class="navlinks"[^>]*>[\s\S]*>Sovereign AI Demo/);
  assert.match(home, /data-sovereign-matrix-link[^>]*target="_blank" rel="noopener noreferrer"/);
  assert.match(home, /opens in a new tab/);
});

test("Systems catalogue renders the configured Decision Matrix card and navigation entry", () => {
  assert.match(demos, /Enterprise Sovereign AI Decision Matrix/);
  assert.match(demos, />Open Mission Control/);
  assert.match(demos, /<nav class="navlinks"[^>]*>[\s\S]*>Sovereign AI Demo/);
});
