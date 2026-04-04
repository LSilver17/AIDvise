type Result = {
    success: true,
} |
{
    success: false,
    error: string,
}

function isNumber(value: string): boolean {
  return !isNaN(Number(value));
}

function checkName(input: string): Result {
    const res: Result = {
        success:true,
    }
    return res;
}

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

function checkGradTerm(input: string): Result {
    // TODO: ensure gradterm follows format
    const res: Result = {
        success:true,
    }
    return res;
}

const testFuncs: readonly{key: string; value : (input: string) => Result}[] = [
    { key: "Name", value: checkName},
    { key: "GPA", value: checkGPA},
    { key: "CreditsEarned", value:checkCreditsEarned},
    { key: "IntendedGraduationTerm", value:checkGradTerm},
]

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