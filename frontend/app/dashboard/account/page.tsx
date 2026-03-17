"use client"

import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import { useSession } from "next-auth/react";

type Props = {
    children: React.ReactNode,
}

export default function Account ({children}: Props) {
    const session = useSession();
    return (
        <DashboardLayout>
            Username: {session?.data?.user?.name};
            {children}
        </DashboardLayout>
    );
}