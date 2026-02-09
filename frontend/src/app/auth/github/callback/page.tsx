"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

/**
 * GitHub OAuth Callback Page
 *
 * After the user authorises on GitHub, GitHub redirects here with a ?code= param.
 * We send that code to our backend which exchanges it for a JWT.
 * Then we store that JWT and redirect to /dashboard.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function GitHubCallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const code = searchParams.get("code");
        if (!code) {
            setError("No authorization code received from GitHub.");
            return;
        }

        const exchangeCode = async () => {
            try {
                const res = await fetch(
                    `${API_BASE}/api/v1/auth/github/callback?code=${encodeURIComponent(code)}`
                );

                if (!res.ok) {
                    const data = await res.json().catch(() => ({ detail: "OAuth exchange failed" }));
                    setError(data.detail ?? "Failed to authenticate with GitHub");
                    return;
                }

                const data = await res.json();
                localStorage.setItem("sentinel_token", data.access_token);
                router.push("/dashboard");
            } catch {
                setError("Network error while authenticating. Please try again.");
            }
        };

        exchangeCode();
    }, [searchParams, router]);

    return (
        <main className="min-h-screen bg-gradient-to-b from-navy-900 to-navy-800 flex flex-col items-center justify-center p-8">
            <div className="w-full max-w-md glass-card p-8 text-center">
                {error ? (
                    <>
                        <div className="w-16 h-16 mx-auto mb-4 bg-red-500/10 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </div>
                        <h1 className="text-xl font-bold text-white mb-2">Authentication Failed</h1>
                        <p className="text-red-400 text-sm mb-6">{error}</p>
                        <button
                            onClick={() => router.push("/login")}
                            className="btn-primary"
                        >
                            Back to Login
                        </button>
                    </>
                ) : (
                    <>
                        <div className="w-16 h-16 mx-auto mb-4 bg-accent-blue/10 rounded-full flex items-center justify-center">
                            <svg className="w-8 h-8 text-accent-blue animate-spin" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                        </div>
                        <h1 className="text-xl font-bold text-white mb-2">Authenticating with GitHub...</h1>
                        <p className="text-gray-400 text-sm">Please wait while we complete your sign-in.</p>
                    </>
                )}
            </div>
        </main>
    );
}

export default function GitHubCallbackPage() {
    return (
        <Suspense fallback={
            <main className="min-h-screen bg-gradient-to-b from-navy-900 to-navy-800 flex flex-col items-center justify-center p-8">
                <div className="w-full max-w-md glass-card p-8 text-center">
                    <div className="w-16 h-16 mx-auto mb-4 bg-accent-blue/10 rounded-full flex items-center justify-center">
                        <svg className="w-8 h-8 text-accent-blue animate-spin" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                    </div>
                    <h1 className="text-xl font-bold text-white mb-2">Loading...</h1>
                </div>
            </main>
        }>
            <GitHubCallbackContent />
        </Suspense>
    );
}
