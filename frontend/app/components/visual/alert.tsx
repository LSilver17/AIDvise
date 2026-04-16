// Components
import { Flex } from "@radix-ui/themes";
import Card from "@/app/components/visual/card"

// Lib
import type { Alert, EventAlert, ClassAlert, AlertTypes } from "@/app/lib/alerts/alert"

export type AlertProps = {
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
        <Flex justify="start" direction="column" height="100%" width="100%" gap="2">
            <Flex justify="start" direction="row" height="100%" width="100%" flexGrow="1" wrap="wrap" gapX="3">
                <div><strong>Date/Time</strong>: {alert.date} {alert.time}</div>
            </Flex>
            <Flex pl="1" pr="1">{alert.description}</Flex>
        </Flex>
    )
}

function ClassAlert({alert}: ClassProps) {
    return (
        <Flex justify="start" direction="column" height="100%" width="100%" gap="2">
            <Flex justify="start" direction="row" height="100%" width="100%" flexGrow="1" wrap="wrap" gapX="3">
                <Flex><strong>{alert.department}-{alert.code}</strong>: {alert.courseName}</Flex>
                <Flex><strong>Credits</strong>: {alert.credits}</Flex>
                <Flex><strong>Requirements</strong>: {alert.requirements}</Flex>
                <Flex direction="row">
                    <Flex><strong>Schedule</strong>: {alert.days} {alert.meetTime}</Flex>
                </Flex>
            </Flex>
            <Flex pl="1" pr="1">{alert.courseDescription}</Flex>
        </Flex>
        
    )
}

export default function SingleAlert({alert}: AlertProps) {
    const minHeight="100px";
    const maxHeight="250px"
    return (
        <Card minHeight={minHeight} maxHeight={maxHeight} title={alert.name}>
            {
                (alert.type === "Event") ? <EventAlert alert={alert as EventAlert}/> : <></>
            }
            {
                (alert.type === "Class") ? <ClassAlert alert={alert as ClassAlert}/> : <></>
            }
        </Card>
    );
}
