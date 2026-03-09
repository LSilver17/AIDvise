"use client"

import { Form } from "radix-ui"; 
import { Flex } from "@radix-ui/themes"
import "@/app/globals.css"
import { SubmitEventHandler } from "react";

// used for type checking of incoming submit prop
type Props = {
    onSubmit: SubmitEventHandler<HTMLFormElement>;
}

export default function LoginForm({onSubmit} : Props) {
    return (
        <Form.Root onSubmit={onSubmit}>
            <Flex justify="center" direction="column" gap="6">
                <Form.Field name="username">
                    <Flex justify="center" width="100%" direction="column" align="start">
                        <Form.Label>Username</Form.Label>
                        <Form.Control asChild>
                            <input name="username" type="username" required/>
                        </Form.Control>
                    </Flex>
                </Form.Field>

                <Form.Field name="password">
                    <Flex justify="center" width="100%" direction="column" align="start">
                        <Form.Label>Password</Form.Label>
                        <Form.Control asChild>
                            <input name="password" type="password" required/>
                        </Form.Control>
                    </Flex>
                </Form.Field>

                <Flex justify="center" width="100%" direction="column" align="center">
                    <Form.Submit asChild>
                        <button className="nightBG">
                            Login
                        </button>
                    </Form.Submit>
                </Flex>
            </Flex>
        </Form.Root>
    );
};