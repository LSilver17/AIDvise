"use client"

import { Avatar } from "radix-ui";
import { redirect } from "next/navigation";

export default function Account() {
    return (
        <Avatar.Root onClick={(e) => {redirect('/account');}}>
            <Avatar.Image />
            <Avatar.Fallback>USER</Avatar.Fallback>
        </Avatar.Root>
    );
}