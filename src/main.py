import os
import logging
import argparse
from typing import Dict, Any

from src.config import Config
from src.prompt_manager import PromptManager
from src.processor import DocumentProcessor
from src.utils import save_to_file, get_preview, ensure_directory_exists

logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Process and map claims in a document to source news.")
    parser.add_argument(
        "--file", 
        "-f", 
        type=str, 
        default="data/documents/Example_2.docx",
        help="Path to the document file to process"
    )
    parser.add_argument(
        "--output", 
        "-o", 
        type=str, 
        default="results/mapping_result.txt",
        help="Path to save the mapping result"
    )
    parser.add_argument(
        "--model", 
        "-m", 
        type=str, 
        help="OpenAI model name to use (overrides config setting)"
    )
    parser.add_argument(
        "--temperature", 
        "-t", 
        type=float, 
        help="Temperature setting for the model (overrides config setting)"
    )
    parser.add_argument(
        "--max-tokens", 
        type=int, 
        help="Maximum number of tokens to generate (overrides config setting)"
    )
    return parser.parse_args()

def get_processor_settings(config: Config, args) -> Dict[str, Any]:
    """
    Get settings for the document processor.
    
    Args:
        config: Application configuration
        args: Command line arguments
        
    Returns:
        Settings for the document processor
    """
    settings = config.get_openai_settings()
    
    # Override settings with command line arguments if provided
    if args.model:
        settings["model_name"] = args.model
    if args.temperature is not None:
        settings["temperature"] = args.temperature
    if args.max_tokens is not None:
        settings["max_tokens"] = args.max_tokens
        
    return settings

def main():
    """
    Main function to run the mapping process.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Initialize configuration
        config = Config()
        
        # Create prompt manager
        prompt_manager = PromptManager(config.example_file)
        
        # Get processor settings
        processor_settings = get_processor_settings(config, args)
        
        # Create document processor
        processor = DocumentProcessor(
            prompt_manager=prompt_manager,
            openai_api_key=config.openai_api_key,
            model_name=processor_settings.get("model_name"),
            temperature=processor_settings.get("temperature"),
            max_tokens=processor_settings.get("max_tokens")
        )
        
        # Process document
        result = processor.process_document(args.file)
        
        # Save result
        save_to_file(result, args.output)
        
        # Print result preview
        print("\nMapping Result Preview:\n")
        print(get_preview(result, 500) + "\n")
        print(f"Full result saved to {args.output}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)