/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
// Components
import { Flex } from "@radix-ui/themes"

// Lib
import Title from "@/app/components/visual/title";

export type Props = {
    children: React.ReactNode,
    minHeight?: string,
    maxHeight?: string,
    height?: string,
    width?: string,
    title: string,
}

/**
 * Visual card component, containing a title and space for extra content. Overflow is cut off.
 * @param props.minHeight - Minimum height of card, if variable size is desired.
 * @param props.maxHeight - Maximum height of card.
 * @param props.height - Fixed height of card.
 * @param props.width - Fixed width of card.
 * @param props.title - String representing card title.
 * @param props.children - Any additional elements/components to be rendered underneath the title.
 * @returns 
 */
export default function Card({children, minHeight, maxHeight, height, width, title} : Props) {
    height = height ?? undefined;
    width = width ?? undefined;
    return (
        <Flex direction="row" minHeight={minHeight} maxHeight={maxHeight} height={height} width={width} overflow="hidden">
            <Flex minHeight={minHeight} maxHeight={maxHeight} height={height} width="10px" style={{background:"orange"}}/>
            <Flex direction="column" width="100%" style={{background:"gainsboro"}} p="2">
                <Title size="6" gap="2" align="start" pl="2">{title}</Title>
                <Flex direction="column" align="center" ml="3">
                    {children}
                </Flex>
            </Flex>
        </Flex>
    );
}