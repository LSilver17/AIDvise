"use client"

import { Flex } from "@radix-ui/themes"

type Props = {
    children: React.ReactNode,
}

export default function DashboardLayout({children}: Props) {
    return(
        <Flex p="10px" direction="column" flexGrow="1">
            {children}
        </Flex>    
    );
}