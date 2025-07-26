import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import { Header } from '../components/layout/Header'
import { Footer } from '../components/layout/Footer'

export const Route = createRootRoute({
  component: () => (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      {process.env.NODE_ENV === 'development' && <TanStackRouterDevtools />}
    </div>
  ),
})
