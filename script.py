# Create a comprehensive CSV with all the GitHub repos and MCP servers for dockerized AI agents
import csv

# Comprehensive data for dockerized AI coding agents
agent_repos = [
    # Core AI Agent Frameworks
    {
        "Category": "Multi-Agent Framework",
        "Name": "Block Goose",
        "Repository": "https://github.com/block/goose",
        "Description": "Open source, extensible AI agent that automates engineering tasks",
        "Docker Support": "Yes - Built-in",
        "MCP Support": "Yes - Native",
        "Local LLM": "Yes - Any model",
        "Specialization": "General development automation",
        "Stars": "20k+",
        "Language": "Rust/TypeScript",
        "Status": "Active"
    },
    {
        "Category": "Coding Agent",
        "Name": "Aider",
        "Repository": "https://github.com/Aider-AI/aider", 
        "Description": "AI pair programming in terminal with git integration",
        "Docker Support": "Yes - Official images",
        "MCP Support": "Partial - Tools integration",
        "Local LLM": "Yes - Ollama, local models",
        "Specialization": "Code editing, git workflows",
        "Stars": "30k+",
        "Language": "Python",
        "Status": "Active"
    },
    {
        "Category": "SWE Agent",
        "Name": "SWE-Agent",
        "Repository": "https://github.com/SWE-agent/SWE-agent",
        "Description": "Agent for automated software engineering tasks",
        "Docker Support": "Yes - Container-based",
        "MCP Support": "Via SWE-ReX",
        "Local LLM": "Yes - Multiple providers",
        "Specialization": "Bug fixing, issue resolution",
        "Stars": "15k+",
        "Language": "Python",
        "Status": "Active"
    },
    {
        "Category": "Multi-Agent Platform",
        "Name": "CrewAI",
        "Repository": "https://github.com/joaomdmoura/crewai",
        "Description": "Framework for orchestrating role-playing autonomous AI agents",
        "Docker Support": "Yes - Docker Compose templates",
        "MCP Support": "Third-party integrations",
        "Local LLM": "Yes - Ollama support",
        "Specialization": "Multi-agent collaboration",
        "Stars": "25k+",
        "Language": "Python",
        "Status": "Active"
    },
    {
        "Category": "Agent Framework",
        "Name": "PydanticAI",
        "Repository": "https://github.com/pydantic/pydantic-ai",
        "Description": "Type-safe agent framework with tool integration",
        "Docker Support": "Yes - Container deployments",
        "MCP Support": "Yes - Built-in MCP server support",
        "Local LLM": "Yes - Multiple providers",
        "Specialization": "Type-safe agent development",
        "Stars": "10k+",
        "Language": "Python",
        "Status": "Active"
    },
    {
        "Category": "VS Code Extension",
        "Name": "Kilo Code",
        "Repository": "https://github.com/Kilo-Org/kilocode",
        "Description": "Open source AI coding assistant with MCP marketplace",
        "Docker Support": "Via VS Code dev containers",
        "MCP Support": "Yes - Marketplace integration",
        "Local LLM": "Yes - Multiple providers",
        "Specialization": "IDE integration, code generation",
        "Stars": "5k+",
        "Language": "TypeScript",
        "Status": "Active"
    },
    {
        "Category": "Terminal Agent",
        "Name": "OpenCode (SST)",
        "Repository": "https://github.com/sst/opencode",
        "Description": "AI coding agent built for the terminal",
        "Docker Support": "Yes - Containerized deployment",
        "MCP Support": "Planning",
        "Local LLM": "Yes - Provider agnostic",
        "Specialization": "Terminal-based development",
        "Stars": "3k+",
        "Language": "TypeScript",
        "Status": "Active"
    },
    {
        "Category": "Self-Improving Agent",
        "Name": "Self-Improving Coding Agent",
        "Repository": "https://github.com/MaximeRobeyns/self_improving_coding_agent",
        "Description": "Agent that works on its own codebase",
        "Docker Support": "Yes - Required for safety",
        "MCP Support": "Custom implementation",
        "Local LLM": "Yes",
        "Specialization": "Self-modification, meta-programming",
        "Stars": "1k+",
        "Language": "Python",
        "Status": "Active"
    }
]

# MCP Servers specifically for development
mcp_servers = [
    {
        "Category": "MCP Server",
        "Name": "Docker MCP Toolkit",
        "Repository": "Built into Docker Desktop",
        "Description": "200+ curated MCP servers with one-click deployment",
        "Docker Support": "Yes - Native",
        "MCP Support": "Yes - Core functionality",
        "Local LLM": "Client agnostic",
        "Specialization": "Tool orchestration, security",
        "Stars": "N/A",
        "Language": "Various",
        "Status": "Active"
    },
    {
        "Category": "MCP Server",
        "Name": "GitHub MCP",
        "Repository": "https://github.com/modelcontextprotocol/servers",
        "Description": "GitHub integration for AI agents",
        "Docker Support": "Yes - Containerized",
        "MCP Support": "Yes - Reference implementation",
        "Local LLM": "Client agnostic",
        "Specialization": "Repository management, issues, PRs",
        "Stars": "2k+",
        "Language": "Python/TypeScript",
        "Status": "Active"
    },
    {
        "Category": "MCP Server",
        "Name": "File System MCP",
        "Repository": "https://github.com/modelcontextprotocol/servers",
        "Description": "File operations for AI agents",
        "Docker Support": "Yes",
        "MCP Support": "Yes - Core server",
        "Local LLM": "Client agnostic",
        "Specialization": "File management, search, editing",
        "Stars": "2k+",
        "Language": "Python",
        "Status": "Active"
    },
    {
        "Category": "MCP Server",
        "Name": "Database MCP",
        "Repository": "https://github.com/modelcontextprotocol/servers",
        "Description": "Database access for AI agents",
        "Docker Support": "Yes",
        "MCP Support": "Yes",
        "Local LLM": "Client agnostic",
        "Specialization": "SQL operations, schema management",
        "Stars": "2k+",
        "Language": "Python",
        "Status": "Active"
    }
]

# Local LLM Infrastructure
llm_infrastructure = [
    {
        "Category": "LLM Infrastructure",
        "Name": "Ollama",
        "Repository": "https://github.com/ollama/ollama",
        "Description": "Run large language models locally",
        "Docker Support": "Yes - Official images",
        "MCP Support": "Via clients",
        "Local LLM": "Yes - Core purpose",
        "Specialization": "Local model serving",
        "Stars": "90k+",
        "Language": "Go",
        "Status": "Active"
    },
    {
        "Category": "LLM Interface",
        "Name": "Open WebUI",
        "Repository": "https://github.com/open-webui/open-webui",
        "Description": "User-friendly AI interface for local models",
        "Docker Support": "Yes - Primary deployment method",
        "MCP Support": "Yes - Recent addition",
        "Local LLM": "Yes - Ollama integration",
        "Specialization": "Web UI, offline operation",
        "Stars": "50k+",
        "Language": "Python/JavaScript",
        "Status": "Active"
    },
    {
        "Category": "Development Stack",
        "Name": "Docker Model Runner",
        "Repository": "Built into Docker Desktop",
        "Description": "Run LLMs locally in Docker containers",
        "Docker Support": "Yes - Native feature",
        "MCP Support": "Yes - Integration ready",
        "Local LLM": "Yes - Core purpose", 
        "Specialization": "Containerized model serving",
        "Stars": "N/A",
        "Language": "Various",
        "Status": "Active"
    }
]

# Combine all data
all_projects = agent_repos + mcp_servers + llm_infrastructure

# Write to CSV
filename = 'dockerized_ai_agents_comprehensive.csv'
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    if all_projects:
        fieldnames = all_projects[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for project in all_projects:
            writer.writerow(project)

print(f"Created {filename} with {len(all_projects)} entries")
print("\nCategories breakdown:")
categories = {}
for project in all_projects:
    cat = project['Category']
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in categories.items():
    print(f"  {cat}: {count}")

print(f"\nTop Docker-native projects for offline AI agents:")
for project in all_projects:
    if project['Docker Support'] == 'Yes - Built-in' or project['Docker Support'] == 'Yes - Official images':
        print(f"  • {project['Name']}: {project['Description']}")