import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from "bcrypt";
import path from "path";
import { error } from 'console';

const dbPath = path.join(process.cwd(), '..', 'AdvisorDB.db');

type LoginResult = 
    | {success: true, username: string, account_type: string, id: string}
    | {success: false, error:string}


type CreationResult =
    | {success:true, id:string, username: string, account_type: string}
    | {success:false, error:string};

//TODO: open actual db file
export async function validate_credentials(username: string, password: string): Promise<LoginResult> {
    let db;
    try {
        db = await open({
            filename: dbPath,
            driver: sqlite3.Database
        });
        await db.exec('PRAGMA foreign_keys = ON');

        const credential = await db.get('SELECT Username, Password, ID FROM Users WHERE Username = ?', username);

        // Compares passwords with shared salt algorithm
        let valid = await bcrypt.compare(password, credential.Password);

        // create specific error return type
        if (!credential) {
            const result: LoginResult = {
                success:false,
                error:"User not found"
            }
            return result;
        }

        if (!valid) {
            const result: LoginResult = {
                success:false,
                error:"Incorrect password"
            }
            return result;
        }

        // TODO: Create unique user ID
        const userCred: LoginResult = {
            success: true,
            username: credential.Username,
            account_type: credential.Username,
            id: credential.ID,
        };

        return userCred;

    } catch (e) {
        const result: LoginResult = {
            success:false,
            error:`Database error: ${e}`
        }
        return result;
        
    } finally {
        if (db) {
            await db.close();
        }
    }
}

export async function create_user(username: string, password: string, account_type: string): Promise<CreationResult> {
    let db;
    try {
        // TODO: add config instead of hardcoding database file
        db = await open({
            filename: dbPath,
            driver: sqlite3.Database
        });
        await db.exec('PRAGMA foreign_keys = ON');

        const existingUser = await db.get('SELECT Username FROM Users WHERE Username = ?', username);
        if (existingUser) {
            const result: CreationResult = {
                success: false,
                error: "User already exists",
            }
            return result;
        }

        // Hash the password before storing it in the database
        const saltRounds = 10;
        const salt = await bcrypt.genSalt(saltRounds);
        const hash = await bcrypt.hash(password, salt);
        await db.run('INSERT INTO Users (Username, Password, AccountType) VALUES (?, ?, ?)', username, hash, account_type);

        // Pull inserted credentials to return in the session
        const credential = await db.get('SELECT Username, Password, Username, ID FROM Users WHERE username = ?', username);

        const result: CreationResult = {
            success: true,
            username: credential.Username,
            account_type: credential.Username,
            id: credential.ID,
        }

        return result;

    } catch (e) {
        const result: CreationResult = {
            success: false,
            error: `Database error: ${e}`,
        }
        return result;
    } finally {
        if (db) {
            await db.close();
        }
    }
}