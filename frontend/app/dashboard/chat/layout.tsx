/*
    Author: Sean Collins
*/
import { authSession } from "@/app/lib/account/authSession";
import { redirect } from "next/navigation";
import { useUserData } from "@/app/lib/account/user_context";
import { StudentContext, UserData } from "@/app/lib/account/account_db_utils";

/**
 * Enforces authorization for chat usage based on account type.
 * @returns 
 */
export default async function ChatCheck({ children, }: Readonly<{children: React.ReactNode;}>) {
  // session validation
  // const session = await authSession();
  // if(!(session?.user.account_type) || session?.user.account_type !== "Student") {
  //     redirect("/dashboard");
  // }

  return (
    <>
        {children}
    </>
  );
}