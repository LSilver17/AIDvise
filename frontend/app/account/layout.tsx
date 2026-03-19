import { Button, Flex } from "@radix-ui/themes"
import { redirect } from "next/navigation";
import authCheck from "@/app/lib/authCheck";
import NavButton from "@/app/components/navigation/navbutton";

export default async function AccountView ({ children, }: Readonly<{children: React.ReactNode;}>) {
  const session = await authCheck();
  if(!session) {
    redirect("/login");
  }
    return (
        <Flex height="100vh" width="100vw" direction="column" justify="center" align="center" gap="9">
            <Flex width="30%" height="70%" justify="center" align="center" className="orangeBG">
                {children}
            </Flex>
            <NavButton href="/dashboard/home">
                Return to dashboard
            </NavButton>
        </Flex>
    );
}