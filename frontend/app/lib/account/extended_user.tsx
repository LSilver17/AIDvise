/*
    Author: Sean Collins
    Description: 
        Expansion of NextAuth module
    Copyright 2026
*/
import { JWT } from "next-auth/jwt"
import NextAuth, { DefaultSession, User } from "next-auth";
import type { AccountType } from '@/app/lib/account/account_type'

/**
 * Expands user object to store more data in the session.
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