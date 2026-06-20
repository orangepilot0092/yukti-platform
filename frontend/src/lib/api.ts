const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.VYUHLEADS_API_KEY || "vyk_live_test_12345";

interface FetchOptions extends RequestInit {
  tenantKey?: string;
}

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { tenantKey, ...fetchOpts } = options;
  
  const res = await fetch(`${API_BASE}${path}`, {
    ...fetchOpts,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": tenantKey || API_KEY,
      ...fetchOpts.headers,
    },
    // Cache analytics for 60s on server side to reduce DB load
    next: path.includes("/analytics/") ? { revalidate: 60 } : undefined,
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }

  return res.json();
}

// Typed API Functions matching FastAPI endpoints
export const api = {
  // Builder Analytics
  getCpLeaderboard: () => 
    apiFetch<Array<{cp_name: string; total_deals: number; total_volume: number}>>("/builder/analytics/cp-leaderboard"),
  
  getTransitHeatmap: () => 
    apiFetch<Array<{transit_line: string; total_demand_leads: number; converted_deals: number; total_converted_volume: number; avg_buyer_eligibility: number}>>("/builder/analytics/transit-heatmap"),
  
  // Billing
  getUsage: () => 
    apiFetch<{tenant: string; plan: string; usage_breakdown: Record<string, number>; estimated_bill_inr: number}>("/billing/usage"),
  
  // CP Ledger
  getCpLedger: (cpName: string) => 
    apiFetch<{cp_name: string; total_earned: number; total_pending: number; transactions: Array<{deal_id: number; amount: number; status: string}>}>(`/deals/cp/ledger/${encodeURIComponent(cpName)}`),
};
