import { Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import { ExecutionDetailPage } from "../executions/ExecutionDetailPage";
import { getExecution } from "../executions/api";
import { useEffect, useState } from "react";
import { PlanDetailsPage } from "../plans/PlanDetailsPage";
import { PlanListPage } from "../plans/PlanListPage";
import { ReportDetailPage } from "../reporting/ReportDetailPage";

function PlanListRoute() { const navigate = useNavigate(); return <PlanListPage onOpen={(id) => navigate(`/plans/${id}/configuration`)} />; }
function PlanRoute({ tab }: { tab: "configuration" | "executions" }) { const { planId = "" } = useParams(); const navigate = useNavigate(); return <PlanDetailsPage planId={planId} tab={tab} onTab={(next) => navigate(`/plans/${planId}/${next}`)} onBack={() => navigate("/")} onExecution={(id, report) => navigate(`/plans/${planId}/executions/${id}/${report ? "report" : "live"}`)} />; }
function LiveRoute() { const { planId = "", executionId = "" } = useParams(); const navigate = useNavigate(); return <ExecutionDetailPage executionId={executionId} onBack={() => navigate(`/plans/${planId}/executions`)} onReport={(id) => navigate(`/plans/${planId}/executions/${id}/report`)} />; }
function ReportRoute() { const { planId = "", executionId = "" } = useParams(); const navigate = useNavigate(); return <ReportDetailPage executionId={executionId} onBack={() => navigate(`/plans/${planId}/executions`)} onMonitor={(id) => navigate(`/plans/${planId}/executions/${id}/live`)} />; }

export function AppRoutes() {
  return <Routes><Route path="/" element={<PlanListRoute />} /><Route path="/plans/:planId" element={<Navigate to="configuration" replace />} /><Route path="/plans/:planId/configuration" element={<PlanRoute tab="configuration" />} /><Route path="/plans/:planId/executions" element={<PlanRoute tab="executions" />} /><Route path="/plans/:planId/executions/:executionId/live" element={<LiveRoute />} /><Route path="/plans/:planId/executions/:executionId/report" element={<ReportRoute />} /><Route path="/configurations/:planId" element={<LegacyConfigurationRoute />} /><Route path="/configurations" element={<Navigate to="/" replace />} /><Route path="/executions" element={<Navigate to="/" replace />} /><Route path="/executions/:executionId" element={<LegacyExecutionRoute report={false} />} /><Route path="/reports/:executionId" element={<LegacyExecutionRoute report />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes>;
}
function LegacyConfigurationRoute() { const { planId = "" } = useParams(); return <Navigate to={`/plans/${planId}/configuration`} replace />; }
function LegacyExecutionRoute({ report }: { report: boolean }) { const { executionId = "" } = useParams(); const [target, setTarget] = useState<string>(); useEffect(() => { let active = true; void getExecution(executionId).then((execution) => { if (!active) return; const terminal = !["pending", "running"].includes(execution.status); setTarget(`/plans/${execution.configuration_id}/executions/${executionId}/${report || terminal ? "report" : "live"}`); }).catch(() => { if (active) setTarget("/"); }); return () => { active = false; }; }, [executionId, report]); return target ? <Navigate to={target} replace /> : null; }
