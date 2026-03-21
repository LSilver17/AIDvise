"use client"

import { HtmlContext } from "next/dist/server/route-modules/pages/vendored/contexts/entrypoints";
import { SubmitEventHandler } from "react";
import { redirect } from "next/navigation";
import { signIn } from "next-auth/react";
import { useState } from "react";

// User Components
import RegistrationForm from "@/app/components/features/forms/formlayout";
import FormField from "@/app/components/features/forms/formfield";
import SelectField from "@/app/components/features/forms/formfieldsel";
import FormSubmit from "@/app/components/features/forms/formsubmit";

// Library
import type { ErrorTypes } from "@/app/lib/form_test_cases";
import { FormError, registrationValidationTests } from "@/app/lib/form_test_cases";
import { alert_popup } from "@/app/lib/alert_popup";

export default function SignUp () {

    const [errors, setErrors] = useState<ErrorTypes>({});

    // Form submission handler
    const handler : SubmitEventHandler<HTMLFormElement> = async (event) => {
        // Prevents default handling
        event.preventDefault();

        // Extracts form data
        const formData = new FormData(event.currentTarget);

        // Entered user and password
        const username = formData.get("username") as string;
        const password = formData.get("password") as string;
        const conf_password = formData.get("conf_password") as string;
        const account_type = formData.get("account_type") as string;

        try {
            const errorCheck = registrationValidationTests(username, password, conf_password, account_type);

            if(errorCheck) {
                throw errorCheck;
            }

            // Sends POST request to registration endpoint
            const response = await fetch("/api/register", {
                method: "POST",
                body: JSON.stringify({
                    username: username,
                    password: password,
                    account_type: account_type,
                }),
            });

            const data = await response.json();

            // handle the response
            if(response) {
                if (response.ok) {
                    // redirect to login if creation succeeded
                    redirect('/login');
                } else {
                    throw new FormError({
                        api_error: `API Request Failure: ${data.error}`,
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
        <RegistrationForm onSubmit={handler}>
            <FormField label="Username" inputName="username" message={errors?.username}/>
            <FormField label="Password" inputName="password" message={errors?.password} isPassword/>
            <FormField label="Confirm password" inputName="conf_password" message={errors?.check_password} isPassword/>
            <SelectField inputName="account_type" message={errors?.account_type}/>
            <FormSubmit>
                Create Account
            </FormSubmit>
        </RegistrationForm>
    );
}