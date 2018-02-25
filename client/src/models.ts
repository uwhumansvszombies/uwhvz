// {"username": "tristan", "first_name": "Tristan", "last_name": "Ohlson", "email": "tsohlson@gmail.com"}
export default class User {
    username: string;
    firstName: string;
    lastName: string;
    email: string;

    constructor(username: string, firstName: string, lastName: string, email: string) {
        this.username = username;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
    }
}
