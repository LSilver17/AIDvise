/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

import { Form } from "radix-ui"; 
import { Flex, Button } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props"
import React, { SubmitEventHandler, useState } from "react";
import "@/app/globals.css"

type Props = {
    children: React.ReactNode,
    size?: Responsive<"4" | "1" | "2" | "3"> | undefined;
}

/**
 * Submission button for form component.
 * @param props.size - Button size.
 * @returns 
 */
export default function FormSubmitButton({children, size} : Props) {
    size = size ?? "4";
    return (
        <Flex justify="start" width="100%" direction="column" align="center" minHeight="20px">
            <Form.Submit asChild>
                <Button radius="full" style={{cursor:"pointer"}} color="orange" size = "4">
                    {children}
                </Button>
            </Form.Submit>
        </Flex>
    );
};