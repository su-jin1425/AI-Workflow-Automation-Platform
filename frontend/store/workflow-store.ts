import { addEdge, applyEdgeChanges, applyNodeChanges, type Connection, type EdgeChange, type NodeChange } from "@xyflow/react";
import { create } from "zustand";

import type { DashboardOverview, ExecutionRecord, FlowEdge, FlowNode, WorkflowDefinition, WorkflowNodeType } from "@/types/workflow";

const defaultNodes: FlowNode[] = [
  {
    id: "start",
    type: "default",
    position: { x: 120, y: 120 },
    data: {
      label: "Start Input",
      type: "logic",
      configuration: { operation: "set", value: { accepted: true } }
    }
  },
  {
    id: "delay-check",
    type: "default",
    position: { x: 420, y: 120 },
    data: {
      label: "Delay",
      type: "delay",
      configuration: { seconds: 0 }
    }
  }
];

const defaultEdges: FlowEdge[] = [{ id: "start-delay-check", source: "start", target: "delay-check" }];

type WorkflowState = {
  workflowId: string | null;
  workflowName: string;
  nodes: FlowNode[];
  edges: FlowEdge[];
  selectedNodeId: string | null;
  execution: ExecutionRecord | null;
  executions: ExecutionRecord[];
  overview: DashboardOverview;
  setWorkflowId: (id: string) => void;
  setWorkflowName: (name: string) => void;
  setSelectedNodeId: (id: string | null) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: (type: WorkflowNodeType) => void;
  updateNodeConfiguration: (nodeId: string, configuration: Record<string, unknown>) => void;
  buildDefinition: () => WorkflowDefinition;
  setExecution: (execution: ExecutionRecord) => void;
  setExecutions: (executions: ExecutionRecord[]) => void;
  setOverview: (overview: DashboardOverview) => void;
};

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  workflowId: null,
  workflowName: "Customer Support AI Workflow",
  nodes: defaultNodes,
  edges: defaultEdges,
  selectedNodeId: null,
  execution: null,
  executions: [],
  overview: { workflows: 0, executions: 0, completed: 0, failed: 0 },
  setWorkflowId: (id) => set({ workflowId: id }),
  setWorkflowName: (workflowName) => set({ workflowName }),
  setSelectedNodeId: (selectedNodeId) => set({ selectedNodeId }),
  onNodesChange: (changes) => set({ nodes: applyNodeChanges(changes, get().nodes) as FlowNode[] }),
  onEdgesChange: (changes) => set({ edges: applyEdgeChanges(changes, get().edges) as FlowEdge[] }),
  onConnect: (connection) =>
    set({
      edges: addEdge({ ...connection, animated: true }, get().edges) as FlowEdge[]
    }),
  addNode: (type) => {
    const id = `${type}-${Date.now()}`;
    const label = nodeLabels[type];
    set({
      nodes: [
        ...get().nodes,
        {
          id,
          type: "default",
          position: { x: 180 + get().nodes.length * 40, y: 220 + get().nodes.length * 20 },
          data: { label, type, configuration: defaultConfiguration(type) }
        }
      ],
      selectedNodeId: id
    });
  },
  updateNodeConfiguration: (nodeId, configuration) =>
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: { ...node.data, configuration }
            }
          : node
      )
    }),
  buildDefinition: () => ({
    nodes: get().nodes.map((node) => ({
      id: node.id,
      type: node.data.type,
      position: node.position,
      configuration: node.data.configuration
    })),
    edges: get().edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      condition: edge.data?.condition
    }))
  }),
  setExecution: (execution) => set({ execution }),
  setExecutions: (executions) => set({ executions }),
  setOverview: (overview) => set({ overview })
}));

export const nodeLabels: Record<WorkflowNodeType, string> = {
  ai_prompt: "AI Prompt",
  api_request: "API Request",
  condition: "Condition",
  delay: "Delay",
  database: "Database",
  webhook: "Webhook",
  email: "Email",
  scheduler: "Scheduler",
  logic: "Logic",
  file_processing: "File Processing"
};

function defaultConfiguration(type: WorkflowNodeType): Record<string, unknown> {
  const configs: Record<WorkflowNodeType, Record<string, unknown>> = {
    ai_prompt: { prompt: "Summarize the input payload: {{ input }}" },
    api_request: { method: "GET", url: "https://httpbin.org/get", headers: {}, params: {} },
    condition: { left: "$.input.accepted", operator: "eq", right: true },
    delay: { seconds: 0 },
    database: { query: "select now() as current_time", params: {} },
    webhook: { url: "https://httpbin.org/post", payload: { event: "workflow.completed" } },
    email: { to: "", subject: "Workflow notification", body: "The workflow finished." },
    scheduler: { delay_seconds: 0 },
    logic: { operation: "set", value: { accepted: true } },
    file_processing: { mode: "text_stats", encoding: "plain", content: "sample text" }
  };
  return configs[type];
}
