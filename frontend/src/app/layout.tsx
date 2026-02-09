import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./context/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "The Sentinel | Visual Vibe Auditor",
    description: "AI-powered visual bug detection and automated fixes for frontend teams. Ship pixel-perfect UIs without the back-and-forth.",
    keywords: ["visual QA", "AI", "frontend", "bug detection", "automated fixes"],
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <AuthProvider>{children}</AuthProvider>
            </body>
        </html>
    );
}
