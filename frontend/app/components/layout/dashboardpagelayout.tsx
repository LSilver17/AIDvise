/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

import { Flex, ScrollArea } from "@radix-ui/themes"

export type Props = {
    children: React.ReactNode,
}

/**
 * Scrollable area layout for containing dashboard pages.
 * @param props.children - Child elements to be held in scrollable container.
 * @returns 
 */
export default function DashboardLayout({children}: Props) {
    return(
        <ScrollArea type="scroll" scrollbars="vertical" style = {{height: "100%", width:"100%", minHeight: "0"}}>
            <Flex p="6" direction="column" flexGrow="1" gap="30px" width="100%">
                {children}
            </Flex>  
        </ScrollArea>  
    );
}