"use client"

import { Form } from "radix-ui"; 
import { Flex, TextField, Select } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";
import "@/app/globals.css"

type FieldProps = {
    label?: string, 
    inputName: string, 
    message: string;
    isPassword?: boolean;
    required?: boolean;
    size?: Responsive<"1" | "2" | "3">;
}

type SelectProps = {
    required?: boolean;
    size?: Responsive<"1" | "2" | "3">;
}

function FieldSelect({required, size}: SelectProps) {
    return (
        <Select.Root size={size} required={required}>
            <Select.Trigger placeholder="Account Type" style={{backgroundColor:"white"}}/>
            <Select.Content>
                <Select.Item value="student">Student</Select.Item>
                <Select.Item value="advisor">Advisor</Select.Item>
            </Select.Content>
        </Select.Root>
    );
}

export default function FormField({label, inputName, message, isPassword, required, size} : FieldProps) {
    var inputType = isPassword ? "password" : "other";
    size = size ?? "3";
    return (
        <Form.Field name={inputName}>
            <Flex justify="start" width="100%" direction="column" align="center" flexGrow="0" flexShrink="0" minHeight="50px">
                <Form.Control asChild name={inputName} type={inputType}>

                    <FieldSelect required size={size}/>
                </Form.Control>
                <Form.Message match="valueMissing">{message}</Form.Message>
            </Flex>
        </Form.Field>
    );
};