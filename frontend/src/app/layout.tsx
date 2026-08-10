import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Document Intelligence",
  description: "Upload financial and legal PDFs. Ask questions. Get cited answers.",
};

import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="h-full antialiased dark">
        <body className="min-h-full flex flex-col bg-slate-950 text-slate-50">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
