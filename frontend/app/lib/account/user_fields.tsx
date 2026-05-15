/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Interface to store metadata about a user data field.
=============================================================================*/
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