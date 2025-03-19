import logging
from typing import Dict, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.document_loader import load_doc
from src.prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processor for documents using LLMs."""
    
    def __init__(
        self, 
        prompt_manager: PromptManager,
        openai_api_key: str,
        model_name: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize the document processor.
        
        Args:
            prompt_manager: Prompt manager
            openai_api_key: OpenAI API key
            model_name: Model name
            temperature: Temperature setting for the model
            max_tokens: Maximum number of tokens to generate
        """
        self.prompt_manager = prompt_manager
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def process_document(self, file_path: str) -> str:
        """
        Process a document using the OpenAI model and mapping prompt.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            The mapping result from the LLM
        """
        try:
            # Load document
            logger.info(f"Loading document from {file_path}")
            document_content = load_doc(file_path)
            
            # Get example annotation
            example = self.prompt_manager.get_example_annotation()
            
            # Create prompt template
            prompt = self.prompt_manager.create_mapping_prompt()
            
            # Initialize LLM
            llm = ChatOpenAI(
                temperature=self.temperature,
                openai_api_key=self.openai_api_key,
                model_name=self.model_name,
                max_tokens=self.max_tokens
            )
            
            # Create LangChain chain using the pipe operator
            chain = (
                {"document_content": RunnablePassthrough(), "example": lambda _: example}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            # Execute chain
            logger.info("Processing document with LLM")
            result = chain.invoke(document_content)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise