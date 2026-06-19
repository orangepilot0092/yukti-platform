"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Building2, TrendingUp } from "lucide-react";

const transitData = [
  { name: "Western", demand: 420, deals: 45 },
  { name: "Central", demand: 310, deals: 28 },
  { name: "Harbour", demand: 680, deals: 82 }, 
];

const cpData = [
  { name: "Ramesh CP", volume: 2.7, color: "#C5A059" },
  { name: "Suresh CP", volume: 1.2, color: "#E7E5E4" },
  { name: "Mumbai Homes", volume: 0.8, color: "#94A3B8" },
];

export default function BuilderDashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-4xl text-stone tracking-tight">Enterprise Market Intelligence</h1>
        <p className="text-stone-muted font-sans mt-2">Macro-demand analytics across Mumbai's transit corridors.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="luxury-panel p-6 rounded-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-serif text-xl text-stone">Transit-Line Demand vs Conversion</h3>
            <Building2 className="w-5 h-5 text-brass" />
          </div>
          {/* FIX: Explicit height={250} prevents the -1 SSR hydration warning */}
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={transitData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} fontFamily="var(--font-sans)" />
              <YAxis stroke="#94A3B8" fontSize={12} fontFamily="var(--font-sans)" />
              <Tooltip 
                contentStyle={{ backgroundColor: "#111827", border: "1px solid rgba(197,160,89,0.2)", borderRadius: "2px", fontFamily: "var(--font-sans)" }}
                labelStyle={{ color: "#E7E5E4" }}
              />
              <Bar dataKey="demand" fill="#C5A059" radius={[2, 2, 0, 0]} name="AI Verified Demand" />
              <Bar dataKey="deals" fill="#E7E5E4" radius={[2, 2, 0, 0]} name="Closed Deals" />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-xs font-sans text-stone-muted mt-4 border-t border-white/5 pt-4">
            <span className="text-brass">Insight:</span> Harbour Line (Mumbai 2.0) shows 680 pre-qualified leads but only 82 closures. <span className="text-emerald-400">Launch new inventory in Kharghar/Panvel immediately.</span>
          </p>
        </div>

        <div className="luxury-panel p-6 rounded-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-serif text-xl text-stone">Channel Partner ROI</h3>
            <TrendingUp className="w-5 h-5 text-brass" />
          </div>
          {/* FIX: Explicit height={250} */}
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={cpData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2} dataKey="volume">
                {cpData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: "#111827", border: "1px solid rgba(197,160,89,0.2)", borderRadius: "2px", fontFamily: "var(--font-sans)" }}
                formatter={(value) => `₹${value} Cr`}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4 border-t border-white/5 pt-4">
            {cpData.map((cp) => (
              <div key={cp.name} className="flex justify-between items-center text-sm font-sans">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cp.color }} />
                  <span className="text-stone-muted">{cp.name}</span>
                </div>
                <span className="text-stone">₹{cp.volume} Cr</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
