import os
import logging
from typing import Dict, Optional
from langchain_core.prompts import PromptTemplate

from src.utils import read_file

logger = logging.getLogger(__name__)

class PromptManager:
    """Manager for creating and handling prompt templates."""
    
    def __init__(self, example_file_path: str):
        """
        Initialize the prompt manager.
        
        Args:
            example_file_path: Path to the example annotation file
        """
        self.example_file_path = example_file_path
        self._example_content = None
        
    def get_example_annotation(self) -> str:
        """
        Get the example annotation content.
        
        Returns:
            The example annotation content
        """
        if self._example_content is None:
            try:
                if os.path.exists(self.example_file_path):
                    self._example_content = read_file(self.example_file_path)
                else:
                    logger.warning(f"Example file not found: {self.example_file_path}")
                    self._example_content = "No example available."
            except Exception as e:
                logger.error(f"Error reading example file: {str(e)}")
                self._example_content = "Error loading example."
                
        return self._example_content
        
    def create_mapping_prompt(self) -> PromptTemplate:
        """
        Create and return the prompt template for the mapping task.
        
        Returns:
            The prompt template
        """
        prompt_template = """
        You are provided with the following text:

        \"\"\"
        {document_content}
        \"\"\"

        Your task is to map every factual claim in the generated output to its corresponding source news. This mapping is essential to rigorously verify the output's factual accuracy by linking each claim directly to its original source.

        Follow these steps:

        1. **Identify Claims in the Generated Output**
        - **Factual Assertions:** Identify all sentences or segments that make verifiable factual assertions.
        - **Types of Assertions:**
            - **Numerical Data:** Explicit figures, statistics, percentages, ratios, etc. (e.g., "GDP grew by 2.5%", "The unemployment rate is 5.3%").
            - **Qualitative Assertions:** Descriptions of changes or states even without numbers (e.g., "rose," "declined," "surged," "increased," "fell," "remained stable," "highest since", etc.). Note that phrases like "Inflation cooled" imply a decrease.
        - **Segmenting Claims:** If a sentence contains multiple claims (e.g., "Unemployment fell to 4.5%, but inflation climbed to 3.2%"), split it into separate claims.

        2. **Map Each Claim to Source News**
        - **Select the Most Specific Source:** For each claim, find the source news item that most directly supports it.
        - **Tag Matching:** Verify that the source's tag aligns with the subject of the claim (e.g., a claim about "inflation" should match a source tagged [INFLATION]).
        - **Assign Citation Markers:** Number each citation sequentially using square brackets (e.g., [1], [2], [3]).
        - **Direct Support Verification:** The source must contain the exact factual details (numerical data, change direction, etc.). Paraphrasing is acceptable only if the meaning remains identical.
        - **Multiple Claims per Source:** It is acceptable to use the same source to support more than one claim. However, each claim must still be assigned its own citation marker.
        - **Unsubstantiated Claims:** If no source supports a claim, mark it with [No Source Found] without guessing or inferring a source.

        3. **Formatting the Output**
        - **Inline Citations:** Insert the citation marker immediately after the claim it supports, before any punctuation (e.g., "The unemployment rate declined to 6.2% [1]").
        - **Source List:** At the end of the output, include a numbered list of all cited sources. Each entry must include:
            - The citation marker (e.g., [1]).
            - The full excerpt from the source news that supports the claim, along with its timestamp.
            - The exact tag associated with the source (e.g., [INTEREST_RATES]).
        - **No Citation Merging:** Each claim should receive its own citation marker, even if multiple claims appear in one sentence.
        - **Completeness and Accuracy:** Ensure every numerical and qualitative claim is accounted for with either a valid citation or a [No Source Found] marker. Prioritize accuracy; if you are uncertain, use [No Source Found].

        **Annotation Examples:**
        {example}

        Your response must strictly adhere to the process outlined above.
        """

        return PromptTemplate(
            input_variables=["document_content", "example"],
            template=prompt_template
        )