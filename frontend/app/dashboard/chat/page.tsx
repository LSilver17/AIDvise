/*
    Author: Sean Collins
*/
"use client"

import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { Flex } from "@radix-ui/themes";

// Lib
import { useUserData } from "@/app/lib/account/user_context";
import type { UserData, UserMetadata, UserInterests, StudentData } from "@/app/lib/account/account_db_utils";
import type { AccountType } from "@/app/lib/account/account_type";

function choose_init_message(name: string, interests: UserInterests, accountType: AccountType): string {
  if(accountType === "Advisor") {
    var message_addition = "How can I help you today?";
    const message = `Hi, ${name}! ${message_addition}`;
    return message;
  } else if (accountType === "Student") {
    var message_addition = "How can I help you today?";
    if (interests.Interests.length == 0) message_addition = "Tell me about your academic and extracurricular interests.";
    const message = `Hi, ${name}! ${message_addition}`;
    return message;
  }
  return "Hello!";
}

/**
 * Displays CopilotKit's CopilotChat component with a customized user welcome message.
 */
export default function Chat() {
  const { userData, userMetadata, userInterests } : {userData: UserData, userMetadata: UserMetadata, userInterests: UserInterests} = useUserData();
  const accountType: AccountType = userMetadata?.AccountType;

  // Set name and message
  var name: string = "User";
  if(accountType) name = accountType as string;
  if(userData && userData.Name.data) name = userData.Name.data;
  const message = choose_init_message(name, userInterests, accountType);

  return (
    <Flex width="100%" height="100%" direction="row">
      <CopilotChat
        labels={{
          title:"Advise Bot",
          initial: message,
        }}
        className="w-full h-full"
      />
    </Flex>
  );
}
