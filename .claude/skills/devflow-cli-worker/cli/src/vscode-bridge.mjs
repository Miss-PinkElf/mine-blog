import { createConnection } from "node:net";

export function requestVscodeAttach({ socketPath, workerId, timeoutMs = 5000 }) {
  return new Promise((resolve, reject) => {
    let settled = false;
    let responseBuffer = "";
    const socket = createConnection(socketPath);
    const timeout = setTimeout(() => finish(new Error("VSCode 插件响应超时，请确认插件已加载。")), timeoutMs);

    socket.setEncoding("utf8");
    socket.on("connect", () => {
      socket.write(`${JSON.stringify({ action: "attach", workerId })}\n`);
    });
    socket.on("data", (chunk) => {
      responseBuffer += chunk;
      const lineEnd = responseBuffer.indexOf("\n");
      if (lineEnd < 0) {
        return;
      }

      try {
        const response = JSON.parse(responseBuffer.slice(0, lineEnd));
        if (!response.ok) {
          finish(new Error(response.error ?? "VSCode 插件拒绝 attach 请求。"));
          return;
        }
        finish(null, response);
      } catch {
        finish(new Error("VSCode 插件返回了无效响应。"));
      }
    });
    socket.on("error", (error) => {
      if (error.code === "ENOENT" || error.code === "ECONNREFUSED") {
        finish(new Error("VSCode 插件未就绪，请打开当前工作区并等待插件激活。"));
        return;
      }
      finish(new Error(`连接 VSCode 插件失败：${error.message}`));
    });
    socket.on("end", () => {
      if (!settled) {
        finish(new Error("VSCode 插件未返回 attach 响应。"));
      }
    });

    function finish(error, response) {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timeout);
      socket.destroy();
      if (error) {
        reject(error);
        return;
      }
      resolve(response);
    }
  });
}
