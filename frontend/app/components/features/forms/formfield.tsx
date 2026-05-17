/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

import { Form } from "radix-ui"; 
import { Flex, Text, TextField, Grid} from "@radix-ui/themes"
import { Responsive } from "@radix-ui/themes/props";
import "@/app/globals.css"

export type Props = {
    label: string, 
    inputName: string, 
    //error message
    message?: string;
    isPassword?: boolean;
    //displayed when field is missing
    hasMissingMessage?: boolean
}

function missingMessage(hasMissingMessage: boolean, isPassword: boolean, inputName: string) {
    return (
        <>
        {
            hasMissingMessage ?
            (
                <Form.Message match="valueMissing">Please enter a {isPassword ? "password" : inputName}</Form.Message>
            ) : null
        }
        </>
    )
}

function errorMessage(message: string) {
    return (
        <Text>{message}</Text>
    )
}

/**
 * Component for adding a single field to a form. Contains space for field and form validation error message.
 * @param props.label - Placeholder text when nothing is entered in field.
 * @param props.inputName - Identifier for form data.
 * @param props.message - Accompanying field message.
 * @param props.isPassword - Determines whether to hide inputs within the form.
 * @param props.hasMissingMessage - Determines whether to display a message when field is empty.
 */
export default function FormField({label, inputName, message, isPassword, hasMissingMessage} : Props) {
    var inputType = isPassword ? "password" : "text";
    hasMissingMessage = hasMissingMessage ?? true;
    return (
        <Form.Field name={inputName}>
            <Grid 
                justify="center" 
                width="12rem" 
                columns="1" 
                rows="2" 
                align="center" 
                flexGrow="0" 
                flexShrink="0" 
                height="5.2rem" 
                overflow="clip" 
                minHeight="0" 
                minWidth="0" 
                mt="1" mb="1"
            >
                <Form.Control asChild name={inputName} type={inputType}>
                    <TextField.Root required placeholder={label} size="3" style={{backgroundColor:"white"}}/>
                </Form.Control>
                <Flex flexShrink="0">
                {
                    (message ? 
                        errorMessage(message as string) : missingMessage(hasMissingMessage, isPassword as boolean, inputName)
                    )
                }
                </Flex>
            </Grid>
        </Form.Field>
    );
};