import type { AccountType } from '@/app/lib/account_type'

export interface User {
    username: string;
    account_type?: AccountType;
    id?: string;
}