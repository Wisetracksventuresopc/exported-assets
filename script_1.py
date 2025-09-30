# Create detailed setup instructions for each specialized agent
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
    },
    "integration": {
        "base_image": "docker:24-dind",
        "tools": ["kubectl", "helm", "terraform", "ansible"],
        "mcp_servers": ["docker", "kubernetes", "cloud-providers"],
        "model": "llama3.1:8b",
        "ports": ["2375:2375"],
        "volumes": ["/var/run/docker.sock:/var/run/docker.sock", "./deployment:/deployment"],
        "env_vars": {"AGENT_ROLE": "devops_engineer", "DOCKER_HOST": "tcp://localhost:2375"}
    },
    "tech_stack": {
        "base_image": "ubuntu:22.04",
        "tools": ["npm", "pip", "cargo", "go"],
        "mcp_servers": ["package-managers", "github", "tech-radar"],
        "model": "mixtral:8x7b",
        "ports": [],
        "volumes": ["./analysis:/analysis", "./recommendations:/recommendations"],
        "env_vars": {"AGENT_ROLE": "tech_advisor", "ANALYSIS_DEPTH": "detailed"}
    },
    "code_review": {
        "base_image": "python:3.11-slim",
        "tools": ["pylint", "black", "sonarqube", "git"],
        "mcp_servers": ["github", "filesystem", "code-analysis"],
        "model": "deepseek-coder:33b",
        "ports": [],
        "volumes": ["./codebase:/code", "./reviews:/reviews"],
        "env_vars": {"AGENT_ROLE": "code_reviewer", "REVIEW_STANDARDS": "strict"}
    },
    "product_requirements": {
        "base_image": "node:18-alpine",
        "tools": ["mermaid-cli", "figma-cli", "notion-api", "jira-cli"],
        "mcp_servers": ["project-management", "design-tools", "documentation"],
        "model": "gpt-4o-mini",
        "ports": [],
        "volumes": ["./requirements:/requirements", "./mockups:/mockups"],
        "env_vars": {"AGENT_ROLE": "product_manager", "OUTPUT_FORMAT": "user_stories"}
    }
}

# Generate Docker Compose file
docker_compose = """version: '3.8'

services:
  # Core Infrastructure
  ollama:
    image: ollama/ollama:latest
    container_name: ollama-server
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
      - ./models:/models
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_HOST=0.0.0.0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-secret}
      - ENABLE_RAG_LOCAL_WEB_FETCH=true
    volumes:
      - open_webui_data:/app/backend/data

  # MCP Gateway
  mcp-gateway:
    image: ghcr.io/docker/mcp-gateway:latest
    container_name: mcp-gateway
    ports:
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./mcp-config:/config
    environment:
      - MCP_CONFIG_PATH=/config

"""

# Add each specialized agent
for agent_name, config in agent_configs.items():
    agent_service = f"""
  {agent_name}-agent:
    build:
      context: ./agents/{agent_name}
      dockerfile: Dockerfile
    container_name: {agent_name}-agent
    depends_on:
      - ollama
      - mcp-gateway"""
    
    if config["ports"]:
        agent_service += f"\n    ports:\n"
        for port in config["ports"]:
            agent_service += f"      - \"{port}\"\n"
    
    agent_service += f"""    volumes:"""
    for volume in config["volumes"]:
        agent_service += f"\n      - {volume}"
    
    agent_service += f"""
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - MCP_GATEWAY_URL=http://mcp-gateway:8080
      - MODEL_NAME={config["model"]}"""
    
    for env_var, value in config["env_vars"].items():
        agent_service += f"\n      - {env_var}={value}"
    
    agent_service += f"""
    networks:
      - agent-network
    restart: unless-stopped
"""
    
    docker_compose += agent_service

# Add networks and volumes
docker_compose += """
networks:
  agent-network:
    driver: bridge

volumes:
  ollama_data:
  open_webui_data:
  shared_workspace:
"""

# Save the Docker Compose file
with open('docker-compose.yml', 'w') as f:
    f.write(docker_compose)

print("Generated docker-compose.yml with all specialized agents")

# Create individual Dockerfiles for each agent
import os

for agent_name, config in agent_configs.items():
    os.makedirs(f'agents/{agent_name}', exist_ok=True)
    
    dockerfile_content = f"""FROM {config["base_image"]}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    wget \\
    jq \\
    && rm -rf /var/lib/apt/lists/*

# Install agent-specific tools
"""
    
    for tool in config["tools"]:
        if tool.startswith("npm") or agent_name == "frontend":
            dockerfile_content += f"RUN npm install -g {tool}\n"
        elif tool.startswith("pip") or agent_name in ["backend", "security", "code_review"]:
            dockerfile_content += f"RUN pip install {tool}\n"
        else:
            dockerfile_content += f"RUN curl -sSL https://install.{tool}.com | sh\n"
    
    dockerfile_content += f"""
# Copy agent code
COPY . .

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set up MCP client
RUN pip install mcp-client pydantic-ai

# Create agent script
COPY agent.py .

EXPOSE {config["ports"][0].split(':')[0] if config["ports"] else "8000"}

CMD ["python", "agent.py"]
"""
    
    with open(f'agents/{agent_name}/Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    # Create basic agent script
    agent_script = f'''#!/usr/bin/env python3
"""
{agent_name.title().replace('_', ' ')} AI Agent
Specialized for: {config["env_vars"].get("AGENT_ROLE", agent_name)}
"""

import os
import asyncio
from pydantic_ai import Agent, RunContext
from mcp import MCPClient
import ollama

class {agent_name.title().replace('_', '')}Agent:
    def __init__(self):
        self.model_name = os.getenv('MODEL_NAME', '{config["model"]}')
        self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.mcp_gateway = os.getenv('MCP_GATEWAY_URL', 'http://localhost:8080')
        
        # Initialize the agent
        self.agent = Agent(
            model=f"ollama:{self.model_name}",
            system_prompt=self._get_system_prompt(),
        )
        
        # Set up MCP servers
        self._setup_mcp_servers()
    
    def _get_system_prompt(self) -> str:
        return f"""
        You are a specialized AI agent for {agent_name.replace('_', ' ')} tasks.
        Your role is: {config["env_vars"].get("AGENT_ROLE", agent_name)}
        
        Available tools: {', '.join(config["tools"])}
        MCP servers: {', '.join(config["mcp_servers"])}
        
        Always prioritize:
        1. Code quality and best practices
        2. Security considerations  
        3. Performance optimization
        4. Clear documentation
        5. Testing and validation
        """
    
    def _setup_mcp_servers(self):
        """Initialize MCP server connections"""
        self.mcp_clients = {{}}
        for server in {config["mcp_servers"]}:
            try:
                # Connect to MCP server through gateway
                client = MCPClient(f"{{self.mcp_gateway}}/{{server}}")
                self.mcp_clients[server] = client
                print(f"Connected to MCP server: {{server}}")
            except Exception as e:
                print(f"Failed to connect to {{server}}: {{e}}")
    
    async def run_task(self, task_description: str, context: dict = None):
        """Execute a task with the agent"""
        try:
            result = await self.agent.run(
                task_description,
                deps={{"context": context, "mcp_clients": self.mcp_clients}}
            )
            return result.output
        except Exception as e:
            return f"Error executing task: {{e}}"
    
    def start_server(self):
        """Start the agent as a service"""
        import uvicorn
        from fastapi import FastAPI
        
        app = FastAPI(title=f"{agent_name.title()} Agent API")
        
        @app.post("/task")
        async def execute_task(task: dict):
            result = await self.run_task(
                task.get("description", ""),
                task.get("context", {{}})
            )
            return {{"result": result}}
        
        @app.get("/health")
        def health_check():
            return {{"status": "healthy", "agent": "{agent_name}"}}
        
        port = int(os.getenv('PORT', {config["ports"][0].split(':')[0] if config["ports"] else "8000"}))
        uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    agent = {agent_name.title().replace('_', '')}Agent()
    agent.start_server()
'''
    
    with open(f'agents/{agent_name}/agent.py', 'w') as f:
        f.write(agent_script)
    
    # Create requirements.txt
    requirements = f"""pydantic-ai>=0.0.12
fastapi>=0.104.0
uvicorn>=0.24.0
ollama>=0.3.0
mcp-client>=0.1.0
aiofiles>=23.0.0
httpx>=0.25.0
"""
    
    with open(f'agents/{agent_name}/requirements.txt', 'w') as f:
        f.write(requirements)

print(f"Created {len(agent_configs)} specialized agent directories with:")
print("  - Dockerfile")
print("  - agent.py (FastAPI service)")
print("  - requirements.txt")
print("\nNext steps:")
print("1. Run: docker-compose up -d")
print("2. Wait for models to download")
print("3. Access Open WebUI at http://localhost:3000")
print("4. Each agent runs as a microservice with REST API")