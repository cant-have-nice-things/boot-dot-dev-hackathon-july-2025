import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/about')({
    component: AboutComponent,
})

function AboutComponent() {
    return (
        <div className="container mx-auto px-4 py-16">
            <div className="max-w-3xl mx-auto space-y-8">
                {/* Header */}
                <div className="text-center space-y-4">
                    <h1 className="text-4xl font-bold tracking-tight">About HackApp</h1>
                    <p className="text-xl text-muted-foreground">
                        A modern React template designed for rapid prototyping and development
                    </p>
                </div>

                {/* Content */}
                <div className="prose prose-gray dark:prose-invert max-w-none space-y-6">
                    <div className="bg-card p-6 rounded-lg border">
                        <h2 className="text-2xl font-semibold mb-4">What is HackApp?</h2>
                        <p className="text-muted-foreground leading-relaxed">
                            HackApp is a production-ready React template built with modern tools and best practices.
                            It provides a solid foundation for building web applications with TypeScript, TanStack Router,
                            Tailwind CSS, and shadcn/ui components.
                        </p>
                    </div>

                    <div className="bg-card p-6 rounded-lg border">
                        <h2 className="text-2xl font-semibold mb-4">Built With</h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <h3 className="font-medium">Frontend</h3>
                                <ul className="text-sm text-muted-foreground space-y-1">
                                    <li>• React 19</li>
                                    <li>• TypeScript</li>
                                    <li>• TanStack Router</li>
                                    <li>• Tailwind CSS</li>
                                </ul>
                            </div>
                            <div className="space-y-2">
                                <h3 className="font-medium">Development</h3>
                                <ul className="text-sm text-muted-foreground space-y-1">
                                    <li>• Vite</li>
                                    <li>• ESLint</li>
                                    <li>• Prettier</li>
                                    <li>• shadcn/ui</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div className="bg-card p-6 rounded-lg border">
                        <h2 className="text-2xl font-semibold mb-4">Features</h2>
                        <ul className="space-y-2 text-muted-foreground">
                            <li>✅ Type-safe routing with TanStack Router</li>
                            <li>✅ Beautiful UI components with shadcn/ui</li>
                            <li>✅ Dark mode support</li>
                            <li>✅ Responsive design</li>
                            <li>✅ Modern development tooling</li>
                            <li>✅ Production-ready configuration</li>
                        </ul>
                    </div>

                    <div className="bg-card p-6 rounded-lg border">
                        <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
                        <p className="text-muted-foreground mb-4">
                            This template is designed to be easily customizable. Simply update the content,
                            add your routes, and start building your application.
                        </p>
                        <div className="bg-muted p-4 rounded-md">
                            <code className="text-sm">
                                npm run dev
                            </code>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}