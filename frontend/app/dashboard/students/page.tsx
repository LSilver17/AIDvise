/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
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

/**
 * Uses {@link ExpandableList} component to dynamically generate a visual list of students
 * under an advisor.
 * @returns 
 */
export default function Students() {
    // Context and state
    const { userMetadata } : { userMetadata: UserMetadata} = useUserData();
    const { userStudents } : { userStudents: UserStudents} = useUserData();
    const minStudents = 3;
    
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