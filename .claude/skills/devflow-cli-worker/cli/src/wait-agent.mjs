export async function waitForStableScreen({
  capture,
  sleep = defaultSleep,
  now = Date.now,
  timeoutMs = 1200_000,
  pollMs = 15_000,
  staleMs = 30_000
}) {
  const startedAt = now();
  let lastScreen = await capture();
  let lastChangedAt = now();

  while (now() - startedAt < timeoutMs) {
    await sleep(pollMs);
    const screen = await capture();

    if (screen !== lastScreen) {
      lastScreen = screen;
      lastChangedAt = now();
      continue;
    }

    if (now() - lastChangedAt >= staleMs) {
      return { status: "stale", screen: lastScreen };
    }
  }

  return { status: "timeout", screen: lastScreen };
}

function defaultSleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
