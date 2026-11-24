"use client";
import { useState, type FormEvent } from "react";

export function Assistant({ enabled }: { enabled: boolean }) {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setAnswer("");
    setSources([]);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
        signal: AbortSignal.timeout(30000)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Request failed.");
      setAnswer(data.response);
      setSources(data.sources);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "Request failed.");
    } finally {
      setBusy(false);
    }
  }

  return <aside className="assistant">
    <span className="eyebrow">EXPLORE OUR WORK</span>
    <h3>Ask the portfolio assistant.</h3>
    <p>Answers use the existing portfolio knowledge base.
      Please leave out personal and confidential information.</p>
    {enabled ? <form onSubmit={submit}>
      <label htmlFor="question">Your question</label>
      <textarea id="question" required maxLength={2000}
        value={message} onChange={e => setMessage(e.target.value)}
        placeholder="What experience do you have with RAG?" />
      <button disabled={busy || !message.trim()}>
        {busy ? "Finding an answer…" : "Ask a question ↗"}
      </button>
    </form> : <p>The assistant is being prepared.</p>}
    <div aria-live="polite" aria-busy={busy}>
      <p className="answer">{answer}</p>
      {sources.length > 0 && <>
        <h4>Sources</h4>
        <ul>{sources.map((s, i) => <li key={i}>{s}</li>)}</ul>
      </>}
    </div>
  </aside>;
}
