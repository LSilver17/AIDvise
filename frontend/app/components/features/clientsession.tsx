"use client"

import { SessionProvider } from "next-auth/react";
import type { Session } from "next-auth";

type ClientSessionProps = Readonly<{
    children: React.ReactNode;
    session: Session | null;
}>

// Wrap root in this
// Session is fetched form the server and can be accessed with client-side useSession() hook
export default function ClientSession ({children, session}: ClientSessionProps ) {
    return (
        <SessionProvider session={session}>
            {children}
        </SessionProvider>
    );
}