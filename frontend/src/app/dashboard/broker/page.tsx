import { ArrowUpRight, IndianRupee, MessageSquare, UserCheck } from "lucide-react";

const stats = [
  { label: "AI Verified Leads", value: "142", change: "+12%", icon: UserCheck },
  { label: "Pipeline Value", value: "₹48.2 Cr", change: "+8%", icon: IndianRupee },
  { label: "Pending Approvals", value: "7", change: "Action Req", icon: MessageSquare },
];

const leads = [
  { name: "Rajesh Kumar", phone: "91XXXXXX3210", intent: "Buy 2BHK", location: "Kharghar", eligibility: "₹63.3L", score: 95, status: "Pending Approval" },
  { name: "Priya Sharma", phone: "91XXXXXX2222", intent: "Buy 3BHK", location: "Powai", eligibility: "₹1.44 Cr", score: 88, status: "Nurturing" },
  { name: "Amit Patel", phone: "91XXXXXX1111", intent: "Investment", location: "Bandra", eligibility: "₹2.10 Cr", score: 92, status: "Site Visit" },
];

export default function BrokerDashboard() {
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

      {/* KPI Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="luxury-panel p-6 rounded-sm">
            <div className="flex justify-between items-start mb-4">
              <stat.icon className="w-5 h-5 text-brass" />
              <span className="text-xs font-sans text-emerald-400">{stat.change}</span>
            </div>
            <p className="font-serif text-3xl text-stone mb-1">{stat.value}</p>
            <p className="text-sm font-sans text-stone-muted">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* AI HITL Inbox & Pipeline Table */}
      <div className="luxury-panel rounded-sm overflow-hidden">
        <div className="p-6 border-b border-white/5 flex justify-between items-center">
          <h2 className="font-serif text-xl text-stone">Live AI Pipeline</h2>
          <div className="flex gap-2">
             <span className="px-3 py-1 bg-brass/10 text-brass text-xs font-sans rounded-sm">All Leads</span>
             <span className="px-3 py-1 bg-white/5 text-stone-muted text-xs font-sans rounded-sm">Hot</span>
          </div>
        </div>
        
        <table className="w-full text-left">
          <thead className="bg-sapphire-light/50 text-xs font-sans text-stone-muted uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4">Profile</th>
              <th className="px-6 py-4">Intent & Location</th>
              <th className="px-6 py-4">AI Eligibility</th>
              <th className="px-6 py-4">Score</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-sans text-sm">
            {leads.map((lead, i) => (
              <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-6 py-4">
                  <p className="text-stone font-medium">{lead.name}</p>
                  <p className="text-stone-muted text-xs font-mono">{lead.phone}</p>
                </td>
                <td className="px-6 py-4 text-stone-muted">{lead.intent} <span className="text-brass">•</span> {lead.location}</td>
                <td className="px-6 py-4 text-brass font-medium">{lead.eligibility}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-sm text-xs ${lead.score > 90 ? 'bg-emerald-400/10 text-emerald-400' : 'bg-yellow-400/10 text-yellow-400'}`}>
                    {lead.score}/100
                  </span>
                </td>
                <td className="px-6 py-4 text-stone-muted">{lead.status}</td>
                <td className="px-6 py-4 text-right">
                  <button className="text-xs text-brass hover:underline">View Transcript</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
