/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Authors:   Sean Collins, NextAuth
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import NextAuth from "next-auth";
import { authOptions } from "@/app/lib/auth/authOptions";

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST, handler}