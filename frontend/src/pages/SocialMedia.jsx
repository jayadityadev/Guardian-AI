import React from 'react';

const SocialMedia = () => {
  return (
    <>
      <header className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="font-display-sm text-display-sm text-on-background">Social Media Intelligence</h2>
          <p className="font-body-md text-body-md text-on-surface-variant mt-1">Real-time analysis of connected platforms.</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-high text-on-surface font-label-sm">
            <span className="w-2 h-2 rounded-full bg-primary"></span>
            Syncing...
          </span>
          <span className="font-label-sm text-label-sm text-on-surface-variant">Last updated: Just now</span>
        </div>
      </header>

      {/* Platform Overview Bento Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Instagram Card */}
        <div className="glass-card rounded-xl p-6 ambient-shadow flex flex-col h-full relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-pink-500/10 to-orange-400/10 rounded-full blur-2xl"></div>
          <div className="flex justify-between items-start mb-4 relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center">
                <span className="material-symbols-outlined text-primary">photo_camera</span>
              </div>
              <div>
                <h3 className="font-headline-md text-headline-md text-on-background">Instagram</h3>
                <p className="font-label-sm text-label-sm text-on-surface-variant">@emma_watches</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-md bg-secondary-container/30 text-on-secondary-container font-label-sm text-label-sm flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">check_circle</span> Connected
            </span>
          </div>
          <div className="mt-auto space-y-4 relative z-10">
            <div className="flex justify-between items-baseline border-b border-outline-variant/20 pb-2">
              <span className="text-sm text-on-surface-variant">Messages Scanned</span>
              <span className="font-headline-md text-headline-md text-on-background">1,240</span>
            </div>
            <div className="flex justify-between items-baseline border-b border-outline-variant/20 pb-2">
              <span className="text-sm text-on-surface-variant">New Followers</span>
              <span className="font-headline-md text-headline-md text-on-background">12</span>
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="font-label-md text-label-md text-on-background">Risk Level</span>
              <span className="px-2 py-0.5 rounded text-secondary bg-secondary-container/20 font-label-sm text-label-sm">Low</span>
            </div>
          </div>
        </div>

        {/* TikTok Card */}
        <div className="glass-card rounded-xl p-6 ambient-shadow flex flex-col h-full relative overflow-hidden">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-blue-500/10 to-red-400/10 rounded-full blur-2xl"></div>
          <div className="flex justify-between items-start mb-4 relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center">
                <span className="material-symbols-outlined text-primary">music_video</span>
              </div>
              <div>
                <h3 className="font-headline-md text-headline-md text-on-background">TikTok</h3>
                <p className="font-label-sm text-label-sm text-on-surface-variant">@emz_dance</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-md bg-secondary-container/30 text-on-secondary-container font-label-sm text-label-sm flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">check_circle</span> Connected
            </span>
          </div>
          <div className="mt-auto space-y-4 relative z-10">
            <div className="flex justify-between items-baseline border-b border-outline-variant/20 pb-2">
              <span className="text-sm text-on-surface-variant">Videos Watched</span>
              <span className="font-headline-md text-headline-md text-on-background">342</span>
            </div>
            <div className="flex justify-between items-baseline border-b border-outline-variant/20 pb-2">
              <span className="text-sm text-on-surface-variant">Comments Scanned</span>
              <span className="font-headline-md text-headline-md text-on-background">89</span>
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="font-label-md text-label-md text-on-background">Risk Level</span>
              <span className="px-2 py-0.5 rounded text-secondary bg-secondary-container/20 font-label-sm text-label-sm">Low</span>
            </div>
          </div>
        </div>

        {/* Discord Card (Alert State) */}
        <div className="glass-card rounded-xl p-6 ambient-shadow flex flex-col h-full relative overflow-hidden border-error/30 bg-error-container/5">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-error/10 to-error/5 rounded-full blur-2xl"></div>
          <div className="flex justify-between items-start mb-4 relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-error-container/50 flex items-center justify-center">
                <span className="material-symbols-outlined text-error">forum</span>
              </div>
              <div>
                <h3 className="font-headline-md text-headline-md text-on-background">Discord</h3>
                <p className="font-label-sm text-label-sm text-on-surface-variant">Emma#4921</p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-md bg-secondary-container/30 text-on-secondary-container font-label-sm text-label-sm flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">check_circle</span> Connected
            </span>
          </div>
          <div className="mt-auto space-y-4 relative z-10">
            <div className="flex justify-between items-baseline border-b border-outline-variant/20 pb-2">
              <span className="text-sm text-on-surface-variant">Servers Active</span>
              <span className="font-headline-md text-headline-md text-on-background">4</span>
            </div>
            <div className="flex justify-between items-baseline border-b border-outline-variant/20 pb-2">
              <span className="text-sm text-on-surface-variant">Direct Messages</span>
              <span className="font-headline-md text-headline-md text-on-background">56</span>
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="font-label-md text-label-md text-on-background">Risk Level</span>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-error animate-pulse"></div>
                <span className="px-2 py-0.5 rounded text-error bg-error-container/50 font-label-sm text-label-sm font-bold">Elevated</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Deep Dive Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Flagged Interactions (Spans 8 cols) */}
        <div className="lg:col-span-8 glass-card rounded-xl p-6 ambient-shadow">
          <div className="flex justify-between items-center mb-6 border-b border-outline-variant/20 pb-4">
            <h3 className="font-headline-lg text-headline-lg text-on-background">Recent Flagged Interactions</h3>
            <button className="text-primary font-label-md text-label-md hover:underline flex items-center gap-1">
              View All <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          </div>
          <div className="space-y-4">
            {/* Alert Item 1 */}
            <div className="p-4 rounded-lg bg-surface-container-lowest border border-error-container hover:shadow-md transition-shadow">
              <div className="flex gap-4">
                <div className="mt-1">
                  <span className="material-symbols-outlined text-error" style={{ fontVariationSettings: "'FILL' 1" }}>warning</span>
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-headline-md text-headline-md text-on-background text-base">Inappropriate Content Detected</h4>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">10 mins ago</span>
                  </div>
                  <p className="text-sm text-on-surface-variant mb-2">Direct Message via Discord from Unknown User "GamerX99"</p>
                  <div className="p-3 bg-surface-container-low rounded border border-outline-variant/30 text-sm italic text-on-surface-variant mb-3">
                    "Message content blurred for safety. Contains explicit language."
                  </div>
                  <div className="flex gap-2">
                    <button className="px-3 py-1.5 bg-primary text-on-primary font-label-sm text-label-sm rounded hover:bg-primary/90 transition-colors">Review Context</button>
                    <button className="px-3 py-1.5 bg-surface-container text-on-surface font-label-sm text-label-sm rounded hover:bg-surface-variant transition-colors border border-outline-variant/30">Block User</button>
                  </div>
                </div>
              </div>
            </div>

            {/* Alert Item 2 */}
            <div className="p-4 rounded-lg bg-surface-container-lowest border border-outline-variant/30 hover:shadow-md transition-shadow">
              <div className="flex gap-4">
                <div className="mt-1">
                  <span className="material-symbols-outlined text-tertiary">person_add</span>
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-headline-md text-headline-md text-on-background text-base">New Connection out of Age Range</h4>
                    <span className="font-label-sm text-label-sm text-on-surface-variant">2 hours ago</span>
                  </div>
                  <p className="text-sm text-on-surface-variant mb-2">New follower on Instagram appears to be significantly older.</p>
                  <div className="flex items-center gap-3 p-2 bg-surface-container-low rounded border border-outline-variant/30 mb-3 w-max">
                    <img alt="Profile pic" className="w-8 h-8 rounded-full" src="https://lh3.googleusercontent.com/aida-public/AB6AXuADBDPrXoO7ZlzE6SqBdV9b2skp327i4P4E4AIfi5ba5R9aXmArFFvup3WFVOhO1UL8T8L0i4zzW8hlu1BYO-RD2AgtMmh-QbuflIft1AO7LtXRor-vgPxfsYvn1beLIrd2gSNjUYlB2t_9C13bkp7axzjwJ-yWJAcX7tGCQjHkDLq6ZjsPURNuqY1o9E0OfrN6SZ8tD2QsVwGyv04gy5FBBUC5n1wD8MIb4dFYLGAAKCV_MRxPuQLuNDGHeurZWFDePo_-8nBzDdSF"/>
                    <span className="font-label-sm text-label-sm text-on-background">@john_smith78</span>
                  </div>
                  <button className="text-primary font-label-sm text-label-sm hover:underline">View Profile Details</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Analysis Summary (Spans 4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-card rounded-xl p-6 ambient-shadow">
            <h3 className="font-headline-lg text-headline-lg text-on-background mb-4">Risk Category Breakdown</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between font-label-sm text-label-sm mb-1">
                  <span className="text-on-background">Cyberbullying</span>
                  <span className="text-secondary">Low (2%)</span>
                </div>
                <div className="w-full bg-surface-container-highest rounded-full h-2">
                  <div className="bg-secondary h-2 rounded-full" style={{ width: '2%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between font-label-sm text-label-sm mb-1">
                  <span className="text-on-background">Explicit Content</span>
                  <span className="text-error font-bold">Elevated (15%)</span>
                </div>
                <div className="w-full bg-surface-container-highest rounded-full h-2">
                  <div className="bg-error h-2 rounded-full" style={{ width: '15%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between font-label-sm text-label-sm mb-1">
                  <span className="text-on-background">Predatory Behavior</span>
                  <span className="text-secondary">Low (0%)</span>
                </div>
                <div className="w-full bg-surface-container-highest rounded-full h-2">
                  <div className="bg-secondary h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6 ambient-shadow bg-primary-container/5 border-primary/20">
            <div className="flex items-start gap-3">
              <span className="material-symbols-outlined text-primary text-[28px]">insights</span>
              <div>
                <h4 className="font-headline-md text-headline-md text-on-background mb-1">AI Insight</h4>
                <p className="text-sm text-on-surface-variant">Overall social media activity is typical for age group, but Discord usage shows a recent spike in unverified contacts. Recommend reviewing privacy settings on that platform.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SocialMedia;
