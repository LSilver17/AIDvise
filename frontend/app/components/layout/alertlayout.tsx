"use client"

import { ScrollArea, Box, Flex } from "@radix-ui/themes";
import { AlertStatus, UserAlert } from "@/app/lib/alert"
import SingleAlert from "@/app/components/features/alert";
import React from "react";

type Props = {
    children: React.ReactNode;
}

export default function AlertLayout({children}: Props) {
    return (
    <>
        <ScrollArea type="scroll" style = {{width: "100%", height: "100%", minHeight: "0"}}>
            <Flex direction="column">
                {children}
            </Flex>
        </ScrollArea>
    </>
    );
}