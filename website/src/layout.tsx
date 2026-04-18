import type { ReactNode } from "react"
import { SidebarProvider } from "./components/ui/sidebar"

type LayoutProps = {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <SidebarProvider>
      <main className="flex w-full justify-center">{children}</main>
    </SidebarProvider>
  )
}
