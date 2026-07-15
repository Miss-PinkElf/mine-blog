import { deepEqual, equal, rejects } from "node:assert/strict";
import { createTmuxDriver, quoteForShell } from "./tmux-driver.mjs";

equal(quoteForShell("a b"), "'a b'");
equal(quoteForShell("a'b"), "'a'\"'\"'b'");

const calls = [];
const driver = createTmuxDriver({
  execFile: async (file, args) => {
    calls.push([file, args]);
    return { stdout: "screen\n", stderr: "" };
  }
});

await driver.newSession({ sessionName: "devflow-worker-alpha", cwd: "/repo", command: "codex" });
await driver.setMouse({ sessionName: "devflow-worker-alpha" });
await driver.sendText({ sessionName: "devflow-worker-alpha", text: "hello", submit: true });
const screen = await driver.capturePane({ sessionName: "devflow-worker-alpha" });
const exists = await driver.hasSession({ sessionName: "devflow-worker-alpha" });

deepEqual(calls[0], ["tmux", ["new-session", "-d", "-s", "devflow-worker-alpha", "-c", "/repo", "codex"]]);
deepEqual(calls[1], ["tmux", ["set-option", "-t", "devflow-worker-alpha", "mouse", "on"]]);
deepEqual(calls[2], ["tmux", ["send-keys", "-t", "devflow-worker-alpha", "-l", "hello"]]);
deepEqual(calls[3], ["tmux", ["send-keys", "-t", "devflow-worker-alpha", "Enter"]]);
deepEqual(calls[4], ["tmux", ["capture-pane", "-p", "-t", "devflow-worker-alpha"]]);
deepEqual(calls[5], ["tmux", ["has-session", "-t", "devflow-worker-alpha"]]);
equal(screen, "screen\n");
equal(exists, true);

const missingDriver = createTmuxDriver({
  execFile: async () => {
    const error = new Error("session not found");
    error.code = 1;
    throw error;
  }
});

equal(await missingDriver.hasSession({ sessionName: "devflow-worker-missing" }), false);

const failingDriver = createTmuxDriver({
  execFile: async () => {
    const error = new Error("permission denied");
    error.code = 2;
    throw error;
  }
});

await rejects(
  failingDriver.hasSession({ sessionName: "devflow-worker-failing" }),
  /tmux 命令失败：permission denied/
);

console.log("tmux-driver tests passed");
