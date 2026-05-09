/*
    Author: Sean Collins
    Copyright 2026
*/
"use client"

import { SessionProvider } from "next-auth/react";
import type { Session } from "next-auth";

type ClientSessionProps = Readonly<{
    children: React.ReactNode;
    session: Session | null;
}>


/**
 * Provider component for session .Session is fetched form the server 
 * and can be accessed with client-side useSession() hook, although it is recommended to use
 * the authSession() hook instead. Place within root component.
 * @param props.session - Session object.
 * @returns 
 */
export default function ClientSession ({children, session}: ClientSessionProps ) {
    return (
        <SessionProvider session={session}>
            {children}
        </SessionProvider>
    );
}