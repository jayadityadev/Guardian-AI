

const Support = () => {
  return (
    <>
      {/* Hero Search Section */}
      <div className="mb-12 text-center max-w-3xl mx-auto">
        <h1 className="font-display-sm text-display-sm text-on-surface mb-4">How can we help you?</h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant mb-8">Search our knowledge base or browse categories below for quick answers.</p>
        <div className="relative w-full max-w-2xl mx-auto shadow-[0_20px_40px_rgba(0,0,0,0.05)] rounded-full">
          <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline">search</span>
          <input className="w-full bg-card/80 backdrop-blur-md border border-border/40 rounded-full py-4 pl-12 pr-6 font-body-lg text-on-surface shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)] focus:outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/10 transition-all placeholder:text-outline-variant" placeholder="Search for 'location tracking' or 'privacy'" type="text" />
        </div>
      </div>

      {/* Category Grid (Bento Style) */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-12">
        {/* Large Category Tile */}
        <div className="md:col-span-8 glass-card rounded-[1.5rem] p-8 hover:shadow-[0_25px_50px_rgba(0,0,0,0.06)] transition-all duration-300 group cursor-pointer relative overflow-hidden">
          <div className="absolute right-[-10%] top-[-10%] w-64 h-64 bg-secondary-container/30 rounded-full blur-3xl group-hover:bg-secondary-container/50 transition-colors"></div>
          <div className="w-14 h-14 bg-secondary-container rounded-xl flex items-center justify-center mb-6 shadow-sm">
            <span className="material-symbols-outlined text-on-secondary-container" style={{ fontVariationSettings: "'FILL' 1", fontSize: '28px' }}>rocket_launch</span>
          </div>
          <h3 className="font-headline-lg text-headline-lg text-on-surface mb-3">Getting Started</h3>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-md">Master the basics. Learn how to connect devices, set up your first safe zones, and configure notifications for maximum peace of mind.</p>
          <div className="mt-8 flex gap-2 flex-wrap">
            <span className="px-3 py-1 bg-surface-variant text-on-surface-variant rounded-full font-label-sm text-label-sm">Device Pairing</span>
            <span className="px-3 py-1 bg-surface-variant text-on-surface-variant rounded-full font-label-sm text-label-sm">Account Setup</span>
          </div>
        </div>

        {/* Small Category Tile 1 */}
        <div className="md:col-span-4 glass-card rounded-[1.5rem] p-8 hover:-translate-y-1 transition-transform duration-300 cursor-pointer flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 bg-primary-container/20 rounded-xl flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-primary-container" style={{ fontVariationSettings: "'FILL' 1" }}>shield_lock</span>
            </div>
            <h3 className="font-headline-md text-headline-md text-on-surface mb-2">Privacy &amp; Data</h3>
            <p className="font-body-md text-body-md text-on-surface-variant">Understand our strict data encryption and how your family's information is protected.</p>
          </div>
          <span className="material-symbols-outlined text-outline self-end mt-4">arrow_forward</span>
        </div>

        {/* Small Category Tile 2 */}
        <div className="md:col-span-4 glass-card rounded-[1.5rem] p-8 hover:-translate-y-1 transition-transform duration-300 cursor-pointer flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 bg-tertiary-container/20 rounded-xl flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-tertiary-container" style={{ fontVariationSettings: "'FILL' 1" }}>settings_alert</span>
            </div>
            <h3 className="font-headline-md text-headline-md text-on-surface mb-2">Technical Support</h3>
            <p className="font-body-md text-body-md text-on-surface-variant">Troubleshoot offline devices, sync issues, and GPS accuracy.</p>
          </div>
          <span className="material-symbols-outlined text-outline self-end mt-4">arrow_forward</span>
        </div>

        {/* Wide Info Tile */}
        <div className="md:col-span-8 bg-muted rounded-[1.5rem] p-8 border border-border/30 shadow-sm flex items-center justify-between gap-6 overflow-hidden relative">
          <div className="z-10 relative">
            <h3 className="font-headline-md text-headline-md text-on-surface mb-2">Billing &amp; Subscription</h3>
            <p className="font-body-md text-body-md text-on-surface-variant">Manage your SafeWatch Pro plan, view invoices, and update payment methods.</p>
          </div>
          <div className="w-16 h-16 bg-card rounded-full flex items-center justify-center shadow-md z-10 shrink-0">
            <span className="material-symbols-outlined text-primary">credit_card</span>
          </div>
        </div>
      </div>

      {/* Contact Section */}
      <div className="mt-16">
        <h2 className="font-headline-lg text-headline-lg text-on-surface mb-6 border-b border-outline-variant/30 pb-4">Still need help?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-primary/5 border border-primary/20 rounded-[1.25rem] p-6 flex items-start gap-4 hover:bg-primary/10 transition-colors cursor-pointer">
            <div className="w-12 h-12 bg-primary text-on-primary rounded-full flex items-center justify-center shadow-lg shrink-0">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>chat</span>
            </div>
            <div>
              <h4 className="font-headline-md text-headline-md text-on-surface mb-1">Live Chat Support</h4>
              <p className="font-body-md text-body-md text-on-surface-variant mb-4">Connect with a safety specialist instantly. Typical response time: <span className="font-medium text-primary">under 2 mins</span>.</p>
              <button className="font-label-md text-label-md text-primary font-semibold flex items-center gap-1">Start Chat <span className="material-symbols-outlined text-sm">arrow_right_alt</span></button>
            </div>
          </div>

          <div className="glass-card rounded-[1.25rem] p-6 flex items-start gap-4 hover:bg-card/80 transition-colors cursor-pointer">
            <div className="w-12 h-12 bg-surface-variant text-on-surface-variant rounded-full flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined">mail</span>
            </div>
            <div>
              <h4 className="font-headline-md text-headline-md text-on-surface mb-1">Email Us</h4>
              <p className="font-body-md text-body-md text-on-surface-variant mb-4">Send us a detailed message. We aim to resolve all email inquiries within 24 hours.</p>
              <button className="font-label-md text-label-md text-on-surface font-semibold flex items-center gap-1">support@safewatch.app</button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Support;
