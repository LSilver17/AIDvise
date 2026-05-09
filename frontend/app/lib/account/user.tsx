/*
    Author: Sean Collins
    Description: 
        Interface to metadata about a user.
    Copyright 2026
*/
import type { AccountType } from '@/app/lib/account/account_type'

/**
 * Used to interface with user session data.
 */
export interface User {
    username: string;
    account_type?: AccountType;
    id?: string;
}