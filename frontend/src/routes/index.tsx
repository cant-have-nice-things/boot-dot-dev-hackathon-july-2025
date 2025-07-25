import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
    component: Index,
})

function Index() {
    return (
        <div className="container mx-auto px-4 py-16">
            <div className="max-w-4xl mx-auto text-center space-y-12">
                {/* Hero Section */}
                <div className="space-y-6">
                    <h1 className="text-4xl font-bold tracking-tight lg:text-6xl">
                        Welcome to{' '}
                        <span
                            style={{
                                background: 'linear-gradient(to right, #0ea5e9, #06b6d4)',
                                WebkitBackgroundClip: 'text',
                                backgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                color: 'transparent',
                            }}
                        >
              HackApp
            </span>
                    </h1>
                    <p className="text-xl leading-8 text-muted-foreground max-w-2xl mx-auto">
                        A modern web application built with React, TypeScript, and TanStack Router.
                        Ready to be customized for your next great idea.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-8">
                    <div className="group p-8 border rounded-lg hover:shadow-lg transition-all duration-300 hover:scale-105">
                        <div className="space-y-4">
                            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">⚡</span>
                            </div>
                            <h3 className="text-xl font-semibold">Fast Development</h3>
                            <p className="text-muted-foreground">
                                Modern tooling with Vite, TypeScript, and TanStack Router for rapid development
                            </p>
                            <div className="pt-2">
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                  Ready to build →
                </span>
                            </div>
                        </div>
                    </div>

                    <div className="group p-8 border rounded-lg hover:shadow-lg transition-all duration-300 hover:scale-105">
                        <div className="space-y-4">
                            <div className="w-12 h-12 bg-cyan-100 dark:bg-cyan-900/20 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">🎨</span>
                            </div>
                            <h3 className="text-xl font-semibold">Beautiful UI</h3>
                            <p className="text-muted-foreground">
                                Clean design with Tailwind CSS and shadcn/ui components for a polished look
                            </p>
                            <div className="pt-2">
                <span className="text-sm font-medium text-cyan-600 dark:text-cyan-400">
                  Customizable →
                </span>
                            </div>
                        </div>
                    </div>

                    <div className="group p-8 border rounded-lg hover:shadow-lg transition-all duration-300 hover:scale-105">
                        <div className="space-y-4">
                            <div className="w-12 h-12 bg-teal-100 dark:bg-teal-900/20 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">🚀</span>
                            </div>
                            <h3 className="text-xl font-semibold">Production Ready</h3>
                            <p className="text-muted-foreground">
                                ESLint, Prettier, and TypeScript configured for clean, maintainable code
                            </p>
                            <div className="pt-2">
                <span className="text-sm font-medium text-teal-600 dark:text-teal-400">
                  Deploy now →
                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* CTA Section */}
                <div className="pt-8">
                    <p className="text-lg text-muted-foreground">
                        Start building your next project with this modern React template.
                    </p>
                </div>
            </div>
        </div>
    )
}