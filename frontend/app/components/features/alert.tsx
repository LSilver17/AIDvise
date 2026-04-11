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

export default function SingleAlert({alert}: Props) {
    const minHeight="100px";
    const maxHeight="250px"
    return (
        <Flex direction="row" minHeight={minHeight} maxHeight={maxHeight} overflow="hidden">
            <Flex minHeight={minHeight} maxHeight={maxHeight} width="10px" style={{background:"orange"}}/>
            <Flex direction="column" width="100%" style={{background:"gainsboro"}} p="2">
                <AlertTitle size="6" gap="2" justify="start" align="start" pl="2">{alert.name}</AlertTitle>
                <Flex direction="column" align="center" ml="3">
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
