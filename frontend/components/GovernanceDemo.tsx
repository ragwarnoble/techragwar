"use client";
import { useReducer } from "react";
import { initialState, transition, type Action } from "../lib/governance-demo";
import styles from "../app/demo/demo.module.css";

export function GovernanceDemo() {
  const [state, dispatch] = useReducer(transition, initialState);
  const controls: { action: Action; label: string; enabled: boolean }[] = [
    { action: "evaluate", label: "Pass evaluation", enabled: state.phase === "ready" },
    { action: "fail", label: "Fail evaluation", enabled: state.phase === "ready" },
    { action: "approve", label: "Approve", enabled: state.phase === "review" },
    { action: "deny", label: "Deny", enabled: state.phase === "review" },
    { action: "authorize", label: "Issue authorization", enabled: state.phase === "approved" },
    { action: "execute", label: "Execute simulation", enabled: state.phase === "authorized" },
    { action: "reset", label: "Reset", enabled: true }
  ];
  return <section className={styles.panel} aria-label="Governance simulation">
    <p>Workload: demo-001 · Synthetic repository update</p>
    <p role="status">State: {state.phase} · Authority: {state.phase === "authorized" ? "Scoped / single use" : state.phase === "executed" ? "Consumed" : "None"}</p>
    <div className={styles.controls}>{controls.map(({ action, label, enabled }) =>
      <button key={action} type="button" disabled={!enabled} onClick={() => dispatch(action)}>{label}</button>
    )}</div>
    <h2>Simulated evidence</h2>
    <ol aria-live="polite">{state.evidence.map((entry, index) => <li key={index}>{entry}</li>)}</ol>
  </section>;
}
