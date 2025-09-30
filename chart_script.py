# Create an improved architecture diagram with better spacing and readability
diagram_code = """
flowchart TD
    %% Orchestration Layer
    ORCH[Docker Orchestration]
    
    %% Agent Containers - arranged in two rows for better spacing
    subgraph AGENTS[AI Agent Containers]
        direction TB
        subgraph ROW1[Frontend & Backend]
            FE[Frontend Agent<br/>React/Vue/UI]
            BE[Backend Agent<br/>API/DB/Server]
            SEC[Security Agent<br/>Scanner/Analysis]
        end
        subgraph ROW2[Integration & Review]
            INT[Integration<br/>CI/CD/Testing]
            TECH[Tech Stack<br/>Architecture]
            CODE[Code Review<br/>Quality/Analysis]
            PROD[Product Req<br/>Stories/Mockups]
        end
    end
    
    %% MCP Servers - simplified layout
    subgraph MCP[MCP Tool Servers]
        direction LR
        GH[GitHub MCP]
        DOC[Docker MCP]
        FS[FileSystem MCP]
        DB_MCP[Database MCP]
        API_MCP[API Test MCP]
        SCAN_MCP[Security MCP]
    end
    
    %% Infrastructure - horizontal layout
    subgraph INFRA[Local LLM Infrastructure]
        direction LR
        OLLAMA[Ollama<br/>Multi Models]
        WEBUI[Open WebUI<br/>Chat Interface]
        GATEWAY[MCP Gateway<br/>Tool Security]
    end
    
    %% Development Tools
    subgraph DEV[Development Workflow]
        direction LR
        AIDER[Aider<br/>AI Programming]
        SWE[SWE-Agent<br/>Issue Resolution]
    end
    
    %% Security & Storage
    subgraph STORAGE[Shared Resources]
        direction LR
        NETWORK[Docker Network]
        VOLUMES[Shared Volumes]
    end
    
    %% Main connections - simplified
    ORCH --> AGENTS
    ORCH --> MCP
    ORCH --> INFRA
    
    %% Agent connections - reduced crossings
    ROW1 --> MCP
    ROW2 --> MCP
    
    %% Infrastructure connections
    MCP --> GATEWAY
    GATEWAY --> OLLAMA
    GATEWAY --> WEBUI
    
    %% Development workflow
    AGENTS --> DEV
    DEV --> STORAGE
    
    %% Shared resources
    AGENTS --> STORAGE
    MCP --> NETWORK
    INFRA --> NETWORK
    
    %% Styling with better contrast
    classDef agentStyle fill:#B3E5EC,stroke:#1FB8CD,stroke-width:3px,color:#000
    classDef mcpStyle fill:#FFCDD2,stroke:#DB4545,stroke-width:3px,color:#000
    classDef infraStyle fill:#A5D6A7,stroke:#2E8B57,stroke-width:3px,color:#000
    classDef devStyle fill:#9FA8B0,stroke:#5D878F,stroke-width:3px,color:#000
    classDef storageStyle fill:#FFEB8A,stroke:#D2BA4C,stroke-width:3px,color:#000
    classDef orchStyle fill:#1FB8CD,stroke:#13343B,stroke-width:4px,color:#fff
    
    class ORCH orchStyle
    class FE,BE,SEC,INT,TECH,CODE,PROD agentStyle
    class GH,DOC,FS,DB_MCP,API_MCP,SCAN_MCP mcpStyle
    class OLLAMA,WEBUI,GATEWAY infraStyle
    class AIDER,SWE devStyle
    class NETWORK,VOLUMES storageStyle
"""

# Create the improved mermaid diagram with larger dimensions
png_path, svg_path = create_mermaid_diagram(
    diagram_code, 
    'architecture_diagram_v2.png', 
    'architecture_diagram_v2.svg',
    width=1600,
    height=1200
)

print(f"Improved architecture diagram saved to: {png_path} and {svg_path}")