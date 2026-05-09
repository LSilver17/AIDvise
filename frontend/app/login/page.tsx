/*
    Author: Sean Collins
    Copyright: 2026
*/
"use client"

import { SubmitEventHandler } from "react";
import { signIn } from "next-auth/react";
import LoginForm from "@/app/components/features/forms/formlayout";
import FormField from "@/app/components/features/forms/formfield";
import FormSubmit from "@/app/components/features/forms/formsubmit";
import { useState } from "react";
import { redirect } from "next/navigation";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

// Library
import type { ErrorTypes } from "@/app/lib/form/form_test_cases";
import { FormError, loginValidationTests } from "@/app/lib/form/form_test_cases";
import { alert_popup } from "@/app/lib/alerts/alert_popup";

/**
 * Login page component that defines an error state and form submission handler for
 * user-entered credentials. Form by default handles basic input validation like 
 * missing fields. After passing the initial check, validation tests are ran on the 
 * input strings. If validation fails or an error is thrown during API call, the error
 * is displayed via a window popup on the front-end. If caught before submission, error
 * messages are displayed near the form field.
 * @returns 
 */
export default function Login () {
    const router = useRouter();
    
    const [errors, setErrors] = useState<ErrorTypes>({});

    
    const handler: SubmitEventHandler<HTMLFormElement> = async (event) => {
        
        // prevents implicit event handling
        event.preventDefault();

        // gets the form element that was submitted and extracts data
        const formData = new FormData(event.currentTarget);

        // extracts key-value pairs
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;

        try {
            const errorCheck = loginValidationTests(username, password);
            if(errorCheck) {
                throw errorCheck;
            }
            // Send sign in request to API endpoint, redirecting to dashboard if valid
            const response = await signIn("credentials", {
                username: username,
                password: password,
                redirect: false,
            });

            // Handle request response
            
            if(response) {
                if(response.ok) {
                    router.push('dashboard/home');
                }
                else {
                    throw new FormError({
                        api_error: `API Request Failure: Invalid credentials`,
                    });
                }
            }
        }
        catch(e) {
            if(e instanceof FormError) {
                setErrors(e.errors);
                if(e.errors?.api_error) {
                    alert_popup(e.errors.api_error);
                }
                return;
            }
        }
    }
    return (
        <LoginForm onSubmit={handler}>
            <FormField label="Enter Username" inputName="username" message={errors?.username}/>
            <FormField label="Enter Password" inputName="password" message={errors?.password} isPassword/>
            <FormSubmit>
                Sign In
            </FormSubmit>
        </LoginForm>
    );
}