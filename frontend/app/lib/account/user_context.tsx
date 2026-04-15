"use client"

import { createContext, useContext, useState } from "react";
import { type UserData, type UserMetadata, type UserAlerts, type UserStudents, type StudentContext, type AdvisorContext, type UserInterests, get_curr_context } from "@/app/lib/account/account_db_utils";

type Props = {
    children: React.ReactNode,
    currContext: StudentContext | AdvisorContext,
}

const UserContext = createContext(null as any);

// Stores personal user info and account metadata

export function UserContextProvider({children, currContext}: Props) {
    const [userData, setUserData] = useState<UserData>(currContext.userData);
    const [userMetadata, setUserMetadata] = useState<UserMetadata>(currContext.userMetadata);

    if(currContext.userMetadata.AccountType === "Student") {
        const studentContext = currContext as StudentContext;
        const [userAlerts, setUserAlerts] = useState<UserAlerts>(studentContext.userAlerts);
        const [userInterests, setUserInterests] = useState<UserInterests>(studentContext.userInterests);

        return (
            <UserContext.Provider value={{
                userData, userMetadata, 
                userAlerts, userInterests,
                setUserData, setUserMetadata,
                setUserAlerts, setUserInterests
            }}>
                {children}
            </UserContext.Provider>
        )
    } else if(currContext.userMetadata.AccountType === "Advisor") {
        const advisorContext = currContext as AdvisorContext;
        const [userStudents, setUserStudents] = useState<UserStudents>(advisorContext.userStudents);
        return (
            <UserContext.Provider value={{
                userData, userMetadata, 
                userStudents, setUserData, 
                setUserMetadata, setUserStudents
            }}>
                {children}
            </UserContext.Provider>
        )
    }
}

export const useUserData = () => useContext(UserContext);