import { execFile as execFileCallback } from "node:child_process";
import { promisify } from "node:util";

const defaultExecFile = promisify(execFileCallback);

export function createMacOSTerminalOpener({ execFile = defaultExecFile } = {}) {
  return {
    async open({ terminalApp, attachCommand }) {
      const script = terminalApp === "iterm"
        ? buildITermScript({ attachCommand })
        : buildTerminalScript({ attachCommand });
      await execFile("osascript", ["-e", script], { encoding: "utf8" });
    }
  };
}

export function buildTerminalScript({ attachCommand }) {
  return [
    'tell application "Terminal"',
    "activate",
    `do script ${JSON.stringify(attachCommand)}`,
    "end tell"
  ].join("\n");
}

export function buildITermScript({ attachCommand }) {
  return [
    'tell application "iTerm2"',
    "activate",
    "create window with default profile",
    `tell current session of current window to write text ${JSON.stringify(attachCommand)}`,
    "end tell"
  ].join("\n");
}
