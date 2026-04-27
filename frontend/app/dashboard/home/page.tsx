/*
    Author: Sean Collins
*/
"use client"

import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import DashTitle from "@/app/components/visual/title"
import { Em, Flex } from "@radix-ui/themes";
import { UserMetadata } from "@/app/lib/account/account_db_utils";
import { useUserData } from "@/app/lib/account/user_context";

/**
 * Default home page with a title and different welcome messages for
 * students and advisors.
 * @returns 
 */
export default function Home () {
    const { userMetadata } : {userMetadata: UserMetadata} = useUserData();
    const message = (userMetadata.AccountType === "Student") ? 
        "Discuss your interests, academic goals, and questions with your AI advisor!" 
        : "View your student's goals and academic standing";
    return(
        <DashboardLayout>
            <DashTitle size="8">
                Welcome to <Em>advise.</Em> !
            </DashTitle>
            <Flex>
                {message}
            </Flex>
        </DashboardLayout>
    );
}