"use client"

import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import { useSession } from "next-auth/react";

// User components
import Title from "@/app/components/visual/title"
import AccountField from "@/app/components/visual/user_info_block";
import DeleteAccount from "@/app/components/features/delete_account";

export default function Account () {
    const session = useSession();
    return (
        <DashboardLayout>
            <Title>Account</Title>
            <AccountField dataField="Name">...</AccountField>
            {/*TODO: Sign out and delete both account/user database entries */}
            <DeleteAccount/>
        </DashboardLayout>
    );
}