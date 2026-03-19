
import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import data from "@/mock/mock.json";

// .venv\Scripts\activate && npx @langchain/langgraph-cli dev --port 8123 --no-browser
// .venv\Scripts\activate && cd frontend && npm run dev

export default function Chat() {
  return (
    <CopilotChat
      labels={{
        title: "Academic Advisor",
        initial: `Hi, ${data.name}! How can I assist you today?`,
      }}
     className="w-full h-full"
    />
  );
}
