import Logo from "@/app/components/visual/logo"
import NavButton from "@/app/components/navigation/navbutton"
import { Flex } from "@radix-ui/themes"

type PropTypes = {
    children: React.ReactNode;
    href?: string;
    buttText?: string;
}

export default function AccountLayout({ children, href, buttText}: PropTypes) {
    buttText = buttText ?? "Placeholder";
    href = href ?? "/"
    return (
        <Flex height="100vh" width="100vw" direction="column" justify="center" align="center" gap="9" className="bg-white" minHeight="800px" p="1">
            <Flex width="20rem" height="5rem" justify="center" align="center" className="bg-orange-500" style={{borderRadius:"40px"}} minWidth="250px" minHeight="100px">
                <Logo size="9"/>
            </Flex>
            <Flex 
                justify="center" 
                align="center" 
                className="bg-orange-500" 
                style={{borderRadius:"40px"}} 
                overflow="hidden" 
                flexGrow="0" 
                flexShrink="0"
                gap="0"
                minWidth="15rem"
                minHeight="20rem"
                width="30rem"
                height="20rem" 
            > 
                {children}
            </Flex>
            <NavButton href={href} size="4">
                {buttText}
            </NavButton>
        </Flex>
    );
}