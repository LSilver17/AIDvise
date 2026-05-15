/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Interface for user metadata.
=============================================================================*/
import type { AccountType } from '@/app/lib/account/account_type'

/**
 * Used to interface with user session data.
 */
export interface User {
    username: string;
    account_type?: AccountType;
    id?: string;
}