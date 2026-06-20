"use client";
import { ArrowUpRight, IndianRupee, MessageSquare, UserCheck } from "lucide-react";

interface UsageData {
  tenant: string;
  plan: string;
  usage_breakdown: Record<string, number>;
  estimated_bill_inr: number;
}

export default function BrokerDashboardClient({ usage }: { usage: UsageData | null }) {
  if (!usage) {
    return (
      <div className="luxury-panel p-12 rounded-sm text-center border border-dashed border-white/10">
        <p className="text-stone-muted font-sans">Unable to load billing data. Please check API connection.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="font-serif text-4xl text-stone tracking-tight">Broker Command Center</h1>
          <p className="text-stone-muted font-sans mt-2">Real-time AI lead qualification and pipeline management.</p>
        </div>
        <button className="px-6 py-3 bg-brass text-sapphire font-sans text-sm uppercase tracking-wider hover:bg-brass-light transition-colors flex items-center gap-2">
          Upload MagicBricks CSV <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>

      {/* Live Billing KPI */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="luxury-panel p-6 rounded-sm">
          <IndianRupee className="w-5 h-5 text-brass mb-4" />
          <p className="font-serif text-3xl text-stone mb-1">₹{usage.estimated_bill_inr || 0}</p>
          <p className="text-sm font-sans text-stone-muted">Estimated Monthly Bill</p>
        </div>
        <div className="luxury-panel p-6 rounded-sm">
          <UserCheck className="w-5 h-5 text-brass mb-4" />
          <p className="font-serif text-3xl text-stone mb-1">{usage.usage_breakdown?.lead_generated || 0}</p>
          <p className="text-sm font-sans text-stone-muted">AI Verified Leads</p>
        </div>
        <div className="luxury-panel p-6 rounded-sm">
          <MessageSquare className="w-5 h-5 text-brass mb-4" />
          <p className="font-serif text-3xl text-stone mb-1">{usage.plan || "Enterprise"}</p>
          <p className="text-sm font-sans text-stone-muted">Current Plan</p>
        </div>
      </div>

      <div className="luxury-panel p-12 rounded-sm text-center border border-dashed border-white/10">
        <p className="text-stone-muted font-sans">Live Lead Pipeline Table will render here once /crm/leads endpoint is validated.</p>
      </div>
    </div>
  );
}
