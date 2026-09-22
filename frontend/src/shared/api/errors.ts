export type SafeApiError = { code: string; message: string };

const sensitivePattern = /(token|secret|credential|ciphertext|authorization|api[-_ ]?key)\s*[:=]?\s*\S*/i;

export function sanitizeError(error: unknown, fallback = "Não foi possível concluir a operação."): SafeApiError {
  const payload = error && typeof error === "object" ? error as Record<string, unknown> : {};
  const code = typeof payload.code === "string" ? payload.code : "request_failed";
  const raw = typeof payload.message === "string" ? payload.message : fallback;
  return { code, message: sensitivePattern.test(raw) ? fallback : raw };
}

export function safeErrorMessage(error: unknown, fallback?: string) {
  return sanitizeError(error, fallback).message;
}
