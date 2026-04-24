import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { redirect } from "next/navigation"

// Components
import { Flex, Box, Button, Separator } from "@radix-ui/themes";

// Library
import Sidebar from "@/app/components/navigation/aside";
import { UserContextProvider } from "@/app/lib/account/user_context";
import { get_curr_context } from "@/app/lib/account/account_db_utils";
import { authSession } from "@/app/lib/account/authSession";

import { signOut } from "next-auth/react";
import path from "path";
import { writeFile } from "fs";
import fs from 'fs';

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

async function createJSON(student_id: string) {
  const id = Number(student_id);
  try {
    const filePath = path.join(__dirname, "../../../../../../../student_id.json");
    const JSONString = JSON.stringify({ student_id: id})
    fs.writeFileSync(filePath, JSONString, 'utf-8');
    console.log(`WRITE SUCCESS: ${filePath}`);
  } catch(e) {
    console.log("WRITE ERROR: ", e);
  }
}

export default async function DashboardLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  // session validation
  const session = await authSession();
  if(!session) {
      redirect("/login");
  }
  
  const currContext = await get_curr_context(session.user.account_type);
  if(!currContext) {
    await signOut({callbackUrl:"/login"});
    redirect("/login");
  }

  if ( "StudentID" in currContext.userData ) {
    await createJSON(currContext.userData.StudentID.data);
  }

  return (
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
  );
}
