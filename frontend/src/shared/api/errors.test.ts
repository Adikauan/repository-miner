import { describe, expect, it } from "vitest";
import { sanitizeError } from "./errors";

describe("sanitizeError", () => {
  it.each(["token=abc", "credential secret", "ciphertext:xyz", "Authorization Bearer value"])("redacts %s", (message) => {
    expect(sanitizeError({ message }).message).not.toContain(message);
  });
  it("preserves safe actionable messages", () => {
    expect(sanitizeError({ code: "rate_limited", message: "Tente novamente mais tarde." })).toEqual({ code: "rate_limited", message: "Tente novamente mais tarde." });
  });
});
