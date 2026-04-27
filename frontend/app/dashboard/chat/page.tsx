/*
    Author: Sean Collins
*/
"use client"

import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-core/v2";
import data from "@/mock/mock.json";

// Lib
import { useUserData } from "@/app/lib/account/user_context";
import type { UserData, UserMetadata, UserInterests, StudentData } from "@/app/lib/account/account_db_utils";
import type { AccountType } from "@/app/lib/account/account_type";

// Hooks
import { useEffect } from "react";
import { useCoAgent } from "@copilotkit/react-core";

function choose_init_message(name: string, interests: UserInterests): string {
  var message_addition = "How can I help you today?";
  if (interests.Interests.length == 0) message_addition = "Tell me about your academic and extracurricular interests.";
  const message = `Hi, ${name}! ${message_addition}`;
  return message;
}

/**
 * Displays CopilotKit's CopilotChat component with a customized user welcome message.
 */
export default function Chat() {
  const { userData, userMetadata, userInterests } : {userData: UserData, userMetadata: UserMetadata, userInterests: UserInterests} = useUserData();
  const accountType: AccountType = userMetadata?.AccountType;
  
  // useEffect(() => {
  //     // if student
  //     if ( "StudentID" in userData ) {
  //       agent.setState({...agent.state, "student_id": userData.StudentID.data});
  //     }
  //   }
  // );

  // Set name and message
  var name: string = "User";
  if(accountType) name = accountType as string;
  if(userData && userData.Name.data) name = userData.Name.data;
  const message = choose_init_message(name, userInterests);

  return (
    <CopilotChat
      labels={{
        welcomeMessageText: message,
      }}
      className="w-full h-full"
    />
  );
}
