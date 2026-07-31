"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Loader2, Shield, User } from "lucide-react";

const STUDENT_LOGIN_URL =
  process.env.NEXT_PUBLIC_STUDENT_PORTAL_URL || "http://localhost:3000";

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e?: React.FormEvent, isGuest = false) {
    if (e) e.preventDefault();
    setError("");
    setLoading(true);

    const loginEmail = isGuest ? "admin@newtonschool.co" : email.trim().toLowerCase();
    const loginPassword = isGuest ? "Admin@NST2024" : password;

    try {
      const res = await fetch(`${STUDENT_LOGIN_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: loginEmail, password: loginPassword }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.message || "Login failed. Please check your credentials.");
        return;
      }

      if (data.data.role !== "admin") {
        setError("Access denied. This portal is for administrators only.");
        return;
      }

      router.push("/overview");
    } catch {
      setError("Unable to connect. Please check your internet connection.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* ── Left brand panel ── */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-[#3341c2] p-16">
        
        <div className="flex items-center gap-3">
          <div className="bg-white/20 rounded px-2 py-1 text-white font-bold text-xs">NST</div>
          <span className="font-bold text-white text-sm">PlacePrep</span>
        </div>

        <div className="max-w-md">
          <h1 className="text-[40px] font-bold text-white leading-tight mb-4 tracking-tight">
            Admin Control Center
          </h1>
          <p className="text-blue-100/90 text-base leading-relaxed mb-12">
            Full visibility into students, faculty, sessions, and placement metrics. Manage the entire NST Interview Prep ecosystem from one place.
          </p>

          <div className="space-y-6">
            <div className="flex items-center gap-6">
              <span className="text-white font-bold text-lg w-20">3</span>
              <span className="text-blue-100/90 text-sm">Portal Management</span>
            </div>
            <div className="flex items-center gap-6">
              <span className="text-white font-bold text-lg w-20">Real-time</span>
              <span className="text-blue-100/90 text-sm">Session Monitoring</span>
            </div>
            <div className="flex items-center gap-6">
              <span className="text-white font-bold text-lg w-20">Full</span>
              <span className="text-blue-100/90 text-sm">Faculty & Student Control</span>
            </div>
          </div>
        </div>

        <div className="opacity-0">
          {/* Spacer for bottom alignment */}
          <p>Newton School of Technology</p>
        </div>
      </div>

      {/* ── Right login panel ── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 bg-white">
        <div className="flex items-center gap-2 mb-10 lg:hidden">
          <div className="bg-blue-600 rounded px-2 py-1 text-white font-bold text-xs">NST</div>
          <span className="font-bold text-gray-900 text-sm">PlacePrep Admin</span>
        </div>

        <div className="w-full max-w-[360px]">
          <div className="mb-8 text-center sm:text-left">
            <h2 className="text-2xl font-bold text-gray-900 mb-1.5 tracking-tight">Admin Sign In</h2>
            <p className="text-gray-500 text-xs">Access the PlacePrep management console</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 text-xs px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={(e) => handleLogin(e, false)} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-[11px] font-bold text-gray-700 tracking-wide">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@newtonschool.co"
                required
                disabled={loading}
                className="w-full bg-white border border-gray-200 text-gray-900 placeholder-gray-400 px-4 py-3.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-bold text-gray-700 tracking-wide">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  disabled={loading}
                  className="w-full bg-white border border-gray-200 text-gray-900 placeholder-gray-400 px-4 py-3.5 pr-11 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full bg-[#1d4ed8] hover:bg-[#1e40af] disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg text-xs transition-all duration-200 flex items-center justify-center gap-2 mt-2 shadow-sm"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Shield className="w-4 h-4" />
              )}
              Sign In to Admin Portal
            </button>
          </form>

          <div className="relative my-7">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-100"></div>
            </div>
            <div className="relative flex justify-center text-[10px] font-medium uppercase tracking-widest text-gray-400">
              <span className="bg-white px-3">Or</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => handleLogin(undefined, true)}
            disabled={loading}
            className="w-full bg-gray-50 border border-gray-100 hover:bg-gray-100 text-gray-700 font-semibold py-3 rounded-lg text-xs transition-all duration-200 flex items-center justify-center gap-2"
          >
            <User className="w-4 h-4 text-gray-500" />
            Guest Access (Demo Mode)
          </button>
          
          <div className="mt-8 pt-6">
            <p className="text-center text-[10px] text-gray-400">
              Access restricted to authorized administrators only.<br/>
              Contact <span className="font-semibold text-gray-500">tech@newtonschool.co</span> for access.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
