#!/usr/bin/env node
/**
 * gpt-image-generate Node 兜底入口（与 run.py CLI / RESULT 契约对齐）
 * 协议: POST {BASE_URL}/chat/completions
 */
import fs from "fs";
import path from "path";
import http from "http";
import https from "https";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SCRIPT_DIR = __dirname;
const ENV_FILE = path.join(SCRIPT_DIR, ".env");
const GEN_DIR = path.join(SCRIPT_DIR, "gen-images");
const DEFAULT_PROMPT_FILE = path.join(SCRIPT_DIR, "prompts", "prompt-image.md");
const CODEC = path.join(SCRIPT_DIR, "lib", "json_codec.cjs");

// 动态加载 cjs codec
import { createRequire } from "module";
const require = createRequire(import.meta.url);
// json_codec.cjs 是脚本风格，export 不足；这里内联关键解析逻辑 + 复用文件时通过 child 或 copy

const MD_IMAGE_RE = /!\[[^\]]*\]\(([^)]+)\)/;
const DATA_URL_RE = /^data:image\/[^;]+;base64,(.+)$/is;

function log(msg) {
  const ts = new Date().toTimeString().slice(0, 8);
  console.log(`[${ts}] ${msg}`);
}
function step(msg) {
  const ts = new Date().toTimeString().slice(0, 8);
  console.log(`\n==> [${ts}] ${msg}`);
}

function loadEnvFile(file) {
  if (!fs.existsSync(file)) return;
  log(`已加载配置: ${file}`);
  const text = fs.readFileSync(file, "utf8");
  for (const raw of text.split(/\r?\n/)) {
    let line = raw.trim();
    if (!line || line.startsWith("#") || !line.includes("=")) continue;
    const i = line.indexOf("=");
    const key = line.slice(0, i).trim();
    let value = line.slice(i + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (key && process.env[key] === undefined) process.env[key] = value;
  }
}

function elapsedText(startMs) {
  const total = Math.max(0, Math.floor((Date.now() - startMs) / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  if (m > 0) return `${m}m${String(s).padStart(2, "0")}s（共 ${total}s）`;
  return `${total}s`;
}

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

function usage() {
  console.log(`用法:
  node run.mjs [选项] [提示词...]

选项:
  -o, --output PATH
  -m, --model NAME
  --base-url URL
  -p, --prompt-file PATH
  -i, --image PATH          (可重复)
  --retries N
  --raw
  --no-open
  --prep off|light|medium|heavy
  --no-prep
  --jpeg-quality 1-100
  --target-bytes N
  --max-edge N              (默认 0=关闭)
  --max-images N
  -h, --help
`);
}

function parseArgs(argv) {
  const out = {
    promptParts: [],
    output: null,
    model: null,
    baseUrl: null,
    promptFile: null,
    images: [],
    retries: null,
    raw: false,
    noOpen: false,
    prep: null,
    noPrep: false,
    jpegQuality: null,
    targetBytes: null,
    maxEdge: null,
    maxImages: null,
    help: false,
  };
  let i = 0;
  while (i < argv.length) {
    const a = argv[i];
    const next = () => {
      const v = argv[i + 1];
      i += 2;
      return v;
    };
    if (a === "-h" || a === "--help") {
      out.help = true;
      i++;
    } else if (a === "-o" || a === "--output") out.output = next();
    else if (a === "-m" || a === "--model") out.model = next();
    else if (a === "--base-url") out.baseUrl = next();
    else if (a === "-p" || a === "--prompt-file") out.promptFile = next();
    else if (a === "-i" || a === "--image") out.images.push(next());
    else if (a === "--retries") out.retries = parseInt(next(), 10);
    else if (a === "--raw") {
      out.raw = true;
      i++;
    } else if (a === "--no-open") {
      out.noOpen = true;
      i++;
    } else if (a === "--prep") out.prep = next();
    else if (a === "--no-prep") {
      out.noPrep = true;
      i++;
    } else if (a === "--jpeg-quality") out.jpegQuality = parseInt(next(), 10);
    else if (a === "--target-bytes") out.targetBytes = parseInt(next(), 10);
    else if (a === "--max-edge") out.maxEdge = parseInt(next(), 10);
    else if (a === "--max-images") out.maxImages = parseInt(next(), 10);
    else if (a.startsWith("-")) {
      console.error(`未知参数: ${a}`);
      usage();
      process.exit(1);
    } else {
      out.promptParts.push(a);
      i++;
    }
  }
  return out;
}

function resolveImagePath(p) {
  if (fs.existsSync(p) && fs.statSync(p).isFile()) return path.resolve(p);
  const cand = path.join(SCRIPT_DIR, p);
  if (fs.existsSync(cand) && fs.statSync(cand).isFile()) return cand;
  console.error(`错误: 参考图不存在: ${p}`);
  process.exit(1);
}

/**
 * Node 端输入预处理：
 * - off: 原样
 * - 其他: 优先调用同目录 Python image_prep（有 Pillow 时质量对齐）；
 *   否则仅允许较小 jpeg 原样，大图报错提示装 pillow 或改用 run.py
 */
async function prepareImageNode(imgPath, opt) {
  const raw = fs.readFileSync(imgPath);
  const originalMime = mimeFor(imgPath);
  const meta = {
    path: imgPath,
    prep: opt.prep,
    original_bytes: raw.length,
    final_bytes: raw.length,
    original_wh: null,
    final_wh: null,
    scaled: false,
    jpeg_quality: null,
    mime: originalMime,
  };
  if (opt.prep === "off") {
    return { mime: originalMime, raw, meta };
  }

  // 尝试用 python 的 image_prep（与主路径算法一致）
  const pyCandidates = process.platform === "win32"
    ? ["py", "python", "python3"]
    : ["python3", "python"];
  for (const py of pyCandidates) {
    try {
      const result = await runPythonPrep(py, imgPath, opt);
      if (result) return result;
    } catch {
      /* try next */
    }
  }

  if (originalMime === "image/jpeg" && raw.length <= 2_000_000) {
    meta.note = "node_passthrough_jpeg_no_prep_engine";
    return { mime: originalMime, raw, meta };
  }
  throw new Error(
    "Node 兜底无法完成编码压缩（未找到可用 Python+Pillow）。" +
      "请安装 Pillow 并用 python run.py，或使用 --prep off 原样上传。"
  );
}

function runPythonPrep(pyBin, imgPath, opt) {
  return new Promise((resolve, reject) => {
    const code = `
import json, sys
sys.path.insert(0, r${JSON.stringify(path.join(SCRIPT_DIR, "lib"))})
from image_prep import PrepOptions, prepare_image
opt = PrepOptions(
    prep=${JSON.stringify(opt.prep)},
    jpeg_quality=${opt.jpegQuality == null ? "None" : opt.jpegQuality},
    target_bytes=${opt.targetBytes == null ? "None" : opt.targetBytes},
    max_edge=${opt.maxEdge || 0},
)
mime, raw, meta = prepare_image(r${JSON.stringify(imgPath)}, opt)
import base64
print(json.dumps({"mime": mime, "b64": base64.b64encode(raw).decode("ascii"), "meta": meta}, ensure_ascii=False))
`;
    const args = pyBin === "py" ? ["-3", "-c", code] : ["-c", code];
    const child = spawn(pyBin, args, { windowsHide: true });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d));
    child.stderr.on("data", (d) => (stderr += d));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `python exit ${code}`));
        return;
      }
      try {
        const obj = JSON.parse(stdout.trim());
        resolve({
          mime: obj.mime,
          raw: Buffer.from(obj.b64, "base64"),
          meta: obj.meta,
        });
      } catch (e) {
        reject(e);
      }
    });
  });
}

function buildBody(model, prompt, images) {
  // images: [{mime, raw: Buffer}]
  if (!images.length) {
    return {
      model,
      stream: false,
      messages: [{ role: "user", content: prompt }],
    };
  }
  const content = [{ type: "text", text: prompt }];
  for (const img of images) {
    content.push({
      type: "image_url",
      image_url: {
        url: `data:${img.mime};base64,${img.raw.toString("base64")}`,
      },
    });
  }
  return {
    model,
    stream: false,
    messages: [{ role: "user", content }],
  };
}

function httpPostJson(url, apiKey, body, maxTimeSec) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const lib = u.protocol === "https:" ? https : http;
    const data = Buffer.from(JSON.stringify(body), "utf8");
    const req = lib.request(
      {
        protocol: u.protocol,
        hostname: u.hostname,
        port: u.port || (u.protocol === "https:" ? 443 : 80),
        path: u.pathname + u.search,
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
          "Content-Length": data.length,
          "User-Agent": "gpt-image-generate/2.0-node",
        },
        timeout: Math.max(1000, maxTimeSec * 1000),
      },
      (res) => {
        const chunks = [];
        res.on("data", (c) => chunks.push(c));
        res.on("end", () => {
          resolve({ status: res.statusCode || 0, raw: Buffer.concat(chunks) });
        });
      }
    );
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("request timeout"));
    });
    req.write(data);
    req.end();
  });
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
    if (target.startsWith("http://") || target.startsWith("https://"))
      return { kind: "url", value: target };
    if (/^data:image\//i.test(target))
      return { kind: "b64", value: stripDataUrl(target) };
    if (target.length > 100)
      return { kind: "b64", value: target.replace(/\s+/g, "") };
  }
  if (/^data:image\//i.test(text))
    return { kind: "b64", value: stripDataUrl(text) };
  if (
    (text.startsWith("http://") || text.startsWith("https://")) &&
    !text.includes("\n") &&
    text.length < 4096
  )
    return { kind: "url", value: text };
  return null;
}

function fromContentArray(content) {
  if (!Array.isArray(content)) return null;
  for (const part of content) {
    if (!part || typeof part !== "object") continue;
    const ptype = part.type;
    if (ptype === "image_url" || ptype === "output_image" || ptype === "image") {
      let url = null;
      if (part.image_url && typeof part.image_url === "object")
        url = part.image_url.url;
      else if (typeof part.image_url === "string") url = part.image_url;
      if (!url) url = part.url || part.image;
      if (typeof url === "string" && url.length > 8) {
        if (url.startsWith("http://") || url.startsWith("https://"))
          return { kind: "url", value: url };
        if (/^data:image\//i.test(url))
          return { kind: "b64", value: stripDataUrl(url) };
        if (url.length > 100)
          return { kind: "b64", value: url.replace(/\s+/g, "") };
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
    }
  }
  if (Array.isArray(obj.data)) {
    for (const item of obj.data) {
      if (!item || typeof item !== "object") continue;
      for (const k of ["b64_json", "result", "image_base64"]) {
        if (typeof item[k] === "string" && item[k].length > 100)
          return { kind: "b64", value: item[k].replace(/\s+/g, "") };
      }
      if (typeof item.url === "string" && item.url.startsWith("http"))
        return { kind: "url", value: item.url };
    }
  }
  return null;
}

function downloadToBuffer(url, timeoutSec) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith("https") ? https : http;
    const req = lib.get(
      url,
      { headers: { "User-Agent": "gpt-image-generate/2.0-node" }, timeout: timeoutSec * 1000 },
      (res) => {
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          downloadToBuffer(res.headers.location, timeoutSec).then(resolve, reject);
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

async function saveImage(obj, outPath, timeoutSec) {
  const src = findImageSource(obj);
  if (!src) throw new Error("响应成功但未解析到图片");
  let buf;
  if (src.kind === "url") {
    log("响应为图片 URL，开始下载...");
    buf = await downloadToBuffer(src.value, timeoutSec);
  } else {
    buf = Buffer.from(src.value, "base64");
  }
  if (!buf || !buf.length) throw new Error("解码后图片为空");
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const tmp = `${outPath}.tmp.${process.pid}`;
  fs.writeFileSync(tmp, buf);
  fs.renameSync(tmp, outPath);
}

function buildDefaultOutput() {
  fs.mkdirSync(GEN_DIR, { recursive: true });
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const stamp = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}-${pad(d.getHours())}-${pad(d.getMinutes())}-${pad(d.getSeconds())}`;
  let p = path.join(GEN_DIR, `${stamp}.png`);
  if (fs.existsSync(p))
    p = path.join(GEN_DIR, `${stamp}-${Math.floor(Math.random() * 10000)}.png`);
  return p;
}

function openImage(p) {
  try {
    if (process.platform === "win32") {
      spawn("cmd", ["/c", "start", "", p], { detached: true, stdio: "ignore" });
    } else if (process.platform === "darwin") {
      spawn("open", [p], { detached: true, stdio: "ignore" });
    } else {
      spawn("xdg-open", [p], { detached: true, stdio: "ignore" });
    }
  } catch (e) {
    log(`自动打开图片失败: ${e.message || e}`);
  }
}

async function main() {
  const start = Date.now();
  loadEnvFile(ENV_FILE);
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    return 0;
  }

  const baseUrl = (
    args.baseUrl ||
    process.env.OPENAI_BASE_URL ||
    "https://shell.wyzlab.ai/v1"
  ).replace(/\/$/, "");
  const model = args.model || process.env.OPENAI_MODEL || "gpt-image-2";
  const apiKey = process.env.OPENAI_API_KEY || "";
  const maxTime = parseFloat(
    process.env.CURL_MAX_TIME || process.env.REQUEST_MAX_TIME || "180"
  );
  const maxRetries =
    args.retries != null
      ? args.retries
      : parseInt(process.env.GPT_IMAGE_RETRIES || "5", 10);
  const maxImages =
    args.maxImages != null
      ? args.maxImages
      : parseInt(process.env.GPT_IMAGE_MAX_IMAGES || "4", 10);

  let prep = args.noPrep
    ? "off"
    : args.prep || process.env.GPT_IMAGE_PREP || "medium";
  let jpegQuality = args.jpegQuality;
  if (jpegQuality == null && process.env.GPT_IMAGE_JPEG_QUALITY)
    jpegQuality = parseInt(process.env.GPT_IMAGE_JPEG_QUALITY, 10);
  let targetBytes = args.targetBytes;
  if (targetBytes == null && process.env.GPT_IMAGE_TARGET_BYTES)
    targetBytes = parseInt(process.env.GPT_IMAGE_TARGET_BYTES, 10);
  let maxEdge =
    args.maxEdge != null
      ? args.maxEdge
      : parseInt(process.env.GPT_IMAGE_MAX_EDGE || "0", 10);

  if (!apiKey || apiKey === "你的key填这里" || apiKey === "sk-xxxx") {
    console.error("错误: 未配置有效的 OPENAI_API_KEY");
    console.error(`请编辑 skill 同级 .env: ${ENV_FILE}`);
    return 1;
  }

  let prompt;
  if (args.promptParts.length) {
    prompt = args.promptParts.join(" ").trim();
    if (!prompt) {
      console.error("错误: 命令行提示词为空");
      return 1;
    }
    log("提示词来源: 命令行参数");
  } else {
    let pf = args.promptFile
      ? path.isAbsolute(args.promptFile)
        ? args.promptFile
        : fs.existsSync(args.promptFile)
          ? args.promptFile
          : path.join(SCRIPT_DIR, args.promptFile)
      : DEFAULT_PROMPT_FILE;
    if (!fs.existsSync(pf)) {
      console.error(`错误: 提示词文件不存在: ${pf}`);
      return 1;
    }
    prompt = fs.readFileSync(pf, "utf8").trim();
    if (!prompt) {
      console.error(`错误: 提示词文件为空: ${pf}`);
      return 1;
    }
    log(`提示词来源: ${pf}`);
  }

  if (args.images.length > maxImages) {
    console.error(
      `错误: 参考图数量 ${args.images.length} 超过上限 ${maxImages}`
    );
    return 1;
  }

  const prepOpt = {
    prep,
    jpegQuality,
    targetBytes,
    maxEdge: maxEdge || 0,
  };

  const prepared = [];
  let inputBefore = 0;
  let inputAfter = 0;
  const sourceList = [];
  let mode = "text";
  let usedQ = null;

  if (args.images.length) {
    step("预处理参考图（仅输入，不影响输出尺寸）");
    log(
      `prep=${prep} jpeg_quality=${jpegQuality} target_bytes=${targetBytes} max_edge=${maxEdge}`
    );
    for (const ip of args.images) {
      const resolved = resolveImagePath(ip);
      try {
        const { mime, raw, meta } = await prepareImageNode(resolved, prepOpt);
        prepared.push({ mime, raw });
        inputBefore += meta.original_bytes || 0;
        inputAfter += meta.final_bytes || 0;
        sourceList.push(resolved);
        if (meta.jpeg_quality != null) usedQ = meta.jpeg_quality;
        log(
          `  ${path.basename(resolved)}: ${meta.original_bytes}B → ${meta.final_bytes}B scaled=${meta.scaled} q=${meta.jpeg_quality} mime=${mime}`
        );
      } catch (e) {
        console.error(`错误: 预处理失败 (${resolved}): ${e.message || e}`);
        return 1;
      }
    }
    mode = "image_edit";
  }

  step("1/4 准备输出目录");
  fs.mkdirSync(GEN_DIR, { recursive: true });
  const output = args.output
    ? path.resolve(args.output)
    : buildDefaultOutput();
  fs.mkdirSync(path.dirname(output), { recursive: true });
  log(`目标图片: ${output}`);
  log(`主模型:   ${model}`);
  log(`Base URL: ${baseUrl}`);
  log(`模式:     ${mode}`);

  step("2/4 组装 Chat Completions 请求");
  const body = buildBody(model, prompt, prepared);
  const bodyBytes = Buffer.byteLength(JSON.stringify(body), "utf8");
  log(
    `请求体已就绪（mode=${mode} / bytes=${bodyBytes} / runtime=node / protocol=chat）`
  );

  const endpoint = `${baseUrl}/chat/completions`;
  const totalAttempts = maxRetries + 1;
  step(`3/4 调用接口（最多 ${totalAttempts} 次尝试）`);
  log(`POST ${endpoint}`);

  let lastError = "";
  let lastRaw = Buffer.alloc(0);
  let success = false;

  for (let attempt = 1; attempt <= totalAttempts; attempt++) {
    log(`---------- 第 ${attempt}/${totalAttempts} 次尝试 ----------`);
    const t0 = Date.now();
    let status, raw;
    try {
      ({ status, raw } = await httpPostJson(endpoint, apiKey, body, maxTime));
    } catch (e) {
      lastError = String(e.message || e);
      log(`❌ ${lastError}`);
      if (attempt < totalAttempts) {
        const sleepS = Math.min(30, attempt * 5);
        log(`将在 ${sleepS}s 后重试...`);
        await new Promise((r) => setTimeout(r, sleepS * 1000));
      }
      continue;
    }
    lastRaw = raw;
    log(
      `本次耗时: ${Math.floor((Date.now() - t0) / 1000)}s | 累计: ${elapsedText(start)}`
    );

    if (status === 401) {
      lastError = `HTTP ${status}（认证失败，不重试）`;
      log(`❌ ${lastError}`);
      console.error(raw.toString("utf8").slice(0, 800));
      break;
    }
    if (status < 200 || status >= 300) {
      lastError = `HTTP ${status}`;
      log(`❌ 请求失败：${lastError}`);
      console.error(raw.toString("utf8").slice(0, 800));
      if (attempt < totalAttempts) {
        const sleepS = Math.min(30, attempt * 5);
        await new Promise((r) => setTimeout(r, sleepS * 1000));
      }
      continue;
    }

    log(`HTTP 状态码: ${status}（成功）`);
    let obj;
    try {
      obj = JSON.parse(raw.toString("utf8"));
    } catch {
      lastError = "响应不是合法 JSON";
      log(`❌ ${lastError}`);
      if (attempt < totalAttempts)
        await new Promise((r) => setTimeout(r, Math.min(30, attempt * 5) * 1000));
      continue;
    }

    if (args.raw) {
      console.log(JSON.stringify(obj, null, 2));
      return 0;
    }

    step("4/4 解析并保存图片");
    try {
      await saveImage(obj, output, maxTime);
    } catch (e) {
      lastError = `保存图片失败: ${e.message || e}`;
      log(`❌ ${lastError}`);
      if (attempt < totalAttempts)
        await new Promise((r) => setTimeout(r, Math.min(30, attempt * 5) * 1000));
      continue;
    }
    if (!fs.existsSync(output) || fs.statSync(output).size <= 0) {
      lastError = "输出文件为空";
      log(`❌ ${lastError}`);
      if (attempt < totalAttempts)
        await new Promise((r) => setTimeout(r, Math.min(30, attempt * 5) * 1000));
      continue;
    }
    success = true;
    log(`✅ 第 ${attempt}/${totalAttempts} 次尝试成功`);
    break;
  }

  if (!success) {
    const failPath = path.join(
      GEN_DIR,
      `failed-${new Date().toISOString().replace(/[:.]/g, "-")}.json`
    );
    try {
      if (lastRaw.length) fs.writeFileSync(failPath, lastRaw);
      console.error(`最后一次响应已保存: ${failPath}`);
    } catch {
      /* ignore */
    }
    console.error(
      `错误: 已尝试 ${totalAttempts} 次仍失败\n最后错误: ${lastError || "unknown"}\n已用时: ${elapsedText(start)}`
    );
    return 1;
  }

  const fileSize = fs.statSync(output).size;
  const elapsedSec = Math.max(0, Math.floor((Date.now() - start) / 1000));
  let outputRel = output;
  if (output.startsWith(SCRIPT_DIR))
    outputRel = path.relative(SCRIPT_DIR, output);

  log(`图片已保存: ${output}`);
  log(`文件大小:   ${fileSize} bytes`);
  log(`总耗时:     ${elapsedText(start)}`);

  if (!args.noOpen) {
    log("正在打开图片...");
    openImage(output);
  }

  console.log(`\n✅ 完成：${output}`);
  console.log(`⏱  总耗时：${elapsedText(start)}`);
  console.log(`📦 文件大小：${fileSize} bytes`);

  console.log("\n---RESULT---");
  console.log("status=ok");
  console.log(`path=${output}`);
  console.log(`path_rel=${outputRel}`);
  console.log(`bytes=${fileSize}`);
  console.log(`elapsed_seconds=${elapsedSec}`);
  console.log(`elapsed_text=${elapsedText(start)}`);
  console.log(`model=${model}`);
  console.log(`mode=${mode}`);
  console.log("json_backend=node");
  console.log("runtime=node");
  console.log(`source_images_count=${sourceList.length}`);
  if (sourceList.length) console.log(`source_image=${sourceList.join("|")}`);
  console.log(`request_body_bytes=${bodyBytes}`);
  console.log(`image_prep=${prep}`);
  if (jpegQuality != null) console.log(`jpeg_quality=${jpegQuality}`);
  else if (usedQ != null) console.log(`jpeg_quality=${usedQ}`);
  if (targetBytes != null) console.log(`target_bytes=${targetBytes}`);
  console.log(`max_edge=${maxEdge || 0}`);
  console.log(`input_bytes_before=${inputBefore}`);
  console.log(`input_bytes_after=${inputAfter}`);
  console.log(`skill_dir=${SCRIPT_DIR}`);
  console.log("---END_RESULT---");
  return 0;
}

main()
  .then((code) => process.exit(code || 0))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
