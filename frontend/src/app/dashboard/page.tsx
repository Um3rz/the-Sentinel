"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../context/AuthContext";

interface AnalysisStep {
    id: string;
    label: string;
    status: "pending" | "processing" | "completed" | "error";
}

export default function DashboardPage() {
    const { user, token, isLoading, logout } = useAuth();
    const router = useRouter();
    const [repoUrl, setRepoUrl] = useState("");
    const [deployedUrl, setDeployedUrl] = useState("");
    const [bugDescription, setBugDescription] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([
        { id: "capture", label: "Capturing visual context", status: "pending" },
        { id: "scout", label: "Scouting relevant files", status: "pending" },
        { id: "analyze", label: "AI analyzing codebase", status: "pending" },
        { id: "generate", label: "Generating fix", status: "pending" },
        { id: "pr", label: "Creating pull request", status: "pending" },
    ]);
    const [analysisResult, setAnalysisResult] = useState<{
        status: string;
        job_id: string;
        pr_url?: string;
        analysis?: { analysis: string; severity: string; fix?: { file_path: string; code: string } };
        error?: string;
    } | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    // Auth guard – redirect to login if not authenticated
    useEffect(() => {
        if (!isLoading && !user) {
            router.push("/login");
        }
    }, [isLoading, user, router]);

    const updateStep = (stepId: string, status: AnalysisStep["status"]) => {
        setAnalysisSteps(prev => prev.map(step =>
            step.id === stepId ? { ...step, status } : step
        ));
    };

    const resetSteps = () => {
        setAnalysisSteps([
            { id: "capture", label: "Capturing visual context", status: "pending" },
            { id: "scout", label: "Scouting relevant files", status: "pending" },
            { id: "analyze", label: "AI analyzing codebase", status: "pending" },
            { id: "generate", label: "Generating fix", status: "pending" },
            { id: "pr", label: "Creating pull request", status: "pending" },
        ]);
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const files = Array.from(e.dataTransfer.files);
            setUploadedFiles(prev => [...prev, ...files]);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const files = Array.from(e.target.files);
            setUploadedFiles(prev => [...prev, ...files]);
        }
    };

    const removeFile = (index: number) => {
        setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleAnalyze = async () => {
        if (!repoUrl || !token) return;
        setIsAnalyzing(true);
        setAnalysisResult(null);
        resetSteps();

        try {
            // Simulate step progression
            updateStep("capture", "processing");
            await new Promise(r => setTimeout(r, 800));
            updateStep("capture", deployedUrl ? "completed" : "pending");

            updateStep("scout", "processing");
            await new Promise(r => setTimeout(r, 600));

            const formData = new FormData();
            formData.append("repo_url", repoUrl);
            if (deployedUrl) formData.append("deployed_url", deployedUrl);
            if (bugDescription) formData.append("bug_description", bugDescription);

            uploadedFiles.forEach((file, i) => {
                if (file.type.startsWith("video/")) {
                    formData.append("video", file);
                } else {
                    formData.append("images", file);
                }
            });

            updateStep("scout", "completed");
            updateStep("analyze", "processing");

            const res = await fetch(`${API_BASE}/api/v1/analyze`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
                body: formData,
            });

            updateStep("analyze", "completed");
            updateStep("generate", "completed");
            updateStep("pr", "processing");
            await new Promise(r => setTimeout(r, 500));

            const data = await res.json();

            if (data.status === "error") {
                updateStep("pr", "error");
            } else {
                updateStep("pr", "completed");
            }

            setAnalysisResult(data);
        } catch {
            updateStep("pr", "error");
            setAnalysisResult({ status: "error", job_id: "", error: "Network error. Is the backend running?" });
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getStepIcon = (status: AnalysisStep["status"]) => {
        switch (status) {
            case "completed":
                return (
                    <svg className="w-5 h-5 text-vibe-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                );
            case "processing":
                return (
                    <svg className="w-5 h-5 text-accent-blue animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                );
            case "error":
                return (
                    <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                );
            default:
                return (
                    <div className="w-5 h-5 rounded-full border-2 border-navy-500" />
                );
        }
    };

    // Show loading while checking auth
    if (isLoading) {
        return (
            <main className="min-h-screen bg-gradient-to-b from-navy-900 to-navy-800 flex items-center justify-center">
                <div className="text-center">
                    <div className="relative">
                        <div className="w-16 h-16 border-4 border-accent-blue/20 border-t-accent-blue rounded-full animate-spin" />
                        <div className="absolute inset-0 w-16 h-16 border-4 border-vibe-green/10 border-t-vibe-green rounded-full animate-spin" style={{ animationDuration: '1.5s' }} />
                    </div>
                    <p className="text-gray-400 mt-4">Initializing Sentinel...</p>
                </div>
            </main>
        );
    }

    if (!user) return null;

    return (
        <main className="min-h-screen bg-gradient-to-b from-navy-900 to-navy-800">
            {/* Animated background grid */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.03)_1px,transparent_1px)] bg-[size:64px_64px]" />
            </div>

            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 border-b border-navy-700/50 backdrop-blur-sm relative z-10">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-vibe-green rounded-lg flex items-center justify-center animate-pulse-glow">
                        <Link href="/">
                            <svg className="w-4 h-4 text-navy-900" fill="currentColor" viewBox="0 0 24 24">
                                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                                <circle cx="12" cy="12" r="4" fill="currentColor" />
                            </svg>
                        </Link>
                    </div>
                    <span className="font-bold text-lg text-white">The Sentinel</span>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={logout}
                        className="px-3 py-1.5 text-sm text-gray-400 hover:text-white border border-navy-500 hover:border-navy-400 rounded-lg transition-all duration-200 hover:shadow-lg"
                    >
                        Logout
                    </button>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-300">{user.full_name || user.email}</span>
                        <div className="w-8 h-8 bg-accent-blue rounded-full flex items-center justify-center text-white text-sm font-medium">
                            {(user.full_name || user.email).charAt(0).toUpperCase()}
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex p-6 gap-6 max-w-7xl mx-auto relative z-10">
                {/* Left Panel - Input Form */}
                <div className="flex-1 space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-2xl font-bold text-white">Vibe Inspector</h1>
                            <p className="text-gray-400 text-sm">Input target vectors for anomaly analysis.</p>
                        </div>
                        <div className="px-4 py-1.5 bg-vibe-green/10 border border-vibe-green/30 rounded-full">
                            <span className="text-vibe-green text-sm font-medium">READY TO SCAN</span>
                        </div>
                    </div>

                    {/* Media Upload Zone */}
                    <div
                        className={`drop-zone p-12 flex flex-col items-center justify-center text-center transition-all duration-300 ${dragActive ? "border-vibe-green bg-vibe-green/5 scale-[1.02]" : ""
                            }`}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                    >
                        <div className="w-16 h-16 bg-navy-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                        </div>
                        <h3 className="text-white font-semibold mb-1">
                            {uploadedFiles.length > 0 ? `${uploadedFiles.length} file(s) selected` : "Drop Screen Recording"}
                        </h3>
                        <p className="text-gray-500 text-sm mb-4">Supports .mp4, .mov, .png, .jpg</p>
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept="video/*,image/*"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="px-4 py-2 bg-transparent border border-vibe-green text-vibe-green rounded-lg hover:bg-vibe-green/10 transition-all duration-200 text-sm font-medium"
                        >
                            BROWSE FILES
                        </button>
                    </div>

                    {/* File List */}
                    {uploadedFiles.length > 0 && (
                        <div className="glass-card p-4 space-y-2 animate-fade-in">
                            <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Selected Files</p>
                            {uploadedFiles.map((file, i) => (
                                <div key={i} className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-2 text-gray-300">
                                        {file.type.startsWith("video/") ? (
                                            <svg className="w-4 h-4 text-accent-blue" fill="currentColor" viewBox="0 0 24 24">
                                                <path d="M21 3H3c-1.11 0-2 .89-2 2v12a2 2 0 002 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5a2 2 0 00-2-2zm0 14H3V5h18v12zm-5-6l-7 4V7l7 4z" />
                                            </svg>
                                        ) : (
                                            <svg className="w-4 h-4 text-vibe-green" fill="currentColor" viewBox="0 0 24 24">
                                                <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" />
                                            </svg>
                                        )}
                                        <span className="truncate max-w-[300px]">{file.name}</span>
                                        <span className="text-gray-500">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                                    </div>
                                    <button
                                        onClick={() => removeFile(i)}
                                        className="text-gray-500 hover:text-red-400 transition-colors"
                                    >
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Repository URL */}
                    <div className="group">
                        <label className="flex items-center gap-2 text-gray-300 text-sm mb-2">
                            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                            </svg>
                            Repository Target
                        </label>
                        <input
                            type="url"
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            placeholder="https://github.com/username/repo"
                            className="w-full bg-navy-700 border border-navy-500 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue transition-all duration-200 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.2)]"
                        />
                    </div>

                    {/* Deployed URL */}
                    <div>
                        <label className="flex items-center gap-2 text-gray-300 text-sm mb-2">
                            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                            </svg>
                            Deployed URL (Optional)
                        </label>
                        <input
                            type="url"
                            value={deployedUrl}
                            onChange={(e) => setDeployedUrl(e.target.value)}
                            placeholder="https://myapp.vercel.app"
                            className="w-full bg-navy-700 border border-navy-500 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue transition-all duration-200 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.2)]"
                        />
                        <p className="text-gray-500 text-xs mt-1">We&apos;ll automatically capture screenshots from this URL</p>
                    </div>

                    {/* Bug Description */}
                    <div>
                        <label className="flex items-center gap-2 text-gray-300 text-sm mb-2">
                            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                            </svg>
                            Bug Description / Context
                        </label>
                        <textarea
                            value={bugDescription}
                            onChange={(e) => setBugDescription(e.target.value)}
                            placeholder="Describe the vibe that's off... e.g. 'The modal transition feels jerky on Safari'"
                            rows={4}
                            className="w-full bg-navy-700 border border-navy-500 rounded-lg py-3 px-4 text-white placeholder-gray-500 focus:outline-none focus:border-accent-blue transition-all duration-200 focus:shadow-[0_0_0_2px_rgba(59,130,246,0.2)] resize-none"
                        />
                    </div>

                    {/* Analyze Button */}
                    <button
                        onClick={handleAnalyze}
                        disabled={isAnalyzing || !repoUrl}
                        className={`w-full btn-vibe flex items-center justify-center gap-2 transition-all duration-300 ${isAnalyzing ? "opacity-70 cursor-not-allowed scale-[0.98]" : "hover:scale-[1.02]"
                            }`}
                    >
                        {isAnalyzing ? (
                            <>
                                <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                ANALYZING...
                            </>
                        ) : (
                            <>
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                                    <circle cx="12" cy="12" r="4" fill="currentColor" />
                                </svg>
                                ANALYZE VIBE
                            </>
                        )}
                    </button>

                    {/* Analysis Progress Steps */}
                    {isAnalyzing && (
                        <div className="glass-card p-6 animate-fade-in">
                            <h3 className="text-white font-semibold mb-4">Analysis Progress</h3>
                            <div className="space-y-3">
                                {analysisSteps.map((step) => (
                                    <div key={step.id} className="flex items-center gap-3">
                                        {getStepIcon(step.status)}
                                        <span className={`text-sm ${step.status === "completed" ? "text-vibe-green" :
                                                step.status === "processing" ? "text-accent-blue" :
                                                    step.status === "error" ? "text-red-400" :
                                                        "text-gray-500"
                                            }`}>
                                            {step.label}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Analysis Result */}
                    {analysisResult && !isAnalyzing && (
                        <div className={`glass-card p-6 animate-fade-in ${analysisResult.status === "error" ? "border-red-500/30" : "border-vibe-green/30"}`}>
                            {analysisResult.status === "error" ? (
                                <div className="flex items-start gap-3">
                                    <div className="w-8 h-8 bg-red-500/10 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                        <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-red-400 font-semibold text-sm">Analysis Failed</h3>
                                        <p className="text-gray-400 text-sm mt-1">{analysisResult.error}</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-vibe-green animate-pulse" />
                                        <h3 className="text-vibe-green font-semibold text-sm">Analysis Complete</h3>
                                    </div>
                                    <p className="text-gray-300 text-sm">Job ID: <code className="text-accent-blue font-mono text-xs">{analysisResult.job_id}</code></p>
                                    {analysisResult.analysis && (
                                        <div className="bg-navy-700/50 rounded-lg p-3 border-l-2 border-vibe-green">
                                            <p className="text-sm text-gray-300">{analysisResult.analysis.analysis}</p>
                                            <div className="flex items-center gap-3 mt-2">
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${analysisResult.analysis.severity === "High" ? "bg-red-500/20 text-red-400" :
                                                        analysisResult.analysis.severity === "Medium" ? "bg-yellow-500/20 text-yellow-400" :
                                                            "bg-green-500/20 text-green-400"
                                                    }`}>
                                                    {analysisResult.analysis.severity}
                                                </span>
                                                {analysisResult.analysis.fix?.file_path && (
                                                    <span className="text-xs text-gray-500 font-mono">
                                                        {analysisResult.analysis.fix.file_path}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                    {analysisResult.pr_url && (
                                        <a
                                            href={analysisResult.pr_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-2 text-accent-blue hover:text-blue-400 text-sm transition-all duration-200 hover:gap-3"
                                        >
                                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                                            </svg>
                                            View Pull Request →
                                        </a>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Right Panel - System Status */}
                <div className="w-96">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-white">System Status</h2>
                        <div className="flex gap-1">
                            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                            <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" style={{ animationDelay: '0.2s' }} />
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" style={{ animationDelay: '0.4s' }} />
                        </div>
                    </div>

                    <div className="terminal h-96 overflow-hidden relative">
                        {/* Scan line effect */}
                        <div className="absolute inset-0 pointer-events-none overflow-hidden">
                            <div className="w-full h-px bg-vibe-green/20 animate-[scan-line_4s_linear_infinite]" />
                        </div>

                        <div className="terminal-header text-xs">
                            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span className="text-gray-400">sentinel-cli — -zsh — 80x24</span>
                            <span className="ml-auto text-gray-600">v1.0.4</span>
                        </div>

                        <div className="p-4 font-mono text-xs space-y-1 text-gray-400">
                            <div>Last login: Today, {new Date().toLocaleTimeString()} on ttys001</div>
                            <div className="text-vibe-green mt-2">→ ~ ./sentinel-init.sh --verbose</div>
                            <div className="mt-2">[{new Date().toLocaleTimeString()}] Sentinel v1.0.4 initializing...</div>
                            <div className="text-vibe-green">[{new Date().toLocaleTimeString()}] Loading neural modules... DONE</div>
                            <div>[{new Date().toLocaleTimeString()}] GPU acceleration: <span className="text-vibe-green">ENABLED</span></div>
                            <div>[{new Date().toLocaleTimeString()}] Connecting to visual cortex...</div>
                            <div className="text-vibe-green">[{new Date().toLocaleTimeString()}] Connection established.</div>
                            {isAnalyzing && (
                                <>
                                    <div className="text-vibe-green mt-2">→ ~ processing_visual_input...</div>
                                    <div className="text-accent-blue">[{new Date().toLocaleTimeString()}] Analyzing repository structure...</div>
                                    <div className="text-accent-blue">[{new Date().toLocaleTimeString()}] Scanning {uploadedFiles.length} media files...</div>
                                </>
                            )}
                            <div className="text-vibe-green mt-2">→ ~ <span className="animate-pulse">▋</span></div>
                        </div>

                        <div className="absolute bottom-0 left-0 right-0 px-4 py-2 border-t border-navy-600 flex items-center justify-between text-xs text-gray-500">
                            <div className="flex items-center gap-4">
                                <span className="flex items-center gap-1">
                                    <span className="w-2 h-2 rounded-full bg-vibe-green animate-pulse" />
                                    ONLINE
                                </span>
                                <span className="flex items-center gap-1">
                                    <span className="w-2 h-2 rounded-full bg-accent-blue animate-pulse" style={{ animationDelay: '0.3s' }} />
                                    SYNC
                                </span>
                            </div>
                            <span>MEM: {isAnalyzing ? '67%' : '24%'}</span>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
