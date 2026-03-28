import path from "path";

export function dbPath () {
    const dbPath = path.join(process.cwd(), '..', 'AdvisorDB.db');
    return dbPath;
}