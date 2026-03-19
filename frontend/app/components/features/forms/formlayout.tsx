"use client"

import { Form } from "radix-ui"; 
import { Flex } from "@radix-ui/themes"
import { SubmitEventHandler, useState } from "react";
import FormField from "@/app/components/features/forms/formfield";
import FormSubmit from "@/app/components/features/forms/formsubmit";
import "@/app/globals.css"

type Props = {
    onSubmit: SubmitEventHandler<HTMLFormElement>;
    children: React.ReactNode;
}

export default function FormRootLayout({onSubmit, children} : Props) {
    return (
        <Form.Root onSubmit={onSubmit}>
            <Flex 
                justify="between" 
                direction="column" 
                gap="6"  
                overflow="hidden" 
                flexGrow="0" 
                flexShrink="0"
                align="center"
            >
                {children}
            </Flex>
        </Form.Root>
    );
};