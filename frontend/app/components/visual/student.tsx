// Lib
import Card from "@/app/components/visual/card"
import type { Student } from "@/app/lib/account/account_db_utils";

export type StudentProps = {
    student: Student,
}

export function Student({student}: StudentProps) {
    const minHeight="15rem";
    const maxHeight="15rem";
    const name = student.Name ?? "Unnamed";
    return (
        <Card minHeight={minHeight} maxHeight={maxHeight} title={name}>
            Student
        </Card>
    );
}