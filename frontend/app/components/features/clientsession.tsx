/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

import { SessionProvider } from "next-auth/react";
import type { Session } from "next-auth";

type ClientSessionProps = Readonly<{
    children: React.ReactNode;
    session: Session | null;
}>


/**
 * Provider component for session .Session is fetched form the server 
 * and can be accessed with client-side {@link useSession} hook, although it is recommended to use
 * the {@link authSession} hook instead. Place within root component.
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