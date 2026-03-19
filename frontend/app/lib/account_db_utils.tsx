import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from "bcrypt";

export async function validate_credentials(username: string, password: string) {
    let db;
    try {
        db = await open({
            filename: 'Test.db',
            driver: sqlite3.Database
        });
        await db.exec('PRAGMA foreign_keys = ON');

        const credential = await db.get('SELECT username, password FROM Users WHERE username = ?', username);

        // Compares passwords with shared salt algorithm
        let valid = await bcrypt.compare(password, credential.password);

        if (!credential || !valid) {
            return null;
        }

        return  {
            username: credential.username,
            // account_type
            id: "1",
        };

    } catch (e) {
        console.error(`Database error: ${e}`);
        return null;
        if (db) {
            await db.close();
        }
    }
}

export async function create_user(username: string, password: string, account_type: string): Promise<boolean> {
    let db;
    try {
        db = await open({
            filename: 'Test.db',
            driver: sqlite3.Database
        });
        await db.exec('PRAGMA foreign_keys = ON');

        const existingUser = await db.get('SELECT username FROM Users WHERE username = ?', username);
        if (existingUser) {
            throw new Error("Username already exists");
        }

        // Hash the password before storing it in the database
        const hashed_password = password;

        await db.run('INSERT INTO Users (username, password, account_type) VALUES (?, ?, ?)', username, hashed_password, account_type);
        return true;

    } catch (e) {
        console.error(`Database error: ${e}`);
        return false;
    } finally {
        if (db) {
            await db.close();
        }
    }
}