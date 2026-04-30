/*
    Author: Sean Collins
*/
import Logo from "@/app/components/visual/logo"
import NavButton from "@/app/components/navigation/navbutton"
import { Flex } from "@radix-ui/themes"

type PropTypes = {
    children: React.ReactNode;
    href?: string;
    buttText?: string;
}

/**
 * Layout for account login/registration, with a button for switching between the two. 
 * The proper field should be given as the child component.
 * @param props.href - Button hyperlink URL.
 * @param props.buttText - Inner button text.
 * @returns 
 */
export default function AccountLayout({ children, href, buttText}: PropTypes) {
    buttText = buttText ?? "Placeholder";
    href = href ?? "/"
    return (
        <Flex height="100vh" width="100vw" direction="column" justify="center" align="center" gap="8" className="bg-white" p="1" style={{boxSizing:"border-box"}}>
            <Flex width="20rem" height="5rem" justify="center" align="center" className="menuColor" style={{borderRadius:"20px"}} p="4">
                <Logo size="8"/>
            </Flex>
            <Flex 
                justify="center" 
                align="center" 
                className="menuColor" 
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