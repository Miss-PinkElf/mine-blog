import { ok } from "node:assert/strict";
import { buildITermScript, buildTerminalScript } from "./macos-terminal.mjs";

const terminalScript = buildTerminalScript({ attachCommand: "tmux attach -t devflow-worker-alpha" });
ok(terminalScript.includes("Terminal"));
ok(terminalScript.includes("tmux attach -t devflow-worker-alpha"));

const itermScript = buildITermScript({ attachCommand: "tmux attach -t devflow-worker-alpha" });
ok(itermScript.includes("iTerm2"));
ok(itermScript.includes("write text"));

console.log("macos-terminal tests passed");
