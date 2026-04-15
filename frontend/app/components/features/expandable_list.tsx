import type { Dispatch, SetStateAction } from "react";
import type { ComponentType } from "react";
import { Flex } from "@radix-ui/themes"

// Lib
import SingleAlert from "@/app/components/visual/alert";
import type { AlertProps } from "@/app/components/visual/alert";
import { Student } from "@/app/components/visual/student";
import type { StudentProps } from "@/app/components/visual/student";
import DefaultButton from "@/app/components/features/default_button"

// hooks & react lib
import { useState, cloneElement, createContext, useContext } from "react";
import React from "react";
import { Responsive, Union } from "@radix-ui/themes/props";

type Props = {
    children: React.ReactNode,
    list: any[],
    min: number,
    Component: ComponentType<AlertProps> | ComponentType<StudentProps>,
    componentType: "Alert" | "Student",
    isExpanded?: boolean,
    direction?: Responsive<"row" | "column" | "row-reverse" | "column-reverse">,
    gap?: Responsive<Union<string, "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9">>,
    width?: Responsive<string>,
    wrap?: Responsive<"wrap" | "nowrap" | "wrap-reverse">
}

type ButtonProps = {
    isExpanded: boolean,
    setExpanded: Dispatch<SetStateAction<boolean>>,
}

const toggleExpansion = (stateVar: any, stateSetter: Dispatch<SetStateAction<boolean>>) => {
    stateVar ? stateSetter(false) : stateSetter(true);
}

function renderComponent(Component: any, val: any, key: number, componentType: string) {
    if (componentType === "Alert") return <Component key={key} alert={val}/>;
    else if (componentType === "Student") return <Component key={key} student={val}/>;
}

const get_children = (children: any, displayName: any) => 
    React.Children.map(children, (child: any) =>
        child.type.displayName === displayName ? child : null
    );

const List = () => {
    const { list, isExpanded, min, Component, componentType, direction, gap, width, wrap} = useContext(ExpandableContext);
    if (!list) return <>Loading...</>
    if (list.length === 0) return null;
    return (
        <Flex direction={direction} gap={gap} width={width} wrap={wrap}>
            {
                list.map((x: any,i: any) => {
                    if(!isExpanded && i >= min) {
                        return null;
                    } else {
                        return renderComponent(Component, x, i, componentType);
                    }
                })
            }
        </Flex>
    );
}
List.displayName = "List";
ExpandableList.List = List;

const ExpandButton = () => {
    const {isExpanded, setExpanded, min, list} = useContext(ExpandableContext);
    if(!list || list.length <= min) return null;
    return (<DefaultButton onClick={() => toggleExpansion(isExpanded, setExpanded)}>
        {isExpanded ? "Show Less" : "Show More"}
    </DefaultButton>);
};
ExpandButton.displayName = "Button";
ExpandableList.Button = ExpandButton;

const ExpandableContext = createContext(null as any);

export function ExpandableList({children, list, min, Component, componentType, direction, gap, width, wrap}: Props) {
    const[isExpanded, setExpanded] = useState(false);
    const List = get_children(children, "List");
    const Button = get_children(children, "Button");

    direction = direction ?? "row";
    gap = gap ?? "1";
    width = width ?? ""
    wrap = wrap ?? "nowrap";

    return (
        <ExpandableContext.Provider value={{isExpanded, setExpanded, list, min, Component, componentType, direction, gap, width, wrap}}>
            {List}
            {Button}
        </ExpandableContext.Provider>
    );
}