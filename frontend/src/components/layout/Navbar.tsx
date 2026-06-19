"use client";
import Link from "next/link";
import { motion } from "framer-motion";

export default function Navbar() {
  return (
    <motion.nav 
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="fixed top-0 left-0 right-0 z-50 px-8 py-6 flex justify-between items-center bg-sapphire/60 backdrop-blur-md border-b border-white/5"
    >
      <Link href="/" className="flex items-center gap-2">
        <div className="w-8 h-8 bg-brass rounded-sm flex items-center justify-center font-serif text-sapphire font-bold text-lg">V</div>
        <span className="font-serif text-xl text-stone tracking-tight">VYUHLEADS</span>
      </Link>
      
      <div className="hidden md:flex items-center gap-10 text-sm font-sans text-stone-muted">
        <Link href="#market" className="hover:text-brass transition-colors">Micro-Markets</Link>
        <Link href="#brokers" className="hover:text-brass transition-colors">For Brokers</Link>
        <Link href="#builders" className="hover:text-brass transition-colors">For Builders</Link>
        <Link href="/login" className="px-5 py-2 border border-brass/30 text-brass hover:bg-brass hover:text-sapphire transition-all">
          Client Login
        </Link>
      </div>
    </motion.nav>
  );
}
