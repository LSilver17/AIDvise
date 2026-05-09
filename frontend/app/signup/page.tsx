/*
    Author: Sean Collins
    Copyright: 2026
*/
"use client"

import { HtmlContext } from "next/dist/server/route-modules/pages/vendored/contexts/entrypoints";
import { SubmitEventHandler } from "react";
import { signIn } from "next-auth/react";
import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

// User Components
import RegistrationForm from "@/app/components/features/forms/formlayout";
import FormField from "@/app/components/features/forms/formfield";
import SelectField from "@/app/components/features/forms/formfieldsel";
import FormSubmit from "@/app/components/features/forms/formsubmit";

// Library
import type { ErrorTypes } from "@/app/lib/form/form_test_cases";
import { FormError, registrationValidationTests } from "@/app/lib/form/form_test_cases";
import { alert_popup } from "@/app/lib/alerts/alert_popup";
import type { AccountType } from '@/app/lib/account/account_type'
import { Flex } from "@radix-ui/themes";

/**
 * Registration page component that defines an error state and form submission handler for
 * user-entered credentials. Form by default handles basic input validation like 
 * missing fields. After passing the initial check, validation tests are ran on the 
 * input strings. If validation fails or an error is thrown during API call, the error
 * is displayed via a window popup on the front-end. If caught before submission, error
 * messages are displayed near the form field.
 * @returns 
 */
export default function SignUp () {
    const router = useRouter();

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
        const account_type = formData.get("account_type") as AccountType;
        const id = formData.get("id") as string;

        try {
            const errorCheck = registrationValidationTests(username, password, conf_password, account_type, id);

            if(errorCheck) {
                throw errorCheck;
            }

            // Sends POST request to registration endpoint
            const response = await fetch(`/api/register`, {
                method: "POST",
                body: JSON.stringify({
                    username: username,
                    password: password,
                    account_type: account_type,
                    id: id,
                }),
            });

            const data = await response.json();

            // handle the response
            if(response) {
                if (response.ok) {
                    // redirect to login if creation succeeded
                    router.push('/login');
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
        <RegistrationForm justify="start" onSubmit={handler}>
            <Flex direction="row" height="9rem" mb="6" gap="2">
                <Flex direction="column" justify="start">
                    <FormField label="Username" inputName="username" message={errors?.username}/>
                    <FormField label="Password" inputName="password" message={errors?.password} isPassword/>
                </Flex>

                <Flex direction="column" justify="between">
                    <FormField label="Student/Advisor ID" inputName="id" message={errors?.id}/>
                    <FormField label="Confirm password" inputName="conf_password" message={errors?.check_password} isPassword/>
                </Flex>
            </Flex>

            <Flex direction="row" justify="center" width="100%" align="end">
                <SelectField inputName="account_type" message={errors?.account_type}/>
            </Flex>
            
            <FormSubmit>
                Create Account
            </FormSubmit>
        </RegistrationForm>
    );
}