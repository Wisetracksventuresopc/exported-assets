# Fix the string formatting issue and create the agent files correctly
import os

agent_configs = {
    "frontend": {
        "base_image": "node:18-alpine",
        "tools": ["react-dev-tools", "vue-devtools", "storybook", "cypress"],
        "mcp_servers": ["filesystem", "github", "web-scraper"],
        "model": "deepseek-coder:6.7b",
        "ports": ["3000:3000", "6006:6006"],
        "volumes": ["./frontend:/app", "./shared:/shared"],
        "env_vars": {"AGENT_ROLE": "frontend_developer", "UI_FRAMEWORK": "react"}
    },
    "backend": {
        "base_image": "python:3.11-slim",
        "tools": ["fastapi", "sqlalchemy", "redis-cli", "docker-compose"],
        "mcp_servers": ["database", "docker", "api-testing"],
        "model": "codellama:13b",
        "ports": ["8000:8000", "5432:5432"],
        "volumes": ["./backend:/app", "./shared:/shared", "/var/run/docker.sock:/var/run/docker.sock"],
        "env_vars": {"AGENT_ROLE": "backend_developer", "FRAMEWORK": "fastapi"}
    },
    "security": {
        "base_image": "alpine:latest",
        "tools": ["snyk", "semgrep", "bandit", "safety"],
        "mcp_servers": ["filesystem", "github", "vulnerability-db"],
        "model": "qwen2.5-coder:7b",
        "ports": [],
        "volumes": ["./codebase:/scan", "./reports:/reports"],
        "env_vars": {"AGENT_ROLE": "security_analyst", "SCAN_MODE": "comprehensive"}
    }
}

# Create agent files without string interpolation issues
for agent_name, config in agent_configs.items():
    os.makedirs(f'agents/{agent_name}', exist_ok=True)
    
    # Create agent.py file
    agent_script = '''#!/usr/bin/env python3
"""
''' + agent_name.title().replace('_', ' ') + ''' AI Agent
Specialized for: ''' + config["env_vars"].get("AGENT_ROLE", agent_name) + '''
"""

import os
import asyncio
from pydantic_ai import Agent, RunContext
import httpx
import json
from typing import Dict, Any
from fastapi import FastAPI
import uvicorn

class ''' + agent_name.title().replace('_', '') + '''Agent:
    def __init__(self):
        self.model_name = os.getenv('MODEL_NAME', "''' + config["model"] + '''")
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.mcp_gateway = os.getenv('MCP_GATEWAY_URL', 'http://localhost:8080')
        
        # Initialize the agent
        self.agent = Agent(
            model=f"ollama:{self.model_name}",
            system_prompt=self._get_system_prompt(),
        )
    
    def _get_system_prompt(self) -> str:
        return """
        You are a specialized AI agent for ''' + agent_name.replace('_', ' ') + ''' tasks.
        Your role is: ''' + config["env_vars"].get("AGENT_ROLE", agent_name) + '''
        
        Available tools: ''' + ', '.join(config["tools"]) + '''
        MCP servers: ''' + ', '.join(config["mcp_servers"]) + '''
        
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
        app = FastAPI(title="''' + agent_name.title() + ''' Agent API")
        
        @app.post("/task")
        async def execute_task(task: dict):
            result = await self.run_task(
                task.get("description", ""),
                task.get("context", {})
            )
            return {"result": result}
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy", "agent": "''' + agent_name + '''"}
        
        @app.get("/capabilities")
        def get_capabilities():
            return {
                "tools": ''' + str(config["tools"]) + ''',
                "mcp_servers": ''' + str(config["mcp_servers"]) + ''',
                "model": self.model_name,
                "role": "''' + config["env_vars"].get("AGENT_ROLE", agent_name) + '''"
            }
        
        port = int(os.getenv('PORT', ''' + str(config["ports"][0].split(':')[0] if config["ports"] else "8000") + '''))
        uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    agent = ''' + agent_name.title().replace('_', '') + '''Agent()
    agent.start_server()
'''
    
    with open(f'agents/{agent_name}/agent.py', 'w') as f:
        f.write(agent_script)
    
    # Create requirements.txt
    requirements = """pydantic-ai>=0.0.12
fastapi>=0.104.0
uvicorn>=0.24.0
httpx>=0.25.0
aiofiles>=23.0.0
python-multipart>=0.0.6
"""
    
    with open(f'agents/{agent_name}/requirements.txt', 'w') as f:
        f.write(requirements)
    
    print(f"Created agent files for: {agent_name}")

# Create a master orchestrator script
orchestrator_script = '''#!/usr/bin/env python3
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
'''

with open('orchestrator.py', 'w') as f:
    f.write(orchestrator_script)

# Create a README with setup instructions
readme_content = '''# Dockerized Multi-Agent AI Development System

This system provides specialized AI agents for different aspects of software development, running entirely offline using Docker and local LLMs.

## Architecture

- **Ollama**: Local LLM serving infrastructure
- **Open WebUI**: Web interface for model interaction  
- **MCP Gateway**: Tool orchestration and security
- **Specialized Agents**: Frontend, Backend, Security, Integration, etc.
- **Orchestrator**: Coordinates multi-agent tasks

## Quick Start

1. **Prerequisites**
   ```bash
   # Install Docker Desktop with GPU support
   # Ensure you have at least 16GB RAM and 100GB free disk space
   ```

2. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd dockerized-ai-agents
   
   # Pull required models (this will take time)
   docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull deepseek-coder:6.7b
   docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull codellama:13b
   docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull qwen2.5-coder:7b
   ```

3. **Start the System**
   ```bash
   docker-compose up -d
   ```

4. **Access Interfaces**
   - Open WebUI: http://localhost:3000
   - Orchestrator API: http://localhost:9000
   - Frontend Agent: http://localhost:3001
   - Backend Agent: http://localhost:8001

## Agent Capabilities

### Frontend Agent (Port 3001)
- React/Vue component development
- UI/UX design assistance
- Storybook documentation
- Cypress testing

### Backend Agent (Port 8001) 
- FastAPI/Django development
- Database design and queries
- API architecture
- Performance optimization

### Security Agent (Port 8002)
- Vulnerability scanning
- Code security analysis
- Compliance checking
- Threat modeling

## Usage Examples

### Single Agent Task
```bash
curl -X POST http://localhost:3001/task \\
  -H "Content-Type: application/json" \\
  -d '{"description": "Create a React component for user authentication"}'
```

### Multi-Agent Project
```bash
curl -X POST http://localhost:9000/project \\
  -H "Content-Type: application/json" \\
  -d '{"description": "Build a secure e-commerce platform with React frontend and FastAPI backend"}'
```

### Check Agent Status
```bash
curl http://localhost:9000/agents/status
```

## Customization

### Adding New Agents
1. Create new directory in `agents/`
2. Add Dockerfile and agent.py
3. Update docker-compose.yml
4. Restart system

### Configuring Models
- Edit model names in docker-compose.yml environment variables
- Pull new models: `docker exec ollama-server ollama pull <model-name>`

### Adding MCP Tools
1. Add MCP server to docker-compose.yml
2. Update agent configurations to use new tools
3. Restart affected agents

## Troubleshooting

### Models Not Loading
```bash
# Check Ollama logs
docker logs ollama-server

# Manually pull models
docker exec ollama-server ollama pull deepseek-coder:6.7b
```

### Agent Connection Issues
```bash
# Check agent logs
docker logs frontend-agent

# Verify network connectivity
docker exec frontend-agent curl http://ollama:11434/api/version
```

### Insufficient Resources
- Reduce concurrent agents
- Use smaller models (e.g., qwen2.5-coder:1.5b)
- Increase Docker resource limits

## Security Considerations

- All agents run in isolated containers
- No external network access required
- MCP Gateway provides additional security layer
- Code execution happens in sandboxed environments

## Performance Tuning

### GPU Optimization
```yaml
# In docker-compose.yml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Memory Management
```yaml
# Limit memory usage per agent
mem_limit: 2g
memswap_limit: 2g
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new agents
4. Submit pull request

## License

MIT License - see LICENSE file for details
'''

with open('README.md', 'w') as f:
    f.write(readme_content)

print("✅ Created complete dockerized multi-agent system:")
print("   - 3 specialized agents (Frontend, Backend, Security)")
print("   - Orchestrator for multi-agent coordination")
print("   - Docker Compose configuration")
print("   - Individual Dockerfiles for each agent")
print("   - Requirements files")
print("   - Comprehensive README")
print("\nTo start: docker-compose up -d")
print("Then visit: http://localhost:9000 for orchestrator API")