"use client"

// Library Imports
import { Flex, Button, Separator } from "@radix-ui/themes";
import { HomeIcon, BellIcon, ChatBubbleIcon, PersonIcon } from "@radix-ui/react-icons";
import { useRouter } from "next/navigation";

// User Imports
import SidebarButton from "@/app/components/navigation/navbutton";
import Logo from "@/app/components/visual/logo"
import SignOut from "@/app/components/features/signout"

export default function Sidebar () {
    const router = useRouter();
    return (
        <Flex direction="column" justify="start" align="stretch" p="4" flexGrow="1" gapY="5" className="bg-orange-500">
            {/*Logo Section*/}
            <Flex direction="column" justify="start" align="center" gapY="5">
                <Logo size="8"/>
                <Separator orientation="horizontal" size="4"/>
            </Flex>
            {/*Main Dashboard*/}
            <Flex direction="column" justify="start" align="stretch" gapY="5" flexGrow="1">
                <SidebarButton href="/dashboard/home">
                    <HomeIcon/>Home
                </SidebarButton>
                <SidebarButton href="/dashboard/alerts">
                    <BellIcon/>Alerts
                </SidebarButton>
                <SidebarButton href="/dashboard/chat">
                    <ChatBubbleIcon/>Chat
                </SidebarButton>
                <SidebarButton href="/dashboard/account">
                    <PersonIcon/>AccountPH
                </SidebarButton>
            </Flex><Flex direction="column" justify="end" align="stretch" gapY="5" flexGrow="1" pb="3">
                <SignOut/>
            </Flex>
        </Flex>
    );
}