"use client"

import { Flex } from "@radix-ui/themes";
import { AlertStatus } from "@/app/lib/alerts/alert"
import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import SingleAlert from "@/app/components/features/alert"
import DashTitle from "@/app/components/visual/title"

// Lib
import type { Alert, EventAlert, ClassAlert } from "@/app/lib/alerts/alert"
import { useUserData } from "@/app/lib/account/user_context";
import { UserAlerts } from "@/app/lib/account/account_db_utils";

export default function Alerts () {
    const { userAlerts } : { userAlerts: UserAlerts} = useUserData();
    return (
        <DashboardLayout>
            <DashTitle size="8">
                Alerts
            </DashTitle>
            <Flex direction="column">
                {
                    userAlerts ? userAlerts.Alerts.map((x,i) => (
                        <SingleAlert key={i} alert={x}/>
                    )) : <>Loading...</>
                }
            </Flex>
        </DashboardLayout>
    );
}