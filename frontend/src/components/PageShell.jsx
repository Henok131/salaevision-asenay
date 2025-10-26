import { Navbar } from './Navbar'

export function PageShell({
  children,
  header = false,
  sidebar = false,
  sidebarContent = null,
  className = '',
  title,
  description,
  actions,
  showSidebar,
}) {
  const renderHeader = () => {
    if (!title && !description && !actions) return null;
    return (
      <div className="mb-6 md:mb-8">
        <div className="flex items-start justify-between gap-4 min-w-0">
          <div className="min-w-0">
            {title && (
              <h1 className="text-3xl md:text-4xl font-bold text-text-primary truncate" aria-live="polite">{title}</h1>
            )}
            {description && (
              <p className="text-sm md:text-base leading-relaxed text-text-secondary mt-1 truncate">{description}</p>
            )}
          </div>
          {actions && (
            <div className="flex-shrink-0 flex items-center gap-2">{actions}</div>
          )}
        </div>
      </div>
    )
  }

  const shouldShowSidebar = typeof showSidebar === 'boolean' ? showSidebar : sidebar

  return (
    <div className="min-h-screen bg-dark-bg pt-16">
      {header && <Navbar />}
      <div className="flex">
        {shouldShowSidebar && sidebarContent}
        <main className="flex-1" role="main">
          <div className={`max-w-screen-2xl 2xl:max-w-[1440px] mx-auto px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8 ${className}`}>
            {renderHeader()}
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default PageShell
