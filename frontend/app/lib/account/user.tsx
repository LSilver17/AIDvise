import type { AccountType } from '@/app/lib/account/account_type'

export interface User {
    username: string;
    account_type?: AccountType;
    id?: string;
}