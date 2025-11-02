# Dockerized Multi-Agent AI Development System

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
curl -X POST http://localhost:3001/task \
  -H "Content-Type: application/json" \
  -d '{"description": "Create a React component for user authentication"}'
```

### Multi-Agent Project
```bash
curl -X POST http://localhost:9000/project \
  -H "Content-Type: application/json" \
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

## Automated Git Sync

Use `auto_git_committer.py` to stage, commit, and push changes across every local repository (including Docker project directories that are not yet versioned). The tool prepares commits and ships them to the `mvallarautomations` GitHub account.

```bash
# Provide a GitHub token with repo scope
export MVALLARAUTOMATIONS_TOKEN=ghp_...

# Dry run to inspect actions
python auto_git_committer.py --dry-run

# Execute for real and create missing GitHub repos
python auto_git_committer.py --create-missing
```

Optional flags:
- `--roots` to scan additional base directories
- `--commit-message` for a custom message
- `--no-init-docker` to skip auto-initialising Docker directories
- `--token-env` if you store the token under a different variable

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
