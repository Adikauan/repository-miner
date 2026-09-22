import { sanitizeError } from "./errors";

export type ApiError = { code: string; message: string; details?: Record<string, unknown> };

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  const operatorId = import.meta.env.VITE_OPERATOR_ID;
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(operatorId ? { "x-operator-id": operatorId } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw sanitizeError(payload.detail, "Não foi possível concluir a consulta.");
  }
  return response.json() as Promise<T>;
}
