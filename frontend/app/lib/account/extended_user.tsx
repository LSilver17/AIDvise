/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Expansion of NextAuth module for session tokens.
=============================================================================*/
import { JWT } from "next-auth/jwt"
import NextAuth, { DefaultSession, User } from "next-auth";
import type { AccountType } from '@/app/lib/account/account_type'

/**
 * Expands NextAuth user object to store more data in the session.
 */

declare module "next-auth" {
    interface User {
        username: string,
        account_type: AccountType,
        id: string
    }

    interface Session {
        user: {
            username: string,
            account_type: AccountType,
            id: string
        } & DefaultSession["user"];
    } 
}

/**
 * Expands JWT token interface.
 */
declare module 'next-auth/jwt' {
    interface JWT {
        username: string,
        account_type: AccountType,
        id: string
    }
}