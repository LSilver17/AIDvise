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
import { authSession } from "@/app/lib/account/authSession";

export type ClientSessionProps = Readonly<{
    children: React.ReactNode;
    session: Session | null;
}>


/**
 * Provider component for session. Session is fetched from the server 
 * and can be accessed with client-side {@link authSession} hook.
 * Pass the session in the session prop and use this component to
 * wrap the application in the root component.
 * @property props.session - Session object.
 * @returns 
 */
export default function ClientSession ({children, session}: ClientSessionProps ) {
    return (
        <SessionProvider session={session}>
            {children}
        </SessionProvider>
    );
}