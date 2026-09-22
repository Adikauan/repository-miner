import { ApiError } from "../shared/api/client";

export type ReportLoadState = "loading" | "success" | "error" | "not_found" | "unavailable";

export function reportErrorState(error: unknown): ReportLoadState {
  const apiError = error as ApiError | undefined;
  if (apiError?.code === "execution_not_found" || apiError?.code === "not_found") return "not_found";
  if (apiError?.code === "report_unavailable") return "unavailable";
  return "error";
}

export function safeErrorMessage(error: unknown): string {
  const apiError = error as ApiError | undefined;
  const message = apiError?.message;
  if (!message || /token|secret|credential|api.?key/i.test(message)) return "Não foi possível carregar o relatório.";
  return message;
}
