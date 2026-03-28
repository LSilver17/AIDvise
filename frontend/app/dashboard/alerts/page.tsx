"use client"

import { ScrollArea, Text, Box, Flex } from "@radix-ui/themes";
import { AlertStatus, UserAlert} from "@/app/lib/alert"
import { alerts } from "@/mock/mock.json";
import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import AlertLayout from "@/app/components/layout/alertlayout"
import SingleAlert from "@/app/components/features/alert"
import DashTitle from "@/app/components/visual/title"
// TODO: import from DB

// final alerts list
const userAlerts: UserAlert[] = [];

// TODO: populate list with DB alerts instead of JSON alerts
if (alerts.length != 0) {
    // iterates through alert list from JSON, storing in new list
    alerts.forEach(curr => {
        var status = ((stat: string) => 
            stat == "Unseen" ? 0 : 1)
        (curr.status);
        var alert = new UserAlert(curr.message, status);
        userAlerts.push(alert);
    })
}

export default function Alerts () {
    return (
        <DashboardLayout>
            <DashTitle size="8">
                Alerts
            </DashTitle>
            <AlertLayout >
                {userAlerts.map((x,i) => (
                    <SingleAlert key={i} status={x.getStatus()} content={x.getMessage()}/>
                ))}
            </AlertLayout>
        </DashboardLayout>
    );
}