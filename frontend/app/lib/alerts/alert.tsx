/*
    Author: Sean Collins
    Description: 
        Defines interfaces for creating and storing alerts.
*/

/**
 * Explicit alert status.
 */
export type AlertStatus = "Seen" | "Unseen";

/**
 * Explicit alert types.
 */
export type AlertTypes = "Event" | "Class";

/**
 * Base alert interface.
 * @property {string} name - Title of the alert.
 * @property {AlertStatus} status - Seen / Unseen
 * @property {AlertTypes} type - Seen / Unseen
 * @property {number} id - Unique identifier for student alert.
 */
export interface Alert {
    readonly name: string,
    readonly status: AlertStatus,
    readonly type: AlertTypes,
    readonly id: number,
}

/**
 * Interface for storing information about an event.
 * @extends Alert
 * @property {string} description - Description of the event.
 * @property {string} date - Date of the event.
 * @property {string} time - Time of the event.
 */
export interface EventAlert extends Alert {
    readonly description: string,
    readonly date: string,
    readonly time: string,
    readonly type: "Event",
}

/**
 * Interface for storing information about a course.
 * @extends Alert
 * @property {string} department - Course department.
 * @property {number} code - Course code.
 * @property {string} courseName - Name of the course.
 * @property {string} courseDescription - Description of course content.
 * @property {number} credits - Number of credit hours.
 * @property {string} requirements - Course requirements to register for the course.
 * @property {string} meetTime - Time frame for the course.
 * @property {string} days - Days the course is held.
 */
export interface ClassAlert extends Alert {
    readonly department: string,
    readonly code: number,
    readonly courseName: string,
    readonly courseDescription: string,
    readonly credits: number,
    readonly requirements: string,
    readonly meetTime: string,
    readonly days: string,
    readonly type: "Class",
}

/**
 * Function for initializing an event alert object.
 * @returns Event alert object.
 */
export function createEventAlert(
    name: string,
    description: string,
    status: AlertStatus,
    time: string,
    date: string,
    id: number,
) {
    const event: EventAlert = {
        name: name,
        description: description,
        status: status,
        time: time,
        date: date,
        type: "Event",
        id: id,
    }
    return event;
}

/**
 * Function for initializing a course alert object.
 * @returns Course alert object.
 */
export function createClassAlert(
    name: string,
    status: AlertStatus,
    department: string,
    code: number,
    courseName: string,
    courseDescription: string,
    credits: number,
    requirements: string,
    meetTime: string,
    days: string,
    id: number,
) {
    const event: ClassAlert = {
        name: name,
        status: status,
        department: department,
        code: code,
        courseName: courseName,
        courseDescription: courseDescription,
        credits: credits,
        requirements: requirements,
        meetTime: meetTime,
        days: days,
        type: "Class",
        id: id,
    }
    return event;
}