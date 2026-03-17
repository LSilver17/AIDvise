import { Text, Em } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";

type PropTypes = {
    size?: Responsive<"1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined;
}

export default function Logo ({size}: PropTypes) {
    size = size ?? "1";
    return (
        <Text size={size} >
            <Em>advise.</Em>
        </Text>
    );
}