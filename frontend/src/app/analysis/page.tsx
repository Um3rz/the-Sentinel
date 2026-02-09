"use client";

import Link from "next/link";

export default function AnalysisResult() {
    // Default analysis data - in production this would come from API/state
    const severity: "High" | "Medium" | "Low" = "High";
    const issue = "Animation Timing Mismatch";
    const description = "The modal transition duration exceeds the design specification by 500ms, causing perceived lag.";
    const expected = "300ms";
    const found = "800ms";
    const filePath = "animation.config.js";
    const lineRange = "Lines 42-48";
    const oldCode = `  duration: 800, // Too slow for spec`;
    const newCode = `  duration: 300, // Correct spec`;
    const prUrl = "https://github.com/user/repo/pull/42";

    const severityColors = {
        High: "bg-red-500/20 text-red-400 border-red-500/30",
        Medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        Low: "bg-green-500/20 text-green-400 border-green-500/30",
    };

    return (
        <main className="min-h-screen bg-gradient-to-b from-navy-900 to-navy-800">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 border-b border-navy-700/50">
                <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-accent-blue rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                                <circle cx="12" cy="12" r="4" fill="currentColor" />
                            </svg>
                        </div>
                        <span className="font-bold text-white">The Sentinel</span>
                    </div>
                    <span className="text-gray-600">›</span>
                    <Link href="/projects" className="text-gray-400 hover:text-white transition-colors">Projects</Link>
                    <span className="text-gray-600">›</span>
                    <Link href="/dashboard" className="text-gray-400 hover:text-white transition-colors">Dashboard</Link>
                    <span className="text-gray-600">›</span>
                    <span className="text-white">Analysis #8821-X</span>
                </div>

                <div className="flex items-center gap-4">
                    <Link href="/docs" className="text-sm text-gray-400 hover:text-white transition-colors">Documentation</Link>
                    <Link href="/support" className="text-sm text-gray-400 hover:text-white transition-colors">Support</Link>
                    <button className="p-2 text-gray-400 hover:text-white transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                    </button>
                    <div className="w-8 h-8 bg-accent-blue rounded-full flex items-center justify-center text-white text-sm">G</div>
                </div>
            </header>

            {/* Subheader */}
            <div className="px-6 py-3 border-b border-navy-700/50 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <span className="px-3 py-1 bg-navy-700 rounded-md text-gray-400 text-xs font-mono">
                        RECORDING_ID_992
                    </span>
                    <span className="text-gray-500 text-sm">Captured 14 mins ago via CI/CD</span>
                </div>
                <div className="flex items-center gap-2">
                    <button className="p-2 text-gray-400 hover:text-white transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                    <button className="p-2 text-gray-400 hover:text-white transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                    </button>
                </div>
            </div>

            <div className="flex p-6 gap-6 max-w-7xl mx-auto">
                {/* Left Panel - Visual Preview */}
                <div className="flex-1">
                    <div className="glass-card overflow-hidden h-[500px] relative">
                        {/* Placeholder for video/screenshot preview */}
                        <div className="absolute inset-0 bg-gradient-to-br from-navy-700 to-navy-800 flex items-center justify-center">
                            <div className="space-y-4 opacity-50">
                                <div className="h-3 w-32 bg-navy-600 rounded mx-auto"></div>
                                <div className="h-3 w-48 bg-navy-600 rounded mx-auto"></div>
                                <div className="h-3 w-40 bg-navy-600 rounded mx-auto"></div>
                            </div>
                        </div>

                        {/* Error highlight */}
                        <div className="absolute top-1/3 left-1/4 right-1/4 p-4 border-2 border-red-500 rounded-lg">
                            <div className="absolute -top-3 right-4 px-2 py-0.5 bg-red-500 text-white text-xs rounded">
                                TIMING ERROR
                            </div>
                            <div className="space-y-3 opacity-30">
                                <div className="h-2 w-full bg-accent-blue rounded"></div>
                                <div className="h-2 w-3/4 bg-accent-blue rounded"></div>
                                <div className="h-2 w-1/2 bg-accent-blue rounded"></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Panel - Analysis Details */}
                <div className="w-[450px] space-y-6">
                    {/* Analysis Card */}
                    <div className="glass-card p-6">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-start gap-3">
                                <div className="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
                                    <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="text-white font-semibold text-sm">VIBE DIFF ANALYSIS</h3>
                                    <p className="text-gray-500 text-xs">Automated detection • Confidence 98%</p>
                                </div>
                            </div>
                            <span className={`px-3 py-1 text-xs font-medium rounded-full border ${severityColors[severity]}`}>
                                {severity} Severity
                            </span>
                        </div>

                        <h2 className="text-xl font-bold text-white mb-2">Issue Detected: {issue}</h2>
                        <p className="text-gray-400 text-sm mb-4">{description}</p>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-navy-800 rounded-lg p-4">
                                <p className="text-gray-500 text-xs uppercase mb-1">Expected</p>
                                <p className="text-vibe-green text-2xl font-bold">{expected}</p>
                            </div>
                            <div className="bg-navy-800 rounded-lg p-4">
                                <p className="text-gray-500 text-xs uppercase mb-1">Found</p>
                                <p className="text-red-400 text-2xl font-bold">{found}</p>
                            </div>
                        </div>
                    </div>

                    {/* Code Diff */}
                    <div className="glass-card overflow-hidden">
                        <div className="flex items-center justify-between px-4 py-3 border-b border-navy-600">
                            <div className="flex items-center gap-2 text-sm text-gray-300">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                                </svg>
                                {filePath}
                            </div>
                            <span className="text-gray-500 text-xs">{lineRange}</span>
                        </div>

                        <div className="p-4 font-mono text-sm">
                            <table className="w-full">
                                <tbody>
                                    <tr>
                                        <td className="text-gray-600 pr-4 text-right w-8">42</td>
                                        <td className="text-gray-600 pr-4 text-right w-8">42</td>
                                        <td className="text-gray-300">export const modalConfig = {"{"}</td>
                                    </tr>
                                    <tr>
                                        <td className="text-gray-600 pr-4 text-right">43</td>
                                        <td className="text-gray-600 pr-4 text-right">43</td>
                                        <td className="text-gray-300 pl-4">type: &apos;slide-up&apos;,</td>
                                    </tr>
                                    <tr className="bg-red-500/10">
                                        <td className="text-gray-600 pr-4 text-right">44</td>
                                        <td className="text-gray-600 pr-4 text-right"></td>
                                        <td className="text-red-400 pl-4">- {oldCode}</td>
                                    </tr>
                                    <tr className="bg-green-500/10">
                                        <td className="text-gray-600 pr-4 text-right"></td>
                                        <td className="text-gray-600 pr-4 text-right">44</td>
                                        <td className="text-vibe-green pl-4">+ {newCode}</td>
                                    </tr>
                                    <tr>
                                        <td className="text-gray-600 pr-4 text-right">45</td>
                                        <td className="text-gray-600 pr-4 text-right">45</td>
                                        <td className="text-gray-300 pl-4">easing: &apos;cubic-bezier(0.4, 0, 0.2, 1)&apos;,</td>
                                    </tr>
                                    <tr>
                                        <td className="text-gray-600 pr-4 text-right">46</td>
                                        <td className="text-gray-600 pr-4 text-right">46</td>
                                        <td className="text-gray-300 pl-4">backdrop: true</td>
                                    </tr>
                                    <tr>
                                        <td className="text-gray-600 pr-4 text-right">47</td>
                                        <td className="text-gray-600 pr-4 text-right">47</td>
                                        <td className="text-gray-300">{"}"};</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="space-y-3">
                        <a
                            href={prUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full btn-vibe flex items-center justify-center gap-2"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            Open Pull Request
                        </a>
                        <a
                            href={prUrl?.replace("/pull/", "")}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full flex items-center justify-center gap-2 text-gray-400 hover:text-white transition-colors py-2"
                        >
                            View on GitHub
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        </main>
    );
}
