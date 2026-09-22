export const terminalStatuses = ["completed", "partially_completed", "failed"] as const;
export const allStatuses = ["pending", "running", ...terminalStatuses] as const;
