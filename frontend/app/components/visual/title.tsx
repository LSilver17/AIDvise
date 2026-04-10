import { Text, Flex, Separator, Em } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";
import React from "react";

type PropTypes = {
    size?: Responsive<"1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined;
    justify?: Responsive<"center" | "start" | "end" | "between"> | undefined;
    align?: Responsive<"center" | "start" | "end" | "baseline" | "stretch"> | undefined
    children: React.ReactNode;
    gap?: "0" | "1" | "3" | "2" | "4" | "5" | "6" | "7" | "8" | "9" | undefined
    pl?: Responsive<"0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined
}

export default function Title ({size, children, justify, align, gap, pl}: PropTypes) {
    size = size ?? "1";
    justify = justify ?? "start";
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