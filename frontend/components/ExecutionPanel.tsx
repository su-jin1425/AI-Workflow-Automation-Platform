"use client";

import { useEffect } from "react";

import { useWorkflowStore } from "@/store/workflow-store";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export function ExecutionPanel() {
  const { execution, setExecution } = useWorkflowStore();

  useEffect(() => {
    if (!execution) {
      return;
    }
    const socket = new WebSocket(`${WS_URL}/ws/executions/${execution.id}`);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setExecution({
        ...execution,
        execution_status: payload.status,
        execution_logs: payload.logs,
        output_payload: payload.output
      });
    };
    return () => socket.close();
  }, [execution?.id]);

  return (
    <section className="p-4">
      <h2 className="mb-3 text-sm font-semibold">Execution</h2>
      {execution ? (
        <div>
          <div className="mb-3 rounded-md border border-line bg-panel p-3 text-sm">
            <div className="text-xs text-slate-500">Status</div>
            <div className="font-semibold">{execution.execution_status}</div>
          </div>
          <div className="max-h-[520px] overflow-auto rounded-md border border-line bg-slate-950 p-3 text-xs leading-5 text-slate-50">
            {execution.execution_logs.length ? (
              execution.execution_logs.map((log, index) => (
                <div key={`${log.time}-${index}`}>
                  <span className="text-slate-400">{log.time}</span> {log.message}
                </div>
              ))
            ) : (
              <div>Waiting for execution logs</div>
            )}
          </div>
        </div>
      ) : (
        <div className="rounded-md border border-line bg-panel p-3 text-sm text-slate-600">No execution has started.</div>
      )}
    </section>
  );
}
