"use client"

import type { MouseEventHandler } from "react";
import { signOut } from "next-auth/react";
import { ExitIcon } from "@radix-ui/react-icons"
import NavButton from "@/app/components/navigation/navbutton";

const clickHandler : MouseEventHandler<HTMLButtonElement> = async (event) => {
  await signOut({callbackUrl:"/login"});
}

export default function SignOut() {
    return (
        <NavButton onClick={clickHandler}>
            <ExitIcon/>Sign Out
        </NavButton>
    );
}
