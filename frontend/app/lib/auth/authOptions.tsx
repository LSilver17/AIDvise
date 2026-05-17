/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Authors:   Sean Collins, NextAuth
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { signIn } from "next-auth/react";

import { validate_credentials } from "@/app/lib/account/account_db_utils";
/**
 * API endpoint options for any NextAuth requests. Currently credentials
 * are the only supported provider. Checks provided credentials and matches them against
 * those stored in the database with {@link validate_credentials}. See {@link https://next-auth.js.org/configuration/options}
 * for details on how to implement your own providers and other authorization options.
 */
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