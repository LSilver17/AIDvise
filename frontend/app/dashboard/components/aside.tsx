"use client"

import { Flex, Button } from "@radix-ui/themes";
import { HomeIcon, BellIcon, ChatBubbleIcon } from "@radix-ui/react-icons";
import { useRouter } from "next/navigation";

export default function Sidebar () {
    const router = useRouter();
    return (
        <Flex direction="column" justify="between" align="center" p="4" flexGrow="1">
            <Button size="4" onClick={() => router.push('/dashboard/home')}>
                <HomeIcon/>Home
            </Button>
            <Button size="4" onClick={() => router.push('/dashboard/alerts')}>
                <BellIcon/>Alerts
            </Button>
            <Button size="4" onClick={() => router.push('/dashboard/chat')}>
                <ChatBubbleIcon/>Chat
            </Button>
        </Flex>
    );
}