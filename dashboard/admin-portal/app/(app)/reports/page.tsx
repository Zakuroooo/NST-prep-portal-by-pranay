"use client";

import { Download, FileText, TrendingUp, Users, GraduationCap } from "lucide-react";

const reports = [
  {
    title: "Student Performance",
    desc: "Detailed breakdown of student roadmap progress, mock interview scores, and placement stats.",
    icon: GraduationCap,
    color: "blue",
  },
  {
    title: "Faculty Engagement",
    desc: "Analytics on faculty session acceptance rates, average ratings, and response times.",
    icon: Users,
    color: "indigo",
  },
  {
    title: "System Utilization",
    desc: "Platform usage metrics including peak hours, active users, and feature adoption.",
    icon: TrendingUp,
    color: "cyan",
  },
];

const COLOR_MAP: Record<string, { bg: string; text: string }> = {
  blue:   { bg: "bg-blue-50",   text: "text-blue-600" },
  indigo: { bg: "bg-indigo-50", text: "text-indigo-600" },
  cyan:   { bg: "bg-cyan-50",   text: "text-cyan-600" },
};

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">Generate and export detailed platform analytics.</p>
      </div>

      {/* Report cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => {
          const c = COLOR_MAP[report.color] ?? { bg: "bg-gray-50", text: "text-gray-600" };
          return (
            <div key={report.title} className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col hover:shadow-md transition-shadow">
              <div className={`w-12 h-12 rounded-xl ${c.bg} ${c.text} flex items-center justify-center mb-4`}>
                <report.icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-semibold text-gray-900 mb-1.5">{report.title}</h3>
              <p className="text-sm text-gray-500 flex-1 mb-6">{report.desc}</p>
              <button className="w-full flex items-center justify-center gap-2 bg-gray-50 hover:bg-gray-100 text-gray-700 py-3 rounded-lg text-sm font-semibold transition-colors border border-gray-100">
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          );
        })}
      </div>

      {/* Recent exports */}
      <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <FileText className="w-5 h-5 text-gray-400" />
          <h3 className="text-base font-semibold text-gray-900">Recent Exports</h3>
        </div>
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-200 mx-auto mb-3" />
          <p className="text-sm text-gray-400">No recent exports found.</p>
        </div>
      </div>
    </div>
  );
}
