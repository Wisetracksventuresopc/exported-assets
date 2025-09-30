#!/usr/bin/env python3
"""
Multi-Agent Orchestrator
Coordinates tasks between specialized AI agents
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any
from fastapi import FastAPI
import uvicorn

class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "frontend": "http://frontend-agent:3000",
            "backend": "http://backend-agent:8000", 
            "security": "http://security-agent:8000"
        }

    async def get_agent_status(self) -> Dict[str, str]:
        """Check health status of all agents"""
        status = {}
        async with httpx.AsyncClient() as client:
            for agent_name, url in self.agents.items():
                try:
                    response = await client.get(f"{url}/health", timeout=5.0)
                    status[agent_name] = response.json().get("status", "unknown")
                except Exception as e:
                    status[agent_name] = f"error: {str(e)}"
        return status

    async def route_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route a task to the appropriate agent based on content"""
        task_lower = task.lower()

        # Simple routing logic - can be enhanced with LLM-based routing
        if any(keyword in task_lower for keyword in ["ui", "frontend", "react", "vue", "component"]):
            agent_url = self.agents["frontend"]
        elif any(keyword in task_lower for keyword in ["api", "backend", "database", "server"]):
            agent_url = self.agents["backend"]
        elif any(keyword in task_lower for keyword in ["security", "vulnerability", "scan", "audit"]):
            agent_url = self.agents["security"]
        else:
            # Default to backend for general tasks
            agent_url = self.agents["backend"]

        # Execute task on selected agent
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{agent_url}/task",
                    json={"description": task, "context": context or {}},
                    timeout=30.0
                )
                return response.json()
            except Exception as e:
                return {"error": f"Failed to execute task: {str(e)}"}

    async def coordinate_multi_agent_task(self, project_description: str) -> Dict[str, Any]:
        """Coordinate a complex task across multiple agents"""

        # Break down the project into agent-specific tasks
        tasks = {
            "frontend": f"Create frontend components for: {project_description}",
            "backend": f"Design backend architecture for: {project_description}", 
            "security": f"Analyze security requirements for: {project_description}"
        }

        results = {}
        async with httpx.AsyncClient() as client:
            for agent_name, task in tasks.items():
                agent_url = self.agents[agent_name]
                try:
                    response = await client.post(
                        f"{agent_url}/task",
                        json={"description": task, "context": {"project": project_description}},
                        timeout=60.0
                    )
                    results[agent_name] = response.json()
                except Exception as e:
                    results[agent_name] = {"error": str(e)}

        return results

def create_app():
    orchestrator = AgentOrchestrator()
    app = FastAPI(title="AI Agent Orchestrator")

    @app.get("/")
    async def root():
        return {"message": "AI Agent Orchestrator", "agents": list(orchestrator.agents.keys())}

    @app.get("/agents/status")
    async def agent_status():
        return await orchestrator.get_agent_status()

    @app.post("/task")
    async def execute_task(request: Dict[str, Any]):
        task = request.get("task", "")
        context = request.get("context", {})
        return await orchestrator.route_task(task, context)

    @app.post("/project")
    async def coordinate_project(request: Dict[str, Any]):
        description = request.get("description", "")
        return await orchestrator.coordinate_multi_agent_task(description)

    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=9000)
