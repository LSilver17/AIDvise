/*
    Author: Sean Collins
    Description: 
        Dynamically rendered alert component, taking
        an alert object as theme.
*/
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
    const requirements = alert.requirements ?? "None";
    const semestersOffered = alert.semestersOffered ?? 'Unknown';
    return (
        <Flex justify="start" direction="column" height="100%" width="100%" gap="2">
            <Flex justify="start" direction="row" height="100%" width="100%" flexGrow="1" wrap="wrap" gapX="3">
                <Flex><strong>{alert.department} {alert.code}-{alert.sectionNumber}</strong>: {alert.courseName}</Flex>
                <Flex><strong>Credits</strong>: {alert.credits}</Flex>
                <Flex><strong>Requirements</strong>: {requirements}</Flex>
                <Flex direction="row">
                    <Flex><strong>Schedule</strong>: {alert.meetSchedule}</Flex>
                </Flex>
                <Flex><strong>Semester Offered</strong>: {semestersOffered}</Flex>
                <Flex><strong>Status</strong>: {alert.sectionStatus}</Flex>
                <Flex><strong>Seats Left</strong>: {alert.seatsLeft}/{alert.seats}</Flex>
                <Flex><strong>Method</strong>: {alert.method}</Flex>
                <Flex><strong>Location</strong>: {alert.location}</Flex>
            </Flex>
            <Flex pl="1" pr="1">{alert.courseDescription}</Flex>
        </Flex>
        
    )
}

/**
 * Dynamically rendered alert component. Takes either a class or event alert
 * as prop and renders the corresponding alert card with the object's properties.
 * @param props.alert - Course or event alert object. 
 * @returns 
 */
export default function SingleAlert({alert}: AlertProps) {
    const minHeight="100px";
    const maxHeight="350px"
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
