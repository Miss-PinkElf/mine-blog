import { equal, ok } from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createSessionStore } from "./session-store.mjs";

const root = await mkdtemp(join(tmpdir(), "devflow-worker-test-"));

try {
  const store = createSessionStore({ repoRoot: root });
  const session = await store.createSession({
    workerId: "alpha",
    command: "codex",
    prompt: "原始提示词",
    visualMode: "terminal"
  });

  equal(session.workerId, "alpha");
  equal(session.relativeResultPath, ".devflow/devflow-cli-worker/sessions/alpha/result.md");
  ok(session.absoluteResultPath.endsWith("result.md"));

  const result = await readFile(session.absoluteResultPath, "utf8");
  equal(result, "");

  const prompt = await readFile(session.absolutePromptPath, "utf8");
  equal(prompt, "原始提示词");

  const metadata = JSON.parse(await readFile(session.absoluteMetadataPath, "utf8"));
  equal(metadata.workerId, "alpha");
  equal(metadata.status, "created");

  console.log("session-store tests passed");
} finally {
  await rm(root, { recursive: true, force: true });
}
