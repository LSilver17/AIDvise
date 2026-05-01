/*
    Author: Sean Collins
*/
import DefaultButton from "@/app/components/features/default_button"
import { AlertDialog, Flex } from "@radix-ui/themes";
import { delete_account } from "@/app/lib/account/account_db_utils"
import { signOut } from "next-auth/react";
import { alert_popup } from "@/app/lib/alerts/alert_popup";
import { authSession } from "@/app/lib/account/authSession";

/**
 * Component for account deletion, including an account deletion handler and
 * an alert dialog informing user about account deletion consequences.
 * @returns 
 */
export default function DeleteAccount() {
    const deleteAccount = async () => {
        const result = await delete_account();
        const session = await authSession();
        if(!result.success) {
            alert_popup(`${result?.error}`);
            return;
        }
        else if (session) {
            await signOut({callbackUrl:"/login"});
        }
    }
    return (
        <AlertDialog.Root>
            <AlertDialog.Trigger>
                <DefaultButton>
                    Delete account
                </DefaultButton>
            </AlertDialog.Trigger>
            <AlertDialog.Content>
                <AlertDialog.Title>Delete account</AlertDialog.Title>
                <AlertDialog.Description>
                    Are you sure you want to delete your account? 
                    Some data associated with your account will not be recoverable.
                </AlertDialog.Description>

                <Flex direction="row" justify="end" pt="10px" gap = "8px">
                    <AlertDialog.Cancel>
                        <DefaultButton size="2">
                            Cancel
                        </DefaultButton>
                    </AlertDialog.Cancel>
                    <AlertDialog.Action>
                        <DefaultButton size="2" onClick={deleteAccount}>
                            Delete account
                        </DefaultButton>
                    </AlertDialog.Action>
                </Flex>
            </AlertDialog.Content>
        </AlertDialog.Root>
    );
}