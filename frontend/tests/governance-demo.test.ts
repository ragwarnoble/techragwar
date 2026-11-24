import { test } from "node:test";
import assert from "node:assert/strict";
import { initialState, transition, type Action } from "../lib/governance-demo";

test("execution requires evaluation, approval and authorization", () => {
  let state = initialState;
  for (const action of ["evaluate", "approve", "authorize"] as const) {
    assert.equal(transition(state, "execute"), state);
    state = transition(state, action);
  }
  const executed = transition(state, "execute");
  assert.equal(executed.phase, "executed");
  assert.equal(transition(executed, "execute"), executed);
  assert.match(executed.evidence.at(-1)!, /consumed/);
});
test("denial and failed evaluation are terminal until reset", () => {
  const blocked = [transition(initialState, "fail"), transition(transition(initialState, "evaluate"), "deny")];
  const actions: Action[] = ["evaluate", "fail", "approve", "deny", "authorize", "execute"];
  for (const state of blocked) {
    for (const action of actions) assert.equal(transition(state, action), state);
    assert.equal(transition(state, "reset"), initialState);
  }
});
test("approval and authorization cannot bypass the gate", () => {
  assert.equal(transition(initialState, "approve"), initialState);
  assert.equal(transition(initialState, "authorize"), initialState);
  const review = transition(initialState, "evaluate");
  assert.equal(transition(review, "authorize"), review);
});
