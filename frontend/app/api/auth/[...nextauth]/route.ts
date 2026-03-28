import NextAuth from "next-auth";
import { NextResponse } from "next/server";
import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcrypt";
import type { User } from "next-auth";

import { validate_credentials } from "@/app/lib/account_db_utils";
import { PassThrough } from "stream";

export const authOptions: NextAuthOptions = {
    providers: [
        CredentialsProvider({
            name: "Credentials",
            credentials: {
                username: { label: "Username", type: "text", placeholder: "johndoe"},
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                // Validates credentials, returning user object if valid and null otherwise
                let loginResponse = null;

                // Type safety guard
                if((credentials?.username !== undefined) && (credentials?.password !== undefined)) {
                    loginResponse = await validate_credentials(credentials.username, credentials.password);
                }
                
                if (loginResponse?.success) {
                    const user = {
                        username: loginResponse.username,
                        account_type: loginResponse.account_type,
                        id: loginResponse.id
                    }
                    return user;
                } 
                
                
                console.log(`Login error: ${loginResponse?.error}`);
                return null;
            }
        }),
    ],
    session: {
        maxAge: 1 * 60 * 60, // 1 hour
    },
    callbacks: {
        async jwt({token, user}) {
            if(user) {
                token.username = user.username;
                token.account_type = user.account_type;
                token.id = user.id;
            }

            return token;
        },
        async session({session, token}) {
            if(token) {
                session.user.username = token.username;
                session.user.account_type = token.account_type;
                session.user.id = token.id;
            }
            return session;
        }
    },
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST, handler}