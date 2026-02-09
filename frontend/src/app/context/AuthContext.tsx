"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface User {
    id: string;
    email: string;
    full_name: string | null;
    github_username: string | null;
    is_verified: boolean;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, fullName?: string) => Promise<void>;
    loginWithGithub: () => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/* ------------------------------------------------------------------ */
/*  Provider                                                           */
/* ------------------------------------------------------------------ */

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    /* ---- Persist / hydrate token from localStorage ---- */
    useEffect(() => {
        const stored = localStorage.getItem("sentinel_token");
        if (stored) {
            setToken(stored);
        } else {
            setIsLoading(false);
        }
    }, []);

    /* ---- Fetch current user whenever token changes ---- */
    const fetchUser = useCallback(async (jwt: string) => {
        try {
            const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
                headers: { Authorization: `Bearer ${jwt}` },
            });
            if (res.ok) {
                const data: User = await res.json();
                setUser(data);
            } else {
                // Token invalid – clear it
                localStorage.removeItem("sentinel_token");
                setToken(null);
                setUser(null);
            }
        } catch {
            // Network error – keep token for retry
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        if (token) {
            fetchUser(token);
        }
    }, [token, fetchUser]);

    /* ---- Email/Password Login ---- */
    const login = async (email: string, password: string) => {
        const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: "Login failed" }));
            throw new Error(err.detail ?? "Login failed");
        }

        const data = await res.json();
        localStorage.setItem("sentinel_token", data.access_token);
        setToken(data.access_token);
        router.push("/dashboard");
    };

    /* ---- Email/Password Registration ---- */
    const register = async (email: string, password: string, fullName?: string) => {
        const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password, full_name: fullName || null }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: "Registration failed" }));
            throw new Error(err.detail ?? "Registration failed");
        }

        // Auto-login after successful registration
        await login(email, password);
    };

    /* ---- GitHub OAuth ---- */
    const loginWithGithub = () => {
        window.location.href = `${API_BASE}/api/v1/auth/github`;
    };

    /* ---- Logout ---- */
    const logout = () => {
        localStorage.removeItem("sentinel_token");
        setToken(null);
        setUser(null);
        router.push("/login");
    };

    return (
        <AuthContext.Provider
            value={{ user, token, isLoading, login, register, loginWithGithub, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}

/* ------------------------------------------------------------------ */
/*  Hook                                                               */
/* ------------------------------------------------------------------ */

export function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return ctx;
}
