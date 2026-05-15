/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author: CopilotKit
CoAuthor: Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import ClientSession from "@/app/components/features/clientsession";
import "@copilotkit/react-ui/styles.css";
import "@radix-ui/themes/styles.css";
import "./globals.css";
import { authSession } from "@/app/lib/account/authSession";
import ThemeProvider from "@/app/components/features/themeprovider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Advise",
  description: "Advisor app",
};

/**
 * Root component, wrapping application in {@link ThemeProvider} and {@link ClientSession}.
 * @param param0 
 * @returns 
 */
export default async function RootLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  const session = await authSession();
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <ClientSession session={session}>
            {children}
          </ClientSession>
        </ThemeProvider>
      </body>
    </html>
  );
}
