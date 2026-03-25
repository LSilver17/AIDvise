import NextAuth from "next-auth";
import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcrypt";

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
                let user = null;

                // Type safety guard
                if((credentials?.username !== undefined) && (credentials?.password !== undefined)) {
                    user = await validate_credentials(credentials.username, credentials.password);
                }

                // TODO: PLEASE REMOVE
                if((credentials?.username !== undefined) && (credentials?.password !== undefined) && (credentials?.username == "test_user") && (credentials?.password == "password123")) {
                    user = {
                        username: credentials.username,
                        id: "1",
                    }
                }
                
                if (!user) return null;

                return user;
            }
        }),
    ],
    session: {
        maxAge: 1 * 60 * 60, // 1 hour
    }
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST, handler}