"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Clock, Users, BookOpen } from "lucide-react";
import { useBookingsData } from "@/lib/hooks";

const MONTH_NAMES = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December",
];
const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function buildCalendarGrid(year: number, month: number) {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrev = new Date(year, month, 0).getDate();

  const cells: { day: number; curr: boolean }[] = [];
  for (let i = firstDay - 1; i >= 0; i--)
    cells.push({ day: daysInPrev - i, curr: false });
  for (let d = 1; d <= daysInMonth; d++)
    cells.push({ day: d, curr: true });
  while (cells.length % 7 !== 0)
    cells.push({ day: cells.length - daysInMonth - firstDay + 1, curr: false });
  return cells;
}

// Synthetic session distribution across the month for demo
const SESSION_DAYS: Record<number, { count: number; type: "upcoming" | "completed" | "mixed" }> = {
  3: { count: 2, type: "upcoming" },
  7: { count: 1, type: "completed" },
  10: { count: 3, type: "mixed" },
  14: { count: 1, type: "upcoming" },
  17: { count: 2, type: "completed" },
  21: { count: 4, type: "mixed" },
  24: { count: 1, type: "upcoming" },
  28: { count: 2, type: "completed" },
};

const STATUS_BADGE: Record<string, string> = {
  upcoming:  "bg-indigo-50 text-indigo-700 border border-indigo-200",
  completed: "bg-blue-600 text-white",
  cancelled: "bg-slate-100 text-slate-500",
  mixed:     "bg-cyan-50 text-cyan-700 border border-cyan-200",
};

const DOT_COLOR: Record<string, string> = {
  upcoming:  "bg-indigo-400",
  completed: "bg-blue-500",
  mixed:     "bg-cyan-400",
};

export default function CalendarPage() {
  const today = new Date();
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [selectedDay, setSelectedDay] = useState<number | null>(today.getDate());

  const cells = buildCalendarGrid(viewYear, viewMonth);
  const isCurrentMonth = viewYear === today.getFullYear() && viewMonth === today.getMonth();

  const prevMonth = () => {
    if (viewMonth === 0) { setViewYear(y => y - 1); setViewMonth(11); }
    else setViewMonth(m => m - 1);
    setSelectedDay(null);
  };
  const nextMonth = () => {
    if (viewMonth === 11) { setViewYear(y => y + 1); setViewMonth(0); }
    else setViewMonth(m => m + 1);
    setSelectedDay(null);
  };

  const { data: bookingsData } = useBookingsData();

  const allSessions = bookingsData?.sessions ?? bookingsData?.data?.sessions ?? [];
  const upcoming  = allSessions.filter((s: any) => ["pending","confirmed","upcoming"].includes((s.status ?? "").toLowerCase())).length;
  const completed = allSessions.filter((s: any) => (s.status ?? "").toLowerCase() === "completed").length;
  const selectedSessions = selectedDay ? SESSION_DAYS[selectedDay] : null;

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Session Calendar</h1>
          <p className="text-sm text-gray-500 mt-0.5">Track all mentorship sessions across the platform.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-50 border border-indigo-100 rounded-full text-sm font-semibold text-indigo-700">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            {upcoming} upcoming
          </span>
          <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 border border-blue-100 rounded-full text-sm font-semibold text-blue-600">
            {completed} completed
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Calendar Grid */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          {/* Month navigation */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
            <button
              onClick={prevMonth}
              className="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors text-gray-500"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <h2 className="text-sm font-bold text-gray-900 tracking-wide">
              {MONTH_NAMES[viewMonth]} {viewYear}
            </h2>
            <button
              onClick={nextMonth}
              className="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors text-gray-500"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Day headers */}
          <div className="grid grid-cols-7 border-b border-gray-100">
            {DAY_LABELS.map(d => (
              <div key={d} className="py-2 text-center text-xs font-bold text-gray-400 uppercase tracking-wider">
                {d}
              </div>
            ))}
          </div>

          {/* Calendar cells */}
          <div className="grid grid-cols-7">
            {cells.map((cell, idx) => {
              const isToday = isCurrentMonth && cell.curr && cell.day === today.getDate();
              const isSelected = cell.curr && cell.day === selectedDay;
              const hasSession = cell.curr && SESSION_DAYS[cell.day];
              const sessionInfo = hasSession ? SESSION_DAYS[cell.day] : null;

              return (
                <button
                  key={idx}
                  onClick={() => cell.curr && setSelectedDay(cell.day)}
                  className={`relative min-h-[64px] p-2 border-b border-r border-gray-50 flex flex-col transition-all ${
                    !cell.curr ? "bg-gray-50/50 cursor-default" :
                    isSelected ? "bg-blue-600" :
                    isToday ? "bg-indigo-50" :
                    "hover:bg-gray-50 cursor-pointer"
                  }`}
                >
                  <span className={`text-sm font-bold self-end leading-none mb-1 ${
                    !cell.curr ? "text-gray-300" :
                    isSelected ? "text-white" :
                    isToday ? "text-indigo-700" :
                    "text-gray-700"
                  }`}>
                    {cell.day}
                  </span>
                  {sessionInfo && (
                    <div className="flex-1 flex flex-col justify-end gap-0.5">
                      <div className={`w-full rounded text-[10px] font-bold px-1 py-0.5 text-center truncate ${
                        isSelected
                          ? "bg-white/20 text-white"
                          : DOT_COLOR[sessionInfo.type].replace("bg-", "bg-").replace("400", "50") + " " +
                            (sessionInfo.type === "completed" ? "text-blue-700" :
                             sessionInfo.type === "upcoming" ? "text-indigo-700" : "text-cyan-700")
                      }`}>
                        {sessionInfo.count} session{sessionInfo.count > 1 ? "s" : ""}
                      </div>
                      <div className="flex gap-0.5 justify-center">
                        {Array.from({ length: Math.min(sessionInfo.count, 4) }, (_, i) => (
                          <div
                            key={i}
                            className={`w-1 h-1 rounded-full ${isSelected ? "bg-white/60" : DOT_COLOR[sessionInfo.type]}`}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 px-5 py-3 border-t border-gray-100 bg-gray-50/50">
            {[
              { label: "Upcoming", dot: "bg-indigo-400" },
              { label: "Completed", dot: "bg-blue-500" },
              { label: "Mixed", dot: "bg-cyan-400" },
            ].map(l => (
              <div key={l.label} className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${l.dot}`} />
                <span className="text-xs font-semibold text-gray-500">{l.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Side panel */}
        <div className="space-y-4">
          {/* Selected day panel */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            {selectedDay ? (
              <>
                <div className="flex items-center gap-5 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex flex-col items-center justify-center shadow-sm">
                    <span className="text-xs font-bold leading-none uppercase">
                      {MONTH_NAMES[viewMonth].slice(0, 3)}
                    </span>
                    <span className="text-2xl font-black leading-none">{selectedDay}</span>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">
                      {DAY_LABELS[new Date(viewYear, viewMonth, selectedDay).getDay()]},{" "}
                      {MONTH_NAMES[viewMonth]} {selectedDay}
                    </p>
                    <p className="text-xs text-gray-400">
                      {selectedSessions ? `${selectedSessions.count} session${selectedSessions.count > 1 ? "s" : ""}` : "No sessions"}
                    </p>
                  </div>
                </div>

                {selectedSessions ? (
                  <div className="space-y-2">
                    {Array.from({ length: selectedSessions.count }, (_, i) => {
                      // Use real session data if available for this day
                      const realSession = allSessions[i];
                      const topic = realSession?.topic ?? "DSA Mock Interview";
                      const mentor = typeof realSession?.facultyId === "object"
                        ? realSession.facultyId?.fullName ?? "Prof. Sharma"
                        : "Prof. Sharma";
                      const times = ["10:00 AM", "2:00 PM", "4:30 PM", "6:00 PM"];
                      return (
                        <div key={i} className="flex items-center gap-5 p-2.5 rounded-lg bg-gray-50 border border-gray-100">
                          <div className={`w-1.5 h-8 rounded-full ${DOT_COLOR[selectedSessions.type]}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-gray-800 truncate">
                              {topic}
                            </p>
                            <p className="text-xs text-gray-400 mt-0.5">
                              {mentor} · {times[i % times.length]}
                            </p>
                          </div>
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${STATUS_BADGE[selectedSessions.type]}`}>
                            {selectedSessions.type}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <BookOpen className="w-10 h-10 text-gray-200 mx-auto mb-2" />
                    <p className="text-sm text-gray-400">No sessions on this day</p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <BookOpen className="w-10 h-10 text-gray-200 mx-auto mb-2" />
                <p className="text-sm text-gray-400 font-medium">Select a date to see sessions</p>
              </div>
            )}
          </div>

          {/* Quick stats */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 space-y-3">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">This Month</h3>
            {[
              { icon: Clock,   label: "Total Sessions", value: "24", color: "text-blue-600 bg-blue-50" },
              { icon: Users,   label: "Unique Students", value: "18", color: "text-indigo-600 bg-indigo-50" },
              { icon: BookOpen,label: "Avg per Day",     value: "3.4", color: "text-cyan-600 bg-cyan-50" },
            ].map(stat => (
              <div key={stat.label} className="flex items-center gap-5">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${stat.color}`}>
                  <stat.icon className="w-4 h-4" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-400 font-semibold uppercase">{stat.label}</p>
                  <p className="text-sm font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
