"use client"

import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import data from "@/mock/mock.json";

//Lib
import { useUserData } from "@/app/lib/account/user_context";
import type { UserData, UserMetadata } from "@/app/lib/account/account_db_utils";
import type { AccountType } from "@/app/lib/account/account_type";

// .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
// .venv\Scripts\activate && cd frontend && npm run dev

export default function Chat() {
  const { userData, userMetadata } : {userData: UserData, userMetadata: UserMetadata} = useUserData();
  const accountType: AccountType = userMetadata?.AccountType;

  var name: string = "User";
  if(accountType) name = accountType as string;
  if(userData && userData.Name.data) name = userData.Name.data;

  return (
    <CopilotChat
      labels={{
        title: "Academic ChatBot",
        initial: `Hi, ${name}! How can I assist you today?`,
      }}
     className="w-full h-full"
    />
  );
}
