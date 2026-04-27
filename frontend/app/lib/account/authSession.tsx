/*
    Author: Sean Collins
    Description: 
        Auth session hook definition
*/
"use server"

import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

/**
 * Validates the active session, returning a session object or null.
 * @returns Session object.
 */
export async function authSession() {
    const session = await getServerSession(authOptions);
    return session;
}