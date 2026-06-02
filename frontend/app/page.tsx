"use client";

import { Activity, BarChart3, GitBranch, LogOut, Play, Save } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AuthPanel } from "@/components/AuthPanel";
import { ExecutionPanel } from "@/components/ExecutionPanel";
import { MetricsPanel } from "@/components/MetricsPanel";
import { WorkflowBuilder } from "@/components/WorkflowBuilder";
import { apiClient } from "@/services/api";
import { useAuthStore } from "@/store/auth-store";
import { useWorkflowStore } from "@/store/workflow-store";

export default function Home() {
  const { token, user, logout } = useAuthStore();
  const {
    workflowId,
    workflowName,
    buildDefinition,
    setWorkflowId,
    setWorkflowName,
    setExecution,
    setExecutions,
    setOverview
  } = useWorkflowStore();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Ready");

  const canOperate = useMemo(() => Boolean(token), [token]);

  useEffect(() => {
    if (!token) {
      return;
    }
    Promise.all([apiClient.overview(token), apiClient.executions(token)])
      .then(([overview, executions]) => {
        setOverview(overview);
        setExecutions(executions);
      })
      .catch(() => setMessage("Could not load dashboard data"));
  }, [token, setExecutions, setOverview]);

  async function saveWorkflow() {
    if (!token) {
      return;
    }
    setBusy(true);
    setMessage("Saving workflow");
    try {
      const payload = {
        workflow_name: workflowName,
        workflow_definition: buildDefinition(),
        status: "active" as const
      };
      const workflow = workflowId
        ? await apiClient.updateWorkflow(token, workflowId, payload)
        : await apiClient.createWorkflow(token, payload);
      setWorkflowId(workflow.id);
      setMessage("Workflow saved");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Workflow save failed");
    } finally {
      setBusy(false);
    }
  }

  async function runWorkflow() {
    if (!token || !workflowId) {
      setMessage("Save the workflow before running it");
      return;
    }
    setBusy(true);
    setMessage("Starting execution");
    try {
      const execution = await apiClient.startExecution(token, workflowId, {
        source: "frontend",
        workflowName
      });
      setExecution(execution);
      setMessage("Execution started");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Execution failed to start");
    } finally {
      setBusy(false);
    }
  }

  if (!canOperate) {
    return <AuthPanel />;
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-line bg-white">
        <div className="flex h-16 items-center justify-between px-5">
          <div className="flex items-center gap-3">
            <GitBranch className="h-6 w-6 text-brand" aria-hidden="true" />
            <div>
              <h1 className="text-lg font-semibold">AI Workflow Automation Platform</h1>
              <p className="text-xs text-slate-500">{user?.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium hover:bg-panel disabled:opacity-50"
              onClick={saveWorkflow}
              disabled={busy}
              type="button"
            >
              <Save className="h-4 w-4" aria-hidden="true" />
              Save
            </button>
            <button
              className="inline-flex h-10 items-center gap-2 rounded-md bg-brand px-3 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              onClick={runWorkflow}
              disabled={busy}
              type="button"
            >
              <Play className="h-4 w-4" aria-hidden="true" />
              Run
            </button>
            <button
              className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-line bg-white hover:bg-panel"
              onClick={logout}
              title="Sign out"
              type="button"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </header>

      <section className="grid min-h-[calc(100vh-64px)] grid-cols-[280px_minmax(0,1fr)_340px]">
        <aside className="border-r border-line bg-white p-4">
          <label className="block text-xs font-semibold uppercase text-slate-500" htmlFor="workflow-name">
            Workflow name
          </label>
          <input
            id="workflow-name"
            className="mt-2 h-10 w-full rounded-md border border-line px-3 text-sm outline-none focus:border-brand"
            value={workflowName}
            onChange={(event) => setWorkflowName(event.target.value)}
          />
          <div className="mt-5">
            <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <Activity className="h-4 w-4 text-brand" aria-hidden="true" />
              Node library
            </div>
            <WorkflowBuilder.NodePalette />
          </div>
          <div className="mt-5 rounded-md border border-line bg-panel p-3 text-sm text-slate-600">
            {message}
          </div>
        </aside>

        <section className="min-w-0 bg-[#eef1f6]">
          <WorkflowBuilder />
        </section>

        <aside className="border-l border-line bg-white">
          <div className="border-b border-line p-4">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <BarChart3 className="h-4 w-4 text-brand" aria-hidden="true" />
              Analytics
            </div>
            <MetricsPanel />
          </div>
          <ExecutionPanel />
        </aside>
      </section>
    </main>
  );
}
