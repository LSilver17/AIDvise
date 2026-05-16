/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Auth hook session definition.
=============================================================================*/
"use server"

import { getServerSession } from "next-auth/next";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";

/**
 * Validates the active session by passing {@link authOptions} to {@link getServerSession},
 * returning a session object or null depending on result.
 * @returns Session object.
 */
export async function authSession() {
    const session = await getServerSession(authOptions);
    return session;
}