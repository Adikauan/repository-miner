import { expect, it } from "vitest";
import { syntheticPlan } from "./fixtures";
it("keeps synthetic fixtures and URLs free of credentials", () => { const rendered = JSON.stringify(syntheticPlan); expect(rendered).not.toMatch(/gitlab_token|ciphertext|Bearer/i); expect(syntheticPlan.gitlab_base_url).not.toContain("@"); });
it("keeps paginated plan data free of credential fields", () => { const page = { items: [{ id: syntheticPlan.id, configuration_id: syntheticPlan.id, status: "completed", started_at: "2026-09-21T12:00:00Z" }], offset: 0, limit: 20 }; expect(JSON.stringify(page)).not.toMatch(/gitlab_token|ciphertext|Bearer/i); });
