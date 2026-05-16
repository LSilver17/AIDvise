/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
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
