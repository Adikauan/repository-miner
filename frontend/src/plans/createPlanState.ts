import type { CreatePlanDraft } from "./types";

export type CreationStep = "editing" | "creating_base" | "validating_connection" | "saving_basics" | "saving_scope" | "saving_users" | "saving_schedule" | "completed" | "failed" | "failed_partial";
export type CreatePlanState = { step: CreationStep; busy: boolean; configurationId?: string; failedStep?: CreationStep; error?: string };
export const initialCreatePlanState: CreatePlanState = { step: "editing", busy: false };

export function beginStep(state: CreatePlanState, step: CreationStep): CreatePlanState {
  if (state.busy) return state;
  return { ...state, step, busy: true, error: undefined };
}
export function failStep(state: CreatePlanState, failedStep: CreationStep, error: string): CreatePlanState {
  return { ...state, step: state.configurationId ? "failed_partial" : "failed", failedStep, busy: false, error };
}
export function invalidateConnection(draft: CreatePlanDraft, change: Partial<Pick<CreatePlanDraft, "gitlab_base_url" | "gitlab_token">>) {
  return { draft: { ...draft, ...change }, connectionValidated: false };
}
