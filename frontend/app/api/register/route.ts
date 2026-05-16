/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import { NextResponse } from "next/server";

// Lib
import { create_user } from "@/app/lib/account/account_db_utils";

/**
 * Request handler for user registration actions. Calls {@link create_user} and returns a 
 * {@link NextResponse} with the result of the
 * creation attempt.
 * @param req 
 * @returns 
 */
export async function POST(req: Request) {

    const credentials = await req.json();
    const { username, password, account_type, id } = credentials;

    // fetches result from create_user attempt and returns
    const result = await create_user(username, password, account_type, id);
    if(result.success) {
        return NextResponse.json({
            id: result.id,
            username: result.username,
            account_type: result.account_type,
            academic_id: result.id,
        })
    } else {
        return NextResponse.json({
            success: result.success,
            error: result.error,
        },
        {
            status: 400
        });
    }
}