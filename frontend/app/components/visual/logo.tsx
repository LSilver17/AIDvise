/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import { Text, Em } from "@radix-ui/themes"
import type { Responsive } from "@radix-ui/themes/props";
import advise from "@/app/components/assets/aidvise.png"

type PropTypes = {
    size?: Responsive<"1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"> | undefined;
}

/**
 * Static logo component for the application.
 * @param size - Logo size. 
 * @returns 
 */
export default function Logo ({size}: PropTypes) {
    size = size ?? "1";
    return (
        <img src={advise.src} alt="advise" />
    );
}