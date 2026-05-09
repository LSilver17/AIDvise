/*
    Author: Sean Collins
    Copyright: 2026
*/
"use client"

import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import { Flex } from "@radix-ui/themes"

// Lib
import Title from "@/app/components/visual/title"
import AccountField from "@/app/components/features/user_field";
import DeleteAccount from "@/app/components/features/delete_account";
import { useUserData } from "@/app/lib/account/user_context";
import { UserData } from "@/app/lib/account/account_db_utils";

/**
 * Grabs user account data to render dynamically as individual fields
 * in account overview page.
 * @returns 
 */
export default function Account () {
    const { userData } : {userData: UserData} = useUserData();
    return (
        <DashboardLayout>
            <Title size="8">Account</Title>
            {   
                userData ? Object.entries(userData).map(([key, value],i: number) => {
                    try {
                        return <AccountField key={i} field={value} fieldName={key}/>;
                    } catch(e) {
                        console.log(`ERROR: Could not log datafield ${key} with field \'${value.title}: ${value.data}\'`);
                        return null;
                    }
                }) : <>Loading...</>
            }
            {/*TODO: Sign out and delete both account/user database entries */}
            <Flex align="end">
                <DeleteAccount/>
            </Flex>
        </DashboardLayout>
    );
}