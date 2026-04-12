import type { Dispatch, SetStateAction } from "react";
import type { ComponentType } from "react";

// Lib
import SingleAlert from "@/app/components/visual/alert";
import type { AlertProps } from "@/app/components/visual/alert";
import { Student } from "@/app/components/visual/student";
import type { StudentProps } from "@/app/components/visual/student";
import DefaultButton from "@/app/components/features/default_button"

type Props = {
    list: any[],
    vis: boolean,
    setVis: Dispatch<SetStateAction<boolean>>,
    min: number,
    Component: ComponentType<AlertProps> | ComponentType<StudentProps>,
    componentType: "Alert" | "Student",
}

const toggleExpansion = (stateVar: any, stateSetter: Dispatch<SetStateAction<boolean>>) => {
    stateVar ? stateSetter(false) : stateSetter(true);
}

function renderComponent(Component: any, val: any, key: number, componentType: string) {
    if (componentType === "Alert") return <Component key={key} alert={val}/>;
    else if (componentType === "Student") return <Component key={key} student={val}/>;
}

export function ExpandableList({list, vis, setVis, min, Component, componentType}: Props) {
    return (
        <>
            {
                list ? list.map((x,i) => {
                    if(!vis && i >= min) {
                        return;
                    } else {
                        return renderComponent(Component, x, i, componentType);
                    }
                }) : <>Loading...</>
            }
            {
                <DefaultButton onClick={() => toggleExpansion(vis, setVis)}>
                    {vis ? "Show Less" : "Show More"}
                </DefaultButton>
            }
        </>
    );
}