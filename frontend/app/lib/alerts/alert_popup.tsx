/*
    Author: Sean Collins
    Description: 
        Function for creating error popups.
*/
"use client"

/**
 * Function for displaying API/backend errors with a window popup.
 * @param content - Contains error message.
 */
export function alert_popup(content: string) {
    window.alert(content);
}
