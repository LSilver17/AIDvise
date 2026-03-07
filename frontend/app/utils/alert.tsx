export enum AlertStatus {
    Unseen,
    Seen
}

export class Alert {
    public constructor(message: string = "Empty", status: AlertStatus = AlertStatus.Unseen) {
        this.message = message;
        this.status = status;
    }

    public getMessage() {
        return this.message;
    }

    public getStatus() {
        return this.status;
    }

    private message: string;
    private status: AlertStatus;
}