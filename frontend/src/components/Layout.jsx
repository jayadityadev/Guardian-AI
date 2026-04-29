import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';

const Layout = () => {
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: 'dashboard' },
    { name: 'Location', path: '/location', icon: 'location_on' },
    { name: 'Social Media', path: '/social', icon: 'share' },
    { name: 'Session History', path: '/history', icon: 'history' },
    { name: 'Support', path: '/support', icon: 'help_outline' },
  ];

  return (
    <div className="text-on-surface font-body-md relative antialiased">
      {/* Decorative 3D Blobs */}
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>

      {/* TopNavBar */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/20 dark:border-slate-800/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl flex justify-between items-center px-6 py-4 max-w-full shadow-[0_20px_40px_rgba(0,0,0,0.05)] tracking-tight">
        <div className="flex items-center gap-md">
          <span className="text-xl font-bold tracking-tighter text-slate-900 dark:text-white">SafeWatch</span>
          <div className="hidden md:flex items-center gap-2 bg-surface-container-low px-3 py-1.5 rounded-full border border-white/40">
            <div className="w-2 h-2 rounded-full bg-green-500 pulse-dot"></div>
            <span className="font-label-sm text-label-sm text-on-surface-variant">Monitoring Active</span>
          </div>
        </div>
        <div className="flex items-center gap-md">
          <div className="flex gap-4 items-center">
            <button className="text-slate-500 dark:text-slate-400 hover:bg-white/20 dark:hover:bg-slate-800/50 transition-all duration-200 p-2 rounded-full">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>notifications</span>
            </button>
            <button className="text-slate-500 dark:text-slate-400 hover:bg-white/20 dark:hover:bg-slate-800/50 transition-all duration-200 p-2 rounded-full">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>settings</span>
            </button>
          </div>
          <div className="w-10 h-10 rounded-full bg-primary-fixed overflow-hidden border-2 border-white cursor-pointer hover:scale-95 transition-transform duration-200">
            <img alt="User profile avatar" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBAh6pDaMp3rioURhHxP7quxPiy4aDaxsDM6x2dCwCmBq7uxTMYvcokO8NMqTp0VgPn28SQ8wJbal-VFFWWK1gBZvkmfguFwagvgvuFjQg2zU2bdZJv-2htisby93puygF5XSad4PAnKy9YwE8V8bsgeMJIxGpmo_YZTNfFtW64j-By4-fTcGHdpTufaPnNQzZxA89-MpX1Quj8FJIkdvLTZ1xsv3gbdKitSiTYQS5CQumpSfQR-fr1LLwIpbXJnFQggRs_2PEoWBJ8"/>
          </div>
        </div>
      </nav>

      {/* SideNavBar & Main Content Wrapper */}
      <div className="flex pt-[76px] min-h-screen">
        {/* SideNavBar (Hidden on Mobile) */}
        <aside className="hidden md:flex flex-col h-[calc(100vh-76px)] py-8 gap-2 w-64 fixed left-0 border-r border-white/20 dark:border-slate-800/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-2xl shadow-2xl z-40">
          <div className="px-6 mb-6 flex flex-col gap-1">
            <div className="w-12 h-12 rounded-full bg-surface-variant mb-2 overflow-hidden border-2 border-white shadow-sm">
              <img alt="Parent Account" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDjAOtof9MOl1pID0dJokHcc8dUK_37J-4utm_fBM9zQL8AX0YIQ6cjUdEKOyPDzS-ZkmRHF1kkxvEJVQrAgTghtgRWCy58Atj1b5jkIljpGurbSUhnyWLUXhOdH3l7dd2-meEj7INc7oG8mo7NDcycTfoAEItBBya2kIM81JOQQkMxjkitoibrz5acfRBnnpr1VMc6ZRAPrMwtaiLUPUbh0HCH7GNwbHLeUUterGh3PxM4fqSOpJmaJIzbvwUiQuVxRjXCpkBlqGKp"/>
            </div>
            <h2 className="font-headline-md text-headline-md text-on-surface">SafeWatch Pro</h2>
            <p className="font-label-sm text-label-sm text-on-surface-variant">Vigilance Active</p>
          </div>
          
          <nav className="flex-1 flex flex-col gap-2 text-sm font-medium">
            {navLinks.map(link => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl mx-2 hover:translate-x-1 transition-transform duration-200 ${isActive ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300' : 'text-slate-600 dark:text-slate-400 hover:text-indigo-500'}`}
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}>{link.icon}</span>
                  {link.name}
                </Link>
              );
            })}
          </nav>

          <div className="px-4 mt-auto flex flex-col gap-4">
            <button className="w-full py-3 bg-primary text-on-primary rounded-lg font-label-md text-label-md shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5 transition-all duration-200">
              Upgrade Safety
            </button>
            <Link to="/logout" className="flex items-center gap-3 px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-indigo-500 hover:translate-x-1 transition-transform duration-200">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>logout</span>
              <span className="font-label-md text-label-md">Logout</span>
            </Link>
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
