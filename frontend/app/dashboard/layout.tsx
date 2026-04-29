/*
    Author: Sean Collins
*/
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { redirect } from "next/navigation"

// Components
import { Flex, Box, Button, Separator } from "@radix-ui/themes";
import { CopilotKit } from "@copilotkit/react-core";

// Library
import Sidebar from "@/app/components/navigation/aside";
import { UserContextProvider } from "@/app/lib/account/user_context";
import { get_curr_context } from "@/app/lib/account/account_db_utils";
import { authSession } from "@/app/lib/account/authSession";

import { signOut } from "next-auth/react";

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

/**
 * Base dashboard layout, on mount authorizing access and initializing user context if there
 * is indeed an active session. Wraps children with CopilotKit and UserContext providers.
 * @returns 
 */
export default async function DashboardLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  // session validation
  const session = await authSession();
  if(!session) {
      redirect("/login");
  }
  
  const currContext = await get_curr_context(session.user.account_type);
  if(!currContext || !currContext.userMetadata.AccountType) {
    await signOut({callbackUrl:"/login"});
    redirect("/login");
  }

  const academicID = ( "StudentID" in currContext.userData ) ? currContext.userData.StudentID.data : currContext.userData.AdvisorID.data;
  const accountType = currContext.userMetadata.AccountType;

  return (
    <CopilotKit 
      runtimeUrl="/api/copilotkit"
    >
      <Flex direction="column" height="100vh" width="100vw">
        <Flex direction="row" align="stretch" flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
          <UserContextProvider currContext={currContext}>
            <Flex flexShrink="1" minHeight="0" minWidth="300px" maxWidth="300px" overflow="hidden">
              <Sidebar/>
            </Flex>
            <Flex flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
              {children}
            </Flex>
          </UserContextProvider>
        </Flex>
      </Flex>
    </CopilotKit>
  );
}
