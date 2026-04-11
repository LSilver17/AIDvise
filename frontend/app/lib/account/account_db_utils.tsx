'use server'

import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from "bcrypt";
import { redirect } from "next/navigation";
import path from "path";
import { signOut } from "next-auth/react";
import data from "../../../../database_config.json"

// User
import type { AccountType } from '@/app/lib/account/account_type';
import type { Alert, EventAlert } from '@/app/lib/alerts/alert';
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
    | {success:true, id:string, username: string, account_type: AccountType}
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

export async function create_user(username: string, password: string, account_type: AccountType): Promise<CreationResult> {
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

        // Hash the password before storing it in the database
        const saltRounds = 10;
        const salt = await bcrypt.genSalt(saltRounds);
        const hash = await bcrypt.hash(password, salt);

        await db.run('INSERT INTO Users (Username, Password, AccountType) VALUES (?, ?, ?)', username, hash, account_type);
        
        // Creates parallel entry into Students/Advisors table
        if(account_type === "Student") {
            const credential = await db.get('SELECT ID FROM Users WHERE Username = ?', username);
            await db.run('INSERT INTO Students (ParentID) VALUES (?)', credential.ID); 
        } else if (account_type === "Advisor") {
            const credential = await db.get('SELECT ID FROM Users WHERE Username = ?', username);
            await db.run('INSERT INTO Advisors (ParentID) VALUES (?)', credential.ID); 
        } else {
            throw "Invalid account type";
        }

        // Pull inserted credentials to return in the session
        const credential = await db.get('SELECT Username, AccountType, ID FROM Users WHERE Username = ?', username);

        const result: CreationResult = {
            success: true,
            username: credential.Username,
            account_type: credential.AccountType,
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

export type UserData = 
// student
{
    Name: UserField,
    GPA: UserField,
    CreditsEarned: UserField
    IntendedGraduationTerm: UserField,
    AdvisorID: UserField,
} |
// advisor
{
    Name: UserField,
} |
null

export type UserMetadata = {
    AccountType: AccountType,
    Username: string,
}

export type UserAlerts = {
    Alerts: Alert[]
}

export async function grabUserData() {
    // TODO: Return user info from table according to session ID
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
            const userInfo = await db.get('SELECT Name, GPA, CreditsEarned, IntendedGraduationTerm, AdvisorID FROM Students WHERE ParentID = ?', id);
            const fieldData = {
                data:{
                    Name: {
                        title:"Name",
                        data:userInfo.Name,
                        editable: true,
                    },
                    GPA: {
                        title:"GPA",
                        data:userInfo.GPA,
                        editable: true,
                    },
                    CreditsEarned:  {
                        title:"Credits Earned",
                        data:userInfo.CreditsEarned,
                        editable: true,
                    },
                    IntendedGraduationTerm: {
                        title:"Expected Graduation",
                        data:userInfo.IntendedGraduationTerm,
                        editable: true,
                    },
                    AdvisorID: {
                        title:"Advisor",
                        data: userInfo.AdvisorID,
                        editable: false,
                    },
                },
                success:true,
            };
            return fieldData;
        }

        else if (accountType.AccountType === "Advisor") {
            // TODO: Expand query when advisor accounts are more fleshed out
            const userInfo = await db.get('SELECT Name FROM Advisors WHERE ParentID = ?', id);
            const fieldData = {
                data: {
                    Name: {
                        title:"Name",
                        data:userInfo.Name,
                        editable: true,
                    },
                },
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

export type Context = {
    userData: UserData,
    userMetadata: UserMetadata,
    userAlerts: UserAlerts,
}

export async function get_curr_context() {
    // session validation
  const session = await authSession();
  
  if(!session) {
      redirect("/login");
  }

  const userData = await getUserObject();

  const userMetadata: UserMetadata = {
    AccountType: session.user.account_type,
    Username: session.user.username
  }

  const userAlerts: UserAlerts = {
    Alerts: temp_alert_fill(),
  }

  const currContext = {
    userData: userData,
    userMetadata: userMetadata,
    userAlerts: userAlerts
  };
  
  return currContext;
}

 // TODO: Delete
function temp_alert_fill(): Alert[] {
  const a1 = createEventAlert (
    "Transfer Event",
    "QCC Transfer Fair in the HLC",
    "Unseen",
    "11:00 AM",
    "4/11/2026",
  );
  const a2 = createClassAlert (
    "Course Opening",
    "Unseen",
    "CSC",
    212,
    "Intro to Software Engineering",
    "CSC 212, the concluding course in the software engineering series, broadens the student's perspective to encompass the full software development lifecycle, from initial concept to ongoing maintenance. Emphasizing the analysis and design of medium-sized systems, the course includes a comprehensive team project covering analysis, design, implementation, and testing phases, along with detailed documentation and test plans. Students are introduced to design patterns and advanced programming techniques using data structures and templates. A significant aspect of the course is the integration of professional ethics, software, and information assurance, addressing security concerns and liabilities in computer-based systems. The course culminates in a collaborative research project, culminating in a presentation to a live audience. This comprehensive approach prepares students for professional software development, emphasizing ethical considerations and a thorough understanding of the software lifecycle.",
    4,
    "CSC 109 with a grade of \"C\" or higher or ROS 109 with a grade of \"C\" or higher",
    "9:00 AM - 12:15 PM",
    "MTW",
  );
  const a3 = createEventAlert (
    "Music Performance",
    "Music Ensemble will be playing in the HLC common.",
    "Unseen",
    "11:30 AM - 1:30 PM",
    "4/23/2026",
  );
  const a4 = createClassAlert (
    "Course Opening",
    "Unseen",
    "CSC",
    208,
    "Introduction to Architecture and Assembly Language",
    "CSC 208 is the fourth installment of a comprehensive five-part computer science series. This course provides a comprehensive exploration of computer systems from a programmer's perspective, bridging the gap between hardware and software. Students will gain a deep understanding of how computer systems execute programs and handle data, delving into topics like data representation, machine-level code, processor architecture, memory hierarchy, system-level I/O, and network programming. Emphasizing the translation of high-level programming languages into machine code, the course enhances skills in software optimization for efficiency and performance. With interactive labs and assignments, it offers practical experience in system-level programming, exploring hardware and software design choices. This course is ideal for those aiming to deepen their knowledge in computer architecture and system software, laying a solid foundation for advanced computer science and engineering studies.",
    4,
    "CSC 109 with a grade of \"C\" or higher or ROS 109 with a grade of \"C\" or higher",
    "1230",
    "MTW",
  )
  const a5 = createClassAlert (
    "NEW CLASS",
    "Unseen",
    "CSC",
    212,
    "Software",
    "This course builds on the material learned in ACC 101. Students use their knowledge of preparing financial statements to analyze and communicate a variety of financial information including accounting for plant assets, stockholders equity, current and long-term liabilities and the statement of cash flows. Students demonstrate the knowledge they gain by working with Web resources to present a financial analysis of a public corporation.",
    4,
    "CSC Core",
    "1230",
    "MTW",
  )
  const a6 = createClassAlert (
    "NEW CLASS",
    "Unseen",
    "CSC",
    212,
    "Software",
    "Build software",
    4,
    "CSC Core",
    "1230",
    "MTW",
  )
  const a7= createClassAlert (
    "NEW CLASS",
    "Unseen",
    "CSC",
    212,
    "Software",
    "This course builds on the material learned in ACC 101. Students use their knowledge of preparing financial statements to analyze and communicate a variety of financial information including accounting for plant assets, stockholders equity, current and long-term liabilities and the statement of cash flows. Students demonstrate the knowledge they gain by working with Web resources to present a financial analysis of a public corporation.",
    4,
    "CSC Core",
    "1230",
    "MTW",
  )
  const alerts: Alert[] = [
    a1, a2, a3, a4, a5, a6
  ]
  return alerts;
}