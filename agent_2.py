#!/usr/bin/env python3
"""
Frontend AI Agent
Specialized for: frontend_developer
"""

import os
import asyncio
from pydantic_ai import Agent, RunContext
import httpx
import json
from typing import Dict, Any
from fastapi import FastAPI
import uvicorn

class FrontendAgent:
    def __init__(self):
        self.model_name = os.getenv('MODEL_NAME', "deepseek-coder:6.7b")
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.mcp_gateway = os.getenv('MCP_GATEWAY_URL', 'http://localhost:8080')

        # Initialize the agent
        self.agent = Agent(
            model=f"ollama:{self.model_name}",
            system_prompt=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        return """
        You are a specialized AI agent for frontend tasks.
        Your role is: frontend_developer

        Available tools: react-dev-tools, vue-devtools, storybook, cypress
        MCP servers: filesystem, github, web-scraper

        Always prioritize:
        1. Code quality and best practices
        2. Security considerations  
        3. Performance optimization
        4. Clear documentation
        5. Testing and validation
        """

    async def call_mcp_tool(self, server: str, method: str, params: Dict[str, Any] = None):
        """Call an MCP server tool through the gateway"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_gateway}/{server}/{method}",
                    json=params or {}
                )
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def run_task(self, task_description: str, context: dict = None):
        """Execute a task with the agent"""
        try:
            result = await self.agent.run(
                task_description,
                deps={"context": context or {}}
            )
            return result.output
        except Exception as e:
            return f"Error executing task: {e}"

    def start_server(self):
        """Start the agent as a service"""
        app = FastAPI(title="Frontend Agent API")

        @app.post("/task")
        async def execute_task(task: dict):
            result = await self.run_task(
                task.get("description", ""),
                task.get("context", {})
            )
            return {"result": result}

        @app.get("/health")
        def health_check():
            return {"status": "healthy", "agent": "frontend"}

        @app.get("/capabilities")
        def get_capabilities():
            return {
                "tools": ['react-dev-tools', 'vue-devtools', 'storybook', 'cypress'],
                "mcp_servers": ['filesystem', 'github', 'web-scraper'],
                "model": self.model_name,
                "role": "frontend_developer"
            }

        port = int(os.getenv('PORT', 3000))
        uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    agent = FrontendAgent()
    agent.start_server()
