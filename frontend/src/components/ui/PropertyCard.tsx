"use client";
import { motion } from "framer-motion";
import { MapPin, TrendingUp } from "lucide-react";
import Image from "next/image";

interface PropertyCardProps {
  title: string;
  location: string;
  price: string;
  image: string;
  tag: string;
}

export default function PropertyCard({ title, location, price, image, tag }: PropertyCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
      className="w-[380px] luxury-panel rounded-sm overflow-hidden group hoverable flex-shrink-0"
    >
      {/* Parent is already 'relative h-64' */}
      <div className="relative h-64 overflow-hidden">
        {/* FIX: Added sizes prop to eliminate console warning */}
        <Image 
          src={image} 
          alt={title} 
          fill 
          sizes="380px"
          className="object-cover transition-transform duration-[3000ms] ease-out group-hover:scale-110" 
        />
        <div className="absolute inset-0 bg-gradient-to-t from-sapphire via-transparent to-transparent opacity-80" />
        
        <div className="absolute top-4 left-4 px-3 py-1 bg-sapphire/80 backdrop-blur-md border border-brass/30 text-brass text-[10px] font-sans uppercase tracking-widest">
          {tag}
        </div>
      </div>

      <div className="p-6">
        <div className="flex items-center gap-2 text-stone-muted text-xs font-sans mb-3">
          <MapPin className="w-3 h-3 text-brass" />
          <span className="uppercase tracking-wider">{location}</span>
        </div>
        
        <h3 className="font-serif text-2xl text-stone mb-4 tracking-tight">{title}</h3>
        
        <div className="flex items-end justify-between pt-4 border-t border-white/5">
          <div>
            <p className="text-[10px] font-sans text-stone-muted uppercase tracking-wider mb-1">AI Valuation</p>
            <p className="font-serif text-2xl text-brass tracking-tight">{price}</p>
          </div>
          <div className="flex items-center gap-1 text-emerald-400 text-sm font-sans">
            <TrendingUp className="w-4 h-4" />
            <span>14.2% Yield</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
