import LoginLayout from "@/app/components/layout/accountstartlayout"
import { redirect } from "next/navigation";
import { authSession } from "@/app/lib/account/authSession";

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