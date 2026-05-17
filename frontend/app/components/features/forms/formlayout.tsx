/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

import { Form } from "radix-ui"; 
import { Flex } from "@radix-ui/themes"
import { SubmitEventHandler, useState } from "react";
import { Responsive } from "@radix-ui/themes/props";
import FormField from "@/app/components/features/forms/formfield";
import FormSubmit from "@/app/components/features/forms/formsubmit";
import FormSelect from "@/app/components/features/forms/formfieldsel";
import "@/app/globals.css"

export type Props = {
    onSubmit: SubmitEventHandler<HTMLFormElement>;
    justify?: Responsive<"center" | "start" | "end" | "baseline" | "stretch"> | undefined,
    children: React.ReactNode;
}

/**
 * Root layout for form components ({@link FormField}, {@link FormSubmit}, {@link FormSelect}).
 * @param props.onSubmit - Form submission handler function.
 */
export default function FormRootLayout({onSubmit, justify, children} : Props) {
    justify = justify ?? "center";
    return (
        <Form.Root onSubmit={onSubmit}>
            <Flex 
                justify="between" 
                direction="column" 
                gap="2"  
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