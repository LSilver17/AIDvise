"use client"

import { Form } from "radix-ui"; 
import { Flex } from "@radix-ui/themes"
import { SubmitEventHandler, useState } from "react";
import { Responsive } from "@radix-ui/themes/props";
import FormField from "@/app/components/features/forms/formfield";
import FormSubmit from "@/app/components/features/forms/formsubmit";
import "@/app/globals.css"

type Props = {
    onSubmit: SubmitEventHandler<HTMLFormElement>;
    justify?: Responsive<"center" | "start" | "end" | "baseline" | "stretch"> | undefined,
    children: React.ReactNode;
}

export default function FormRootLayout({onSubmit, justify, children} : Props) {
    justify = justify ?? "center";
    return (
        <Form.Root onSubmit={onSubmit}>
            <Flex 
                justify="between" 
                direction="column" 
                gap="4"  
                overflow="hidden" 
                flexGrow="0" 
                flexShrink="0"
                align={justify}
                wrap="wrap"
            >
                {children}
            </Flex>
        </Form.Root>
    );
};