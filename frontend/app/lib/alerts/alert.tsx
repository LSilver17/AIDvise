export type AlertStatus = "Seen" | "Unseen";

export type AlertTypes = "Event" | "Class";

export interface Alert {
    readonly name: string,
    readonly status: AlertStatus,
    readonly type: AlertTypes,
}

export interface EventAlert extends Alert {
    readonly description: string,
    readonly time: string,
    readonly date: string,
    readonly type: "Event",
}

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

export function createEventAlert(
    name: string,
    description: string,
    status: AlertStatus,
    time: string,
    date: string,
) {
    const event: EventAlert = {
        name: name,
        description: description,
        status: status,
        time: time,
        date: date,
        type: "Event",
    }
    return event;
}

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
    }
    return event;
}