import { describe, expect, it } from "vitest";
import { beginStep, failStep, initialCreatePlanState } from "./createPlanState";
describe("createPlanState", () => { it("moves through busy and partial failure states", () => { const busy = beginStep(initialCreatePlanState, "creating_base"); expect(busy.busy).toBe(true); expect(failStep({ ...busy, configurationId: "synthetic-id" }, "saving_schedule", "safe").step).toBe("failed_partial"); }); });
