#!/usr/bin/env node
/* JSON 组装 / 抽取回退（无 jq 时由 run.sh 调用） */
const fs = require("fs");
const path = require("path");

function mimeFor(p) {
  const ext = path.extname(p).toLowerCase();
  const map = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
  };
  return map[ext] || "image/png";
}

function findB64(obj) {
  if (Array.isArray(obj)) {
    for (const x of obj) {
      const r = findB64(x);
      if (r) return r;
    }
    return null;
  }
  if (!obj || typeof obj !== "object") return null;
  if (obj.type === "image_generation_call") {
    for (const k of ["result", "image_base64", "b64_json"]) {
      if (typeof obj[k] === "string" && obj[k].length > 100) return obj[k];
    }
  }
  if (Array.isArray(obj.output)) {
    for (const item of obj.output) {
      if (item && item.type === "image_generation_call") {
        for (const k of ["result", "image_base64", "b64_json"]) {
          if (typeof item[k] === "string" && item[k].length > 100) return item[k];
        }
      }
      if (item && Array.isArray(item.content)) {
        for (const c of item.content) {
          for (const k of ["image_url", "b64_json", "image_base64", "result"]) {
            let v = c && c[k];
            if (typeof v === "string" && v.length > 100) {
              if (v.startsWith("data:") && v.includes(",")) v = v.split(",")[1];
              return v;
            }
          }
        }
      }
    }
  }
  if (Array.isArray(obj.data)) {
    for (const item of obj.data) {
      for (const k of ["b64_json", "result", "image_base64"]) {
        if (item && typeof item[k] === "string" && item[k].length > 100) return item[k];
      }
    }
  }
  return null;
}

function build(argv) {
  const get = (k) => {
    const i = argv.indexOf(k);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const model = get("--model");
  const prompt = get("--prompt");
  const out = get("--out");
  const image = get("--image");
  const mime = get("--mime") || (image ? mimeFor(image) : "image/png");
  let body;
  if (image) {
    const b64 = fs.readFileSync(image).toString("base64");
    body = {
      model,
      input: [
        {
          role: "user",
          content: [
            { type: "input_text", text: prompt },
            { type: "input_image", image_url: `data:${mime};base64,${b64}` },
          ],
        },
      ],
      tools: [{ type: "image_generation", action: "edit" }],
    };
  } else {
    body = {
      model,
      input: prompt,
      tools: [{ type: "image_generation", action: "generate" }],
    };
  }
  fs.writeFileSync(out, JSON.stringify(body));
}

function extract(argv) {
  const i = argv.indexOf("--json");
  const jp = argv[i + 1];
  const obj = JSON.parse(fs.readFileSync(jp, "utf8"));
  const b64 = findB64(obj);
  if (!b64) process.exit(2);
  process.stdout.write(String(b64).replace(/\s+/g, ""));
}

function has(argv) {
  const i = argv.indexOf("--json");
  const jp = argv[i + 1];
  const obj = JSON.parse(fs.readFileSync(jp, "utf8"));
  const b64 = findB64(obj);
  process.exit(typeof b64 === "string" && b64.length > 100 ? 0 : 1);
}

function meta(argv) {
  const ji = argv.indexOf("--json");
  const fi = argv.indexOf("--field");
  const obj = JSON.parse(fs.readFileSync(argv[ji + 1], "utf8"));
  const field = argv[fi + 1];
  const outs = Array.isArray(obj.output) ? obj.output : [];
  const ig = outs.find((x) => x && x.type === "image_generation_call") || {};
  let v = "";
  if (field === "tool_model") v = (obj.tools && obj.tools[0] && obj.tools[0].model) || "";
  else v = ig[field] || "";
  process.stdout.write(v == null ? "" : String(v));
}

const cmd = process.argv[2];
const rest = process.argv.slice(2);
if (cmd === "build") build(rest);
else if (cmd === "extract") extract(rest);
else if (cmd === "has") has(rest);
else if (cmd === "meta") meta(rest);
else {
  console.error("usage: json_codec.js build|extract|has|meta ...");
  process.exit(1);
}
