import React from 'react';

const Location = () => {
  return (
    <div className="relative w-full h-[calc(100vh-120px)] rounded-3xl overflow-hidden shadow-[0_20px_40px_rgba(0,0,0,0.05)]">
      {/* Interactive Map Placeholder */}
      <div className="absolute inset-0 z-0 bg-surface-variant">
        <img className="w-full h-full object-cover opacity-90" data-alt="High altitude clean aerial map view of a modern city grid and suburbs with subtle premium color grading and soft lighting" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBP5C4ZzDymNlCP9kPMleMorm8r2b_iBhmxO3v4wHQZ8YpsY6tCyBEEfW5Tsa-T9rk5ODACqJayfNNYKfjcwFr7Cn3nG1QBzweley4GL3vWXrkLEQxWRpi_uVQfz-nJyXhQLKX-mNLmf85Swrgcl7xLVy4KDekVsTOpezhMfWhmMpoKIzMmPiFQGNpQBhEkjR9EGDCFfPfn7SLiwQP-9e38FyqM5D6l4lthSPprBcm-j2IJCtIfzZcURqktFXXP0mS2E69FlG3rT3Pc"/>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-transparent via-transparent to-black/20 pointer-events-none"></div>
        
        {/* Simulated User Map Marker */}
        <div className="absolute top-[45%] left-[55%] transform -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center pointer-events-none">
          <div className="bg-primary text-on-primary font-label-sm text-label-sm px-3 py-1.5 rounded-full shadow-lg mb-2 backdrop-blur-md bg-opacity-90 border border-white/20">
            Emma is here
          </div>
          <div className="relative w-14 h-14">
            {/* Static representation of pulsing alert for 'Live' focus */}
            <div className="absolute inset-0 rounded-full bg-primary opacity-20 scale-150"></div>
            <div className="absolute inset-0 rounded-full bg-primary opacity-40 scale-110"></div>
            <div className="relative w-full h-full bg-white rounded-full p-1 shadow-xl border-2 border-primary">
              <img className="w-full h-full rounded-full object-cover" data-alt="Portrait of a young teenage girl" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAYfO0rXac708GrAtiWhCQVnscoTO03qH-slDq1bqeq89emT45_EQRbosilbCvloXVWsnD5BVkm87a7HLwhbWUMpZvIMD74VKDrdegwZaahyDDG6F7Vv21DRt2iGDv0Q_QiJquoHvSfORRo2FVTH0mz9t2y8XTCqJeg-Hu6IAl5U-OfnMYDI9dFWE0-5Q1NsqLC7xIejh4MuRN_jxF7FjyE82d1NRQrzszk62uIh8JS1RFvGDMHLqmY-5zFwvsVJHjseJEU8HXVZfmO"/>
            </div>
          </div>
        </div>
      </div>

      {/* Floating UI Layer */}
      <div className="relative z-20 h-full p-6 lg:p-lg flex flex-col justify-between pointer-events-none max-w-container-max mx-auto">
        {/* Top Section: Status & Controls */}
        <div className="flex justify-between items-start w-full">
          {/* Real-time Status Card */}
          <div className="glass-card rounded-xl p-6 w-[340px] pointer-events-auto">
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-outline-variant/20">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full overflow-hidden border border-white">
                  <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDPqTORWV3_KFUZhLFaUFP3O5A_pNAaDgBg97HrWBERvSGA-CdVct_K_KKUMo3dWA8w0BYDombeviyJCjVwvIBTGZPQbHrJcowqWW_GJyj718XAKZ0xE-em3JxPofjlqmFamk49R_9761sbxXs9D9ofAGP1sOHJvF5S2QsvAzg45oiXyG62jXYPs6RfacvX8xebV_XeqZNWJ68d_so4L45iL96zYOGIVkG2dj4JwHB-soAlpw8dmOFDT57w2C6rqvQoCFMYT0Tu1fXc" alt="Emma" />
                </div>
                <div>
                  <h3 className="font-headline-md text-headline-md text-on-surface">Emma</h3>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span className="w-2 h-2 rounded-full bg-error block relative">
                      <span className="absolute inset-0 rounded-full bg-error opacity-50 scale-150"></span>
                    </span>
                    <span className="font-label-sm text-label-sm text-error">Live Tracking</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col items-end">
                <span className="material-symbols-outlined text-outline" style={{ fontVariationSettings: "'FILL' 1" }}>battery_5_bar</span>
                <span className="font-label-sm text-label-sm text-outline mt-1">82%</span>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[18px]">near_me</span>
                </div>
                <div>
                  <p className="font-label-md text-label-md text-on-surface-variant">Current Location</p>
                  <p className="font-body-md text-body-md text-on-surface font-medium">1420 Washington Blvd</p>
                  <p className="font-label-sm text-label-sm text-outline mt-0.5">Updated just now</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="mt-0.5 w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-secondary">
                  <span className="material-symbols-outlined text-[18px]">directions_walk</span>
                </div>
                <div>
                  <p className="font-label-md text-label-md text-on-surface-variant">Movement</p>
                  <p className="font-body-md text-body-md text-on-surface font-medium">Walking • 3 mph</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Map Tools */}
          <div className="glass-card rounded-full p-2 flex flex-col gap-2 pointer-events-auto">
            <button className="w-10 h-10 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface/50 hover:text-primary transition-colors">
              <span className="material-symbols-outlined">add</span>
            </button>
            <div className="h-px bg-outline-variant/30 w-6 mx-auto"></div>
            <button className="w-10 h-10 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface/50 hover:text-primary transition-colors">
              <span className="material-symbols-outlined">remove</span>
            </button>
            <div className="h-px bg-outline-variant/30 w-6 mx-auto"></div>
            <button className="w-10 h-10 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface/50 hover:text-primary transition-colors">
              <span className="material-symbols-outlined">layers</span>
            </button>
          </div>
        </div>

        {/* Bottom Section: Safe Zones & History */}
        <div className="flex gap-6 w-full items-end justify-start pb-4 overflow-x-auto">
          {/* Safe Zones Panel */}
          <div className="glass-card rounded-xl p-6 min-w-[380px] pointer-events-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">security</span>
                Safe Zones
              </h3>
              <button className="text-primary font-label-md text-label-md hover:underline">Edit</button>
            </div>
            
            <div className="space-y-3">
              <div className="bg-surface-container-lowest/60 rounded-lg p-3 border border-outline-variant/20 flex items-center justify-between group hover:border-primary/30 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant">
                    <span className="material-symbols-outlined">home</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface font-semibold">Home</p>
                    <p className="font-label-sm text-label-sm text-outline">Radius: 200m</p>
                  </div>
                </div>
                <div className="px-2.5 py-1 rounded-md bg-surface-variant text-on-surface-variant font-label-sm text-label-sm">
                  Away
                </div>
              </div>

              <div className="bg-surface-container-lowest/60 rounded-lg p-3 border border-outline-variant/20 flex items-center justify-between group hover:border-primary/30 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <span className="material-symbols-outlined">school</span>
                  </div>
                  <div>
                    <p className="font-label-md text-label-md text-on-surface font-semibold">Lincoln High</p>
                    <p className="font-label-sm text-label-sm text-outline">Radius: 500m</p>
                  </div>
                </div>
                <div className="px-2.5 py-1 rounded-md bg-primary-container/20 text-primary font-label-sm text-label-sm flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary"></span> Inside
                </div>
              </div>
            </div>
            
            <button className="w-full mt-4 py-2.5 border border-outline-variant/50 rounded-lg font-label-md text-label-md text-on-surface-variant hover:bg-surface-container/50 hover:text-on-surface transition-colors flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-[18px]">add_circle</span>
              Create New Zone
            </button>
          </div>

          {/* Recent Activity Panel */}
          <div className="glass-card rounded-xl p-6 min-w-[320px] pointer-events-auto relative overflow-hidden">
            <div className="absolute -top-10 -right-10 w-32 h-32 bg-secondary/10 rounded-full blur-[30px]"></div>
            <div className="relative z-10">
              <h3 className="font-headline-md text-headline-md text-on-surface mb-5 flex items-center gap-2">
                <span className="material-symbols-outlined text-secondary">schedule</span>
                Today's Path
              </h3>
              
              <div className="relative border-l-2 border-surface-variant ml-4 space-y-6">
                <div className="relative pl-6">
                  <div className="absolute w-3 h-3 bg-surface-container border-2 border-primary rounded-full -left-[7.5px] top-1"></div>
                  <p className="font-label-sm text-label-sm text-outline mb-0.5">3:15 PM</p>
                  <p className="font-body-md text-body-md text-on-surface font-medium">Left Lincoln High</p>
                </div>
                
                <div className="relative pl-6">
                  <div className="absolute w-3 h-3 bg-surface-container border-2 border-outline-variant rounded-full -left-[7.5px] top-1"></div>
                  <p className="font-label-sm text-label-sm text-outline mb-0.5">1:00 PM</p>
                  <p className="font-body-md text-body-md text-on-surface font-medium">Arrived at Campus Cafe</p>
                  <p className="font-label-sm text-label-sm text-on-surface-variant mt-1">Stayed for 45 mins</p>
                </div>
                
                <div className="relative pl-6 pb-2">
                  <div className="absolute w-3 h-3 bg-surface-container border-2 border-outline-variant rounded-full -left-[7.5px] top-1"></div>
                  <p className="font-label-sm text-label-sm text-outline mb-0.5">8:10 AM</p>
                  <p className="font-body-md text-body-md text-on-surface font-medium">Arrived at Lincoln High</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Location;
