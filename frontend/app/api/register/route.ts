import { NextResponse } from "next/server";
import bcrypt from "bcrypt";

import { create_user } from "@/app/lib/account_db_utils";

export async function POST(req: Request) {
    const saltRounds = 14;

    const credentials = await req.json();
    const { username, password } = credentials;

    // ensure that username doesnt already exist in db, returning null if so (I will implement error handling)

    // inserts new user w/ salted & hashed password
    bcrypt.genSalt(saltRounds, function(err, salt) {
        bcrypt.hash(password, salt, function(err, hash) {
           // TODO: store hashed password in db
        });
    });
    
    return NextResponse.json({
        success: true,
    })
}