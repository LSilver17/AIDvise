/*
    Author: Sean Collins
    Description: 
        Extension of the DefaultButton component for
        creating navigation buttons.
    Copyright 2026
*/
"use client"

import { Button, Flex } from "@radix-ui/themes"
import { useRouter, usePathname } from "next/navigation"
import type { Responsive } from "@radix-ui/themes/props"
import type { MouseEventHandler } from "react"
import ThemeProvider from "@/app/components/features/themeprovider";
import "@radix-ui/themes/styles.css";
import DefaultButton from "@/app/components/features/default_button"

type ButtonProps = {
    href?: string;
    children: React.ReactNode;
    size?: Responsive<"4" | "1" | "2" | "3"> | undefined;
    onClick?: MouseEventHandler<HTMLButtonElement>;
}

/**
 * Button component based on DefaultButton that takes an href as prop
 * to redirect user.
 * @param props.href - URL extension of base URL used for on-click redirection.
 * @param props.onClick - Optional custom handler function for click event.
 * @param props.size - Size of the button.
 * @returns 
 */
export default function NavButton({href, children, size, onClick,}: ButtonProps) {
    const router = useRouter();
    href = href ?? "/";
    size = size ?? "4";
    onClick = onClick ?? (() => router.push(href));
    const activePath = usePathname() === href;
    return (
        <DefaultButton 
            size={size} 
            onClick={onClick}
            variant={activePath ? "surface": "solid"}
        >
            <Flex direction="row" justify="start" align="center" width="100%" gap="3">
                {children}
            </Flex>
        </DefaultButton>
    );
}