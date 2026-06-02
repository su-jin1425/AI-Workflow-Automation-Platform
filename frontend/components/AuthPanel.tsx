"use client";

import { Lock, UserPlus } from "lucide-react";
import { FormEvent, useState } from "react";

import { apiClient } from "@/services/api";
import { useAuthStore } from "@/store/auth-store";

export function AuthPanel() {
  const { setSession } = useAuthStore();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("Developer");
  const [email, setEmail] = useState("developer@example.com");
  const [password, setPassword] = useState("ChangeMe123");
  const [message, setMessage] = useState("Sign in to manage workflows");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      if (mode === "register") {
        await apiClient.register(name, email, password);
      }
      const session = await apiClient.login(email, password);
      setSession(session.access_token, session.user);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-[#eef1f6] px-4">
      <form className="w-full max-w-md rounded-md border border-line bg-white p-6 shadow-sm" onSubmit={submit}>
        <div className="mb-5 flex items-center gap-3">
          {mode === "login" ? <Lock className="h-5 w-5 text-brand" /> : <UserPlus className="h-5 w-5 text-brand" />}
          <div>
            <h1 className="text-xl font-semibold">AI Workflow Automation Platform</h1>
            <p className="text-sm text-slate-500">{message}</p>
          </div>
        </div>
        <div className="mb-4 grid grid-cols-2 rounded-md border border-line p-1">
          <button
            type="button"
            className={`h-9 rounded ${mode === "login" ? "bg-brand text-white" : "text-slate-600"}`}
            onClick={() => setMode("login")}
          >
            Login
          </button>
          <button
            type="button"
            className={`h-9 rounded ${mode === "register" ? "bg-brand text-white" : "text-slate-600"}`}
            onClick={() => setMode("register")}
          >
            Register
          </button>
        </div>
        {mode === "register" ? (
          <label className="mb-3 block text-sm font-medium">
            Name
            <input className="mt-1 h-10 w-full rounded-md border border-line px-3" value={name} onChange={(event) => setName(event.target.value)} />
          </label>
        ) : null}
        <label className="mb-3 block text-sm font-medium">
          Email
          <input
            className="mt-1 h-10 w-full rounded-md border border-line px-3"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label className="mb-5 block text-sm font-medium">
          Password
          <input
            className="mt-1 h-10 w-full rounded-md border border-line px-3"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="h-10 w-full rounded-md bg-brand font-medium text-white disabled:opacity-50" disabled={busy} type="submit">
          {mode === "login" ? "Login" : "Create account"}
        </button>
      </form>
    </main>
  );
}
