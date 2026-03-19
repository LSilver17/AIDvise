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