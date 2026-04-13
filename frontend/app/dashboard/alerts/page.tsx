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
import { useState } from "react";

function AlertContainer({children} : {children: React.ReactNode}) {
    return ( 
        <Flex direction="column" gap="5" width="100%">
            {children}
        </Flex>
    )
}

export default function Alerts () {
    // grab user alerts
    const { userAlerts } : { userAlerts: UserAlerts} = useUserData();

    // setup agent
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

    // alert view state
    const[isUExpanded, setUExpanded] = useState(false);
    const[isSExpanded, setSExpanded] = useState(false);
    const shownAlerts = 3;

    const toggleExpansion = (stateVar: any, stateSetter: any) => {
        stateVar ? stateSetter(false) : stateSetter(true);
    }

    return (
        <DashboardLayout>
            <DashTitle size="8">
                Alerts
            </DashTitle>
            <Flex width="100%" direction="row" gap="2">
                <Flex width="60rem">
                    <DefaultButton onClick={generate_alerts} >
                        Check for new alerts
                    </DefaultButton>
                </Flex>
            </Flex>
            <Flex direction="column" gap="5">
                <DashTitle size="7" gap="1">
                    Unseen
                </DashTitle>
                <AlertContainer>
                    {
                        userAlerts ? userAlerts.Alerts.map((x,i) => {
                            if(!isUExpanded && i >= shownAlerts) {
                                return;
                            } else {
                                return <SingleAlert key={i} alert={x}/>
                            }
                        }) : <>Loading...</>
                    }
                    {
                        <DefaultButton onClick={() => toggleExpansion(isUExpanded, setUExpanded)}>
                            {isUExpanded ? "Show Less" : "Show More"}
                        </DefaultButton>
                    }
                </AlertContainer>
                <Flex height="30px"/>
                <DashTitle size="7" gap="1">
                    Seen
                </DashTitle>
                <AlertContainer>
                    {
                        userAlerts ? userAlerts.Alerts.map((x,i) => {
                            if(!isSExpanded && i >= shownAlerts) {
                                return;
                            } else {
                                return <SingleAlert key={i} alert={x}/>
                            }
                        }) : <>Loading...</>
                    }
                    {
                        <DefaultButton onClick={() => toggleExpansion(isSExpanded, setSExpanded)}>
                            {isSExpanded ? "Show Less" : "Show More"}
                        </DefaultButton>
                    }
                </AlertContainer>
            </Flex>
        </DashboardLayout>
    );
}