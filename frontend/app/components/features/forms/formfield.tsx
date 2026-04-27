"use client"

import { Form } from "radix-ui"; 
import { Flex, Text, TextField} from "@radix-ui/themes"
import { Responsive } from "@radix-ui/themes/props";
import "@/app/globals.css"

type Props = {
    label: string, 
    inputName: string, 
    //error message
    message?: string;
    isPassword?: boolean;
    //displayed when field is missing
    hasMissingMessage?: boolean
}

/**
 * Component for adding a single field to a form.
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
            <Flex justify="start" width="100%" direction="column" align="center" flexGrow="0" flexShrink="0" height="5rem">
                <Form.Control asChild name={inputName} type={inputType}>
                    <TextField.Root required placeholder={label} size="3" style={{backgroundColor:"white"}}/>
                </Form.Control>
                {
                    message ? 
                    (
                        <Text>{message}</Text>
                    ) : null
                }
                {
                    hasMissingMessage ?
                    (
                        <Form.Message match="valueMissing">Please enter a {isPassword ? "password" : inputName}</Form.Message>
                    ) : null
                }
                
            </Flex>
        </Form.Field>
    );
};