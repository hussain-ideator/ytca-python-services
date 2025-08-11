# Environment Configuration Guide

## Overview

The YouTube Channel Strategy Analyzer now uses environment-based configuration to avoid hardcoding database paths and other settings in the code. This makes the application more flexible and secure.

## Configuration Files

### 1. `config.env` (Main Configuration)
This is the primary configuration file that contains all environment variables:

```env
# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_PATH=sqlite
DATABASE_FILE=yt_insights.db
DATABASE_URL=sqlite:///sqlite/yt_insights.db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_LOG_LEVEL=info

# Environment
ENVIRONMENT=development
DEBUG=false
```

### 2. `config.example` (Template)
A template file showing all available configuration options. Copy this to `config.env` and modify as needed.

## Configuration Options

### Database Settings
- `DATABASE_TYPE`: Type of database (currently supports `sqlite`)
- `DATABASE_PATH`: Directory where the database file will be stored
- `DATABASE_FILE`: Name of the database file
- `DATABASE_URL`: Full database URL (optional, auto-generated if not provided)

### Ollama Settings
- `OLLAMA_BASE_URL`: Base URL for Ollama service
- `OLLAMA_MODEL`: Model name to use for LLM operations

### API Settings
- `API_HOST`: Host address for the API server
- `API_PORT`: Port number for the API server
- `API_WORKERS`: Number of worker processes
- `API_LOG_LEVEL`: Logging level (`debug`, `info`, `warning`, `error`)

### Environment Settings
- `ENVIRONMENT`: Application environment (`development`, `production`, `testing`)
- `DEBUG`: Enable debug mode (`true`/`false`)

## Usage

### 1. Setup Configuration
Copy the example configuration and modify as needed:
```bash
cp config.example config.env
# Edit config.env with your settings
```

### 2. Dependencies
Install required dependencies:
```bash
pip install python-dotenv
```

### 3. Verification
Test your configuration:
```bash
python test_env_config.py
```

### 4. Health Check
Check the running application configuration:
```bash
python test_health.py
```

## Configuration Loading Order

The application loads configuration in this order:
1. First tries to load from `config.env`
2. Falls back to `.env` if `config.env` doesn't exist
3. Uses default values if environment variables are not set

## Security Notes

- Never commit `.env` files to version control
- Use `config.env` for local development
- Set environment variables directly in production
- The `config.example` file can be safely committed as it contains no secrets

## API Configuration Endpoint

The health endpoint now includes configuration information:
```bash
GET /health
```

Response includes a `configuration` section with current settings (sensitive data excluded).

## Changing Database Location

To use a different database location, update these variables in `config.env`:
```env
DATABASE_PATH=/path/to/your/database/directory
DATABASE_FILE=your_database.db
```

Or set the full URL directly:
```env
DATABASE_URL=sqlite:///path/to/your/database.db
```

## Production Deployment

For production, set environment variables directly instead of using config files:
```bash
export DATABASE_PATH=/var/lib/youtube-analyzer
export DATABASE_FILE=production.db
export ENVIRONMENT=production
export DEBUG=false
```

## Troubleshooting

1. **Configuration not loading**: Ensure `config.env` exists and is in the correct format
2. **Database path issues**: Check that the directory has proper permissions
3. **Port conflicts**: Change `API_PORT` in configuration if 8000 is already in use
4. **Ollama connection issues**: Verify `OLLAMA_BASE_URL` and ensure Ollama is running

## Migration from Hardcoded Configuration

If upgrading from a version with hardcoded configuration:
1. Create `config.env` with your current settings
2. The application will automatically use the new configuration system
3. Previous database files will continue to work in their current locations

