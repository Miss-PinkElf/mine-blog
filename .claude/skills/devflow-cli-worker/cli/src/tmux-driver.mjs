import { execFile as execFileCallback } from "node:child_process";
import { promisify } from "node:util";

const defaultExecFile = promisify(execFileCallback);

export function createTmuxDriver({ execFile = defaultExecFile } = {}) {
  async function run(args) {
    try {
      return await execFile("tmux", args, { encoding: "utf8" });
    } catch (error) {
      const message = error.code === "ENOENT"
        ? "未找到 tmux（tmux）。请先在 macOS 上安装 tmux，例如：brew install tmux。"
        : `tmux 命令失败：${error.message}`;
      throw new Error(message);
    }
  }

  return {
    async hasSession({ sessionName }) {
      try {
        await execFile("tmux", ["has-session", "-t", sessionName], { encoding: "utf8" });
        return true;
      } catch (error) {
        if (error.code === 1) {
          return false;
        }

        const message = error.code === "ENOENT"
          ? "未找到 tmux（tmux）。请先在 macOS 上安装 tmux，例如：brew install tmux。"
          : `tmux 命令失败：${error.message}`;
        throw new Error(message);
      }
    },

    async newSession({ sessionName, cwd, command }) {
      await run(["new-session", "-d", "-s", sessionName, "-c", cwd, command]);
    },

    async setMouse({ sessionName }) {
      await run(["set-option", "-t", sessionName, "mouse", "on"]);
    },

    async sendText({ sessionName, text, submit }) {
      await run(["send-keys", "-t", sessionName, "-l", text]);
      if (submit) {
        await new Promise((resolve) => setTimeout(resolve, 75));
        await run(["send-keys", "-t", sessionName, "Enter"]);
      }
    },

    async sendKey({ sessionName, key }) {
      await run(["send-keys", "-t", sessionName, key]);
    },

    async capturePane({ sessionName }) {
      const result = await run(["capture-pane", "-p", "-t", sessionName]);
      return result.stdout;
    },

    async killSession({ sessionName }) {
      await run(["kill-session", "-t", sessionName]);
    }
  };
}

export function quoteForShell(value) {
  return `'${String(value).replaceAll("'", "'\"'\"'")}'`;
}
