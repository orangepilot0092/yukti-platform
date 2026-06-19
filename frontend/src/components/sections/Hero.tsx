"use client";
import { motion } from "framer-motion";
import { ArrowUpRight, Building2 } from "lucide-react";
import Image from "next/image";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.15, delayChildren: 0.4 } }
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 1, ease: [0.22, 1, 0.36, 1] } }
};

export default function Hero() {
  return (
    <section className="relative w-full min-h-screen overflow-hidden flex items-center justify-center arch-grid">
      
      {/* FIX: Parent is now strictly 'relative w-full h-full' */}
      <div className="absolute inset-0 z-0">
        <motion.div 
          initial={{ scale: 1.1 }}
          animate={{ scale: 1.0 }}
          transition={{ duration: 20, ease: "linear", repeat: Infinity, repeatType: "reverse" }}
          className="relative w-full h-full"
        >
          {/* FIX: Changed to a valid, stable Unsplash URL, added sizes="100vw" */}
          <Image 
            src="https://images.unsplash.com/photo-1486325212027-8081e485255e?q=80&w=2070&auto=format&fit=crop" 
            alt="Mumbai Skyline at Dusk" 
            fill 
            sizes="100vw"
            className="object-cover opacity-40"
            priority
          />
        </motion.div>
        <div className="absolute inset-0 bg-gradient-to-b from-sapphire/80 via-sapphire/60 to-sapphire" />
        <div className="absolute inset-0 bg-gradient-to-r from-sapphire/90 via-transparent to-sapphire/90" />
      </div>

      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="relative z-10 text-center px-6 max-w-5xl mx-auto pt-20"
      >
        <motion.div variants={item} className="inline-flex items-center gap-3 px-5 py-2 rounded-full border border-brass/30 bg-sapphire-light/50 backdrop-blur-md mb-10">
          <Building2 className="w-4 h-4 text-brass" />
          <span className="text-xs font-sans text-stone-muted tracking-[0.2em] uppercase">Exclusive Network // Mumbai Market</span>
        </motion.div>
        
        <motion.h1 variants={item} className="font-serif text-5xl md:text-7xl lg:text-8xl font-light tracking-tight mb-8 text-stone leading-[1.1]">
          The Intelligence Layer for <br />
          <span className="text-gold-gradient italic font-normal">Mumbai Real Estate</span>
        </motion.h1>

        <motion.p variants={item} className="text-stone-muted text-lg md:text-xl max-w-2xl mx-auto font-light leading-relaxed mb-14 font-sans">
          From Worli to Kharghar. We intercept portal noise, verify financial capacity, 
          and deliver bank-approved closures to your existing CRM.
        </motion.p>

        <motion.div variants={item} className="flex flex-col sm:flex-row gap-5 justify-center items-center">
          <button className="hoverable group relative px-10 py-4 bg-brass text-sapphire font-medium tracking-wide overflow-hidden transition-all hover:bg-brass-light shadow-lg shadow-brass/10">
            <span className="relative z-10 flex items-center gap-2 font-sans text-sm uppercase tracking-wider">
              Request Private Demo
              <ArrowUpRight className="w-4 h-4 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
            </span>
          </button>
          <button className="hoverable px-10 py-4 border border-stone/20 text-stone font-medium tracking-wide hover:bg-white/5 transition-colors backdrop-blur-sm font-sans text-sm uppercase tracking-wider">
            View Transit Heatmaps
          </button>
        </motion.div>
      </motion.div>
      
      <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-sapphire to-transparent z-[2] pointer-events-none" />
    </section>
  );
}
