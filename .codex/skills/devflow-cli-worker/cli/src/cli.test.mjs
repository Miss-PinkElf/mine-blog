import { equal, ok, rejects } from "node:assert/strict";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runCli } from "./cli.mjs";

const root = await mkdtemp(join(tmpdir(), "devflow-cli-test-"));
const output = [];
const tmuxCalls = [];
let existingTmuxSession = false;
const bridgeCalls = [];
const fakeTmux = {
  newSession: async () => tmuxCalls.push("newSession"),
  setMouse: async () => tmuxCalls.push("setMouse"),
  sendText: async () => {},
  sendKey: async () => {},
  capturePane: async () => "worker screen\nContext 100% left",
  killSession: async () => {},
  hasSession: async () => existingTmuxSession
};
const fakeTerminal = { open: async () => {} };
const fakeBridge = {
  requestAttach: async ({ workerId }) => {
    bridgeCalls.push(workerId);
    return { ok: true, workerId, reused: false };
  }
};

try {
  await runCli(["--help"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal
  });

  ok(output.join("").includes("可用命令：start、start-in-vscode"));

  await runCli(["start", "--id", "alpha", "--command", "codex", "--prompt", "原始提示词"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal
  });

  ok(output.join("").includes(".devflow/devflow-cli-worker/sessions/alpha/result.md"));

  await runCli(["capture", "alpha"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal
  });

  const screen = await readFile(join(root, ".devflow/devflow-cli-worker/sessions/alpha/screen.txt"), "utf8");
  equal(screen, "worker screen\nContext 100% left");

  await runCli(["ensure-in-vscode", "--id", "reused", "--command", "codex"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal
  });

  ok(tmuxCalls.includes("newSession"));
  ok(output.join("").includes("worker reused started"));

  const reusedResultPath = join(root, ".devflow/devflow-cli-worker/sessions/reused/result.md");
  await writeFile(reusedResultPath, "existing result", "utf8");
  const newSessionCount = tmuxCalls.filter((call) => call === "newSession").length;
  existingTmuxSession = true;

  await runCli(["ensure-in-vscode", "--id", "reused", "--command", "codex"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal
  });

  equal(tmuxCalls.filter((call) => call === "newSession").length, newSessionCount);
  equal(await readFile(reusedResultPath, "utf8"), "existing result");
  ok(output.join("").includes("worker reused reused"));

  await runCli(["open-in-vscode", "--id", "reused"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal,
    bridge: fakeBridge
  });

  equal(bridgeCalls.at(-1), "reused");
  ok(output.join("").includes("worker reused opened in VSCode"));

  const mouseCallCount = tmuxCalls.filter((call) => call === "setMouse").length;
  await rejects(
    runCli(["ensure-in-vscode", "--id", "orphaned", "--command", "codex"], {
      cwd: root,
      stdout: { write: (text) => output.push(text) },
      stderr: { write: (text) => output.push(text) },
      tmux: fakeTmux,
      terminal: fakeTerminal
    }),
    /worker orphaned 的 tmux 会话存在，但 CLI 会话元数据不存在。请先运行 tmux kill-session -t devflow-worker-orphaned 清理孤立会话后重试。/
  );
  equal(tmuxCalls.filter((call) => call === "setMouse").length, mouseCallCount);

  const bridgeCallCount = bridgeCalls.length;
  await rejects(
    runCli(["open-in-vscode", "--id", "orphaned"], {
      cwd: root,
      stdout: { write: (text) => output.push(text) },
      stderr: { write: (text) => output.push(text) },
      tmux: fakeTmux,
      terminal: fakeTerminal,
      bridge: fakeBridge
    }),
    /worker orphaned 的 tmux 会话存在，但 CLI 会话元数据不存在。请先运行 tmux kill-session -t devflow-worker-orphaned 清理孤立会话后重试。/
  );
  equal(bridgeCalls.length, bridgeCallCount);

  const mismatchedSessionPath = join(root, ".devflow/devflow-cli-worker/sessions/mismatched");
  await mkdir(mismatchedSessionPath, { recursive: true });
  await writeFile(join(mismatchedSessionPath, "cli-session.json"), JSON.stringify({
    workerId: "another-worker",
    tmuxSessionName: "devflow-worker-another-worker",
    relativeSessionPath: ".devflow/devflow-cli-worker/sessions/mismatched",
    relativeResultPath: ".devflow/devflow-cli-worker/sessions/mismatched/result.md"
  }), "utf8");

  const mismatchedMouseCallCount = tmuxCalls.filter((call) => call === "setMouse").length;
  await rejects(
    runCli(["ensure-in-vscode", "--id", "mismatched", "--command", "codex"], {
      cwd: root,
      stdout: { write: (text) => output.push(text) },
      stderr: { write: (text) => output.push(text) },
      tmux: fakeTmux,
      terminal: fakeTerminal
    }),
    /worker mismatched 的 CLI 会话元数据与当前 tmux 会话不匹配/
  );
  equal(tmuxCalls.filter((call) => call === "setMouse").length, mismatchedMouseCallCount);

  const mismatchedBridgeCallCount = bridgeCalls.length;
  await rejects(
    runCli(["open-in-vscode", "--id", "mismatched"], {
      cwd: root,
      stdout: { write: (text) => output.push(text) },
      stderr: { write: (text) => output.push(text) },
      tmux: fakeTmux,
      terminal: fakeTerminal,
      bridge: fakeBridge
    }),
    /worker mismatched 的 CLI 会话元数据与当前 tmux 会话不匹配/
  );
  equal(bridgeCalls.length, mismatchedBridgeCallCount);

  existingTmuxSession = false;
  await rejects(
    runCli(["open-in-vscode", "--id", "missing"], {
      cwd: root,
      stdout: { write: (text) => output.push(text) },
      stderr: { write: (text) => output.push(text) },
      tmux: fakeTmux,
      terminal: fakeTerminal,
      bridge: fakeBridge
    }),
    /worker missing 未运行/
  );
  equal(bridgeCalls.includes("missing"), false);

  existingTmuxSession = true;
  await runCli(["start-and-open-in-vscode", "--id", "speed-smoke", "--command", "bash"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal,
    bridge: fakeBridge
  });
  equal(bridgeCalls.at(-1), "speed-smoke");

  await runCli(["clear", "alpha"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal,
    bridge: fakeBridge
  });
  ok(output.join("").includes("worker alpha conversation cleared"));

  await runCli(["command", "alpha", "/compact"], {
    cwd: root,
    stdout: { write: (text) => output.push(text) },
    stderr: { write: (text) => output.push(text) },
    tmux: fakeTmux,
    terminal: fakeTerminal,
    bridge: fakeBridge
  });

  await rejects(
    runCli(["command", "alpha", "not-a-slash-command"], {
      cwd: root,
      stdout: { write: (text) => output.push(text) },
      stderr: { write: (text) => output.push(text) },
      tmux: fakeTmux,
      terminal: fakeTerminal,
      bridge: fakeBridge
    }),
    /command 只接受/
  );

  console.log("cli tests passed");
} finally {
  await rm(root, { recursive: true, force: true });
}
