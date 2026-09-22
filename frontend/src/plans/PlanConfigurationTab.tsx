import type { VerificationPlanDetail } from "./types";
import { ConfigurationEditor } from "../configurations/ConfigurationEditor";
export function PlanConfigurationTab({ plan, onSaved, onRun }: { plan: VerificationPlanDetail; onSaved: () => void; onRun: (id: string) => void }) { return <ConfigurationEditor configuration={plan} onSaved={onSaved} onRun={onRun} />; }
