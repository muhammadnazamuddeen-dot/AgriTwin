"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";
import Icon from "@/components/Icon";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [selectedRole, setSelectedRole] = useState<"farmer" | "extension_officer">("farmer");

  const handleInstantDemoLogin = async (demoEmail: string, demoRole: string) => {
    setDemoLoading(demoRole);
    setError(null);
    try {
      const res = await api.login({ email: demoEmail, password: "password123" });
      login(res.access_token, res.user);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
      setDemoLoading(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === "register") {
        await api.register({
          name,
          email,
          phone: phone || undefined,
          role: selectedRole,
          password,
        });
      }

      const res = await api.login({ email, password });
      login(res.access_token, res.user);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand text-abyss">
            <Icon name="sprout" size={24} strokeWidth={2.2} />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">
            Agri<span className="text-brand">Twin</span> AI
          </h1>
          <p className="mt-1 text-sm text-mist">
            Punjab Agriculture Intelligence Platform
          </p>
        </div>

        {/* Main Card */}
        <div className="glass-panel p-6 sm:p-7">
          {/* Demo Accounts */}
          <div className="mb-5 rounded-xl border border-edge bg-abyss p-3">
            <div className="mb-2 flex items-center justify-between px-0.5">
              <span className="flex items-center gap-1.5 text-xs font-medium text-mist">
                <Icon name="spark" size={12} className="text-brand" />
                <span>Demo Accounts</span>
              </span>
              <span className="text-[11px] text-dim">One-tap login</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleInstantDemoLogin("farmer@agritwin.pk", "farmer")}
                disabled={demoLoading !== null}
                className="flex items-center justify-between rounded-lg border border-emerald-600/20 bg-emerald-500/10 px-3 py-2 text-sm font-medium text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/20 transition-colors disabled:opacity-50"
              >
                <span className="flex items-center gap-2">
                  <Icon name="wheat" size={14} />
                  <span>Farmer</span>
                </span>
                {demoLoading === "farmer" ? (
                  <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                ) : (
                  <span className="text-xs opacity-50">→</span>
                )}
              </button>
              <button
                type="button"
                onClick={() => handleInstantDemoLogin("officer@agritwin.pk", "officer")}
                disabled={demoLoading !== null}
                className="flex items-center justify-between rounded-lg border border-sky-600/20 bg-sky-500/10 px-3 py-2 text-sm font-medium text-sky-700 dark:text-sky-300 hover:bg-sky-500/20 transition-colors disabled:opacity-50"
              >
                <span className="flex items-center gap-2">
                  <Icon name="activity" size={14} />
                  <span>Officer</span>
                </span>
                {demoLoading === "officer" ? (
                  <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                ) : (
                  <span className="text-xs opacity-50">→</span>
                )}
              </button>
            </div>
          </div>

          {/* Form Header */}
          <div className="mb-4 flex items-center justify-between border-b border-edge pb-3">
            <h2 className="text-sm font-semibold text-ink">
              {mode === "login" ? "Sign in to your account" : "Create a new account"}
            </h2>
            <button
              type="button"
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError(null);
              }}
              className="text-xs font-medium text-brand hover:underline"
            >
              {mode === "login" ? "Create Account" : "Sign In instead"}
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "register" && (
              <>
                {/* Role Switcher for Custom Registration */}
                <div>
                  <label className="mb-1.5 block text-xs font-medium text-mist">
                    Select Account Role
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setSelectedRole("farmer")}
                      className={`flex items-center gap-2 rounded-lg p-2.5 border text-left transition-colors ${selectedRole === "farmer"
                          ? "border-brand/40 bg-brand/10"
                          : "border-edge bg-abyss hover:bg-ink/[0.03]"
                        }`}
                    >
                      <Icon name="wheat" size={14} className={selectedRole === "farmer" ? "text-brand" : "text-dim"} />
                      <div>
                        <div className={`text-xs font-medium ${selectedRole === "farmer" ? "text-brand" : "text-mist"}`}>Punjab Farmer</div>
                        <div className="text-[10px] text-dim">Field Landowner</div>
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setSelectedRole("extension_officer")}
                      className={`flex items-center gap-2 rounded-lg p-2.5 border text-left transition-colors ${selectedRole === "extension_officer"
                          ? "border-sky-500/40 bg-sky-500/10"
                          : "border-edge bg-abyss hover:bg-ink/[0.03]"
                        }`}
                    >
                      <Icon name="activity" size={14} className={selectedRole === "extension_officer" ? "text-sky-600 dark:text-sky-400" : "text-dim"} />
                      <div>
                        <div className={`text-xs font-medium ${selectedRole === "extension_officer" ? "text-sky-600 dark:text-sky-400" : "text-mist"}`}>Agri Officer</div>
                        <div className="text-[10px] text-dim">Supervisory Mode</div>
                      </div>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-mist">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="input-theme px-3.5 py-2 text-sm"
                    placeholder="e.g. Tariq Mahmood"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-mist">
                    Phone Number (Optional)
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="input-theme px-3.5 py-2 text-sm"
                    placeholder="03001234567"
                  />
                </div>
              </>
            )}

            <div>
              <label className="mb-1 block text-xs font-medium text-mist">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input-theme px-3.5 py-2 text-sm"
                placeholder="user@agritwin.pk"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-mist">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="input-theme px-3.5 py-2 text-sm"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="rounded-lg border border-rose-500/20 bg-rose-500/10 p-2.5 text-xs text-rose-600 dark:text-rose-400">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand py-2.5 text-sm font-medium text-abyss transition-colors hover:bg-brand-dark disabled:opacity-50"
            >
              {loading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              ) : mode === "login" ? (
                "Sign In"
              ) : (
                `Register as ${selectedRole === "extension_officer" ? "Agri Officer" : "Farmer"}`
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
