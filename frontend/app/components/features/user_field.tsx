/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
"use client"

// Next
import { alert_popup } from "@/app/lib/alerts/alert_popup";

// Components
import { Flex, Separator } from "@radix-ui/themes"
import { Pencil1Icon, PaperPlaneIcon, Cross2Icon } from "@radix-ui/react-icons";
import { UserField } from "@/app/lib/account/user_fields";
import { Form } from "radix-ui"
import Button from "@/app/components/features/default_button"

// User
import FormField from "@/app/components/features/forms/formfield";
import { AccountDetailFormValidation } from "@/app/lib/form/form_test_cases";
import { update_user_entry } from "@/app/lib/account/account_db_utils";
import { useUserData } from "@/app/lib/account/user_context";

// Hooks
import { SubmitEventHandler, useState } from "react"

type AccountFieldPropTypes = {
    field: UserField,
    fieldName: string,
    children?: React.ReactNode,
}

/**
 * Renders single account field. Accepts a {@link UserField} object which defines the properties of the field,
 * such as value, title, and editability. Editable fields can be changed by the user and are passed through
 * {@link AccountDetailFormValidation}.
 * @param props.field - UserField object with field data.
 * @param props.fieldName - Name of field, used to select proper field validation function.
 * @returns 
 */
export default function AccountField({field, children, fieldName}: AccountFieldPropTypes) {
    const [isEditing, setIsEditing] = useState(false);
    const {userData, userMetadata} = useUserData();

    if (field.title == undefined) {
        return null;
    }

    const title = field.title;
    const data = field.data ?? "Empty";
    const editable = field.editable ?? false;

    const width = "400px"
    const submitHandler : SubmitEventHandler<HTMLFormElement> = async (event) => {
        const formData = new FormData(event.currentTarget);
        const newVal = formData.get(`${field.title}`) as string;
        
        try {
            if(!newVal) {
                throw Error("No new value")
            }
            const fieldVal = AccountDetailFormValidation(newVal);
            const result = await update_user_entry(userData, userMetadata, fieldVal, fieldName);
            if(!result?.success) {
                throw Error(result?.error);
            } else if (!result) {
                throw Error("Unknown error");
            }
        } catch(e: any) {
            alert_popup(`ERROR: ${e.message}`);
        }
        setIsEditing(false);
    }
    return (
        <Form.Root onSubmit={submitHandler}>
            <Flex direction="row" gap="2" align="center">
                <Flex direction="column" maxWidth={width} minWidth={width} minHeight="40px" maxHeight="40px" gap="2">
                    <Flex direction="row" maxWidth={width} minWidth={width} gap="2">
                        {
                            !isEditing ?
                            (
                                <>
                                    <Flex justify="start">
                                        {title}
                                    </Flex>
                                    <Flex justify="end" flexGrow="1">
                                        {data}
                                    </Flex>
                                </>
                            ) :
                            (
                                <FormField label={title} inputName={title} hasMissingMessage={false}/>
                            )
                        }
                    </Flex>
                    {!isEditing ? <Separator orientation="horizontal" size="4"/> : null}
                    
                </Flex>
                {
                    isEditing ? 
                    (
                        <>
                            <Form.Submit asChild>
                                <Button size="1">
                                    <PaperPlaneIcon/>
                                </Button>
                            </Form.Submit>
                            <Button size="1" onClick={() => setIsEditing(false)}>
                                <Cross2Icon/>
                            </Button>
                        </>
                    )
                    : (
                        <>
                            {
                                field.editable ? 
                                <Button size="1" onClick={() => setIsEditing(true)}>
                                    <Pencil1Icon/>
                                </Button> : <></>
                            }
                        </>
                    )
                }
            </Flex>
        </Form.Root>
    );
}