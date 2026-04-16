"use client"

import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import data from "@/mock/mock.json";

// Lib
import { useUserData } from "@/app/lib/account/user_context";
import type { UserData, UserMetadata, UserInterests, StudentData } from "@/app/lib/account/account_db_utils";
import type { AccountType } from "@/app/lib/account/account_type";

// Hooks
import { useEffect } from "react";
import { useAgent } from "@copilotkit/react-core/v2";

function choose_init_message(name: string, interests: UserInterests): string {
  var message_addition = "How can I help you today?";
  if (interests.Interests.length == 0) message_addition = "Tell me about your academic and extracurricular interests.";
  const message = `Hi, ${name}! ${message_addition}`;
  return message;
}

export default function Chat() {
  const { userData, userMetadata, userInterests } : {userData: UserData, userMetadata: UserMetadata, userInterests: UserInterests} = useUserData();
  const { agent } = useAgent({agentId:"default", updates:[]});
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
        title: "Academic ChatBot",
        initial: message,
      }}
     className="w-full h-full"
    />
  );
}
