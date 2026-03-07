import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

// Components
import { Flex, Box, Button, Separator } from "@radix-ui/themes"

// User Components
import Sidebar from "./components/aside";

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

export default function DashboardLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  return (
    <Flex direction="column" height="100vh" width="100vw">
      <Flex direction="row" align="stretch" flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
        <Flex width="200px">
          <Sidebar/>
        </Flex>
        <Flex flexGrow="1" flexShrink="1" minHeight="0" minWidth="0">
          {children}  
        </Flex>  
      </Flex>
      <Flex className="orangeBG" direction="row" height="100px" flexShrink="0">

      </Flex>
    </Flex>
  );
}
