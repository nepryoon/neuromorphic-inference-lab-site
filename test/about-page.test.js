import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../about/index.html", import.meta.url), "utf8");

const matches = (pattern) => [...html.matchAll(pattern)];

test("About page has required document metadata and semantic landmarks", () => {
  assert.equal(matches(/<main(?:\s|>)/g).length, 1);
  assert.equal(matches(/<h1(?:\s|>)/g).length, 1);
  assert.match(html, /<title>[^<]+<\/title>/);
  assert.match(html, /<meta name="description" content="[^"]+"/);
  assert.match(html, /<link rel="canonical" href="https:\/\/www\.neuromorphicinference\.com\/about\/"/);
  assert.match(html, /href="\/about\/" aria-current="page"/);

  const headingLevels = matches(/<h([1-6])(?:\s|>)/g).map((match) => Number(match[1]));
  headingLevels.slice(1).forEach((level, index) => {
    assert.ok(level <= headingLevels[index] + 1, `heading level jumps from h${headingLevels[index]} to h${level}`);
  });
});

test("About page IDs and build provenance remain valid", () => {
  const ids = matches(/\s id="([^"]+)"/g).map((match) => match[1]);
  assert.equal(new Set(ids).size, ids.length, "IDs must be unique");
  for (const id of ["build-branch", "build-commit", "build-time"]) {
    assert.equal(ids.filter((candidate) => candidate === id).length, 1, `${id} must occur once`);
  }
  assert.equal(matches(/<script src="\/build-info\.js"><\/script>/g).length, 1);
});

test("About page presents the approved positioning and evidence boundaries", () => {
  const required = [
    "Luca Lillo · Applied AI Engineer &amp; Solution Architect",
    "Ontology engineering, knowledge graphs and governed LLM agents",
    "Psychology-Informed Governance | Evidence-Led Evaluation",
    "From June to September 2026 I was Chief Technology Officer",
    "up to 30% in some territories (internal before-and-after measure)",
    "both platforms existed before I joined",
    "Implementation in development",
    "Runnable PoC",
    "PoC with live demo",
    "Runnable architecture PoC",
    "Live demos on simulated data",
    "not peer reviewed",
    "They are not a validated framework or completed benchmark.",
    "academic requirements completed; formal award pending",
    "Open to relocation within the EU"
  ];
  required.forEach((phrase) => assert.ok(html.includes(phrase), `missing required phrase: ${phrase}`));
});

test("About page excludes obsolete claims and stale metrics", () => {
  const prohibited = [
    /Solution Architect at Sistemi e Automazione/i,
    /AI\/MLOps &amp; LLMOps/i,
    /sub-200\s*ms/i,
    /30% processing/i,
    /zero unplanned downtime/i,
    /5\s*TB\+/i,
    /99\.9% uptime/i,
    /40% decision/i,
    /MTTR reductions?/i,
    /10\+ engineers/i,
    /CKA in progress/i,
    /published formal control framework/i,
    /production-grade RAG/i,
    /Luca Lillo · Chief Technology Officer/,
    /Currently,? I serve as Chief Technology Officer/i,
    /June 2026\s*[–-]\s*present/i,
    /German visa/i,
    /relocation across Germany/i,
    /AI (?:specialisation|focus) (?:is recent|began in 2025)/i,
    /specialisation in AI began in 2025/i,
    /Deployed reference PoC/i,
    /electricity grid automation/i,
    /trained 1,500/i,
    /led Grid Blue Sky/i,
    /signed releases?/i
  ];
  prohibited.forEach((pattern) => assert.doesNotMatch(html, pattern));
});

test("new-tab external links expose security and accessibility cues", () => {
  const links = matches(/<a\b[^>]*target="_blank"[^>]*>[\s\S]*?<\/a>/g).map((match) => match[0]);
  assert.ok(links.length > 0);
  links.forEach((link) => {
    assert.match(link, /rel="noopener noreferrer"/);
    assert.match(link, /opens in a new tab/);
  });
});
