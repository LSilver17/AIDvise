"use client"

import { createContext, useContext, useState } from "react";
import type { UserData, UserMetadata, UserAlerts, Context } from "@/app/lib/account/account_db_utils";

type Props = {
    children: React.ReactNode,
    currContext: Context,
}

const UserContext = createContext(null as any);

// Stores personal user info and account metadata

export function UserContextProvider({children, currContext}: Props) {
    const [userData, setUserData] = useState<UserData | null>(currContext.userData);
    const [userMetadata, setUserMetadata] = useState<UserMetadata | null>(currContext.userMetadata);
    const [userAlerts, setUserAlerts] = useState<UserAlerts | null>(currContext.userAlerts);
    
    return (
        <UserContext.Provider value={{userData, userMetadata, userAlerts}}>
            {children}
        </UserContext.Provider>
    )
}

export const useUserData = () => useContext(UserContext);