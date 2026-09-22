import * as configurations from "../configurations/api";
import { listExecutions } from "../executions/api";
import type { PaginatedPlanPage, VerificationPlanDetail } from "./types";

export const planApi = {
  list: (params: { offset?: number; limit?: number } = {}) => configurations.listConfigurations(params) as Promise<PaginatedPlanPage>,
  get: (id: string) => configurations.getConfiguration(id) as Promise<VerificationPlanDetail>,
  createBase: configurations.createConfiguration,
  update: configurations.updateConfiguration,
  updateConnection: configurations.updateConnection,
  validateConnection: configurations.validateConnection,
  getTree: configurations.getGitLabTree,
  getBranches: configurations.getBranches,
  saveScope: configurations.saveScope,
  saveAllowedUsers: configurations.saveAllowedUsers,
  saveSchedule: configurations.saveSchedule,
  startExecution: configurations.startExecution,
  listExecutions,
};
