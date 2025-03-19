import os
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, create it if it doesn't.
    
    Args:
        path: Path to the directory
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            logger.info(f"Created directory: {path}")
        except Exception as e:
            logger.error(f"Error creating directory {path}: {str(e)}")
            raise

def save_to_file(content: str, file_path: str) -> None:
    """
    Save content to a file.
    
    Args:
        content: Content to save
        file_path: Path to the file
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)
            
        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Content saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving content to {file_path}: {str(e)}")
        raise

def read_file(file_path: str) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file content as a string
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise

def get_preview(text: str, max_length: int = 500) -> str:
    """
    Get a preview of a text.
    
    Args:
        text: Text to preview
        max_length: Maximum length of the preview
        
    Returns:
        A preview of the text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."