import { NextResponse } from "next/server";
import { parseMessage, parseAnswer } from "../../../lib/chat";

export async function POST(request: Request) {
  const reply = (body: object, status: number) =>
    NextResponse.json(body, {
      status, headers: { "Cache-Control": "no-store" }
    });

  if (
    process.env.RAG_CHAT_ENABLED !== "true" ||
    !process.env.RAG_API_URL
  ) return reply({ error: "The assistant is not available yet." }, 503);

  if (request.headers.get("origin") !== new URL(request.url).origin) {
    return reply({ error: "Request not allowed." }, 403);
  }
  if (!request.headers.get("content-type")?.startsWith("application/json")) {
    return reply({ error: "Expected JSON." }, 415);
  }

  let payload: unknown;
  try {
    const reader = request.body?.getReader();
    if (!reader) return reply({ error: "A message is required." }, 400);
    const chunks: Uint8Array[] = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 10000) {
        await reader.cancel();
        return reply({ error: "Message is too large." }, 413);
      }
      chunks.push(value);
    }
    payload = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    return reply({ error: "Invalid request body." }, 400);
  }

  const message = parseMessage(payload);
  if (!message) {
    return reply({ error: "Enter a message of 1–2,000 characters." }, 400);
  }

  try {
    const url = new URL("/api/chat", process.env.RAG_API_URL);
    const local = process.env.NODE_ENV !== "production" &&
      url.hostname === "localhost" && url.protocol === "http:";
    if (url.protocol !== "https:" && !local) {
      throw new Error("Invalid backend URL");
    }
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(25000)
    });
    if (!response.ok) throw new Error("Backend unavailable");
    return reply(parseAnswer(await response.json()), 200);
  } catch {
    return reply({
      error: "The assistant is temporarily unavailable. Please try again later."
    }, 502);
  }
}
