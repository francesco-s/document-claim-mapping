import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the application."""
    
    def __init__(self):
        """Initialize the configuration."""
        self._load_environment_variables()
        self._configure_logging()

    def _load_environment_variables(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv()
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not defined in the .env file")
            
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.default_temperature = float(os.getenv("DEFAULT_TEMPERATURE", "0.0"))
        self.default_max_tokens = self._parse_int_env("DEFAULT_MAX_TOKENS")
        
        self.data_dir = os.getenv("DATA_DIR", "data")
        self.results_dir = os.getenv("RESULTS_DIR", "results")
        self.example_file = os.path.join(self.data_dir, os.getenv("EXAMPLE_FILE", "annotations\example_annotation.txt"))
        
    def _parse_int_env(self, key: str) -> Optional[int]:
        """Parse an integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Could not parse {key} as integer: {value}")
            return None
    
    def _configure_logging(self) -> None:
        """Configure logging for the application."""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_format = os.getenv(
            "LOG_FORMAT", 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format
        )

    def get_openai_settings(self) -> Dict[str, Any]:
        """Return settings for OpenAI API."""
        return {
            "openai_api_key": self.openai_api_key,
            "model_name": self.default_model,
            "temperature": self.default_temperature,
            "max_tokens": self.default_max_tokens
        }