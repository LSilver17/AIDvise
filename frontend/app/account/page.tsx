"use client"

import { Text } from "@radix-ui/themes"
import { useSession } from "next-auth/react";

export default function AccountInfo () {
    const session = useSession();
    return (
        <>
            <Text>
                Username: {session?.data?.user?.name}
            </Text>
        </>
    );
}