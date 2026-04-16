'use server'

import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from "bcrypt";
import { redirect } from "next/navigation";
import path from "path";
import { signOut } from "next-auth/react";
import data from "../../../../database_config.json"
import type { Database } from 'sqlite3';

// User
import type { AccountType } from '@/app/lib/account/account_type';
import type { Alert, EventAlert, ClassAlert } from '@/app/lib/alerts/alert';
import { createEventAlert, createClassAlert } from '@/app/lib/alerts/alert';
import { authSession } from "@/app/lib/account/authSession";
import { UserField } from '@/app/lib/account/user_fields';
import { ensureFieldFormat } from '@/app/lib/form/user_fields_format_test';

function dbPath () {
    // TODO: Use config to decide which database to use
    const dbPath = path.join(process.cwd(), '..', `${data.database}.db`);
    return dbPath;
}

async function openDB(path = dbPath()) {
    const db = await open({
        filename: path,
        driver: sqlite3.Database
    });
    await db.exec('PRAGMA foreign_keys = ON');
    return db;
}

type LoginResult = 
    | {success: true, username: string, account_type: AccountType, id: string}
    | {success: false, error:string}

type CreationResult =
    | {success:true, id:string, username: string, account_type: AccountType, academic_id: string}
    | {success:false, error:string};

export async function validate_credentials(username: string, password: string): Promise<LoginResult> {
    var db;
    try {
        db = await openDB(dbPath());

        const credential = await db.get('SELECT Username, Password, ID, AccountType FROM Users WHERE Username = ?', username);

        // Compares passwords with shared salt algorithm
        let valid = await bcrypt.compare(password, credential.Password);

        // create specific error return type
        if (!credential) {
            const result: LoginResult = {
                success: false,
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
            account_type: credential.AccountType,
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

async function delete_invalid_entry(db: any, username: string) {
    if (db) {
        const user = await db.get('SELECT Username, AccountType, ID FROM Users WHERE Username = ?', username);
        if(user) {
            await db.run("DELETE FROM Users WHERE Username = ?", username);
        }
    }
}

type ValidationResult = {valid: true, table: string} | {valid: false, err: string}

async function id_validation(db: any, account_type: AccountType, person_id: string) {
    if(account_type) {
        const table = (account_type === "Student") ? "Students" : "Advisors";
        const personID = await db.get(`SELECT ID FROM ${table} WHERE ID = ?`, person_id);
        if(!personID) {
            const result: ValidationResult = {
                valid: false,
                err: `${account_type} does not exist`,
            }
            return result;
        }
        const associatedAcc = await db.get(`SELECT ParentID FROM ${table} WHERE ID = ?`, person_id);
        if(associatedAcc.ParentID != null) {
            const result: ValidationResult = {
                valid: false,
                err: "There is already an account associated with this ID",
            }
            return result;
        }
        const result: ValidationResult = {
            valid: true,
            table: table,
        }
        return result;
    } else {
        throw "Invalid account type";
    }
}

export async function create_user(username: string, password: string, account_type: AccountType, person_id: string): Promise<CreationResult> {
    var db;
    const validAccountTypes = ["Student", "Advisor"];
    
    try {
        if (!account_type || !validAccountTypes.includes(account_type)) {
            throw "Invalid account type";
        }

        db = await openDB(dbPath());

        const existingUser = await db.get('SELECT Username FROM Users WHERE Username = ?', username);
        if (existingUser) {
            const result: CreationResult = {
                success: false,
                error: "User already exists",
            }
            return result;
        }

        // Ensures ID matches existing student/advisor entry and there is no account already associated
        const valid = await id_validation(db, account_type, person_id);
        let tableName = null;
        if (valid.valid) {tableName = valid.table}
        else {throw valid.err};

        // Hash the password before storing it in the database
        const saltRounds = 10;
        const salt = await bcrypt.genSalt(saltRounds);
        const hash = await bcrypt.hash(password, salt);

        await db.run('INSERT INTO Users (Username, Password, AccountType) VALUES (?, ?, ?)', username, hash, account_type);

        // Pull inserted credentials to return in the session
        const credential = await db.get('SELECT Username, AccountType, ID FROM Users WHERE Username = ?', username);

        // Link existing Student/Advisor record to new User entry
        await db.run(`UPDATE ${tableName} SET ParentID = ? WHERE ID = ?`, credential.ID, person_id);

        const result: CreationResult = {
            success: true,
            username: credential.Username,
            account_type: credential.AccountType,
            id: credential.ID,
            academic_id: person_id,
        }

        return result;

    } catch (e) {
        const result: CreationResult = {
            success: false,
            error: `Database error: ${e}`,
        }
        await delete_invalid_entry(db, username);
        return result;
    } finally {
        if (db) {
            await db.close();
        }
    }
}

type Result = { success: true, query?:string } | { success: false, error: string } | null;

function accountTypeToTable(type: string | undefined) {
    var tableName;
    switch(type) {
        case "Student": tableName = "Students"; break;
        case "Advisor": tableName = "Advisors"; break;
        default: tableName = null; break;
    }
    return tableName;
}

export async function update_user_entry(userData: UserData, userMetadata: UserMetadata, newVal: string | null, updatedField: string): Promise<Result> {
    var db;
    const session = await authSession();
    if(!session) {
        redirect("/login");
    }
    try {
        // Ensure data exists
        if (!userData) {
            throw Error("User data not found");
        } else if(!userMetadata) {
            throw Error("User metadata not found");
        } else if(!session) {
            throw Error("No active session");
        }

        db = await openDB(dbPath());

        // setup constants for query
        const table = accountTypeToTable(userMetadata.AccountType);
        const checkFormat = ensureFieldFormat(updatedField, newVal);
        if(!checkFormat.success) {
            throw Error(`${checkFormat.error}`);
        }

        // run query
        const query = `UPDATE ${table} SET ${updatedField} = ? WHERE ParentID = ?`;
        await db.run(query, newVal, session.user.id);
    
        const result: Result = {
            success:true,
            query: query,
        }
        return result;
    } catch(e: any) {
        const result: Result = {
            success: false,
            error: `${e.message}`,
        }
        return result;
    } finally {
        if (db) {
            await db.close();
        }
    }
}

export async function delete_account() {
    let db;
    const session = await authSession();
    if(!session) {
        redirect("/login");
    }
    try {
        if (!session?.user?.id) {
            throw Error("Unauthorized session");
        }

        db = await openDB(dbPath());
        const userID = session.user.id;
        const account_type = session.user.account_type;
        const account_table = (account_type === "Student") ? "Students" : "Advisors";

        if(!account_table) {
            throw Error("No valid account type");
        }

        await db.run(`UPDATE ${account_table} SET ParentID = ? WHERE ParentID = ?`, null, userID);
        await db.run("DELETE FROM Users WHERE ID = ?", userID);
        
        const result: Result = {
            success:true,
        }
        return result;
    } catch(e: any) {
        const result: Result = {
            success: false,
            error: `${e.message}`,
        }
        return result;
    } finally {
        if (db) {
            await db.close();
        }
    }
}


export type StudentData = {
    Name: UserField,
    GPA: UserField,
    CreditsEarned: UserField
    IntendedGraduationTerm: UserField,
    AdvisorID: UserField,
    StudentID: UserField,
}
export type AdvisorData = {
    Name: UserField,
    AdvisorID: UserField,
}

export type UserData = StudentData | AdvisorData;

export type UserMetadata = {
    AccountType: AccountType,
    Username: string,
}

export type UserAlerts = {
    UnseenAlerts: Alert[],
    SeenAlerts: Alert[],
}

export type UserInterests = {
    Interests: string[],
}

export type Student = {
    ID?: string,
    Name: string | null,
    GPA: number | null,
    CreditsEarned: number | null,
    IntendedGraduationTerm: string | null,
}

export type UserStudents = {
    Students: Student[],
}

export async function grabUserData() {
    const session = await authSession();
    if(!session) {
        redirect("/login");
    }
    const id = session?.user?.id;
    var db;
    try {
        db = await openDB(dbPath());

        const accountType = await db.get('SELECT AccountType FROM Users WHERE ID = ?', id);

        if (accountType.AccountType === "Student") {
            const userInfo = await db.get('SELECT Name, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID, ID FROM Students WHERE ParentID = ?', id);
            const advisor_name = await db.get('SELECT Name FROM Advisors WHERE ID = ?', userInfo.AdvisorID);
            const advisor_string = advisor_name?.Name ?? "Advising Center";
            const data: UserData = {
                Name: {
                    title:"Name",
                    data:userInfo.Name,
                    editable: false,
                },
                GPA: {
                    title:"GPA",
                    data:userInfo.GPA,
                    editable: false,
                },
                CreditsEarned:  {
                    title:"Credits Earned",
                    data:userInfo.CreditsEarned,
                    editable: false,
                },
                IntendedGraduationTerm: {
                    title:"Expected Graduation",
                    data:userInfo.IntendedGraduationTerm,
                    editable: false,
                },
                AdvisorID: {
                    title:"Advisor",
                    data: advisor_string,
                    editable: false,
                },
                StudentID: {
                    title: "Student ID",
                    data: userInfo.ID,
                    editable: false,
                }
            }
            const fieldData = {
                data: data,
                success:true,
            };
            return fieldData;
        }

        else if (accountType.AccountType === "Advisor") {
            // TODO: Expand query when advisor accounts are more fleshed out
            const userInfo = await db.get('SELECT Name, ID FROM Advisors WHERE ParentID = ?', id);
            const data: UserData = {
                Name: {
                    title:"Name",
                    data:userInfo.Name,
                    editable: true,
                },
                AdvisorID: {
                    title:"Advisor ID",
                    data: userInfo.ID,
                    editable: false,
                },
            }
            const fieldData = {
                data: data,
                success: true,
            };
            return fieldData;
        }
        else {
            throw `Account of type ${accountType.AccountType} with ID ${id} does not exist`;
        }
    } catch(e) {
        const error = {
            success: false,
            error:`ERROR: ${e}`,
        };
        return error;
    } finally {
        if (db) {
            await db.close();
        }
    }
}

export async function getUserObject() {
    // grab user data from database
    try {
        const userData = await grabUserData();
        if(!userData?.success) {
            if("error" in userData) {throw new Error(userData.error)}
            else {throw new Error("Undefined error")};
        } else if(userData.success && "data" in userData) {
            const userObject=userData.data;
            return userObject;
        }
        else {
            throw new Error("No data found");
        }
    } catch(e: any) {
        const error = e.message;
        console.log(`ERROR: ${error}`);
        redirect("/login");
    }
}

interface Context {
    userData: UserData,
    userMetadata: UserMetadata,
}
export interface StudentContext extends Context{
    userAlerts: UserAlerts,
    userInterests: UserInterests,
}
export interface AdvisorContext extends Context{
    userStudents: UserStudents,
}

type AlertReturn = {
    unseen: Alert[],
    seen: Alert[],
}

export async function get_curr_context(account_type: AccountType) {
        // session validation
    const session = await authSession();
    
    if(!session) {
        redirect("/login");
    }

    const userMetadata: UserMetadata = {
        AccountType: session.user.account_type,
        Username: session.user.username
    }

    if(account_type === "Student") {
        const userData = await getUserObject() as StudentData;
        const userAlerts = await get_alerts(userData.StudentID.data);
        const interests = await get_interests(userData.StudentID.data);
        
        const userInterests: UserInterests = {
            Interests: interests,
        }
        const currContext = {
            userData: userData,
            userMetadata: userMetadata,
            userAlerts: userAlerts,
            userInterests: userInterests,
        };
        return currContext;
    } else if(account_type === "Advisor") {
        const userData = await getUserObject() as AdvisorData;
        const userStudents: UserStudents = {
            Students: await student_fill(userData.AdvisorID.data),
        }
        const currContext = {
            userData: userData,
            userMetadata: userMetadata,
            userStudents: userStudents,
        };
        return currContext;
    }
}

async function get_interests(student_id: string) {
    var db;
    var interests: string[] = [];
    try {
        db = await openDB(dbPath());
        const db_interests = await db.all(`SELECT Interest FROM Interests WHERE ParentID = ?`, student_id);
        for (let interest of db_interests) {
            interests.push(interest.Interest);
        }
    } catch(e) {
        console.log(`ERROR: ${e}`)
        return interests;
    } finally {
        if (db) {
            await db.close();
        }
    }
    return interests;
}

export async function get_alerts(student_id: string): Promise<UserAlerts> {
    const alerts = await alert_fill(student_id);
    const userAlerts: UserAlerts = {
        UnseenAlerts: alerts.unseen,
        SeenAlerts: alerts.seen,
    }
    return userAlerts;
}

async function alert_fill(student_id: string): Promise<AlertReturn> {
    var db;
    let unseenAlerts: Alert[] = [];
    let seenAlerts: Alert[] = [];
    try {
        db = await openDB(dbPath());
        const db_event_alerts = await db.all(`SELECT EventID, AlertStatus, ID FROM RelevantEvents WHERE ParentID = ?`, student_id);
        for (let alert of db_event_alerts) {
            const eventID = alert.EventID;
            const dbEvent = await db.get(`SELECT Name, Description FROM Events WHERE ID = ?`, eventID);
            const dbEventTimes = await db.get(`SELECT Date, StartTime, EndTime FROM EventDates WHERE ParentID = ?`, eventID);
            const time = `${dbEventTimes.StartTime} - ${dbEventTimes.EndTime}`;
            // TODO: check for seen status
            const newAlert = createEventAlert(dbEvent.Name, dbEvent.Description, alert.AlertStatus, time, dbEventTimes.Date, alert.ID);
            if (newAlert.status === "Unseen") { unseenAlerts.push(newAlert); }
            else if (newAlert.status === "Seen") { seenAlerts.push(newAlert); };
        }
        // TODO: Implement class alerts
        // const db_class_alerts = await db.all(`SELECT EventID FROM RelevantEvents WHERE ParentID = ?`, student_id);
        // const last_check = await db.get(`SELECT LastSectionStatusCheck FROM Students WHERE ID = ?`, student_id)
        // for (let course of db_class_alerts) {
        //     console.log(last_check.LastSectionStatusCheck);
        //     //createClassAlert()
        // }
    } catch(e) {
        console.log(`ERROR: ${e}`)
        const alerts: AlertReturn = {
            unseen: unseenAlerts,
            seen: seenAlerts,
        }
        return alerts;
    } finally {
        if (db) {
            await db.close();
        }
    }
    const alerts: AlertReturn = {
        unseen: unseenAlerts,
        seen: seenAlerts,
    }
    return alerts;
}

export async function mark_alerts_as_seen(alerts: UserAlerts): Promise<UserAlerts> {
    var db;
    const unseen_alerts = alerts.UnseenAlerts;
    try {
        db = await openDB(dbPath());
        for (const alert of unseen_alerts) {
            await db.run(`UPDATE RelevantEvents SET AlertStatus = ? WHERE ID = ?`, "Seen", alert.id);
        }
        const userAlerts: UserAlerts = {
            UnseenAlerts: [],
            SeenAlerts: [
                ...alerts.SeenAlerts,
                ...alerts.UnseenAlerts
            ]
        }
        return userAlerts;
    } catch(e) {
        console.log(`ERROR: ${e}`)
        return alerts;
    } finally {
        if (db) {
            await db.close();
        }
    }
}

async function student_fill(advisor_id: string) : Promise<Student[]> {
    var db;
    let students: Student[] = [];
    try {
        db = await openDB(dbPath());

        const db_students = await db.all(`SELECT ID, Name, GPA, CreditsEarned, IntendedGraduationTerm FROM Students WHERE AdvisorID = ?`, advisor_id)
        for (let student of db_students) {
            // TODO: check for seen status
            const newStudent: Student = {
                Name: student.Name,
                ID: student.ID,
                GPA: student.GPA,
                CreditsEarned: student.CreditsEarned,
                IntendedGraduationTerm: student.IntendedGraduationTerm,
            }
            students.push(newStudent);
        }
    } catch(e) {
        console.log(`ERROR: ${e}`)
        return students;
    } finally {
        if (db) {
            await db.close();
        }
    }
    return students;
}
