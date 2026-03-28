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
        <Flex height="100vh" width="100vw" direction="column" justify="center" align="center" gap="8" className="bg-white" minHeight="800px">
            <Flex width="20%" height="20%" justify="center" align="center" className="bg-orange-500" style={{borderRadius:"40px"}} minWidth="250px" minHeight="100px">
                <Logo size="9"/>
            </Flex>
            <Flex 
                width="20%" 
                height="50%" 
                justify="center" 
                align="center" 
                className="bg-orange-500" 
                style={{borderRadius:"40px"}} 
                overflow="hidden" 
                flexGrow="0" 
                flexShrink="0"
                gap="0"
                minWidth="250px"
                minHeight="350px"
            > 
                {children}
            </Flex>
            <NavButton href={href} size="4">
                {buttText}
            </NavButton>
        </Flex>
    );
}