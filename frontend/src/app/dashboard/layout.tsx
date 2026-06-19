import Sidebar from "@/components/dashboard/Sidebar";
import { Bell, Search } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-sapphire">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Topbar */}
        <header className="h-16 border-b border-white/5 bg-sapphire-light/50 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-muted" />
            <input 
              type="text" 
              placeholder="Search leads, projects, CPs..." 
              className="w-full bg-sapphire border border-white/5 rounded-sm pl-10 pr-4 py-2 text-sm font-sans text-stone focus:border-brass focus:outline-none"
            />
          </div>
          
          <div className="flex items-center gap-6">
            <button className="relative text-stone-muted hover:text-brass transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-brass rounded-full" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-brass/20 border border-brass/30 flex items-center justify-center text-xs font-sans text-brass">AS</div>
              <div className="text-right hidden md:block">
                <p className="text-sm font-sans text-stone leading-none">Ankit Sanap</p>
                <p className="text-xs font-sans text-stone-muted">Enterprise Admin</p>
              </div>
            </div>
          </div>
        </header>
        
        {/* Main Content Area */}
        <main className="flex-1 p-8 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
