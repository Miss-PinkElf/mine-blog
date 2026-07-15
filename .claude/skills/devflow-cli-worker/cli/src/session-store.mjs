import { appendFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

const SESSION_ROOT = ".devflow/devflow-cli-worker/sessions";

export function createSessionStore({ repoRoot }) {
  const absoluteRepoRoot = resolve(repoRoot);

  function resolveSession(workerId) {
    const relativeSessionPath = `${SESSION_ROOT}/${workerId}`;
    const absoluteSessionPath = join(absoluteRepoRoot, relativeSessionPath);

    return {
      workerId,
      relativeSessionPath,
      absoluteSessionPath,
      relativeResultPath: `${relativeSessionPath}/result.md`,
      absoluteResultPath: join(absoluteSessionPath, "result.md"),
      absolutePromptPath: join(absoluteSessionPath, "prompt.md"),
      absoluteMetadataPath: join(absoluteSessionPath, "cli-session.json"),
      absoluteTranscriptPath: join(absoluteSessionPath, "transcript.log"),
      absoluteScreenPath: join(absoluteSessionPath, "screen.txt")
    };
  }

  async function createSession({ workerId, command, prompt, visualMode }) {
    validateWorkerId(workerId);
    const session = resolveSession(workerId);
    await mkdir(session.absoluteSessionPath, { recursive: true });
    await writeFile(session.absoluteResultPath, "", "utf8");
    await writeFile(session.absolutePromptPath, prompt, "utf8");

    const metadata = {
      workerId,
      command,
      visualMode,
      status: "created",
      tmuxSessionName: `devflow-worker-${workerId}`,
      relativeSessionPath: session.relativeSessionPath,
      relativeResultPath: session.relativeResultPath,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    await writeJson(session.absoluteMetadataPath, metadata);
    await writeFile(session.absoluteTranscriptPath, "", "utf8");
    await writeFile(session.absoluteScreenPath, "", "utf8");
    return { ...session, ...metadata };
  }

  async function readSession(workerId) {
    const session = resolveSession(workerId);
    const metadata = JSON.parse(await readFile(session.absoluteMetadataPath, "utf8"));
    assertSessionMetadataMatches(session, metadata);
    return { ...session, ...pickMetadata(metadata) };
  }

  async function updateSession(workerId, patch) {
    const session = await readSession(workerId);
    const next = { ...session, ...patch, updatedAt: new Date().toISOString() };
    await writeJson(session.absoluteMetadataPath, pickMetadata(next));
    return next;
  }

  async function appendTranscript(workerId, line) {
    const session = resolveSession(workerId);
    await mkdir(dirname(session.absoluteTranscriptPath), { recursive: true });
    await appendFile(session.absoluteTranscriptPath, `${new Date().toISOString()} ${line}\n`, "utf8");
  }

  return { resolveSession, createSession, readSession, updateSession, appendTranscript };
}

function assertSessionMetadataMatches(session, metadata) {
  const expectedTmuxSessionName = `devflow-worker-${session.workerId}`;
  if (
    metadata?.workerId !== session.workerId ||
    metadata?.tmuxSessionName !== expectedTmuxSessionName ||
    metadata?.relativeSessionPath !== session.relativeSessionPath ||
    metadata?.relativeResultPath !== session.relativeResultPath
  ) {
    throw new Error(
      `worker ${session.workerId} 的 CLI 会话元数据与当前 tmux 会话不匹配。请先检查或清理 ${expectedTmuxSessionName} 后重试。`
    );
  }
}

function validateWorkerId(workerId) {
  if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$/.test(workerId)) {
    throw new Error("worker id 只能包含字母、数字、点、下划线和短横线，且长度不超过 64。");
  }
}

async function writeJson(path, value) {
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function pickMetadata(session) {
  return {
    workerId: session.workerId,
    command: session.command,
    visualMode: session.visualMode,
    status: session.status,
    tmuxSessionName: session.tmuxSessionName,
    relativeSessionPath: session.relativeSessionPath,
    relativeResultPath: session.relativeResultPath,
    createdAt: session.createdAt,
    updatedAt: session.updatedAt
  };
}
