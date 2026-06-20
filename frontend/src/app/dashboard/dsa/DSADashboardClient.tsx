"use client";
import RazorpayButton from "@/components/RazorpayButton";
import { ShieldCheck, TrendingUp, IndianRupee } from "lucide-react";

interface DSALead {
  lead_id: number;
  intent: string;
  max_loan_eligibility: number;
  monthly_income: number;
  dti_ratio: number;
  eligibility_confidence: string;
  masked_phone: string;
  score: number;
}

export default function DSADashboardClient({ leads }: { leads: DSALead[] }) {
  const highConfidenceLeads = leads.filter(l => l.eligibility_confidence === "High").length;
  const avgDTI = leads.length > 0 
    ? (leads.reduce((sum, l) => sum + l.dti_ratio, 0) / leads.length).toFixed(1) 
    : "0.0";

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-serif text-4xl text-stone tracking-tight">DSA Blind Auction</h1>
          <p className="text-stone-muted font-sans mt-2">Pre-underwritten financial profiles. Bid to unlock PII.</p>
        </div>
        <RazorpayButton amountInr={5000} purpose="dsa_wallet" entityId={1} label="Top Up Wallet ₹5,000" />
      </div>

      {/* Moat KPIs */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="luxury-panel p-6 rounded-sm">
          <ShieldCheck className="w-5 h-5 text-emerald-400 mb-4" />
          <p className="font-serif text-3xl text-stone mb-1">{highConfidenceLeads}</p>
          <p className="text-sm font-sans text-stone-muted">High Confidence Profiles</p>
        </div>
        <div className="luxury-panel p-6 rounded-sm">
          <TrendingUp className="w-5 h-5 text-brass mb-4" />
          <p className="font-serif text-3xl text-stone mb-1">{avgDTI}%</p>
          <p className="text-sm font-sans text-stone-muted">Avg Portfolio DTI</p>
        </div>
        <div className="luxury-panel p-6 rounded-sm">
          <IndianRupee className="w-5 h-5 text-brass mb-4" />
          <p className="font-serif text-3xl text-stone mb-1">{leads.length}</p>
          <p className="text-sm font-sans text-stone-muted">Available for Auction</p>
        </div>
      </div>

      {/* Auction Table */}
      <div className="luxury-panel rounded-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-sapphire-light/50 text-xs font-sans text-stone-muted uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4">Lead ID</th>
              <th className="px-6 py-4">Eligibility</th>
              <th className="px-6 py-4">DTI Ratio</th>
              <th className="px-6 py-4">AI Confidence</th>
              <th className="px-6 py-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-sans text-sm">
            {leads.slice(0, 10).map((lead) => (
              <tr key={lead.lead_id} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-6 py-4 text-stone font-mono">#{lead.lead_id}</td>
                <td className="px-6 py-4 text-brass font-semibold">₹{(lead.max_loan_eligibility / 100000).toFixed(1)}L</td>
                <td className="px-6 py-4 text-stone">
                  {lead.dti_ratio === 0 ? (
                    <span className="text-stone-muted italic">No EMI</span>
                  ) : (
                    <span className={lead.dti_ratio > 50 ? "text-red-400" : "text-emerald-400"}>
                      {lead.dti_ratio}%
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-sm text-xs font-semibold uppercase tracking-wider ${
                    lead.eligibility_confidence === "High" ? "bg-emerald-400/10 text-emerald-400" :
                    lead.eligibility_confidence === "Medium" ? "bg-yellow-400/10 text-yellow-400" :
                    "bg-red-400/10 text-red-400"
                  }`}>
                    {lead.eligibility_confidence}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="px-4 py-2 bg-brass/10 text-brass border border-brass/20 hover:bg-brass hover:text-sapphire transition-all text-xs uppercase tracking-wider">
                    Place Bid
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
