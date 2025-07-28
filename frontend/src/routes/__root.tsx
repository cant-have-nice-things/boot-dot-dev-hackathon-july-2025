import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { Header } from '../components/layout/Header'
import { Footer } from '../components/layout/Footer'
import { Toaster } from '@/components/ui/toaster.tsx'

export const Route = createRootRoute({
  component: () => (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1">
        <Outlet />
        <Toaster />
      </main>
    </div>
  ),
})
