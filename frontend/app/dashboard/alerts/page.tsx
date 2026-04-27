/*
    Author: Sean Collins
*/
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
import { get_curr_context, UserAlerts, UserEventAlerts, UserCourseAlerts, mark_alerts_as_seen } from "@/app/lib/account/account_db_utils";
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

function unseenAlerts(alerts: UserAlerts): boolean {
    return unseenEventAlerts(alerts.EventAlerts) || unseenCourseAlerts(alerts.CourseAlerts);
}

function unseenEventAlerts(alerts: UserEventAlerts): boolean {
    return alerts.UnseenAlerts.length !== 0;
}

function seenEventAlerts(alerts: UserEventAlerts): boolean {
    return !unseenEventAlerts(alerts);
}

function unseenCourseAlerts(alerts: UserCourseAlerts): boolean {
    return alerts.UnseenAlerts.length !== 0;
}

function seenCourseAlerts(alerts: UserCourseAlerts): boolean {
    return !unseenCourseAlerts(alerts);
}

/**
 * Dynamically renders user alerts with the ExpandableList component. Alerts are categorized into Event
 * and Course alerts, marked as either Seen or Unseen. The user can mark all seen alerts as seen or
 * call the alert agent to generate new alerts based on any added interests or events.
 * @returns 
 */
export default function Alerts () {
    
    const { userAlerts, setUserAlerts } : { userAlerts: UserAlerts, setUserAlerts: Dispatch<SetStateAction<UserAlerts | null>>} = useUserData();
    const { userData } : {userData: StudentData} = useUserData();
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
    const eventAlerts = userAlerts.EventAlerts;
    const courseAlerts = userAlerts.CourseAlerts;

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
                        unseenAlerts(userAlerts) ? <DefaultButton onClick={mark_as_seen}>
                            Mark all as seen
                        </DefaultButton> : null
                    }
                </Flex>
            </Flex>
            {
                (userInterests.Interests && !(userInterests.Interests.length === 0)) ? 
                <Flex direction="column" gap="5">
                    {unseenEventAlerts(eventAlerts) ? <>
                        <DashTitle size="7" gap="1">
                            Unseen Events
                        </DashTitle>
                        <ExpandableList 
                            list={eventAlerts.UnseenAlerts}
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
                    {(seenEventAlerts(eventAlerts)) ? <>
                        <DashTitle size="7" gap="1">
                            Seen Events
                        </DashTitle>
                        <ExpandableList 
                            list={eventAlerts.SeenAlerts}
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