import { authSession } from "@/app/lib/account/authSession";
import { redirect } from "next/navigation";

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