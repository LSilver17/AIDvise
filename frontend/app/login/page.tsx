"use client"

import { SubmitEventHandler } from "react";
import { signIn } from "next-auth/react";
import LoginForm from "@/app/components/features/forms/formlayout";
import FormField from "@/app/components/features/forms/formfield";
import FormSubmit from "@/app/components/features/forms/formsubmit";

export default function Login () {
    const handler: SubmitEventHandler<HTMLFormElement> = async (event) => {
        
        // prevents implicit event handling
        event.preventDefault();

        // gets the form element that was submitted and extracts data
        const formData = new FormData(event.currentTarget);

        // extracts key-value pairs
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;

        // Send sign in request to API endpoint, redirecting to dashboard if valid
        const response = await signIn("credentials", {
            username: username,
            password: password,
            callbackUrl: '/dashboard/home'
        });

        // Handle request response
        if(response) {
            if (!(response.ok)) {
                console.log("Invalid login.");
            }
        }
    }
    return (
        <LoginForm onSubmit={handler}>
            <FormField label="Enter Username" inputName="username" message="Please enter a username."/>
            <FormField label="Enter Password" inputName="password" message="Please enter a password." isPassword/>
            <FormSubmit>
                Sign In
            </FormSubmit>
        </LoginForm>
    );
}