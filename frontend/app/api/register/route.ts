/*
    Author: Sean Collins
*/
import { NextResponse } from "next/server";

// Lib
import { create_user } from "@/app/lib/account/account_db_utils";

/**
 * Request handler for user registration actions. Calls the create_user function from
 * /app/lib/account/account_db_utils and returns a NextResponse with the result of the
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