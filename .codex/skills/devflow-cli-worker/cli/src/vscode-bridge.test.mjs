import { deepEqual, equal, rejects } from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { requestVscodeAttach } from "./vscode-bridge.mjs";

const root = await mkdtemp(join(tmpdir(), "devflow-vscode-bridge-test-"));
const socketPath = join(root, "bridge.sock");
let request;
const server = createServer((socket) => {
  socket.on("data", (data) => {
    request = JSON.parse(data.toString("utf8").trim());
    socket.end(`${JSON.stringify({ ok: true, workerId: request.workerId, reused: false })}\n`);
  });
});

try {
  await new Promise((resolve) => server.listen(socketPath, resolve));
  const response = await requestVscodeAttach({ socketPath, workerId: "research-a", timeoutMs: 1000 });
  deepEqual(request, { action: "attach", workerId: "research-a" });
  deepEqual(response, { ok: true, workerId: "research-a", reused: false });

  await rejects(
    requestVscodeAttach({ socketPath: join(root, "missing.sock"), workerId: "research-a", timeoutMs: 100 }),
    /VSCode 插件未就绪/
  );

  console.log("vscode-bridge tests passed");
} finally {
  await new Promise((resolve) => server.close(resolve));
  await rm(root, { recursive: true, force: true });
}
