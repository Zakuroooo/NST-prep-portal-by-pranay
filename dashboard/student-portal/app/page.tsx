import Link from "next/link";
import { Building2, Map, BarChart, Rocket, PlayCircle, Shield } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white font-['Inter']">
      {/* Top bar */}
      <header className="flex items-center justify-between px-6 md:px-8 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="bg-blue-700 rounded px-2 py-1 text-white font-bold text-sm">NST</div>
          <span className="font-bold text-gray-900 hidden sm:inline">| PlacePrep</span>
        </div>
        <Link
          href="/login"
          className="border border-gray-300 text-gray-700 text-sm px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors font-medium"
        >
          Login
        </Link>
      </header>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 md:px-8 pt-12 md:pt-16 pb-12 flex flex-col lg:flex-row items-center gap-12">
        <div className="flex-1 max-w-xl text-center lg:text-left">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 text-xs font-semibold px-3 py-1.5 rounded-full mb-6 border border-blue-200">
            <Rocket className="w-3.5 h-3.5" />
            NEW PLATFORM
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-5">
            Crack Your Dream<br className="hidden lg:block" />Company Interview
          </h1>
          <p className="text-gray-600 text-base md:text-lg leading-relaxed mb-8 mx-auto lg:mx-0 max-w-md lg:max-w-none">
            India&apos;s first structured, data-driven interview prep portal built exclusively
            for NST students to master technical and behavioral rounds.
          </p>
          <div className="flex items-center justify-center lg:justify-start gap-3">
            <Link
              href="/login"
              className="bg-gray-900 text-white text-sm font-semibold px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
            >
              Start Prep Now
            </Link>
          </div>
        </div>

        {/* Hero image placeholder — dashboard mockup */}
        <div className="flex-1 hidden lg:block w-full">
          <div className="rounded-2xl border border-gray-200 shadow-2xl overflow-hidden bg-gray-50">
            <div className="bg-gray-800 flex items-center gap-2 px-4 py-3">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <div className="p-6 space-y-3">
              <div className="flex gap-3">
                <div className="w-32 h-4 bg-blue-200 rounded" />
                <div className="w-20 h-4 bg-gray-200 rounded" />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="h-20 bg-blue-50 rounded-lg border border-blue-100" />
                <div className="h-20 bg-green-50 rounded-lg border border-green-100" />
                <div className="h-20 bg-blue-50 rounded-lg border border-blue-100" />
              </div>
              <div className="h-32 bg-gradient-to-r from-blue-100 to-blue-50 rounded-lg" />
              <div className="flex gap-2">
                <div className="h-4 w-24 bg-gray-200 rounded" />
                <div className="h-4 w-16 bg-gray-200 rounded" />
                <div className="h-4 w-20 bg-gray-200 rounded" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-t border-b border-gray-100 bg-gray-50">
        <div className="max-w-3xl mx-auto px-6 md:px-8 py-8 grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-0 divide-y md:divide-y-0 md:divide-x divide-gray-200 text-center">
          <div className="px-8 pt-4 md:pt-0">
            <div className="text-3xl font-bold text-gray-900">658+</div>
            <div className="text-sm text-gray-500 mt-1">Companies Covered</div>
          </div>
          <div className="px-8 pt-6 md:pt-0">
            <div className="text-3xl font-bold text-gray-900">18,000+</div>
            <div className="text-sm text-gray-500 mt-1">Real Questions</div>
          </div>
          <div className="px-8 pt-6 md:pt-0">
            <div className="flex items-center justify-center gap-2">
              <Shield className="w-5 h-5 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">Built for NST</span>
            </div>
            <div className="text-sm text-gray-500 mt-1">Tailored Curriculum</div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 md:px-8 py-16 md:py-20">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-900 text-center mb-3">
          Everything you need to succeed
        </h2>
        <p className="text-gray-500 text-center mb-10 md:mb-12 max-w-xl mx-auto text-sm md:text-base">
          Stop guessing what they&apos;ll ask. We&apos;ve mapped out the exact requirements, questions,
          and roadmaps for top tech companies.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
              <Building2 className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Company Intel</h3>
            <p className="text-gray-500 text-sm leading-relaxed">
              Deep dive into specific company hiring patterns, recent interview experiences,
              and core focus areas to target your prep.
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
              <Map className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Custom Roadmaps (4–16 Weeks)</h3>
            <p className="text-gray-500 text-sm leading-relaxed">
              Pick your target duration — 4, 8, 12, or 16 weeks — and get a personalized
              day-by-day study plan tailored to your chosen companies.
            </p>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
              <BarChart className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Curriculum Gap</h3>
            <p className="text-gray-500 text-sm leading-relaxed">
              Identify exactly what isn&apos;t taught in standard courses but is highly expected
              by elite engineering teams.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 px-6 md:px-8 py-8 md:py-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="bg-blue-700 rounded px-2 py-1 text-white font-bold text-xs">NST</div>
          </div>
          <p className="text-sm text-gray-400 text-center md:text-left">© 2024 PlacePrep by NST. All rights reserved.</p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400">
            <a href="#" className="hover:text-gray-600">Privacy Policy</a>
            <a href="#" className="hover:text-gray-600">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
