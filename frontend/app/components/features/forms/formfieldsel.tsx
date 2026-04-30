/*
    Author: Sean Collins
*/
"use client"

import { Form } from "radix-ui"; 
import { Flex, Text, Select } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";
import "@/app/globals.css"

type FieldProps = {
    label?: string, 
    inputName: string, 
    message?: string;
    isPassword?: boolean;
    required?: boolean;
    size?: Responsive<"1" | "2" | "3">;
}

type SelectProps = {
    required?: boolean;
    name: string;
}

/**
 * @param props.required
 * @param props.name
 */
function FieldSelect({required, name}: SelectProps) {
    return (
        <select required={required} name={name} title={name} style={{backgroundColor:"white", borderRadius:"8px", padding:"8px", cursor:"pointer"}}>
            <option style={{backgroundColor:"white", borderRadius:"8px", padding:"8px", cursor:"pointer"}} value="Student">Student</option>
            <option style={{backgroundColor:"white", borderRadius:"8px", padding:"8px", cursor:"pointer"}} value="Advisor">Advisor</option>
        </select>
    );
}

/**
 * Field component for dropdown selections. Currently only used for account type selection.
 * @param props.label - Placeholder text.
 * @param props.inputName - Input identifier.
 * @param props.required - Determines if field is required.
 */
export default function FormField({inputName, message, isPassword, required, size} : FieldProps) {
    var inputType = isPassword ? "password" : "text";
    size = size ?? "3";
    required = required ?? false;
    return (
        <Form.Field name={inputName}>
            <Flex justify="start" width="100%" direction="column" align="center" flexGrow="0" flexShrink="0" minHeight="50px">
                <Form.Control asChild name={inputName} type={inputType}>
                    <FieldSelect required={required} name={inputName}/>
                </Form.Control>
                {message ? 
                    (
                        <Text>{message}</Text>
                    ) : null
                }
                <Form.Message match="valueMissing">Please enter a {inputName}</Form.Message>
            </Flex>
        </Form.Field>
    );
};