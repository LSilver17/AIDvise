import LoginLayout from "@/app/components/layout/accountstartlayout"
import { redirect } from "next/navigation";
//import auth from "@/app/api/auth/[...nextauth]/route"

export default async function LoginPage ({ children, }: Readonly<{children: React.ReactNode;}>) {
    //const session = sess
    return (
        <LoginLayout href="/signup" buttText="Register">
            {children}
        </LoginLayout>
    );
}