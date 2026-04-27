/*
    Author: Sean Collins
*/
"use client"

import type { MouseEventHandler } from "react";
import { signOut } from "next-auth/react";
import { ExitIcon } from "@radix-ui/react-icons"
import NavButton from "@/app/components/navigation/navbutton";

/**
 * Sign out event handler.
 * @param event 
 */
const clickHandler : MouseEventHandler<HTMLButtonElement> = async (event) => {
  await signOut({callbackUrl:"/login"});
}

/**
 * Button that clears a user session and returns them to login page.
 * @returns 
 */
export default function SignOut() {
    return (
        <NavButton onClick={clickHandler}>
            <ExitIcon/>Sign Out
        </NavButton>
    );
}
