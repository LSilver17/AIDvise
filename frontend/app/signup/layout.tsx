import LoginLayout from "@/app/components/layout/accountstartlayout"
import { redirect } from "next/navigation";
import { authSession } from "@/app/lib/account/authSession";

/**
 * Base layout for login, checking session to redirect user to dashboard if logged
 * in.
 * @returns 
 */
export default async function CreationPage ({ children, }: Readonly<{children: React.ReactNode;}>) {
    const session = await authSession();
    if(session) {
        redirect("/dashboard");
    }

    return (
        <LoginLayout href="/login" buttText="Log in">
            {children}
        </LoginLayout>
    );
}