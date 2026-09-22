import { safeErrorMessage } from "../shared/api/errors";
import { planApi } from "./api";
import type { CreatePlanDraft } from "./types";
import type { CreatePlanState, CreationStep } from "./createPlanState";

type ResumeContext = { configurationId?: string; connectionValidated?: boolean };

export async function createPlan(draft: CreatePlanDraft, notify: (state: CreatePlanState) => void, resume: ResumeContext = {}) {
  let configurationId = resume.configurationId;
  let step: CreationStep = configurationId ? "saving_basics" : "creating_base";
  const update = () => notify({ step, busy: true, configurationId });
  try {
    if (!configurationId) {
      update();
      const base = await planApi.createBase({ name: draft.name.trim(), gitlab_base_url: draft.gitlab_base_url, gitlab_token: draft.gitlab_token, timezone: draft.timezone, enabled: draft.enabled });
      configurationId = base.id;
      draft.gitlab_token = "";
    } else {
      update();
      await planApi.update(configurationId, { name: draft.name.trim(), timezone: draft.timezone, enabled: draft.enabled });
    }
    if (!resume.connectionValidated) { step = "validating_connection"; update(); await planApi.validateConnection(configurationId); }
    step = "saving_scope"; update(); await planApi.saveScope(configurationId, draft.target_branch, draft.selections);
    step = "saving_users"; update(); await planApi.saveAllowedUsers(configurationId, draft.allowed_emails);
    step = "saving_schedule"; update(); await planApi.saveSchedule(configurationId, draft.schedule);
    const result: CreatePlanState = { step: "completed", busy: false, configurationId };
    notify(result); return result;
  } catch (error) {
    const result: CreatePlanState = { step: configurationId ? "failed_partial" : "failed", busy: false, configurationId, failedStep: step, error: safeErrorMessage(error) };
    notify(result); return result;
  }
}
