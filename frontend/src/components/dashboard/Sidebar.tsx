"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, Building2, Handshake, Wallet, Settings, LogOut } from "lucide-react";

const navigation = [
  { name: "Overview", href: "/dashboard/broker", icon: LayoutDashboard, persona: "broker" },
  { name: "Lead Pipeline", href: "/dashboard/broker/pipeline", icon: Users, persona: "broker" },
  { name: "Market Intel", href: "/dashboard/builder", icon: Building2, persona: "builder" },
  { name: "CP Network", href: "/dashboard/builder/cps", icon: Handshake, persona: "builder" },
  { name: "My Commission", href: "/dashboard/cp", icon: Wallet, persona: "cp" },
  { name: "Lead Auction", href: "/dashboard/dsa", icon: Wallet, persona: "dsa" },
];

export default function Sidebar() {
  const pathname = usePathname();
  
  return (
    <aside className="w-64 bg-sapphire-light border-r border-white/5 flex flex-col h-screen sticky top-0">
      <div className="p-6 border-b border-white/5">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brass rounded-sm flex items-center justify-center font-serif text-sapphire font-bold text-lg">V</div>
          <span className="font-serif text-xl text-stone tracking-tight">VYUHLEADS</span>
        </Link>
      </div>
      
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-sm text-sm font-sans transition-all ${
                isActive 
                  ? "bg-brass/10 text-brass border-l-2 border-brass" 
                  : "text-stone-muted hover:bg-white/5 hover:text-stone border-l-2 border-transparent"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-white/5 space-y-1">
        <Link href="#" className="flex items-center gap-3 px-4 py-3 rounded-sm text-sm font-sans text-stone-muted hover:bg-white/5 hover:text-stone">
          <Settings className="w-4 h-4" /> Settings
        </Link>
        <Link href="/" className="flex items-center gap-3 px-4 py-3 rounded-sm text-sm font-sans text-stone-muted hover:bg-white/5 hover:text-stone">
          <LogOut className="w-4 h-4" /> Sign Out
        </Link>
      </div>
    </aside>
  );
}
