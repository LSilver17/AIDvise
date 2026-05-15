/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Defines interfaces for creating and storing alerts.
=============================================================================*/
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
 * @property {string} date - Date of the alert.
 * @property {string} time - Time of the alert.
 * @property {AlertStatus} status - Seen / Unseen
 * @property {AlertTypes} type - Seen / Unseen
 * @property {number} id - Unique identifier for student alert.
 */
export interface Alert {
    readonly name: string,
    readonly date: string,
    readonly time: string,
    readonly status: AlertStatus,
    readonly type: AlertTypes,
    readonly id: number,
}

/**
 * Interface for storing information about an event.
 * @extends Alert
 * @property {string} description - Description of the event.
 */
export interface EventAlert extends Alert {
    readonly description: string,
    readonly type: "Event",
}

/**
 * Interface for storing information about a course.
 * @extends Alert
 * @property {string} department - Three letter department code.
 * @property {number} code - Three digit course code.
 * @property {string} courseName - Name of course.
 * @property {string} courseDescription - Description of course.
 * @property {number} credits - Number of credits.
 * @property {string} requirements - List of required courses as a single string.
 * @property {string} meetSchedule - Schedule in format "Day: StartTime-Endtime, ...".
 * @property {string} semestersOffered - Semesters course is offered (e.g. "F/SU").
 * @property {number} sectionNumber - Section number code.
 * @property {string} sectionStatus - Section status (Open, Closed, etc.).
 * @property {number} seats - Max seats.
 * @property {number} seatsLeft - Open seats.
 * @property {string} method - How the course is held (e.g. online, in-person).
 * @property {string} location - Room/building the class is held in.
 */
export interface ClassAlert extends Alert {
    readonly department: string,
    readonly code: number,
    readonly courseName: string,
    readonly courseDescription: string,
    readonly credits: number,
    readonly requirements: string,
    readonly meetSchedule: string,
    readonly semestersOffered: string,
    readonly sectionNumber: number,
    readonly sectionStatus: string,
    readonly seats: number,
    readonly seatsLeft: number,
    readonly method: string,
    readonly location:string
    readonly type: "Class",
}

/**
 * Function for initializing an event alert object.
 * @property {string} name - Description of the event.
 * @property {string} description - Description of the event.
 * @property {string} status - Status (Seen/Unseen)
 * @property {string} time - Time of the event.
 * @property {string} date - Date of the event.
 * @property {string} id - Unique ID in RelevantEvents table.
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
 * @property {string} name - Name of the alert (e.g. "Course Open").
 * @property {string} status - Seen/Unseen.
 * @property {string} date - Date of course status change.
 * @property {string} time - Time of course status change.
 * @property {string} department - Three letter department code.
 * @property {number} code - Three digit course code.
 * @property {string} courseName - Name of course.
 * @property {string} courseDescription - Description of course.
 * @property {number} credits - Number of credits.
 * @property {string} requirements - List of required courses as a single string.
 * @property {string} meetSchedule - Schedule in format "Day: StartTime-Endtime, ...".
 * @property {string} semestersOffered - Semesters course is offered (e.g. "F/SU").
 * @property {number} sectionNumber - Section number code.
 * @property {string} sectionStatus - Section status (Open, Closed, etc.).
 * @property {number} seats - Max seats.
 * @property {number} seatsLeft - Open seats.
 * @property {string} method - How the course is held (e.g. online, in-person).
 * @property {string} location - Room/building the class is held in.
 * @property {string} id - Unique ID in StudentSectionStatusChanges table.
 * @returns Course alert object.
 */
export function createClassAlert(
    name: string,
    status: AlertStatus,
    date: string,
    time: string,
    department: string,
    code: number,
    courseName: string,
    courseDescription: string,
    credits: number,
    requirements: string,
    meetSchedule: string,
    semestersOffered: string,
    sectionNumber: number,
    sectionStatus: string,
    seats: number,
    seatsLeft: number,
    method: string,
    location: string,
    id: number,
) {
    const event: ClassAlert = {
        name: name,
        status: status,
        department: department,
        date: date,
        time: time,
        code: code,
        courseName: courseName,
        courseDescription: courseDescription,
        credits: credits,
        requirements: requirements,
        meetSchedule: meetSchedule,
        semestersOffered: semestersOffered,
        sectionNumber: sectionNumber,
        sectionStatus: sectionStatus,
        seats: seats,
        seatsLeft: seatsLeft,
        method: method,
        location: location,
        type: "Class",
        id: id,
    }
    return event;
}