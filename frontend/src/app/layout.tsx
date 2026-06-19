import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({ 
  subsets: ["latin"], 
  variable: "--font-fraunces",
  display: "swap" 
});

const inter = Inter({ 
  subsets: ["latin"], 
  variable: "--font-inter",
  display: "swap" 
});

export const metadata: Metadata = {
  title: "VYUHLEADS | The Intelligence Layer for Mumbai Real Estate",
  description: "From Bandra to Panvel. We turn portal leads into bank-approved closures. The operating system for Mumbai's elite brokerages and developers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${fraunces.variable} ${inter.variable} antialiased overflow-x-hidden`}>
        <main className="relative">
          {children}
        </main>
      </body>
    </html>
  );
}
