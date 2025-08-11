"""
Configuration module for YouTube Channel Strategy Analyzer
Handles environment variable loading and provides configuration settings
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # Load environment variables from config.env file
        env_file = Path("config.env")
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # Fallback to .env file if config.env doesn't exist
            load_dotenv()
    
    # Database Configuration
    @property
    def database_type(self) -> str:
        return os.getenv("DATABASE_TYPE", "sqlite")
    
    @property
    def database_path(self) -> Path:
        path_str = os.getenv("DATABASE_PATH", "sqlite")
        return Path(path_str)
    
    @property
    def database_file(self) -> str:
        return os.getenv("DATABASE_FILE", "yt_insights.db")
    
    @property
    def database_url(self) -> str:
        """Get the full database URL"""
        custom_url = os.getenv("DATABASE_URL")
        if custom_url:
            return custom_url
        
        # Construct URL from components
        db_path = self.database_path / self.database_file
        return f"sqlite:///{db_path}"
    
    @property
    def database_full_path(self) -> Path:
        """Get the full path to the database file (only for local databases)"""
        if self.is_cloud_database:
            # For cloud databases, return a placeholder path
            return Path("cloud_database")
        return self.database_path / self.database_file
    
    @property
    def is_cloud_database(self) -> bool:
        """Check if we're using a cloud database"""
        db_url = os.getenv("DATABASE_URL", "")
        return db_url.startswith("sqlitecloud://")
    
    @property
    def cloud_connection_string(self) -> Optional[str]:
        """Get the cloud database connection string"""
        if self.is_cloud_database:
            return os.getenv("DATABASE_URL")
        return None
    
    # Ollama Configuration
    @property
    def ollama_base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    @property
    def ollama_model(self) -> str:
        return os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    
    # API Configuration
    @property
    def api_host(self) -> str:
        return os.getenv("API_HOST", "0.0.0.0")
    
    @property
    def api_port(self) -> int:
        return int(os.getenv("API_PORT", "8000"))
    
    @property
    def api_workers(self) -> int:
        return int(os.getenv("API_WORKERS", "1"))
    
    @property
    def api_log_level(self) -> str:
        return os.getenv("API_LOG_LEVEL", "info")
    
    # Environment Configuration
    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def debug(self) -> bool:
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
    
    def ensure_database_directory(self):
        """Ensure the database directory exists (only for local databases)"""
        if not self.is_cloud_database:
            self.database_path.mkdir(parents=True, exist_ok=True)
    
    def get_config_summary(self) -> dict:
        """Get a summary of current configuration (without sensitive data)"""
        summary = {
            "database_type": self.database_type,
            "database_path": str(self.database_path),
            "database_file": self.database_file,
            "is_cloud_database": self.is_cloud_database,
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "environment": self.environment,
            "debug": self.debug
        }
        
        if self.is_cloud_database:
            # Hide sensitive API key but show that we're using cloud
            cloud_url = self.cloud_connection_string or ""
            if "apikey=" in cloud_url:
                masked_url = cloud_url.split("apikey=")[0] + "apikey=***masked***"
                summary["database_cloud_url"] = masked_url
            else:
                summary["database_cloud_url"] = cloud_url
        
        return summary

# Global settings instance
settings = Settings()
