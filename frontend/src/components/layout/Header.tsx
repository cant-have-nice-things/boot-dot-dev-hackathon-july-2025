import { Link } from '@tanstack/react-router'

export function Header() {
  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo/Brand */}
          <div className="flex items-center space-x-4">
            <Link
              to="/"
              className="text-2xl font-bold"
              style={{
                background: 'linear-gradient(to right, #0ea5e9, #06b6d4)',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                color: 'transparent',
              }}
            >
              Nice Things
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              to="/"
              className="text-sm font-medium transition-colors hover:text-primary [&.active]:text-primary"
              activeProps={{ className: 'text-primary' }}
              activeOptions={{ exact: true }}
            >
              Home
            </Link>
            <Link
              to="/about"
              className="text-sm font-medium transition-colors hover:text-primary [&.active]:text-primary"
              activeProps={{ className: 'text-primary' }}
            >
              About
            </Link>
          </nav>

          {/* Action Button - hidden for now since the main page will have the form */}
          <div className="flex items-center">
            {/* You can add a user menu or other actions here later */}
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-4">
          <nav className="flex items-center space-x-4">
            <Link
              to="/"
              className="text-sm font-medium transition-colors hover:text-primary [&.active]:text-primary"
              activeProps={{ className: 'text-primary' }}
              activeOptions={{ exact: true }}
            >
              Home
            </Link>
            <Link
              to="/about"
              className="text-sm font-medium transition-colors hover:text-primary [&.active]:text-primary"
              activeProps={{ className: 'text-primary' }}
            >
              About
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
