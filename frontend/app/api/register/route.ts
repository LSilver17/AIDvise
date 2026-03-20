import { NextResponse } from "next/server";
import bcrypt from "bcrypt";

import { create_user } from "@/app/lib/account_db_utils";

export async function POST(req: Request) {

    const credentials = await req.json();
    const { username, password, account_type } = credentials;

    // fetches result from create_user attempt and returns
    const result = await create_user(username, password, account_type);
    if(result.success) {
        return NextResponse.json({
            id: result.id,
            username: result.username,
            account_type: result.account_type,
        })
    } else {
        return NextResponse.json({
            success: result.success,
            error: result.error,
        });
    }
}