/*
    Author: Sean Collins
*/
import { authSession } from "@/app/lib/account/authSession";
import { redirect } from "next/navigation";

/**
 * Page authorization check, ensuring that only students can access alerts.
 * @returns 
 */
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