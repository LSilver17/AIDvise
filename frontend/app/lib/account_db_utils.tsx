import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from "bcrypt";
import { error } from 'console';

type LoginResult = {
    username: string;
    account_type: string;
    id: string;
}

type CreationResult =
    | {success:true, id:string, username: string, account_type: string}
    | {success:false, error:string};

export async function validate_credentials(username: string, password: string): Promise<LoginResult | null> {
    let db;
    try {
        db = await open({
            filename: 'Test.db',
            driver: sqlite3.Database
        });
        await db.exec('PRAGMA foreign_keys = ON');

        const credential = await db.get('SELECT username, password, account_type FROM Users WHERE username = ?', username);

        // Compares passwords with shared salt algorithm
        let valid = await bcrypt.compare(password, credential.password);

        if (!credential || !valid) {
            return null;
        }

        const userCred: LoginResult = {
            username: credential.username,
            account_type: credential.account_type,
            id: "1",
        };

        return userCred;

    } catch (e) {
        console.error(`Database error: ${e}`);
        return null;
        
    } finally {
        if (db) {
            await db.close();
        }
    }
}

export async function create_user(username: string, password: string, account_type: string): Promise<CreationResult> {
    let db;
    try {
        db = await open({
            filename: 'Test.db',
            driver: sqlite3.Database
        });
        await db.exec('PRAGMA foreign_keys = ON');

        const existingUser = await db.get('SELECT username FROM Users WHERE username = ?', username);
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
        await db.run('INSERT INTO Users (username, password, account_type) VALUES (?, ?, ?)', username, hash, account_type);

        const result: CreationResult = {
            success: true,
            username: username,
            account_type: account_type,
            id: "1",
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