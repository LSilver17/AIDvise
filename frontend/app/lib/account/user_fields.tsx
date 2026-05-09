/*
    Author: Sean Collins
    Description: 
        Interface to store metadata about a user data field.
    Copyright 2026
*/

/**
 * Stores data and metadata about a user field. Used for front-end rendering.
 * @param title - Title of the field.
 * @param data - Data contained in the field.
 * @param editable - Ability for user to edit the field.
 */
export interface UserField {
    title: string,
    data: string,
    editable: boolean,
}