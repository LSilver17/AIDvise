import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { LangGraphAgent } from "@copilotkit/runtime/langgraph";
import { NextRequest } from "next/server";

const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
  agents: {
    "default": new LangGraphAgent({
      deploymentUrl:  process.env.LANGGRAPH_DEPLOYMENT_URL || "http://localhost:8123",
      graphId: "chat_agent",
      langsmithApiKey: process.env.LANGSMITH_API_KEY || "",
    }),
    "alerts": new LangGraphAgent({
      deploymentUrl:  process.env.LANGGRAPH_DEPLOYMENT_URL || "http://localhost:8123",
      graphId: "alert_agent",
      langsmithApiKey: process.env.LANGSMITH_API_KEY || "",
    }),
  }
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};