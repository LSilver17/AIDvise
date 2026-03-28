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
            <Flex direction="row" justify="start" align="center" gap="3" width="100%">
                {children}
            </Flex>
        </DefaultButton>
        
    );
}