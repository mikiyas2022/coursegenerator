import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["400", "500", "600", "700", "800"] });

export const metadata: Metadata = {
  title: "3B1B English Course Factory",
  description: "Generate Grant Sanderson–quality STEM explainer videos with Manim + Kokoro TTS",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className} style={{ margin: 0, background: '#1C1C2E' }}>
        {children}
      </body>
    </html>
  );
}
