import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Geist, Geist_Mono } from "next/font/google";

// Components
import { Flex, Box, Button, Separator } from "@radix-ui/themes";

// User Components
import Sidebar from "@/app/components/navigation/aside";
import SignOut from "@/app/components/features/signout";
import ClientSession from "@/app/components/features/clientsession";

// Helpers
import {authCheck} from "@/app/lib/authCheck";

// Hooks & Types
import { getSession } from "next-auth/react";
import type { Session } from "next-auth";

// const geistSans = Geist({
//   variable: "--font-geist-sans",
//   subsets: ["latin"],
// });

// const geistMono = Geist_Mono({
//   variable: "--font-geist-mono",
//   subsets: ["latin"],
// });

export const metadata: Metadata = {
  title: "Dashboard",
  description: "User dashboard",
};

export default async function DashboardLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  const session = await authCheck();
  if(!session) {
    redirect("/login");
  }
  return (
    <Flex direction="column" height="100vh" width="100vw">
      <Flex direction="row" align="stretch" flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
        <Flex flexShrink="1" minHeight="0" minWidth="300px" maxWidth="300px" overflow="hidden">
          <Sidebar/>
        </Flex>
        <Flex flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
          {children}
        </Flex>  
      </Flex>
    </Flex>
  );
}
