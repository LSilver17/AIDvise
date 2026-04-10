"use client"

import { Flex } from "@radix-ui/themes";
import { AlertStatus } from "@/app/lib/alerts/alert"
import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import SingleAlert from "@/app/components/features/alert"
import DashTitle from "@/app/components/visual/title"
import DefaultButton from "@/app/components/features/default_button"

// Lib
import type { Alert, EventAlert, ClassAlert } from "@/app/lib/alerts/alert"
import { useUserData } from "@/app/lib/account/user_context";
import { UserAlerts } from "@/app/lib/account/account_db_utils";
import { redirect } from "next/navigation";
import { useCopilotKit } from "@copilotkit/react-core/v2";

// Hooks
import { useAgent } from "@copilotkit/react-core/v2";
import { authSession } from "@/app/lib/account/authSession";

export default function Alerts () {
    const { userAlerts } : { userAlerts: UserAlerts} = useUserData();

    const { agent } = useAgent({agentId:"alerts", updates:[]});
    const { copilotkit } = useCopilotKit();

    const generate_alerts = async () => {
        const session = await authSession();
        if(!session) {
            redirect("/login");
        }
        agent.setState({...agent.state, "student_id": session.user.id});
        await copilotkit.runAgent({agent});
    };

    return (
        <DashboardLayout>
            <DashTitle size="8">
                Alerts
            </DashTitle>
            <DefaultButton onClick={generate_alerts}>
                Check for new alerts
            </DefaultButton>
            <Flex direction="column">
                <DashTitle size="5">
                    Unseen
                </DashTitle>
                <Flex direction="column">
                    {
                        userAlerts ? userAlerts.Alerts.map((x,i) => (
                            <SingleAlert key={i} alert={x}/>
                        )) : <>Loading...</>
                    }
                </Flex>
                <DashTitle size="5">
                    Seen
                </DashTitle>
            </Flex>
        </DashboardLayout>
    );
}