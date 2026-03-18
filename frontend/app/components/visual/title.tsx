import { Text, Flex, Separator, Em } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";
import React from "react";

type PropTypes = {
    size?: Responsive<"1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined;
    justify?: Responsive<"center" | "start" | "end" | "between"> | undefined;
    children: React.ReactNode;
}

export default function Title ({size, children, justify}: PropTypes) {
    size = size ?? "1";
    justify = justify ?? "start";
    return (
        <Flex direction="column" justify="start" align="center" gapY="5">
            <Text size={size}>
                {children}
            </Text>
            <Separator orientation="horizontal" size="4"/>
        </Flex>
    );
}