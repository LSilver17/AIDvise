/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import LoginLayout from "@/app/components/layout/accountstartlayout"
import { redirect } from "next/navigation";
import { authSession } from "@/app/lib/account/authSession";

/**
 * Base layout for login, checking session and redirecting user to dashboard if logged
 * in.
 * @returns 
 */
export default async function LoginPage ({ children, }: Readonly<{children: React.ReactNode;}>) {
    const session = await authSession();
    if(session) {
        redirect("/dashboard");
    }

    return (
        <LoginLayout href="/signup" buttText="Register">
            {children}
        </LoginLayout>
    );
}