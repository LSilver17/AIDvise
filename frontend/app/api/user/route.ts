import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";

// SQLite
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// User Functions
import { authCheck } from "@/app/lib/authCheck"
import { dbPath } from "@/app/lib/database_path";

export async function GET(req: Request) {
    // TODO: Return user info from table according to session ID
    const session = await authCheck();
    const id = session?.user?.id;
    let db;
    try {
        db = await open({
            filename: dbPath(),
            driver: sqlite3.Database
        });
    } catch(e) {

    } finally {
        if (db) {
            await db.close();
        }
    }
}