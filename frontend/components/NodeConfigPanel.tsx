"use client";

import { X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useWorkflowStore } from "@/store/workflow-store";

export function NodeConfigPanel() {
  const { nodes, selectedNodeId, setSelectedNodeId, updateNodeConfiguration } = useWorkflowStore();
  const node = useMemo(() => nodes.find((item) => item.id === selectedNodeId), [nodes, selectedNodeId]);
  const [draft, setDraft] = useState(() => JSON.stringify(node?.data.configuration ?? {}, null, 2));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(JSON.stringify(node?.data.configuration ?? {}, null, 2));
    setError(null);
  }, [node?.id]);

  if (!node) {
    return null;
  }

  function save() {
    if (!node) {
      return;
    }
    try {
      const parsed = JSON.parse(draft) as Record<string, unknown>;
      updateNodeConfiguration(node.id, parsed);
      setError(null);
    } catch {
      setError("Configuration must be valid JSON");
    }
  }

  return (
    <section className="absolute right-4 top-4 z-10 w-[360px] rounded-md border border-line bg-white shadow-sm">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <div>
          <h2 className="text-sm font-semibold">{node.data.label}</h2>
          <p className="text-xs text-slate-500">{node.id}</p>
        </div>
        <button className="grid h-8 w-8 place-items-center rounded-md hover:bg-panel" type="button" onClick={() => setSelectedNodeId(null)}>
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
      <div className="p-4">
        <label className="block text-xs font-semibold uppercase text-slate-500" htmlFor="node-config">
          Configuration JSON
        </label>
        <textarea
          id="node-config"
          className="mt-2 h-64 w-full resize-none rounded-md border border-line bg-slate-950 p-3 font-mono text-xs leading-5 text-slate-50 outline-none focus:border-brand"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
        />
        <button className="mt-3 h-10 w-full rounded-md bg-brand text-sm font-medium text-white" onClick={save} type="button">
          Apply configuration
        </button>
        {error ? <p className="mt-2 text-sm text-danger">{error}</p> : null}
      </div>
    </section>
  );
}
