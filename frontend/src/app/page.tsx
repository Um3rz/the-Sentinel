import Link from "next/link";

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-b from-navy-900 to-navy-800">
            {/* Navigation */}
            <nav className="flex items-center justify-between px-8 py-4 border-b border-navy-700/50">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-accent-blue rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" />
                            <circle cx="12" cy="12" r="4" fill="currentColor" />
                        </svg>
                    </div>
                    <span className="font-bold text-lg text-white">The Sentinel</span>
                </div>



                <div className="flex items-center gap-4">
                    <Link href="/login" className="text-sm text-gray-300 hover:text-white transition-colors">
                        Log in
                    </Link>
                    <Link href="/dashboard" className="btn-primary text-sm">
                        Get Started
                    </Link>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="pt-20 pb-16 px-8 text-center max-w-4xl mx-auto">
                <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 leading-tight">
                    Engineering the{" "}
                    <span className="text-accent-blue">Perfect Vibe.</span>
                </h1>

                <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
                    AI-powered visual bug detection and automated fixes for frontend teams.
                    Ship pixel-perfect UIs without the back-and-forth.
                </p>

                <div className="flex items-center justify-center gap-4">
                    <Link href="/dashboard" className="btn-primary flex items-center gap-2">
                        Get Started
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                    </Link>
                    <Link href="/docs" className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors border border-navy-500 rounded-lg px-6 py-3">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        Read the Docs
                    </Link>
                </div>


            </section>

            {/* Demo Terminal */}
            <section className="px-8 pb-16 max-w-5xl mx-auto">
                <div className="terminal overflow-hidden">
                    <div className="terminal-header">
                        <div className="flex gap-2">
                            <div className="terminal-dot bg-red-500"></div>
                            <div className="terminal-dot bg-yellow-500"></div>
                            <div className="terminal-dot bg-green-500"></div>
                        </div>
                        <span className="text-gray-500 text-xs ml-4">sentinel-cli run analysis</span>
                    </div>

                    <div className="flex">
                        {/* Code Section */}
                        <div className="flex-1 p-6 border-r border-navy-600">
                            <div className="text-xs text-gray-500 mb-2">src/components/Button.tsx</div>
                            <div className="space-y-1 font-mono text-sm">
                                <div className="text-gray-400">export const Button = () =&gt; {"{"}</div>
                                <div className="text-gray-400 pl-4">return (</div>
                                <div className="pl-8 text-red-400 line-through">&lt;div className=&quot;p-2 bg-blue-500&quot;&gt;</div>
                                <div className="pl-8 text-vibe-green">&lt;button className=&quot;px-4 py-2 bg-primary rounded&quot;&gt;</div>
                                <div className="pl-12 text-gray-300">Submit</div>
                                <div className="pl-8 text-gray-400">&lt;/button&gt;</div>
                                <div className="pl-4 text-gray-400">)</div>
                                <div className="text-gray-400">{"}"}</div>
                            </div>
                            <div className="mt-4 inline-block px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded">
                                Bug Detected
                            </div>
                        </div>

                        {/* Preview Section */}
                        <div className="w-64 p-6">
                            <div className="text-xs text-gray-500 mb-4 text-right">Preview</div>
                            <div className="space-y-4">
                                <div>
                                    <div className="text-xs text-gray-500 mb-2">BEFORE</div>
                                    <button className="w-full bg-blue-500 px-4 py-2 text-white rounded-md">
                                        Submit
                                    </button>
                                </div>
                                <div>
                                    <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                                        AFTER <span className="w-2 h-2 bg-vibe-green rounded-full"></span>
                                    </div>
                                    <button className="w-full bg-accent-blue px-4 py-2 text-white rounded-lg font-medium">
                                        Submit
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="px-8 py-16 max-w-5xl mx-auto">
                <h2 className="text-3xl font-bold text-white mb-4">Automated UI Perfection</h2>
                <p className="text-gray-400 mb-12 max-w-xl">
                    Detect visual regressions, fix CSS issues automatically, and merge with confidence.
                    Our AI understands your design system.
                </p>

                <div className="grid md:grid-cols-3 gap-6">
                    {/* Feature 1 */}
                    <div className="glass-card p-6">
                        <div className="w-10 h-10 bg-accent-blue/20 rounded-lg flex items-center justify-center mb-4">
                            <svg className="w-5 h-5 text-accent-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                        </div>
                        <h3 className="text-white font-semibold mb-2">Pixel-Perfect Detection</h3>
                        <p className="text-gray-400 text-sm">
                            Identify visual bugs down to the sub-pixel level before they reach production.
                            Our engine compares rendering across all modern browsers.
                        </p>
                    </div>

                    {/* Feature 2 */}
                    <div className="glass-card p-6">
                        <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <h3 className="text-white font-semibold mb-2">Auto-Fix PRs</h3>
                        <p className="text-gray-400 text-sm">
                            The Sentinel doesn&apos;t just find bugs; it fixes them.
                            We automatically generate pull requests with the exact CSS adjustments needed.
                        </p>
                    </div>

                    {/* Feature 3 */}
                    <div className="glass-card p-6">
                        <div className="w-10 h-10 bg-vibe-green/20 rounded-lg flex items-center justify-center mb-4">
                            <svg className="w-5 h-5 text-vibe-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h3 className="text-white font-semibold mb-2">CLI Integration</h3>
                        <p className="text-gray-400 text-sm">
                            Seamlessly integrate with your existing CI/CD pipeline.
                            Works with GitHub Actions, GitLab CI, and CircleCI out of the box.
                        </p>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="px-8 py-20 text-center">
                <h2 className="text-3xl font-bold text-white mb-4">Ready to ship flawless UIs?</h2>

                <div className="flex items-center justify-center gap-4">
                    <Link href="/signup" className="btn-primary">Start for free</Link>
                    <Link href="/contact" className="border border-navy-500 rounded-lg px-6 py-3 text-white hover:bg-navy-700 transition-colors">
                        Contact Sales
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-navy-700/50 px-8 py-8">
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-accent-blue rounded-full flex items-center justify-center">
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                        </div>
                        <span className="font-semibold text-white">The Sentinel</span>
                    </div>
                    <p className="text-gray-500 text-sm">© 2024 The Sentinel. All rights reserved.</p>
                    <div className="flex items-center gap-4 text-gray-500">
                        <a href="#" className="hover:text-white transition-colors">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" /></svg>
                        </a>
                        <a href="#" className="hover:text-white transition-colors">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" /></svg>
                        </a>
                    </div>
                </div>
            </footer>
        </main>
    );
}
