import NextAuth from "next-auth";
import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { user } from "@/mock/mock.json"
import { User } from "@/app/lib/user"

let userCred = Object.assign(new User(), user);

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
                if (userCred.getPassword() == credentials?.password && 
                    userCred.getUser() == credentials?.username) {
                    return {
                        id: "1",
                        name: userCred.getUser(),
                    };
                }

                return null;
            }
        }),
    ],
    pages: {
        signIn: '/login',
    },
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST}