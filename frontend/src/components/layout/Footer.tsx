import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-sapphire border-t border-white/5 py-16 px-8">
      <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-12">
        <div className="col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-brass rounded-sm flex items-center justify-center font-serif text-sapphire font-bold text-lg">V</div>
            <span className="font-serif text-xl text-stone tracking-tight">VYUHLEADS</span>
          </div>
          <p className="text-stone-muted font-sans text-sm max-w-sm leading-relaxed">
            The proprietary intelligence layer for Mumbai real estate. 
            From Bandra to Panvel, we engineer bank-approved closures.
          </p>
        </div>
        
        <div>
          <h4 className="font-serif text-stone mb-4">Platform</h4>
          <ul className="space-y-2 text-sm font-sans text-stone-muted">
            <li><Link href="#" className="hover:text-brass">Broker OS</Link></li>
            <li><Link href="#" className="hover:text-brass">Builder Intelligence</Link></li>
            <li><Link href="#" className="hover:text-brass">CP Ledger</Link></li>
          </ul>
        </div>
        
        <div>
          <h4 className="font-serif text-stone mb-4">Institutional</h4>
          <ul className="space-y-2 text-sm font-sans text-stone-muted">
            <li><Link href="#" className="hover:text-brass">Security & DPDP</Link></li>
            <li><Link href="#" className="hover:text-brass">API Documentation</Link></li>
            <li><Link href="#" className="hover:text-brass">Contact Mumbai HQ</Link></li>
          </ul>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto mt-16 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-xs font-sans text-stone-muted/50">
        <p>© 2026 VYUHLEADS Technologies Pvt. Ltd. // RERA Compliant Infrastructure</p>
        <p>Mumbai • Singapore • Dubai</p>
      </div>
    </footer>
  );
}
