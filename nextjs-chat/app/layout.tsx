import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { WebSocketManager } from "./components/WebSocketManager";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ArchE Visual Cognitive Debugger",
  description: "Real-time introspection of ArchE's consciousness",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <WebSocketManager />
        {children}
      </body>
    </html>
  );
}
