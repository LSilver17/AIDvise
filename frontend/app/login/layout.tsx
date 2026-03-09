import { Flex } from "@radix-ui/themes"
import Logo from "@/app/components/visual/logo";

export default function LoginPage ({ children, }: Readonly<{children: React.ReactNode;}>) {
    return (
        <Flex height="100vh" width="100vw" direction="column" justify="center" align="center" gap="9">
            <Flex width="30%" height="20%" justify="center" align="center" className="orangeBG">
                <Logo/>
            </Flex>
            <Flex width="30%" height="40%" justify="center" align="center" className="orangeBG"> 
                {children}
            </Flex>
        </Flex>
    );
}