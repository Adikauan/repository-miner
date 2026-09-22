import { expect, it } from "vitest";
import { sanitizeError } from "../../src/shared/api/errors";
it("does not expose a synthetic credential in errors", () => { const token = "synthetic-sensitive-value"; expect(JSON.stringify(sanitizeError({ message: `token=${token}` }))).not.toContain(token); });
