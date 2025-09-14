import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ArchE Resonant Interface",
  description: "Web interface for the ResonantiA Protocol",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="bg-gray-800 text-white p-4">
          <nav className="container mx-auto flex justify-between">
            <Link href="/" className="text-xl font-bold text-cyan-400">
              ArchE Interface
            </Link>
            <div>
              <Link href="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">Home</Link>
              <Link href="/mcp" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700">MCP</Link>
            </div>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}

