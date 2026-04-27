/*
    Author: Sean Collins
*/
"use client"

import { Button, Flex } from "@radix-ui/themes"
import { useRouter, usePathname } from "next/navigation"
import type { Responsive } from "@radix-ui/themes/props"
import type { MouseEventHandler } from "react"
import ThemeProvider from "@/app/components/features/themeprovider";
import "@radix-ui/themes/styles.css";

type ButtonProps = {
    href?: string;
    children: React.ReactNode;
    size?: Responsive<"4" | "1" | "2" | "3"> | undefined;
    onClick?: MouseEventHandler<HTMLButtonElement>;
    variant?: "classic" | "solid" | "soft" | "surface" | "outline" | "ghost" | undefined;
}

/**
 * Default button formatting for the frontend.
 * @param props.size - Prop determining button size.
 * @param props.onClick - Handler for button click event.
 * @param props.variant - Visual variant for button.
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