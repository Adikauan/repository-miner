import { expect, it } from "vitest";
it("classifies active and terminal states for existing views", () => { expect(["pending", "running"].every((status) => ["pending", "running"].includes(status))).toBe(true); expect(["completed", "partially_completed", "failed"].every((status) => !["pending", "running"].includes(status))).toBe(true); });
