import { JWT } from "next-auth/jwt"
import NextAuth, { DefaultSession, User } from "next-auth";
import type { AccountType } from '@/app/lib/account_type'

// Expands user object to access more data from session
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

declare module 'next-auth/jwt' {
    interface JWT {
        username: string,
        account_type: AccountType,
        id: string
    }
}