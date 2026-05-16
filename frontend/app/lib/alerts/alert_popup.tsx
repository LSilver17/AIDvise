/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Function for error popups.
=============================================================================*/
"use client"

/**
 * Function for displaying API/backend errors with a window popup.
 * @param content - Contains error message.
 */
export function alert_popup(content: string) {
    window.alert(content);
}
