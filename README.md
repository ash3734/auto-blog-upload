# Auto Reply Service

This repository contains the Auto Reply Service project, which is structured into four main components: Frontend, Backend, Infrastructure, and MCP Servers.

## Project Structure

- **Frontend (`auto-reply-service-front/`)**: 
  - Built with modern web technologies.
  - Contains the source code for the user interface.
  - Key files: `package.json`, `tsconfig.json`.

- **Backend (`auto-reply-service-server/`)**: 
  - Developed using a server-side framework.
  - Manages the core logic and data processing.
  - Key files: `requirements.txt`, `docker-compose.yml`, `manage.py`.

- **Infrastructure (`auto-reply-service-infra/`)**: 
  - Configured using Terraform.
  - Deploys AWS resources such as S3, DynamoDB, Lambda, and API Gateway.
  - Key file: `main.tf`.

- **MCP Servers (`mcp-servers/`)**: 
  - Contains additional server components for integration.
  - Subdirectories: `notion-server/`, `cursor-talk-to-figma-mcp/`.

## Getting Started

### Prerequisites

- Node.js and npm for the frontend.
- Python and Docker for the backend.
- Terraform for infrastructure deployment.
- AWS account for deploying cloud resources.

### Installation

1. **Frontend**:
   ```bash
   cd auto-reply-service-front
   npm install
   ```

2. **Backend**:
   ```bash
   cd auto-reply-service-server
   pip install -r requirements.txt
   ```

3. **Infrastructure**:
   ```bash
   cd auto-reply-service-infra
   terraform init
   ```

### Deployment

- **Frontend**: Use npm scripts to build and deploy.
- **Backend**: Use Docker to containerize and deploy.
- **Infrastructure**: Use Terraform to apply the configuration and deploy AWS resources.

## Contributing

Feel free to open issues or submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. 