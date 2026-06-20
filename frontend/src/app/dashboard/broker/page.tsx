import BrokerDashboardClient from "./BrokerDashboardClient";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.VYUHLEADS_API_KEY || "vyk_live_test_12345";

async function getUsage() {
  try {
    const res = await fetch(`${API_BASE}/billing/usage`, {
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },
      next: { revalidate: 60 },
    });

    if (!res.ok) {
      console.error(`API Error: ${res.status} ${res.statusText}`);
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error("Failed to fetch usage:", error);
    return null;
  }
}

export default async function BrokerDashboardPage() {
  const usage = await getUsage();
  return <BrokerDashboardClient usage={usage} />;
}
