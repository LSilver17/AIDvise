"use client"

import type { MouseEventHandler } from "react";
import { signOut } from "next-auth/react";

const clickHandler : MouseEventHandler<HTMLButtonElement> = async (event) => {
  signOut({callbackUrl:"/login"});
}

export default function SignOut() {
    return (
        <button onClick={clickHandler}>
            Sign Out
        </button>
    );
}
