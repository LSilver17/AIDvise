import { Theme } from "@radix-ui/themes"

type Props = {
    children: React.ReactNode;
}

export default function ThemeProvider({children}: Props) {
    return (
        <Theme accentColor="orange">
            {children}
        </Theme>
    );
}