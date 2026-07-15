import { equal } from "node:assert/strict";
import { waitForStableScreen } from "./wait-agent.mjs";

const screens = ["a", "b", "b", "b"];
let index = 0;

const result = await waitForStableScreen({
  capture: async () => screens[Math.min(index++, screens.length - 1)],
  sleep: async () => {},
  now: (() => {
    let time = 0;
    return () => {
      time += 1000;
      return time;
    };
  })(),
  timeoutMs: 10000,
  pollMs: 1000,
  staleMs: 2000
});

equal(result.status, "stale");
equal(result.screen, "b");

console.log("wait-agent tests passed");
