import { Navbar } from './Navbar'

export function PageShell({
  children,
  header = false,
  sidebar = false,
  sidebarContent = null,
  className = ''
}) {
  return (
    <div className="min-h-screen bg-dark-bg pt-16">
      {header && <Navbar />}
      <div className="flex">
        {sidebar && sidebarContent}
        <main className="flex-1">
          <div className={`max-w-screen-2xl 2xl:max-w-[1440px] mx-auto px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8 ${className}`}>
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default PageShell
