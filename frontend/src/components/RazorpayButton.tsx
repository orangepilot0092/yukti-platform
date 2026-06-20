"use client";
import { useState } from "react";

interface RazorpayButtonProps {
  amountInr: number;
  purpose: "dsa_wallet" | "saas_subscription";
  entityId: number;
  onSuccess?: () => void;
  label: string;
}

export default function RazorpayButton({ amountInr, purpose, entityId, onSuccess, label }: RazorpayButtonProps) {
  const [loading, setLoading] = useState(false);
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handlePayment = async () => {
    setLoading(true);
    try {
      // 1. Create Order on Backend
      const orderRes = await fetch(`${API_BASE}/payments/create-order`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount_inr: amountInr, purpose, entity_id: entityId }),
      });
      
      if (!orderRes.ok) {
        const err = await orderRes.json();
        throw new Error(err.detail || "Failed to create order");
      }
      
      const orderData = await orderRes.json();

      // 2. Load Razorpay Script dynamically if not already loaded
      if (!(window as any).Razorpay) {
        await new Promise<void>((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "https://checkout.razorpay.com/v1/checkout.js";
          script.onload = () => resolve();
          script.onerror = () => reject(new Error("Failed to load Razorpay script"));
          document.body.appendChild(script);
        });
      }

      const Razorpay = (window as any).Razorpay;

      // 3. Initialize Checkout
      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: "VYUHLEADS",
        description: purpose === "dsa_wallet" ? "DSA Wallet Top-up" : "Enterprise SaaS Subscription",
        order_id: orderData.order_id,
        handler: async function (response: any) {
          // 4. Verify Payment on Backend (Cryptographic Signature Check)
          const verifyRes = await fetch(`${API_BASE}/payments/verify`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              order_id: response.razorpay_order_id,
              payment_id: response.razorpay_payment_id,
              signature: response.razorpay_signature,
              purpose,
              entity_id: entityId,
              amount_inr: amountInr,
            }),
          });
          
          const verifyData = await verifyRes.json();
          if (verifyRes.ok) {
            alert("✅ Payment Successful! " + verifyData.message);
            if (onSuccess) onSuccess();
          } else {
            alert("❌ Payment Verification Failed: " + verifyData.detail);
          }
        },
        prefill: {
          name: "Ankit Sanap",
          email: "ankit@vyuhleads.org",
          contact: "9999999999",
        },
        theme: {
          color: "#C5A059", // VYUHLEADS Brass Luxury Theme
        },
      };

      const rzp = new Razorpay(options);
      rzp.open();
    } catch (error: any) {
      alert("Payment Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handlePayment}
      disabled={loading}
      className="px-6 py-3 bg-brass text-sapphire font-sans text-sm uppercase tracking-wider hover:bg-brass-light transition-colors disabled:opacity-50 flex items-center gap-2"
    >
      {loading ? "Processing..." : label}
    </button>
  );
}
