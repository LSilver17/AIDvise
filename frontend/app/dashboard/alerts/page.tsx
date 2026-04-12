"use client"

import { Flex } from "@radix-ui/themes";
import { AlertStatus } from "@/app/lib/alerts/alert"
import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import SingleAlert from "@/app/components/visual/alert"
import DashTitle from "@/app/components/visual/title"
import DefaultButton from "@/app/components/features/default_button"

// Lib
import type { Alert, EventAlert, ClassAlert } from "@/app/lib/alerts/alert"
import { useUserData } from "@/app/lib/account/user_context";
import { UserAlerts } from "@/app/lib/account/account_db_utils";
import { redirect } from "next/navigation";
import { useCopilotKit } from "@copilotkit/react-core/v2";
import type { UserMetadata } from "@/app/lib/account/account_db_utils";
import { ExpandableList } from "@/app/components/features/expandable_list";

// Hooks
import { useAgent } from "@copilotkit/react-core/v2";
import { authSession } from "@/app/lib/account/authSession";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { getSession, useSession } from "next-auth/react";

// Next
import { NextResponse } from "next/server";

function AlertContainer({children} : {children: React.ReactNode}) {
    return ( 
        <Flex direction="column" gap="5" width="100%">
            {children}
        </Flex>
    )
}

export default function Alerts () {
    // TODO: Actually redirect
    const session = useSession();
    const router = useRouter();
    
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
                    <ExpandableList 
                        list={userAlerts?.Alerts} 
                        vis={isUExpanded} 
                        setVis={setUExpanded} 
                        min={shownAlerts} 
                        Component={SingleAlert} 
                        componentType="Alert"
                    />
                </AlertContainer>
                <Flex height="30px"/>
                <DashTitle size="7" gap="1">
                    Seen
                </DashTitle>
                <AlertContainer>
                    <ExpandableList 
                        list={userAlerts?.Alerts} 
                        vis={isSExpanded} 
                        setVis={setSExpanded} 
                        min={shownAlerts} 
                        Component={SingleAlert} 
                        componentType="Alert"
                    />
                </AlertContainer>
            </Flex>
        </DashboardLayout>
    );
}