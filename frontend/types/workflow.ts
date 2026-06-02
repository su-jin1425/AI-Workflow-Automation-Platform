import type { Edge, Node } from "@xyflow/react";

export type WorkflowNodeType =
  | "ai_prompt"
  | "api_request"
  | "condition"
  | "delay"
  | "database"
  | "webhook"
  | "email"
  | "scheduler"
  | "logic"
  | "file_processing";

export type WorkflowDefinition = {
  nodes: Array<{
    id: string;
    type: WorkflowNodeType;
    position: { x: number; y: number };
    configuration: Record<string, unknown>;
  }>;
  edges: Array<{
    id?: string;
    source: string;
    target: string;
    condition?: boolean;
  }>;
};

export type WorkflowRecord = {
  id: string;
  workflow_name: string;
  workflow_definition: WorkflowDefinition;
  status: string;
  created_by: string;
  created_at: string;
  updated_at: string;
};

export type ExecutionRecord = {
  id: string;
  workflow_id: string;
  execution_status: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown> | null;
  started_at: string | null;
  completed_at: string | null;
  execution_logs: Array<{ time: string; message: string }>;
  created_at: string;
};

export type DashboardOverview = {
  workflows: number;
  executions: number;
  completed: number;
  failed: number;
};

export type FlowNode = Node<{ label: string; type: WorkflowNodeType; configuration: Record<string, unknown> }>;
export type FlowEdge = Edge<{ condition?: boolean }>;
