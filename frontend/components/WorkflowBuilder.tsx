"use client";

import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import { Plus } from "lucide-react";

import { NodeConfigPanel } from "@/components/NodeConfigPanel";
import { nodeLabels, useWorkflowStore } from "@/store/workflow-store";
import type { WorkflowNodeType } from "@/types/workflow";

const palette = Object.entries(nodeLabels) as Array<[WorkflowNodeType, string]>;

function WorkflowBuilderCanvas() {
  const { nodes, edges, selectedNodeId, onNodesChange, onEdgesChange, onConnect, setSelectedNodeId } = useWorkflowStore();

  return (
    <div className="relative h-full min-h-[calc(100vh-64px)]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, node) => setSelectedNodeId(node.id)}
        fitView
      >
        <Background gap={24} size={1} />
        <MiniMap pannable zoomable />
        <Controls />
      </ReactFlow>
      {selectedNodeId ? <NodeConfigPanel /> : null}
    </div>
  );
}

function NodePalette() {
  const addNode = useWorkflowStore((state) => state.addNode);

  return (
    <div className="grid gap-2">
      {palette.map(([type, label]) => (
        <button
          key={type}
          type="button"
          className="flex h-10 items-center justify-between rounded-md border border-line bg-white px-3 text-left text-sm hover:border-brand hover:bg-panel"
          onClick={() => addNode(type)}
        >
          <span>{label}</span>
          <Plus className="h-4 w-4 text-slate-500" aria-hidden="true" />
        </button>
      ))}
    </div>
  );
}

export const WorkflowBuilder = Object.assign(WorkflowBuilderCanvas, { NodePalette });
