"use client"

// Flex
import { Flex } from "@radix-ui/themes";

// Lib
import DashboardLayout from "@/app/components/layout/dashboardpagelayout";
import DashTitle from "@/app/components/visual/title";
import Card from "@/app/components/visual/card";
import type { UserMetadata } from "@/app/lib/account/account_db_utils";
import type { UserStudents } from "@/app/lib/account/account_db_utils";
import { ExpandableList } from "@/app/components/features/expandable_list";
import { Student } from "@/app/components/visual/student";

// Hooks
import { useUserData } from "@/app/lib/account/user_context";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Students() {
    // Context and state
    const { userMetadata } : { userMetadata: UserMetadata} = useUserData();
    const { userStudents } : { userStudents: UserStudents} = useUserData();
    const minStudents = 3;
    
    //TODO: redirect
    if(userMetadata.AccountType !== "Advisor") {
        const router = useRouter();
        router.push("/dashboard/home");
    }

    return (
        <DashboardLayout>
            <DashTitle size="8">
                Students
            </DashTitle>
            
            <ExpandableList
                list={userStudents?.Students}
                min={minStudents}
                Component={Student}
                componentType="Student"
                wrap="wrap"
                gap="6"
            >
                <ExpandableList.List/>
                <ExpandableList.Button/>
            </ExpandableList>
        </DashboardLayout>
    );
}