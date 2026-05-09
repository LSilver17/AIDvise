/*
    Author: Sean Collins
    Copyright 2026
*/
import { Theme } from "@radix-ui/themes"

type Props = {
    children: React.ReactNode;
    accentColor?: "ruby" | "orange" | "gray" | "gold" | "bronze" | "brown" | "yellow" | "amber" | "tomato" | "red" | "crimson" | "pink" | "plum" | "purple" | "violet" | "iris" | "indigo" | "blue" | "cyan" | "teal" | "jade" | "green" | "grass" | "lime" | "mint" | "sky" | undefined
}

/**
 * Provides theme colors for child components, by default orange.
 * @param props.accentColor - Theme color for front end.
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