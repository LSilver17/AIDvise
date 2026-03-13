"use client"

import { HtmlContext } from "next/dist/server/route-modules/pages/vendored/contexts/entrypoints";
import { SubmitEventHandler } from "react";
import { redirect } from "next/navigation";

// User Components
import RegistrationForm from "@/app/components/features/registration";

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

        // Sends POST request to registration endpoint
        const response = await fetch("/api/register", {
            method: "POST",
            body: JSON.stringify({
                username: username,
                password: password,
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
        <> 
            <RegistrationForm onSubmit={handler}></RegistrationForm>
        </>
    );
}