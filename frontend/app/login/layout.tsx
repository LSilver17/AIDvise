import LoginLayout from "@/app/components/layout/accountstartlayout"

export default function LoginPage ({ children, }: Readonly<{children: React.ReactNode;}>) {
    return (
        <LoginLayout href="/signup" buttText="Register">
            {children}
        </LoginLayout>
    );
}