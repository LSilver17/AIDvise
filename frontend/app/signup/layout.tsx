import LoginLayout from "@/app/components/layout/accountstartlayout"

export default function CreationPage ({ children, }: Readonly<{children: React.ReactNode;}>) {
    return (
        <LoginLayout href="/login" buttText="Log in">
            {children}
        </LoginLayout>
    );
}