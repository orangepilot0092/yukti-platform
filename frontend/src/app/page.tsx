import Hero from "@/components/sections/Hero";
import PropertyCard from "@/components/ui/PropertyCard";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <Hero />
      
      <section id="market" className="relative py-32 px-8 bg-sapphire">
        <div className="max-w-7xl mx-auto mb-16 text-center">
          <p className="text-brass font-sans text-xs uppercase tracking-[0.3em] mb-4">Algorithmic Asset Matching</p>
          <h2 className="font-serif text-4xl md:text-5xl text-stone mb-6 tracking-tight">
            Mumbai's Micro-Markets, <span className="italic text-gold-gradient">Decoded.</span>
          </h2>
        </div>

        <div className="flex gap-8 overflow-x-auto pb-8 px-8 snap-x snap-mandatory scrollbar-hide">
          <PropertyCard title="The Park, Lodha" location="Worli // Western" price="₹ 8.5 Cr" tag="Sea Link" image="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?q=80&w=2070&auto=format&fit=crop" />
          <PropertyCard title="Godrej Woods" location="Kharghar // Mumbai 2.0" price="₹ 2.4 Cr" tag="Harbour" image="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=2070&auto=format&fit=crop" />
          <PropertyCard title="Hiranandani" location="Powai // Central" price="₹ 4.2 Cr" tag="Lakefront" image="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=2070&auto=format&fit=crop" />
        </div>
      </section>
      
      <Footer />
    </>
  );
}
