import type { Metadata } from "next";
import { IBM_Plex_Mono, Playfair_Display } from "next/font/google";
import "./globals.css";
import Providers from "@/components/providers";

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["300", "400", "500"],
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair-display",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PolyLRC",
  description: "A minimal prediction market platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${ibmPlexMono.variable} ${playfair.variable} antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}