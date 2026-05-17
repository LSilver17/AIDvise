/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import { Theme } from "@radix-ui/themes"

export type Props = {
    children: React.ReactNode;
    accentColor?: "ruby" | "orange" | "gray" | "gold" | "bronze" | "brown" | "yellow" | "amber" | "tomato" | "red" | "crimson" | "pink" | "plum" | "purple" | "violet" | "iris" | "indigo" | "blue" | "cyan" | "teal" | "jade" | "green" | "grass" | "lime" | "mint" | "sky" | undefined
}

/**
 * Provides theme colors for child components, by default orange.
 * @param props.accentColor - Theme color for front end.
 * @param props.children - Child elements to be wrapped in theme.
 * @returns 
 */
export default function ThemeProvider({children, accentColor}: Props) {
    accentColor = accentColor ?? "orange";
    return (
        <Theme accentColor={accentColor}>
            {children}
        </Theme>
    );
}