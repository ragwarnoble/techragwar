export function parseMessage(input: unknown): string | null {
  if (!input || typeof input !== "object") return null;
  const message = (input as Record<string, unknown>).message;
  return typeof message === "string" &&
    message.trim().length > 0 && message.length <= 2000
    ? message.trim() : null;
}

export function parseAnswer(input: unknown) {
  if (!input || typeof input !== "object") {
    throw new Error("Invalid answer");
  }
  const data = input as Record<string, unknown>;
  if (
    typeof data.response !== "string" ||
    data.response.length > 50000 ||
    !Array.isArray(data.sources) ||
    data.sources.length > 100 ||
    !data.sources.every(s => typeof s === "string" && s.length <= 2000)
  ) throw new Error("Invalid answer");
  return { response: data.response, sources: data.sources as string[] };
}
