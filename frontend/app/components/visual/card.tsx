import { Flex } from "@radix-ui/themes"

// Lib
import Title from "@/app/components/visual/title";

type Props = {
    children: React.ReactNode,
    minHeight: string,
    maxHeight: string,
    title: string,
}

export default function Card({children, minHeight, maxHeight, title} : Props) {
    return (
        <Flex direction="row" minHeight={minHeight} maxHeight={maxHeight} overflow="hidden">
            <Flex minHeight={minHeight} maxHeight={maxHeight} width="10px" style={{background:"orange"}}/>
            <Flex direction="column" width="100%" style={{background:"gainsboro"}} p="2">
                <Title size="6" gap="2" justify="start" align="start" pl="2">{title}</Title>
                <Flex direction="column" align="center" ml="3">
                    {children}
                </Flex>
            </Flex>
        </Flex>
    );
}