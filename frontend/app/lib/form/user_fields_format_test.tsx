/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Validates user-entered form values.
=============================================================================*/

/**
 * Object containing result data.
 */
type Result = {
    success: true,
} |
{
    success: false,
    error: string,
}

/**
 * Ensures string represents a number.
 * @returns 
 */
function isNumber(value: string): boolean {
  return !isNaN(Number(value));
}

/**
 * Validation function for name.
 * @returns 
 */
function checkName(input: string): Result {
    const res: Result = {
        success:true,
    }
    return res;
}

/**
 * Validation function for GPA.
 * @returns 
 */
function checkGPA(input: string): Result {
    const gpa = parseFloat(input);
    if((gpa < 0.0) || (gpa > 4.0)) {
        const res: Result = {
            success:false,
            error:"Invalid GPA",
        }
        return res;
    } else if(!isNumber(input)){
        const res: Result = {
            success:false,
            error:"Not a Number",
        }
        return res;
    } else {
        const res: Result = {
            success:true,
        }
        return res;
    }
}

/**
 * Validation function for credits.
 * @returns 
 */
function checkCreditsEarned(input: string): Result {
    const credits = parseFloat(input);

    if(credits < 0) {
        const res: Result = {
            success:false,
            error:"Invalid credit number",
        }
        return res;
    } else if(!isNumber(input)){
        const res: Result = {
            success:false,
            error:"Not a Number",
        }
        return res;
    } else {
        const res: Result = {
            success:true,
        }
        return res;
    }
}

/**
 * Validation function for intended graduation term.
 * @returns 
 */
function checkGradTerm(input: string): Result {
    const res: Result = {
        success:true,
    }
    return res;
}

/**
 * List of test functions. Each function returns a result object.
 */
const testFuncs: readonly{key: string; value : (input: string) => Result}[] = [
    { key: "Name", value: checkName},
    { key: "GPA", value: checkGPA},
    { key: "CreditsEarned", value:checkCreditsEarned},
    { key: "IntendedGraduationTerm", value:checkGradTerm},
]

/**
 * Validates a potential new value for a user field using an array of validation functions.
 * @param fieldName - Name of field to be validated.
 * @param inVal - Value to be validated
 * @returns 
 */
export function ensureFieldFormat(fieldName: string, inVal: string | null) {
    if(!inVal) {
        const res: Result = {
            success: true,
        };
        return res;
    }

    var res: Result = {
        success: false,
        error: "Field does not exist",
    };
    testFuncs.forEach((element) => {
        if (element.key == fieldName) {
            res = element.value(inVal);
        }
    });
    return res;
}