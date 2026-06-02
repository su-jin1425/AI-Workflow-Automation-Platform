import type { DashboardOverview, ExecutionRecord, WorkflowDefinition, WorkflowRecord } from "@/types/workflow";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type LoginResponse = {
  access_token: string;
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
    created_at: string;
  };
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    }
  });
  const payload = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    const detail = payload && typeof payload === "object" && "detail" in payload ? String(payload.detail) : response.statusText;
    throw new Error(detail);
  }
  return payload as T;
}

function authHeader(token: string) {
  return { Authorization: `Bearer ${token}` };
}

export const apiClient = {
  register(name: string, email: string, password: string) {
    return request<LoginResponse["user"]>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password })
    });
  },
  async login(email: string, password: string) {
    const body = new URLSearchParams({ username: email, password });
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail ?? "Login failed");
    }
    return payload as LoginResponse;
  },
  createWorkflow(
    token: string,
    payload: { workflow_name: string; workflow_definition: WorkflowDefinition; status: "draft" | "active" | "paused" }
  ) {
    return request<WorkflowRecord>("/workflows", {
      method: "POST",
      headers: authHeader(token),
      body: JSON.stringify(payload)
    });
  },
  updateWorkflow(
    token: string,
    id: string,
    payload: { workflow_name: string; workflow_definition: WorkflowDefinition; status: "draft" | "active" | "paused" }
  ) {
    return request<WorkflowRecord>(`/workflows/${id}`, {
      method: "PUT",
      headers: authHeader(token),
      body: JSON.stringify(payload)
    });
  },
  startExecution(token: string, workflowId: string, inputPayload: Record<string, unknown>) {
    return request<ExecutionRecord>("/executions/start", {
      method: "POST",
      headers: authHeader(token),
      body: JSON.stringify({ workflow_id: workflowId, input_payload: inputPayload })
    });
  },
  executions(token: string) {
    return request<ExecutionRecord[]>("/executions", {
      headers: authHeader(token)
    });
  },
  overview(token: string) {
    return request<DashboardOverview>("/analytics/overview", {
      headers: authHeader(token)
    });
  }
};
