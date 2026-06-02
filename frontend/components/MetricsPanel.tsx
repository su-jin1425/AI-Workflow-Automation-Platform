"use client";

import { useWorkflowStore } from "@/store/workflow-store";

export function MetricsPanel() {
  const overview = useWorkflowStore((state) => state.overview);
  const metrics = [
    ["Workflows", overview.workflows],
    ["Executions", overview.executions],
    ["Completed", overview.completed],
    ["Failed", overview.failed]
  ];

  return (
    <div className="grid grid-cols-2 gap-2">
      {metrics.map(([label, value]) => (
        <div key={label} className="rounded-md border border-line bg-panel p-3">
          <div className="text-xs text-slate-500">{label}</div>
          <div className="mt-1 text-xl font-semibold">{value}</div>
        </div>
      ))}
    </div>
  );
}
