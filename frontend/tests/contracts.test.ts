import test from "node:test";
import assert from "node:assert/strict";
import { localContent, parseContent } from "../lib/content";
import { parseMessage, parseAnswer } from "../lib/chat";
import { POST } from "../app/api/chat/route";

test("CMS content validates required fields", () => {
  assert.deepEqual(parseContent(localContent), localContent);
  for (const input of [
    null, {}, { ...localContent, services: [] },
    { ...localContent, headline: "x".repeat(161) }
  ]) assert.throws(() => parseContent(input));
});

test("chat contracts reject malformed data", () => {
  assert.equal(parseMessage({ message: " hello " }), "hello");
  for (const input of [null, {}, { message: " " },
    { message: "x".repeat(2001) }]) {
    assert.equal(parseMessage(input), null);
  }
  assert.deepEqual(
    parseAnswer({ response: "Answer", sources: ["about.md"] }),
    { response: "Answer", sources: ["about.md"] }
  );
  assert.throws(() => parseAnswer({ response: "Answer", sources: [1] }));
});

test("disabled chat rejects requests", async () => {
  const previous = process.env.RAG_CHAT_ENABLED;
  try {
    process.env.RAG_CHAT_ENABLED = "false";
    const response = await POST(new Request(
      "https://ragwartech.com/api/chat", { method: "POST" }
    ));
    assert.equal(response.status, 503);
  } finally {
    if (previous === undefined) delete process.env.RAG_CHAT_ENABLED;
    else process.env.RAG_CHAT_ENABLED = previous;
  }
});
