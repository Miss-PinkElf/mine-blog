#!/usr/bin/env node
/* JSON 组装 / 抽取回退（无 jq 时由 run.sh 调用）
 *
 * 协议：OpenAI Chat Completions（POST /v1/chat/completions）
 * - 文生图：messages 纯文本
 * - 图生图：messages 多模态 text + image_url（data URL）
 * - 响应：choices[0].message.content 内 Markdown 图片 / data URL / 数组 image_url
 */
const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

const MD_IMAGE_RE = /!\[[^\]]*\]\(([^)]+)\)/;
const DATA_URL_RE = /^data:image\/[^;]+;base64,(.+)$/is;

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

function stripDataUrl(s) {
  const m = String(s).trim().match(DATA_URL_RE);
  if (m) return m[1].replace(/\s+/g, "");
  return String(s).replace(/\s+/g, "");
}

function fromContentString(content) {
  if (typeof content !== "string") return null;
  const text = content.trim();
  if (!text) return null;

  const m = text.match(MD_IMAGE_RE);
  if (m) {
    const target = m[1].trim();
    if (target.startsWith("http://") || target.startsWith("https://")) {
      return { kind: "url", value: target };
    }
    if (/^data:image\//i.test(target)) {
      return { kind: "b64", value: stripDataUrl(target) };
    }
    if (target.length > 100) {
      return { kind: "b64", value: target.replace(/\s+/g, "") };
    }
  }

  if (/^data:image\//i.test(text)) {
    return { kind: "b64", value: stripDataUrl(text) };
  }
  if (
    (text.startsWith("http://") || text.startsWith("https://")) &&
    !text.includes("\n") &&
    text.length < 4096
  ) {
    return { kind: "url", value: text };
  }
  return null;
}

function fromContentArray(content) {
  if (!Array.isArray(content)) return null;
  for (const part of content) {
    if (!part || typeof part !== "object") continue;
    const ptype = part.type;
    if (ptype === "image_url" || ptype === "output_image" || ptype === "image") {
      let url = null;
      if (part.image_url && typeof part.image_url === "object") url = part.image_url.url;
      else if (typeof part.image_url === "string") url = part.image_url;
      if (!url) url = part.url || part.image;
      if (typeof url === "string" && url.length > 8) {
        if (url.startsWith("http://") || url.startsWith("https://")) {
          return { kind: "url", value: url };
        }
        if (/^data:image\//i.test(url)) {
          return { kind: "b64", value: stripDataUrl(url) };
        }
        if (url.length > 100) {
          return { kind: "b64", value: url.replace(/\s+/g, "") };
        }
      }
    }
    if (ptype === "text" && typeof part.text === "string") {
      const got = fromContentString(part.text);
      if (got) return got;
    }
  }
  return null;
}

function findImageSource(obj) {
  if (!obj || typeof obj !== "object") return null;

  // 1) Chat Completions
  if (Array.isArray(obj.choices) && obj.choices[0]) {
    const msg = obj.choices[0].message;
    if (msg && typeof msg === "object") {
      const content = msg.content;
      if (typeof content === "string") {
        const got = fromContentString(content);
        if (got) return got;
      } else if (Array.isArray(content)) {
        const got = fromContentArray(content);
        if (got) return got;
      }
      for (const key of ["images", "image_url", "image"]) {
        const extra = msg[key];
        if (typeof extra === "string" && extra.length > 8) {
          if (extra.startsWith("http://") || extra.startsWith("https://")) {
            return { kind: "url", value: extra };
          }
          if (/^data:image\//i.test(extra)) {
            return { kind: "b64", value: stripDataUrl(extra) };
          }
        }
        if (Array.isArray(extra)) {
          const normalized = extra.map((x) =>
            typeof x === "string" || (x && typeof x === "object" && !x.type)
              ? { type: "image_url", image_url: x }
              : x
          );
          const got = fromContentArray(normalized);
          if (got) return got;
        }
      }
    }
  }

  // 2) Images API 兼容
  if (Array.isArray(obj.data)) {
    for (const item of obj.data) {
      if (!item || typeof item !== "object") continue;
      for (const k of ["b64_json", "result", "image_base64"]) {
        if (typeof item[k] === "string" && item[k].length > 100) {
          return { kind: "b64", value: item[k].replace(/\s+/g, "") };
        }
      }
      if (typeof item.url === "string" && item.url.startsWith("http")) {
        return { kind: "url", value: item.url };
      }
    }
  }

  // 3) 旧 Responses 兜底
  if (Array.isArray(obj.output)) {
    for (const item of obj.output) {
      if (!item || typeof item !== "object") continue;
      if (item.type === "image_generation_call") {
        for (const k of ["result", "image_base64", "b64_json"]) {
          if (typeof item[k] === "string" && item[k].length > 100) {
            return { kind: "b64", value: item[k].replace(/\s+/g, "") };
          }
        }
      }
      if (Array.isArray(item.content)) {
        const got = fromContentArray(item.content);
        if (got) return got;
      }
    }
  }

  return null;
}

function downloadToBuffer(url) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith("https") ? https : http;
    const req = lib.get(
      url,
      { headers: { "User-Agent": "gpt-image-generate/1.0" }, timeout: 120000 },
      (res) => {
        // 跟随一次重定向
        if (
          res.statusCode >= 300 &&
          res.statusCode < 400 &&
          res.headers.location
        ) {
          downloadToBuffer(res.headers.location).then(resolve, reject);
          res.resume();
          return;
        }
        if (res.statusCode < 200 || res.statusCode >= 300) {
          reject(new Error(`HTTP ${res.statusCode}`));
          res.resume();
          return;
        }
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => resolve(Buffer.concat(chunks)));
        res.on("error", reject);
      }
    );
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("download timeout"));
    });
  });
}

function collectImages(argv) {
  const images = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--image" || argv[i] === "-i") {
      const p = argv[i + 1];
      if (p) images.push(p);
    }
  }
  return images;
}

function build(argv) {
  const get = (k) => {
    const i = argv.indexOf(k);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const model = get("--model");
  const prompt = get("--prompt");
  const out = get("--out");
  const images = collectImages(argv);
  const mimeOverride = get("--mime");
  let body;
  if (images.length > 0) {
    const content = [{ type: "text", text: prompt }];
    for (let idx = 0; idx < images.length; idx++) {
      const image = images[idx];
      const mime =
        images.length === 1 && mimeOverride
          ? mimeOverride
          : mimeFor(image);
      const b64 = fs.readFileSync(image).toString("base64");
      content.push({
        type: "image_url",
        image_url: { url: `data:${mime};base64,${b64}` },
      });
    }
    body = {
      model,
      stream: false,
      messages: [{ role: "user", content }],
    };
  } else {
    body = {
      model,
      stream: false,
      messages: [{ role: "user", content: prompt }],
    };
  }
  fs.writeFileSync(out, JSON.stringify(body));
}

async function extract(argv) {
  const i = argv.indexOf("--json");
  const jp = argv[i + 1];
  const obj = JSON.parse(fs.readFileSync(jp, "utf8"));
  const src = findImageSource(obj);
  if (!src) process.exit(2);
  if (src.kind === "b64") {
    process.stdout.write(src.value);
    return;
  }
  if (src.kind === "url") {
    try {
      const buf = await downloadToBuffer(src.value);
      process.stdout.write(buf.toString("base64"));
    } catch (e) {
      console.error("下载图片失败:", e && e.message ? e.message : e);
      process.exit(3);
    }
    return;
  }
  process.exit(2);
}

function has(argv) {
  const i = argv.indexOf("--json");
  const jp = argv[i + 1];
  const obj = JSON.parse(fs.readFileSync(jp, "utf8"));
  const src = findImageSource(obj);
  if (!src) process.exit(1);
  if (src.kind === "url" && src.value.startsWith("http")) process.exit(0);
  // 1x1 PNG 的 base64 仅约 96 字符；阈值不宜过高
  if (src.kind === "b64" && src.value.length >= 32) process.exit(0);
  process.exit(1);
}

function meta(argv) {
  const ji = argv.indexOf("--json");
  const fi = argv.indexOf("--field");
  const obj = JSON.parse(fs.readFileSync(argv[ji + 1], "utf8"));
  const field = argv[fi + 1];
  let v = "";
  if (field === "tool_model") v = obj.model || "";
  else if (field === "revised_prompt" || field === "size" || field === "quality" || field === "output_format") {
    v = "";
  }
  if (!v && Array.isArray(obj.output)) {
    const ig = obj.output.find((x) => x && x.type === "image_generation_call") || {};
    if (field === "tool_model") {
      v = (obj.tools && obj.tools[0] && obj.tools[0].model) || obj.model || "";
    } else {
      v = ig[field] || "";
    }
  }
  process.stdout.write(v == null ? "" : String(v));
}

function kind(argv) {
  const i = argv.indexOf("--json");
  const jp = argv[i + 1];
  const obj = JSON.parse(fs.readFileSync(jp, "utf8"));
  const src = findImageSource(obj);
  if (!src) {
    process.stdout.write("empty");
    process.exit(1);
  }
  process.stdout.write(src.kind);
}

const cmd = process.argv[2];
const rest = process.argv.slice(2);
if (cmd === "build") build(rest);
else if (cmd === "extract") {
  extract(rest).catch((e) => {
    console.error(e);
    process.exit(1);
  });
} else if (cmd === "has") has(rest);
else if (cmd === "meta") meta(rest);
else if (cmd === "kind") kind(rest);
else {
  console.error("usage: json_codec.js build|extract|has|meta|kind ...");
  process.exit(1);
}
