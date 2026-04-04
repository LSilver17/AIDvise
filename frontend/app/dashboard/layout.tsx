import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Geist, Geist_Mono } from "next/font/google";

// Components
import { Flex, Box, Button, Separator } from "@radix-ui/themes";

// Library
import Sidebar from "@/app/components/navigation/aside";
import { UserContextProvider } from "@/app/lib/account/user_context";
import { getUserObject } from "@/app/lib/account/account_db_utils";
import type { UserMetadata } from "@/app/lib/account/account_db_utils";

// Helpers
import {authSession} from "@/app/lib/account/authSession";
import { useUserData } from "@/app/lib/account/user_context";

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
  const session = await authSession();
  if(!session) {
    redirect("/login");
  }

  const userData = await getUserObject();
  const userMetadata: UserMetadata = {
    AccountType: session.user.account_type,
    Username: session.user.username
  }

  const currContext = {
    userData: userData,
    metadata: userMetadata
  };

  return (
    <Flex direction="column" height="100vh" width="100vw">
      <Flex direction="row" align="stretch" flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
        <Flex flexShrink="1" minHeight="0" minWidth="300px" maxWidth="300px" overflow="hidden">
          <Sidebar/>
        </Flex>
        <Flex flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
          <UserContextProvider currContext={currContext}>{children}</UserContextProvider>
        </Flex>  
      </Flex>
    </Flex>
  );
}
