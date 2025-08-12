# AI Virtual Agent - Development Setup

This document describes how to set up the AI Virtual Agent for local development using containerized services.

## Quick Start (New - Single Command!)

### Prerequisites

Ensure you have the following running on your system:

- **Podman** with podman-compose support
- **Ollama** service running on `localhost:11434`
- **Required Ollama model**: `llama3.2:3b-instruct-fp16` loaded and ready

### Start Development Environment

```bash
# Option 1: Using Makefile (recommended)
make dev-compose-up

# Option 2: Using the script directly
./scripts/dev/start-dev.sh
```

**Note**: First startup takes longer due to image downloads.

That's it! All services will be running:

- **Frontend**: http://localhost:5173 (with hot reload)
- **Backend**: http://localhost:8000 (with hot reload)
- **Database**: postgresql://admin:password@localhost:5432/ai_virtual_agent
- **LlamaStack**: http://localhost:8321

### Stop Development Environment

```bash
# Option 1: Using Makefile (recommended)
make dev-compose-down

# Option 2: Using the script directly
./scripts/dev/stop-dev.sh
```

## Service Details

### Services Included

1. **PostgreSQL Database** - Persistent storage for application data
2. **LlamaStack** - AI model server with Ollama integration
3. **Backend** - FastAPI server with hot reload
4. **Frontend** - Vite dev server with hot reload

### Environment Configuration

The development setup uses `.env` for configuration. Copy from the template:

```bash
cp .env.example .env
```

Default configuration:
- **Database**: PostgreSQL on port 5432
- **Backend**: FastAPI on port 8000 with `LOCAL_DEV_ENV_MODE=true`
- **Frontend**: Vite dev server on port 5173
- **LlamaStack**: AI server on port 8321

### Development Features

- ✅ **Hot Reload**: Both backend and frontend automatically reload on code changes
- ✅ **Network Isolation**: All services run in a dedicated Docker network
- ✅ **Health Checks**: Services wait for dependencies to be ready
- ✅ **Volume Mounts**: Source code is mounted for live editing
- ✅ **Local Dev Mode**: Authentication bypass enabled for development
- ✅ **Persistent Data**: Database data persists between restarts

## Troubleshooting

### Common Issues

1. **Ollama not accessible**
   - Ensure Ollama is running on `localhost:11434`
   - Verify the model `llama3.2:3b-instruct-fp16` is loaded

2. **Port conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :5432 -i :8000 -i :5173 -i :8321
   
   # Customize ports in .env
   vim .env
   ```

3. **Permission issues**
   ```bash
   # Ensure scripts are executable
   chmod +x scripts/dev/*.sh
   ```

4. **View service logs**
   ```bash
   # All services (using Makefile)
   make dev-compose-logs
   
   # All services (direct command)
   podman compose -f compose.dev.yaml logs -f
   
   # Specific service
   podman compose -f compose.dev.yaml logs -f backend
   ```

### Useful Commands

#### Using Makefile (Recommended)

```bash
# View service logs
make dev-compose-logs

# Check service status  
make dev-compose-status

# Restart all services
make dev-compose-restart

# Rebuild and restart services
make dev-compose-build

# See all available development commands
make help
```

#### Using podman compose directly

```bash
# Restart a specific service
podman compose -f compose.dev.yaml restart backend

# Rebuild a service
podman compose -f compose.dev.yaml up --build backend

# Access a service shell
podman exec -it ai-va-backend-dev bash

# Remove all data (fresh start)
podman compose -f compose.dev.yaml down --volumes
```

## Migration from Manual Setup

### Before (4 Terminals Required)
```bash
# Terminal 1: Database
podman compose --file compose.yaml up --detach

# Terminal 2: LlamaStack  
cd scripts/dev/local_llamastack_server/
bash activate_llama_server.sh

# Terminal 3: Backend
source venv/bin/activate && export LOCAL_DEV_ENV_MODE=true && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Frontend
cd frontend && npm install && npm run dev
```

### After (1 Command)
```bash
# Using Makefile (recommended)
make dev-compose-up

# Or using script directly
./scripts/dev/start-dev.sh
```

## Development Container Commands Reference

The following Makefile targets are available for containerized development:

- `make dev-compose-up` - Start development services (uses .env and compose.dev.yaml)
- `make dev-compose-down` - Stop development services
- `make dev-compose-restart` - Restart development services
- `make dev-compose-logs` - View logs from development services
- `make dev-compose-build` - Rebuild and start development services
- `make dev-compose-status` - Show status of development services

For all available make targets, run `make help`.

## Next Steps

- Customize `.env` for your specific needs
- Add additional services to `compose.dev.yaml` as needed
- Use the existing `compose.yaml` for production-like testing
- Run `make help` to see all available project commands