// Components
import { Flex, Text } from "@radix-ui/themes";
import { AlertStatus } from "@/app/lib/alerts/alert"
import AlertTitle from "@/app/components/visual/title"

// Lib
import type { Alert, EventAlert, ClassAlert, AlertTypes } from "@/app/lib/alerts/alert"

type Props = {
    alert: Alert,
}

type EventProps = {
    alert: EventAlert,
}

type ClassProps = {
    alert: ClassAlert,
}

function EventAlert({alert}: EventProps) {
    return (
        <Flex width="100%" height="100%" direction="column">
            <Flex>
                {alert.description}
            </Flex>
            <Flex direction="row" justify="between">
                <div>{alert.date}</div>
                <div>{alert.time}</div>
            </Flex>
        </Flex>
    )
}

function ClassAlert({alert}: ClassProps) {
    return (
        <Flex justify="start" direction="column" height="100%" width="100%">
            <Flex justify="between" direction="row" height="100%" width="100%" flexGrow="1">
                <div>{alert.department}-{alert.code}: {alert.courseName}</div>
                <div>Credits: {alert.credits}</div>
            </Flex>
                {alert.courseDescription}
                Requirements: {alert.requirements}
            <Flex justify="end" direction="column">
                Schedule: 
                {alert.meetTime}
                {alert.days}
            </Flex>
        </Flex>
        
    )
}

export default function SingleAlert({alert}: Props) {
    return (
        <Flex direction="row" height="150px" overflow="hidden" mt="3">
            <Flex height="100%" width="10px" style={{background:"orange"}}/>
            <Flex direction="column" width="500px" style={{background:"lightgray"}} p="2">
                <AlertTitle size="6">{alert.name}</AlertTitle>
                <Flex direction="column" align="center">
                    {
                        (alert.type === "Event") ? <EventAlert alert={alert as EventAlert}/> : <></>
                    }
                    {
                        (alert.type === "Class") ? <ClassAlert alert={alert as ClassAlert}/> : <></>
                    }
                </Flex>
            </Flex>
        </Flex>
    );
}
