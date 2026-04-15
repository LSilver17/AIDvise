"use client"

import { Flex } from "@radix-ui/themes";
import { AlertStatus } from "@/app/lib/alerts/alert"
import DashboardLayout from "@/app/components/layout/dashboardpagelayout"
import SingleAlert from "@/app/components/visual/alert"
import DashTitle from "@/app/components/visual/title"
import DefaultButton from "@/app/components/features/default_button"
import type { SetStateAction, Dispatch } from "react";

// Lib
import type { Alert, EventAlert, ClassAlert } from "@/app/lib/alerts/alert"
import { useUserData } from "@/app/lib/account/user_context";
import { get_curr_context, UserAlerts, mark_alerts_as_seen } from "@/app/lib/account/account_db_utils";
import { redirect } from "next/navigation";
import { useCopilotKit } from "@copilotkit/react-core/v2";
import { UserData, StudentData, UserMetadata, UserInterests, get_alerts } from "@/app/lib/account/account_db_utils";
import { ExpandableList } from "@/app/components/features/expandable_list";

// Hooks
import { useAgent } from "@copilotkit/react-core/v2";
import { authSession } from "@/app/lib/account/authSession";

const direction = "column";
const gap="5";
const width = "100%";

export default function Alerts () {
    
    const { userAlerts, setUserAlerts } : { userAlerts: UserAlerts, setUserAlerts: Dispatch<SetStateAction<UserAlerts | null>>} = useUserData();
    const { userData } : {userData: StudentData} = useUserData();
    const { userMetadata } : {userMetadata: UserMetadata} = useUserData();
    const { userInterests } : {userInterests: UserInterests} = useUserData();

    // setup agent
    const { agent } = useAgent({agentId:"alerts", updates:[]});
    const { copilotkit } = useCopilotKit();

    const generate_alerts = async () => {
        const session = await authSession();
        if(!session) {
            redirect("/login");
        }
        if(userData) {
            agent.setState({...agent.state, "student_id": userData.StudentID.data});
            await copilotkit.runAgent({agent});
            const new_alerts = await get_alerts(userData.StudentID.data);
            setUserAlerts(new_alerts);
        }
    };

    const mark_as_seen = async() => {
        const session = await authSession();
        if(!session) {
            redirect("/login");
        }
        if(userData) {
            const seen_alerts: UserAlerts = await mark_alerts_as_seen(userAlerts);
            setUserAlerts(seen_alerts);
        }
    }

    const shownAlerts = 3;
    const num_unseen = userAlerts.UnseenAlerts.length;
    const num_seen = userAlerts.SeenAlerts.length;

    return (
        <DashboardLayout>
            <DashTitle size="8">
                Alerts
            </DashTitle>
            <Flex width="100%" direction="row" gap="2">
                <Flex width="60rem" gap="4">
                    <DefaultButton onClick={generate_alerts} >
                        Check for new alerts
                    </DefaultButton>
                    {
                        userAlerts.UnseenAlerts.length !== 0 ? <DefaultButton onClick={mark_as_seen}>
                            Mark all as seen
                        </DefaultButton> : null
                    }
                </Flex>
            </Flex>
            {
                (userInterests.Interests && !(userInterests.Interests.length === 0)) ? 
                <Flex direction="column" gap="5">
                    {(userAlerts.UnseenAlerts.length !== 0) ? <>
                        <DashTitle size="7" gap="1">
                            Unseen
                        </DashTitle>
                        <ExpandableList 
                            list={userAlerts.UnseenAlerts}
                            min={shownAlerts} 
                            Component={SingleAlert} 
                            componentType="Alert"
                            direction={direction}
                            gap={gap}
                            width={width}
                        >
                            <ExpandableList.List/>
                            <ExpandableList.Button/>
                        </ExpandableList>
                    </> : null}
                <Flex height="30px"/>
                    {(userAlerts.SeenAlerts.length !== 0) ? <>
                        <DashTitle size="7" gap="1">
                            Seen
                        </DashTitle>
                        <ExpandableList 
                            list={userAlerts?.SeenAlerts}
                            min={shownAlerts} 
                            Component={SingleAlert} 
                            componentType="Alert"
                            direction={direction}
                            gap={gap}
                            width={width}
                        >
                            <ExpandableList.List/>
                            <ExpandableList.Button/>
                        </ExpandableList>
                    </> : null}
                </Flex> : <>Looks like you have no alerts. Start talking to your AI advisor about your interests!</>
            }
        </DashboardLayout>
    );
}