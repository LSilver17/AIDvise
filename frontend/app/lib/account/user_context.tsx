/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Definition of UserContext, which allows for the data of an 
    active user to be shared among the provider's child
    components.
=============================================================================*/
"use client"

import { createContext, useContext, useState } from "react";
import { type UserData, type UserMetadata, type UserAlerts, type UserStudents, type StudentContext, type AdvisorContext, type UserInterests, get_curr_context } from "@/app/lib/account/account_db_utils";

type Props = {
    children: React.ReactNode,
    currContext: StudentContext | AdvisorContext,
}

const UserContext = createContext(null as any);

/**
 * A provider component for user context. The context stores user data, metadata, and account type specific data such as alerts and
 * students. 
 * @param {object} props.currContext - {@link StudentContext} or {@link AdvisorContext} object for initializing context variables.
 * @param {React.ReactNode} props.children - Child component to be wrapped in the provider.
 * @param {StudentContext | AdvisorContext} props.currContext - An object containing data to place inside the user context.
 */
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

/**
 * Hook to take state objects from user context given by the nearest provider. 
 * @returns Object containing the context's state variables.
 */
export const useUserData = () => useContext(UserContext);