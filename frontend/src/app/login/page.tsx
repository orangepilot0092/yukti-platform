import Link from "next/link";
import { ArrowLeft, Building2 } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-screen grid md:grid-cols-2 bg-sapphire">
      {/* Left: Institutional Branding */}
      <div className="hidden md:flex flex-col justify-between p-12 border-r border-white/5 bg-sapphire-light arch-grid">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brass rounded-sm flex items-center justify-center font-serif text-sapphire font-bold text-lg">V</div>
          <span className="font-serif text-xl text-stone">VYUHLEADS</span>
        </Link>
        
        <div>
          <h1 className="font-serif text-5xl text-stone mb-6 leading-tight">
            The Operating System for <span className="italic text-gold-gradient">Mumbai Real Estate.</span>
          </h1>
          <p className="text-stone-muted font-sans max-w-md leading-relaxed">
            Secure access for verified Brokerages, Developers, and Channel Partners. 
            If you require an institutional license, please contact our Mumbai HQ.
          </p>
        </div>
        
        <p className="text-xs font-sans text-stone-muted/50">© 2026 VYUHLEADS Technologies. DPDP Compliant.</p>
      </div>

      {/* Right: Login Form */}
      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-sans text-stone-muted hover:text-brass mb-12 transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Platform
          </Link>
          
          <h2 className="font-serif text-3xl text-stone mb-2">Client Portal</h2>
          <p className="text-stone-muted font-sans text-sm mb-10">Enter your credentials to access your workspace.</p>
          
          <form className="space-y-6">
            <div>
              <label className="block text-xs font-sans text-stone-muted uppercase tracking-wider mb-2">Work Email</label>
              <input type="email" className="w-full bg-sapphire-light border border-white/10 rounded-sm px-4 py-3 text-stone font-sans focus:border-brass focus:outline-none transition-colors" placeholder="name@lodha.com" />
            </div>
            <div>
              <label className="block text-xs font-sans text-stone-muted uppercase tracking-wider mb-2">Password</label>
              <input type="password" className="w-full bg-sapphire-light border border-white/10 rounded-sm px-4 py-3 text-stone font-sans focus:border-brass focus:outline-none transition-colors" placeholder="••••••••" />
            </div>
            
            <button type="button" className="w-full bg-brass text-sapphire font-sans font-medium py-4 uppercase tracking-wider text-sm hover:bg-brass-light transition-colors shadow-lg shadow-brass/10">
              Access Workspace
            </button>
          </form>
          
          <div className="mt-12 pt-8 border-t border-white/5">
            <p className="text-xs font-sans text-stone-muted mb-4 text-center">Select Demo Persona</p>
            <div className="grid grid-cols-2 gap-3">
              <Link href="/dashboard/broker" className="p-3 border border-white/10 rounded-sm text-center text-xs font-sans text-stone hover:border-brass hover:text-brass transition-colors">Broker OS</Link>
              <Link href="/dashboard/builder" className="p-3 border border-white/10 rounded-sm text-center text-xs font-sans text-stone hover:border-brass hover:text-brass transition-colors">Builder Intel</Link>
              <Link href="/dashboard/cp" className="p-3 border border-white/10 rounded-sm text-center text-xs font-sans text-stone hover:border-brass hover:text-brass transition-colors">CP Ledger</Link>
              <Link href="/dashboard/dsa" className="p-3 border border-white/10 rounded-sm text-center text-xs font-sans text-stone hover:border-brass hover:text-brass transition-colors">DSA Auction</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
