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
        <Flex direction="row" justify="between">
            {alert.date}
            {alert.time}
        </Flex>
    )
}

function ClassAlert({alert}: ClassProps) {
    return (
        <Flex direction="row">
            <Flex justify="start" direction="column">
                Course Opening: {alert.department}-{alert.code}
                {alert.courseName}
                {alert.courseDescription}
                Credits: {alert.credits}
                Requirements: {alert.requirements}
            </Flex>
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
        <Flex direction="column" width = "500px">
            <AlertTitle size="6">{alert.name}</AlertTitle>
            <Flex direction="column">
                {alert.description}
                {
                    (alert.type === "Event") ? <EventAlert alert={alert as EventAlert}/> : <></>
                }
                {
                    (alert.type === "Class") ? <ClassAlert alert={alert as ClassAlert}/> : <></>
                }
            </Flex>
        </Flex>
    );
}
