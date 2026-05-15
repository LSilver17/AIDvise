/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

// Library Imports
import { Flex, Button, Separator, Em, ScrollArea } from "@radix-ui/themes";
import { HomeIcon, BellIcon, ChatBubbleIcon, PersonIcon } from "@radix-ui/react-icons";
import { useRouter } from "next/navigation";

// Lib
import SidebarButton from "@/app/components/navigation/navbutton";
import Logo from "@/app/components/visual/logo"
import SignOut from "@/app/components/features/signout"
import DashTitle from "@/app/components/visual/title"
import { useUserData } from "@/app/lib/account/user_context";
import type { UserMetadata } from "@/app/lib/account/account_db_utils";
import type { AccountType } from "@/app/lib/account/account_type";

/**
 * Component constructing the sidebar used for navigating the dashboard.
 * Account type is fetched from context with the {@link useUserData} hook and is used for conditional
 * rendering of navigation buttons.
 * @returns 
 */
export default function Sidebar () {
    const { userMetadata } : { userMetadata: UserMetadata} = useUserData();
    const account_type: AccountType = userMetadata.AccountType;
    return (
        <Flex direction="column" justify="start" align="stretch" p="10px" flexGrow="1" gapY="5" className="menuColor">
            {/*Logo Section*/}
            <DashTitle size="8">
                <Logo/>
            </DashTitle>
            {/*Main Dashboard*/}
            <Flex direction="column" justify="start" align="stretch" gapY="5" flexGrow="1">
                <SidebarButton href="/dashboard/home">
                    <HomeIcon/>Home
                </SidebarButton>
                {
                    (account_type === "Student") ? 
                    <SidebarButton href="/dashboard/alerts">
                        <BellIcon/>Alerts
                    </SidebarButton> :
                    <SidebarButton href="/dashboard/students">
                        <PersonIcon/>Students
                    </SidebarButton>
                }
                
                <SidebarButton href="/dashboard/chat">
                    <ChatBubbleIcon/>Chat
                </SidebarButton>
                <SidebarButton href="/dashboard/account">
                    <PersonIcon/>Account
                </SidebarButton>
            </Flex><Flex direction="column" justify="end" align="stretch" gapY="5" flexGrow="1" pb="3">
                <SignOut/>
            </Flex>
        </Flex>
    );
}