// gta6-meme-x-01 entry: the post is the entry. This program copies POST.json
// (the X post's address, {"url": "https://x.com/<handle>/status/<id>"}) from
// the repository root to /output, where the gate reads it. Nothing else this
// program writes is judged: the house reads the post itself from X — its
// first picture and its text — and hands that to the AI judge.
//
// The meme this entry hands in is meme.png: "GTA VI IS 212 GB. IT ATE MY
// WHOLE CONSOLE." — a Vice City sunset with make.fun's ghost mascot floating
// over a storage bar that GTA VI has eaten. compose_meme.py rebuilds it from
// the background art and the press-kit ghost.
//
// Run it the way the grader does:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const src = join(BOT_DIR, "POST.json");
const dst = join(OUTPUT_DIR, "POST.json");

// Fail fast on a missing or malformed post file, so a bad entry is caught
// here instead of being graded invalid without explanation.
let raw: string;
try {
  raw = readFileSync(src, "utf8");
} catch (err) {
  console.error(
    `POST.json could not be read from ${src}: ${(err as Error).message}`,
  );
  process.exit(1);
}
let parsed: unknown;
try {
  parsed = JSON.parse(raw);
} catch (err) {
  console.error(`POST.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}
if (
  typeof parsed !== "object" ||
  parsed === null ||
  typeof (parsed as { url?: unknown }).url !== "string"
) {
  console.error('POST.json must be a JSON object with a string "url" field');
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
copyFileSync(src, dst);
