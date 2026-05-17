/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/

import { Text, Flex, Separator, Em } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";
import React from "react";

export type PropTypes = {
    size?: Responsive<"1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined;
    //justify?: Responsive<"center" | "start" | "end" | "between"> | undefined;
    align?: Responsive<"center" | "start" | "end" | "baseline" | "stretch"> | undefined
    children: React.ReactNode;
    gap?: "0" | "1" | "3" | "2" | "4" | "5" | "6" | "7" | "8" | "9" | undefined
    pl?: Responsive<"0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined
}

/**
 * Standardized title component, containing text and a horizontal rule.
 * @param props.size - Size of title text.
 * @param props.children - Title text.
 * @param props.align - Alignment of title text.
 * @param props.gap - Space between title and horizontal rule.
 * @param props.pl - Left padding of title text.
 * @returns 
 */
export default function Title ({size, children, align, gap, pl}: PropTypes) {
    size = size ?? "1";
    // justify = justify ?? "start";
    gap = gap ?? "5";
    align = align ?? "center"
    pl = pl ?? "0"
    return (
        <Flex direction="column" justify="center" align={align} gapY={gap} pl={pl}>
            <Text size={size}>
                {children}
            </Text>
            <Separator orientation="horizontal" size="4"/>
        </Flex>
    );
}