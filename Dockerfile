FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install agent-specific tools
RUN npm install -g react-dev-tools
RUN npm install -g vue-devtools
RUN npm install -g storybook
RUN npm install -g cypress

# Copy agent code
COPY . .

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set up MCP client
RUN pip install mcp-client pydantic-ai

# Create agent script
COPY agent.py .

EXPOSE 3000

CMD ["python", "agent.py"]
