/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

import { Button, Flex } from "@radix-ui/themes"
import { useRouter, usePathname } from "next/navigation"
import type { Responsive } from "@radix-ui/themes/props"
import type { MouseEventHandler } from "react"
import ThemeProvider from "@/app/components/features/themeprovider";
import "@radix-ui/themes/styles.css";

export type ButtonProps = {
    href?: string;
    children: React.ReactNode;
    size?: Responsive<"4" | "1" | "2" | "3"> | undefined;
    onClick?: MouseEventHandler<HTMLButtonElement>;
    variant?: "classic" | "solid" | "soft" | "surface" | "outline" | "ghost" | undefined;
}

/**
 * Default button formatting for the frontend. Takes a handler function in the onClick prop.
 * @returns 
 */
export default function AppButton({variant, size, onClick, children} : ButtonProps) {
    size = size ?? "4";
    variant = variant ?? "solid";
    return (
        <Button 
            size={size} 
            onClick={onClick} 
            radius="full" 
            style={{
                cursor:"pointer"
            }} 
            color="orange" 
            variant={variant}
        >
            {children}
        </Button>
    );
}