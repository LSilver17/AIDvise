/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   CopilotKit
CoAuthor: Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
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

/**
 * API endpoint handler for CopilotKit integration. A runtime object for CopilotKit 
 * request handlers is used to allow interaction with agents
 * defined in langgraph.json. See CopilotKit documentation for more info 
 * {@link https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime}.
 */
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};