import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { CopilotKit } from "@copilotkit/react-core";
import ClientSession from "@/app/components/features/clientsession";
import "@copilotkit/react-ui/styles.css";
import "@radix-ui/themes/styles.css";
import "./globals.css";
import authCheck from "@/app/lib/authCheck";
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
  title: "advise.",
  description: "Advisor app",
};

export default async function RootLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  const session = await authCheck();
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <CopilotKit runtimeUrl="/api/copilotkit" agent="sample_agent">
            <ClientSession session={session}>
              {children}
            </ClientSession>  
          </CopilotKit>
        </ThemeProvider>
      </body>
    </html>
  );
}
