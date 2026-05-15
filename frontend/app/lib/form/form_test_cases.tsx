/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Runs test cases for user form submissions.
=============================================================================*/
import type { AccountType } from '@/app/lib/account/account_type'

/**
 * Object containing error strings for potential field input errors.
 */
export type ErrorTypes = {
    username?: string,
    password?: string,
    check_password?: string,
    account_type?: string,
    id?: string,
    api_error?: string,
}

/**
 * Object reporting validation status and list of errors.
 */
export class FormError extends Error {
    errors: ErrorTypes;

    constructor(errors: ErrorTypes) {
        super("Validation failure");
        this.name = "FormError";
        this.errors = errors;
    }
}

/**
 * Checks whether a string is a number.
 * @param value - Value to check.
 * @returns String number condition.
 */
function isNumber(value: string): boolean {
  return !isNaN(Number(value));
}

/**
 * Series of validation tests to verify valid registration input after initial form validation.
 * Ensures that passwords match, fields are not overly long, usernames contain valid characters,
 * account type is valid, and ID is a number.
 * @returns 
 */
export function registrationValidationTests(username: string, password: string, conf_password: string, account_type: AccountType, id: string): FormError | null {
    let errorFlag: boolean = false;

    let ePass, eCheckPass, eUsername, eAccount, eID : string = "";

    username.trim();
    password.trim();

    const validAccountTypes = ["Student", "Advisor"];

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

    // Validate ID
    if(!isNumber(id)) {
        errorFlag = true;
        eID = "ID must be a number"
    }

    if(errorFlag) {
        const thrownErrors: ErrorTypes = {
            username: eUsername,
            password: ePass,
            check_password: eCheckPass,
            account_type: eAccount,
            id: eID,
        };
        return new FormError(thrownErrors);
    }

    return null;
}

/**
 * Series of validation tests to verify valid login input after initial form validation.
 * Ensures that fields are under maximum character count and contain valid characters.
 * @returns 
 */
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
            api_error:`${eUsername} ${ePass}`
        };
        return new FormError(thrownErrors);
    }

    return null;
}

/**
 * Sanitizes form field string by shortening string ensuring it is not
 * empty.
 * @param field - Field to be checked.
 * @returns Sanitized string if valid, null if only contains whitespace.
 */
export function AccountDetailFormValidation(field : string) {
    field = field.substring(0, 32);
    if(field.replace(/\s/g, "") === "") {
        return null;
    } 
    return field.trim();
}