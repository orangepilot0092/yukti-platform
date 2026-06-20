import DSADashboardClient from "./DSADashboardClient";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const DSA_PHONE = "919000000001"; // Demo DSA from stress test

async function getAvailableLeads() {
  try {
    // DSA endpoint uses phone auth, not X-API-Key tenant auth
    const res = await fetch(`${API_BASE}/dsa/leads/available?dsa_phone=${DSA_PHONE}`, {
      next: { revalidate: 30 }, // Revalidate every 30s for live auction feel
    });
    if (!res.ok) {
      console.error(`DSA API Error: ${res.status}`);
      return [];
    }
    return await res.json();
  } catch (error) {
    console.error("Failed to fetch DSA leads:", error);
    return [];
  }
}

export default async function DSADashboardPage() {
  const leads = await getAvailableLeads();
  return <DSADashboardClient leads={leads} />;
}
