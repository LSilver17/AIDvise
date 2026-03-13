import NextAuth from "next-auth";
import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { user } from "@/mock/mock.json"
import { User } from "@/app/lib/user"
import bcrypt from "bcrypt";
// TODO: import user database

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
                /*
                Replace above validation with:
                // compare username with database username
                const saltRounds = 14;
                bcrypt.genSalt(saltRounds, function(err, salt) {
                    bcrypt.hash(password, salt, function(err, hash) {
                        // Compare with hashed password stored in database
                    });
                });
                (Return the same user object as already implemented, although
                 you can implement a user id creation system if desired)
                */

                return null;
            }
        }),
    ],
    session: {
        maxAge: 1 * 60 * 60, // 1 hour
    }
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST}