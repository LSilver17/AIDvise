"use client"

import { Button } from "@radix-ui/themes"
import { useRouter } from "next/navigation"

export default function NavButton({href, children}: {href: string, children: React.ReactNode}) {
    const router = useRouter();
    return (
        <Button onClick = {() => {router.push(href)}}>
            {children}
        </Button>
    )
}