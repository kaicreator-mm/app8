"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { detectCase } = require("./detector.cjs");

function canonicalFileText(s) { return s.endsWith("\n") ? s.slice(0, -1) : s; }
function sha256(s) { return crypto.createHash("sha256").update(s, "utf8").digest("hex"); }
function readJson(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }

const repoRoot = path.resolve(__dirname, "../../..");
const config = readJson(path.join(__dirname, "config.json"));
const manifestPath = path.join(repoRoot, "research/e00/corpus/manifest.json");
const catalogPath = path.join(repoRoot, "research/e00/corpus/catalog.json");
const casesPath = path.join(repoRoot, "research/e00/corpus/cases.json");
const manifestText = fs.readFileSync(manifestPath, "utf8");
const catalogText = fs.readFileSync(catalogPath, "utf8");
const casesText = fs.readFileSync(casesPath, "utf8");

const observed = {
  case_manifest_sha256: sha256(canonicalFileText(manifestText)),
  catalog_sha256: sha256(canonicalFileText(catalogText)),
  cases_sha256: sha256(canonicalFileText(casesText))
};
for (const k of Object.keys(observed)) {
  if (observed[k] !== config.corpus[k]) throw new Error("corpus digest drift: " + k);
}

const catalog = JSON.parse(catalogText).catalog;
const cases = JSON.parse(casesText).cases;
const byRef = new Map(catalog.map(x => [x.fixture_ref, x]));
const predictions = cases.map(c => {
  const fixture = byRef.get(c.fixture_ref);
  if (!fixture) return { case_id: c.case_id, category: "unknown", prediction: "UNKNOWN", reason: "fixture_ref not found" };
  const source = fixture.profiles[c.profile];
  if (typeof source !== "string") return { case_id: c.case_id, category: fixture.category, prediction: "UNKNOWN", reason: "profile source not found" };
  const r = detectCase(fixture, source);
  return { case_id: c.case_id, category: fixture.category, prediction: r.prediction, reason: r.reason };
});
const core = { schema: "app8.e00.predictions.v1", predictions };
const canonical_output_sha256 = sha256(JSON.stringify(core));
const output = {
  schema: "app8.e00.blind-run.v1",
  base_commit: config.base_commit,
  protocol_blob: config.protocol_blob,
  corpus: config.corpus,
  opaque_commitments: config.opaque_commitments,
  detector_bundle_sha256: process.env.APP8_E00_BUNDLE_SHA256 || null,
  runtime_identity: process.version + " " + process.platform + "/" + process.arch,
  replay_command: "APP8_E00_BUNDLE_SHA256=<frozen-digest> node research/e00/detector/run.cjs",
  case_count: predictions.length,
  unknown_count: predictions.filter(x => x.prediction === "UNKNOWN").length,
  canonical_output_digest_rule: "sha256(JSON.stringify({schema:'app8.e00.predictions.v1',predictions}))",
  canonical_output_sha256,
  predictions
};
const out = path.join(repoRoot, "research/e00/runs/e00-blind-run.json");
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify(output, null, 2) + "\n", "utf8");
console.log(JSON.stringify({ out, case_count: output.case_count, unknown_count: output.unknown_count, canonical_output_sha256 }, null, 2));
