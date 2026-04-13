"use client"

import { Flex, ScrollArea } from "@radix-ui/themes"

type Props = {
    children: React.ReactNode,
}

export default function DashboardLayout({children}: Props) {
    return(
        <ScrollArea type="scroll" scrollbars="vertical" style = {{height: "100%", width:"100%", minHeight: "0"}}>
            <Flex p="6" direction="column" flexGrow="1" gap="30px" width="100%">
                {children}
            </Flex>  
        </ScrollArea>  
    );
}