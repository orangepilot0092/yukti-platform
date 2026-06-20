"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Building2, TrendingUp, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

export default function BuilderDashboard() {
  const [transitData, setTransitData] = useState<any[]>([]);
  const [cpData, setCpData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [heatmap, leaderboard] = await Promise.all([
          api.getTransitHeatmap(),
          api.getCpLeaderboard()
        ]);
        
        setTransitData(heatmap.map(h => ({
          name: h.transit_line,
          demand: h.total_demand_leads,
          deals: h.converted_deals
        })));
        
        setCpData(leaderboard.slice(0, 5).map((cp, i) => ({
          name: cp.cp_name,
          volume: Number((cp.total_volume / 10000000).toFixed(1)), // Convert to Cr
          color: ["#C5A059", "#E7E5E4", "#94A3B8", "#64748B", "#475569"][i % 5]
        })));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-96">
      <Loader2 className="w-8 h-8 text-brass animate-spin" />
    </div>
  );

  if (error) return (
    <div className="p-8 text-red-400 font-sans">Error: {error}</div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-4xl text-stone tracking-tight">Enterprise Market Intelligence</h1>
        <p className="text-stone-muted font-sans mt-2">Live macro-demand analytics across Mumbai's transit corridors.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Transit Line Heatmap */}
        <div className="luxury-panel p-6 rounded-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-serif text-xl text-stone">Transit-Line Demand vs Conversion</h3>
            <Building2 className="w-5 h-5 text-brass" />
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={transitData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} fontFamily="var(--font-sans)" />
              <YAxis stroke="#94A3B8" fontSize={12} fontFamily="var(--font-sans)" />
              <Tooltip 
                contentStyle={{ backgroundColor: "#111827", border: "1px solid rgba(197,160,89,0.2)", borderRadius: "2px" }}
                labelStyle={{ color: "#E7E5E4" }}
              />
              <Bar dataKey="demand" fill="#C5A059" radius={[2, 2, 0, 0]} name="AI Verified Demand" />
              <Bar dataKey="deals" fill="#E7E5E4" radius={[2, 2, 0, 0]} name="Closed Deals" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* CP ROI Leaderboard */}
        <div className="luxury-panel p-6 rounded-sm">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-serif text-xl text-stone">Channel Partner ROI</h3>
            <TrendingUp className="w-5 h-5 text-brass" />
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={cpData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={2} dataKey="volume">
                {cpData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: "#111827", border: "1px solid rgba(197,160,89,0.2)", borderRadius: "2px" }}
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
