import { Flex } from "@radix-ui/themes"

type Props = {
    children: React.ReactNode,
}

export default function DashboardSelection({children}: Props) {
    return(
        <Flex p="10px">
            {children}
        </Flex>    
    );
}