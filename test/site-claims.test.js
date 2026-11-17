import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

const pages = {
  "index.html": await read("index.html"),
  "demos/index.html": await read("demos/index.html"),
  "research/index.html": await read("research/index.html"),
  "research/ehd/index.html": await read("research/ehd/index.html"),
  "evidence/index.html": await read("evidence/index.html"),
  "demos/mv-grid-fault-risk/index.html": await read("demos/mv-grid-fault-risk/index.html"),
  "demos/rag-copilot/index.html": await read("demos/rag-copilot/index.html")
};

const prohibited = [
  /arXiv/i,
  /\bSNN\b/,
  /A production ML system/i,
  /production deployment/i,
  /production inference/i,
  /production-grade RAG/i,
  /RandomForestClassifier/,
  /NeuroGrid/,
  /MSc Data Science and AI/,
  /ocor-detailed-design/
];

test("public pages carry no claims outside the verified record", () => {
  for (const [path, html] of Object.entries(pages)) {
    prohibited.forEach((pattern) => assert.doesNotMatch(html, pattern, `${path} matches ${pattern}`));
  }
});

const unlisted = /\/demos\/(?:anomalyforge|centrico-livelab|forecast-studio|tabular-risk|visual-inspector|open-banking-enrichment|gliner-financial-ner|ehd-watch|edgepulse)\b/;

test("home, systems and research pages link only to listed projects", () => {
  for (const path of ["index.html", "demos/index.html", "research/index.html"]) {
    assert.doesNotMatch(pages[path], unlisted, `${path} links to an unlisted project`);
    assert.doesNotMatch(pages[path], /resources-nodes-system-design/, `${path} links to an unlisted project`);
  }
});

test("home and systems pages list OCOR with its status", () => {
  for (const path of ["index.html", "demos/index.html"]) {
    assert.ok(pages[path].includes("https://github.com/nepryoon/ocor\""), `${path} must link the OCOR repository`);
    assert.ok(pages[path].includes("in development"), `${path} must show the OCOR status`);
  }
});
