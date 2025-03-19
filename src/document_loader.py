import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def load_doc(file_path: str) -> str:
    """
    Load a document and return its contents as a string.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        The document content as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file type is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    # Process based on file type
    if extension == '.txt':
        return _load_text_file(file_path)
    elif extension == '.docx':
        return _load_docx_file(file_path)
    elif extension == '.csv':
        return _load_csv_file(file_path)
    elif extension == '.xlsx':
        return _load_excel_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

def _load_text_file(file_path: str) -> str:
    """Load a text file and return its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading text file: {str(e)}")
        raise

def _load_docx_file(file_path: str) -> str:
    """Load a Word document and return its contents."""
    try:
        import docx2txt
        logger.info(f"Processing DOCX file: {file_path}")
        return docx2txt.process(file_path)
    except ImportError:
        logger.warning("docx2txt not found, trying with python-docx")
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            logger.error("Neither docx2txt nor python-docx are installed")
            raise

def _load_csv_file(file_path: str) -> str:
    """Load a CSV file and return its contents as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error loading CSV file: {str(e)}")
        raise

def _load_excel_file(file_path: str) -> str:
    """Load an Excel file and return its contents as a string."""
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        return df.to_string()
    except Exception as e:
        logger.error(f"Error loading Excel file: {str(e)}")
        raise