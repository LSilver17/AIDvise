"use client"

import { Form } from "radix-ui"; 
import { Flex, Text, TextField} from "@radix-ui/themes"
import "@/app/globals.css"

type Props = {
    label: string, 
    inputName: string, 
    message?: string;
    isPassword?: boolean;
}

export default function FormField({label, inputName, message, isPassword} : Props) {
    var inputType = isPassword ? "password" : "text";
    return (
        <Form.Field name={inputName}>
            <Flex justify="start" width="100%" direction="column" align="center" flexGrow="0" flexShrink="0" minHeight="50px">
                <Form.Control asChild name={inputName} type={inputType}>
                    <TextField.Root required placeholder={label} size="3" style={{backgroundColor:"white"}}/>
                </Form.Control>
                {message ? 
                    (
                        <Text>{message}</Text>
                    ) : null
                }
                <Form.Message match="valueMissing">Please enter a {isPassword ? "password" : inputName}</Form.Message>
            </Flex>
        </Form.Field>
    );
};