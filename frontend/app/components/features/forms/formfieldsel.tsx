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

function FieldSelect({required, name}: SelectProps) {
    return (
        <select required={required} name={name}>
            <option value="student">Student</option>
            <option value="advisor">Advisor</option>
        </select>
        // currently not compatible with radix elements
        // <Select.Root size={size} required={required}>
        //     <Select.Trigger placeholder="Account Type" style={{backgroundColor:"white"}}/>
        //     <Select.Content>
        //         <Select.Item value="student">Student</Select.Item>
        //         <Select.Item value="advisor">Advisor</Select.Item>
        //     </Select.Content>
        // </Select.Root>
    );
}

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