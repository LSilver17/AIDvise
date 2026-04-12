// Library
import Sidebar from "@/app/components/navigation/aside";
import { UserContextProvider } from "@/app/lib/account/user_context";
import { get_curr_context } from "@/app/lib/account/account_db_utils";
import { authSession } from "@/app/lib/account/authSession";

import { signOut } from "next-auth/react";
import { redirect } from "next/navigation";

export default async function AlertCheck({ children, }: Readonly<{children: React.ReactNode;}>) {
  // session validation
  const session = await authSession();
  if(session?.user.account_type !== "Student") {
      redirect("/dashboard");
  }

  return (
    <>
        {children}
    </>
  );
}