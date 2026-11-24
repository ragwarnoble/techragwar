export type Phase = "ready" | "review" | "approved" | "authorized" | "executed" | "denied" | "failed";
export type Action = "evaluate" | "fail" | "approve" | "authorize" | "execute" | "deny" | "reset";
export type State = { phase: Phase; evidence: readonly string[] };
export const initialState: State = { phase: "ready", evidence: ["Synthetic workload registered."] };
const transitions: Partial<Record<Phase, Partial<Record<Action, [Phase, string]>>>> = {
  ready: { evaluate: ["review", "Synthetic evaluation and policy gate passed."], fail: ["failed", "Evaluation failed; execution blocked."] },
  review: { approve: ["approved", "Simulated human approval recorded."], deny: ["denied", "Human denial recorded; execution blocked."] },
  approved: { authorize: ["authorized", "Synthetic single-use authority issued for demo-001."] },
  authorized: { execute: ["executed", "Synthetic execution completed; authority consumed; simulated provenance recorded."] }
};
export function transition(state: State, action: Action): State {
  if (action === "reset") return initialState;
  const next = transitions[state.phase]?.[action];
  return next ? { phase: next[0], evidence: [...state.evidence, next[1]] } : state;
}
