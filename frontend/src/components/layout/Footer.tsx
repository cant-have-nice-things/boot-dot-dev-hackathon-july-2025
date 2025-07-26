import { Link } from '@tanstack/react-router'

export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-3">
            <h3
              className="text-lg font-semibold"
              style={{
                background: 'linear-gradient(to right, #0ea5e9, #06b6d4)',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                color: 'transparent',
              }}
            >
              HackApp
            </h3>
            <p className="text-sm text-muted-foreground">
              A modern React template for rapid development and deployment.
            </p>
          </div>

          {/* Features */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Features</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>React + TypeScript</li>
              <li>TanStack Router</li>
              <li>Tailwind CSS</li>
              <li>shadcn/ui</li>
            </ul>
          </div>

          {/* Navigation */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Navigation</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/" className="hover:text-primary transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-primary transition-colors">
                  About
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a
                  href="https://tanstack.com/router"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  TanStack Router
                </a>
              </li>
              <li>
                <a
                  href="https://tailwindcss.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  Tailwind CSS
                </a>
              </li>
              <li>
                <a
                  href="https://ui.shadcn.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors"
                >
                  shadcn/ui
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-8 pt-6 border-t text-center text-sm text-muted-foreground">
          <p>
            &copy; {new Date().getFullYear()} HackApp. Built with React, TypeScript, and modern
            tools.
          </p>
        </div>
      </div>
    </footer>
  )
}
