import { Outlet, Link, useLocation } from 'react-router-dom';
import DotField from './DotField';
import { AnimatedThemeToggler } from "@/components/ui/animated-theme-toggler";

const Layout = () => {
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: 'dashboard' },
    { name: 'Upload', path: '/upload', icon: 'upload' },
    { name: 'Location', path: '/location', icon: 'location_on' },
    { name: 'Social Media', path: '/social', icon: 'share' },
    { name: 'Session History', path: '/history', icon: 'history' },
    { name: 'Support', path: '/support', icon: 'help_outline' },
  ];

  return (
    <div className="text-on-surface font-body-md relative antialiased">
      <DotField className="absolute inset-0 -z-10 pointer-events-none" dotSpacing={14} />
      {/* Decorative 3D Blobs */}
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>

      {/* TopNavBar */}
      <nav className="fixed top-0 w-full z-50 border-b border-border/30 bg-background/70 backdrop-blur-xl flex justify-between items-center px-6 py-4 max-w-full shadow-[0_20px_40px_rgba(0,0,0,0.05)] tracking-tight">
        <div className="flex items-center gap-md">
          <span className="text-xl font-bold tracking-tighter text-foreground">SafeWatch</span>
          <div className="hidden md:flex items-center gap-2 bg-muted/60 px-3 py-1.5 rounded-full border border-border/40">
            <div className="w-2 h-2 rounded-full bg-green-500 pulse-dot"></div>
            <span className="font-label-sm text-label-sm text-muted-foreground">Monitoring Active</span>
          </div>
        </div>
        <div className="flex items-center gap-md">
          <div className="flex gap-4 items-center">
            <button className="text-muted-foreground hover:bg-muted/50 transition-all duration-200 p-2 rounded-full">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>notifications</span>
            </button>
            <button className="text-muted-foreground hover:bg-muted/50 transition-all duration-200 p-2 rounded-full">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>settings</span>
            </button>
          </div>
          <div className="w-10 h-10 rounded-full bg-secondary overflow-hidden border-2 border-border cursor-pointer hover:scale-95 transition-transform duration-200">
            <img alt="User profile avatar" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBAh6pDaMp3rioURhHxP7quxPiy4aDaxsDM6x2dCwCmBq7uxTMYvcokO8NMqTp0VgPn28SQ8wJbal-VFFWWK1gBZvkmfguFwagvgvuFjQg2zU2bdZJv-2htisby93puygF5XSad4PAnKy9YwE8V8bsgeMJIxGpmo_YZTNfFtW64j-By4-fTcGHdpTufaPnNQzZxA89-MpX1Quj8FJIkdvLTZ1xsv3gbdKitSiTYQS5CQumpSfQR-fr1LLwIpbXJnFQggRs_2PEoWBJ8" />
          </div>
        </div>
      </nav>

      {/* SideNavBar & Main Content Wrapper */}
      <div className="flex pt-[76px] min-h-screen">
        {/* SideNavBar (Hidden on Mobile) */}
        <aside className="hidden md:flex flex-col h-[calc(100vh-76px)] py-8 gap-2 w-64 fixed left-0 border-r border-border/30 bg-background/70 backdrop-blur-2xl shadow-2xl z-40">
          <div className="px-6 mb-6 flex flex-col gap-1">
            <div className="w-12 h-12 rounded-full bg-muted mb-2 overflow-hidden border-2 border-border shadow-sm">
              <img alt="Parent Account" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDjAOtof9MOl1pID0dJokHcc8dUK_37J-4utm_fBM9zQL8AX0YIQ6cjUdEKOyPDzS-ZkmRHF1kkxvEJVQrAgTghtgRWCy58Atj1b5jkIljpGurbSUhnyWLUXhOdH3l7dd2-meEj7INc7oG8mo7NDcycTfoAEItBBya2kIM81JOQQkMxjkitoibrz5acfRBnnpr1VMc6ZRAPrMwtaiLUPUbh0HCH7GNwbHLeUUterGh3PxM4fqSOpJmaJIzbvwUiQuVxRjXCpkBlqGKp" />
            </div>
            <h2 className="font-headline-md text-headline-md text-foreground">GUARDIAN-AI</h2>
            <p className="font-label-sm text-label-sm text-muted-foreground">Vigilance Active</p>
          </div>

          <nav className="flex-1 flex flex-col gap-2 text-sm font-medium">
            {navLinks.map(link => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl mx-2 hover:translate-x-1 transition-transform duration-200 ${isActive ? 'bg-primary/10 text-primary font-semibold' : 'text-muted-foreground hover:text-primary'}`}
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}>{link.icon}</span>
                  {link.name}
                </Link>
              );
            })}
          </nav>

          {/* ✅ Theme Toggle — pinned to sidebar bottom */}
          <div className="px-6 pt-4 border-t border-border/30 flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-medium">Theme</span>
            <AnimatedThemeToggler />
          </div>
        </aside>

        {/* Main Canvas */}
        <main className="flex-1 md:ml-64 p-6 lg:p-lg max-w-[1440px] mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
