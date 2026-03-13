"use client"

import { Form } from "radix-ui"; 
import { Flex } from "@radix-ui/themes"
import { SubmitEventHandler, useState } from "react";
import "@/app/globals.css"
// used for type checking of incoming submit prop
type Props = {
    onSubmit: SubmitEventHandler<HTMLFormElement>;
}

export default function RegistrationForm({onSubmit} : Props) {
    return (
        <Form.Root onSubmit={onSubmit}>
            <Flex justify="center" direction="column" gap="6">
                <Form.Field name="username">
                    <Flex justify="center" width="100%" direction="column" align="start">
                        <Form.Label>Username</Form.Label>
                        <Form.Control asChild>
                            <input name="username" type="username" required/>
                        </Form.Control>
                        <Form.Message match="valueMissing">Please enter a username.</Form.Message>
                    </Flex>
                </Form.Field>

                <Form.Field name="password">
                    <Flex justify="center" width="100%" direction="column" align="start">
                        <Form.Label>Password</Form.Label>
                        <Form.Control asChild>
                            <input name="password" type="password" required/>
                        </Form.Control>
                        <Form.Message match="valueMissing">Please enter a password.</Form.Message>
                    </Flex>
                </Form.Field>

                <Flex justify="center" width="100%" direction="column" align="center">
                    <Form.Submit asChild>
                        <button className="nightBG">
                            Create Account
                        </button>
                    </Form.Submit>
                </Flex>
            </Flex>
        </Form.Root>
    );
};