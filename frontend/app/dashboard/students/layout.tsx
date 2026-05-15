/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import { authSession } from "@/app/lib/account/authSession";
import { redirect } from "next/navigation";

/**
 * Enforces authorization  with {@link authSession} so that only advisors can access the student page.
 * @returns 
 */
export default async function StudentCheck({ children, }: Readonly<{children: React.ReactNode;}>) {
  // session validation
  const session = await authSession();
  if(session?.user.account_type !== "Advisor") {
      redirect("/dashboard");
  }

  return (
    <>
        {children}
    </>
  );
}