"use client"

import { HtmlContext } from "next/dist/server/route-modules/pages/vendored/contexts/entrypoints";
import { SubmitEventHandler } from "react";
import { redirect } from "next/navigation";
import { signIn } from "next-auth/react";

// User Components
import RegistrationForm from "@/app/components/features/forms/formlayout";
import FormField from "@/app/components/features/forms/formfield";
import FormSubmit from "@/app/components/features/forms/formsubmit";

export default function SignUp () {
    // Form submission handler
    const handler : SubmitEventHandler<HTMLFormElement> = async (event) => {
        // Prevents default handling
        event.preventDefault();

        // Extracts form data
        const formData = new FormData(event.currentTarget);

        // Entered user and password
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;
        const account_type = formData.get("account_type") as string;

        // Sends POST request to registration endpoint
        const response = await fetch("/api/register", {
            method: "POST",
            body: JSON.stringify({
                username: username,
                password: password,
                account_type: account_type,
            }),
        });

        // handle the response
        if(response) {
            if (response.status) {
                // redirect to login if creation succeeded
                redirect('/login');
            } else {
                console.log("Account creation failed.");
            }
        }
    }
    
    return (
        <RegistrationForm onSubmit={handler}>
            <FormField label="Username" inputName="username" message="Please enter a username."/>
            <FormField label="Password" inputName="password" message="Please enter a password." isPassword/>
            <FormField label="Password" inputName="password" message="Please enter a password." isPassword/>
            <FormSubmit>
                Create Account
            </FormSubmit>
        </RegistrationForm>
    );
}