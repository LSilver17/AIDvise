export class User {
    public constructor(username: string = "", password: string = "") {
        this.username = username;
        this.password = password;
    }
    public getUser() {
        return this.username;
    }
    public getPassword() {
        return this.password;
    }
    username: string = "";
    password: string = "";
}