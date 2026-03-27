import type { AccountType } from '@/app/lib/account_type'

export type ErrorTypes = {
    username?: string,
    password?: string,
    check_password?: string,
    account_type?: string,
    api_error?: string,
}

export class FormError extends Error {
    errors: ErrorTypes;

    constructor(errors: ErrorTypes) {
        super("Validation failure");
        this.name = "FormError";
        this.errors = errors;
    }
}

export function registrationValidationTests(username: string, password: string, conf_password: string, account_type: AccountType): FormError | null {
    let errorFlag: boolean = false;

    let ePass, eCheckPass, eUsername, eAccount : string = "";

    username.trim();
    password.trim();

    const validAccountTypes = ["student", "advisor"];

    // Test cases
    
    // Validate passwords
    if (password !== conf_password) {
        errorFlag = true;
        ePass = "Passwords do not match";
        eCheckPass = "Passwords do not match";
    } else if(password.includes(" ")) {
        errorFlag = true;
        ePass = "Password cannot contain whitespace";
        eCheckPass = "Password cannot contain whitespace";
    } else if(password.length < 12) {
        errorFlag = true;
        ePass = "Minimum password length is 12 characters";
        eCheckPass = "Minimum password length is 12 characters";
    } else if(password.length > 128) {
        errorFlag = true;
        ePass = "Maximum password length is 128 characters";
        eCheckPass = "Maximum password length is 128 characters";
    }

    // Validate username
    if (username.includes(" ")) {
        errorFlag = true;
        eUsername = "Username cannot contain whitespace"
    } else if(username.length < 6) {
        errorFlag = true;
        eUsername = "Minimum username length is 6 characters"
    } else if(username.length > 128) {
        errorFlag = true;
        eUsername = "Maximum username length is 128 characters"
    }

    if(!account_type) {
        errorFlag = true;
        eAccount = "Select an account type"
    } else if(!validAccountTypes.includes(account_type)) {
        errorFlag = true;
        eAccount = "Invalid account type"
    }

    if(errorFlag) {
        const thrownErrors: ErrorTypes = {
            username: eUsername,
            password: ePass,
            check_password: eCheckPass,
            account_type: eAccount,
        };
        return new FormError(thrownErrors);
    }

    return null;
}

export function loginValidationTests(username: string, password: string): FormError | null {
    let errorFlag: boolean = false;

    let ePass, eUsername: string = "";

    // Test cases
    
    // Validate passwords
    if(password.includes(" ")) {
        errorFlag = true;
        ePass = "Password contains whitespace!";
    } else if(password.length > 128) {
        errorFlag = true;
        ePass = "Password exceeds maximum length (128 characters)!";
    }

    // Validate username
    if (username.includes(" ")) {
        errorFlag = true;
        eUsername = "Username contains whitespace!"
    } else if(username.length > 128) {
        errorFlag = true;
        eUsername = "Username exceeds maximum length (128 characters)!"
    }

    if(errorFlag) {
        const thrownErrors: ErrorTypes = {
            username: eUsername,
            password: ePass,
        };
        return new FormError(thrownErrors);
    }

    return null;
}