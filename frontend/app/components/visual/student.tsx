/*
    Author: Sean Collins
*/
// Lib
import Card from "@/app/components/visual/card"
import type { Student } from "@/app/lib/account/account_db_utils";
import { Flex, Text } from "@radix-ui/themes";

export type StudentProps = {
    student: Student,
}

/**
 * Renders student card for the "Students" page in an advisor account.
 * @param props.student - Student object.
 * @returns 
 */
export function Student({student}: StudentProps) {
    const height="15rem";
    const width="15rem";
    const name = student.Name ?? "Unnamed";
    return (
        <Card height={height} width={width} title={name}>
            <Flex direction="column">
                {student.ID ? 
                    <Flex direction="row">
                        <Text weight="bold">Student ID</Text>: {student.ID}
                    </Flex> : <></>
                }
                {student.GPA ? 
                    <Flex direction="row">
                        <Text weight="bold">GPA</Text>: {student.GPA}
                    </Flex> : <></>
                }
                {student.CreditsEarned ? 
                    <Flex direction="row">
                        <Text weight="bold">Credits</Text>: {student.CreditsEarned}
                    </Flex> : <></>
                }
                {student.IntendedGraduationTerm ?
                    <Flex direction="row" wrap="wrap">
                        <Text weight="bold">Intended Graduation<Text weight="regular">:</Text></Text> {student.IntendedGraduationTerm}
                    </Flex> : <></>
                }
            </Flex>
        </Card>
    );
}