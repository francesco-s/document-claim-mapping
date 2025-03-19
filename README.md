# Document Claim Mapping

This application processes documents and maps factual claims to their corresponding source news.

## Project Structure

```
project_root/
├── src/                       # Source code directory
│   ├── __init__.py            # Makes the directory a package
│   ├── config.py              # Configuration management
│   ├── document_loader.py     # Document loading functionality
│   ├── prompt_manager.py      # Prompt template creation and management
│   ├── processor.py           # Document processing logic
│   ├── utils.py               # Utility functions
│   └── main.py                # Entry point script
├── data/                      # Data directory
│   ├── annotations/           # Examples and annotations
│   ├── ground_truth/          # Ground truth
│   └── documents/             # Input documents
├── results/                   # Results directory
├── .env                       # Environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the application with default settings:

```
python -m src.main
```

Command line options:

- `--file`, `-f`: Path to the document file to process
- `--output`, `-o`: Path to save the mapping result
- `--model`, `-m`: OpenAI model name to use
- `--temperature`, `-t`: Temperature setting for the model
- `--max-tokens`: Maximum number of tokens to generate

Examples:

```
python -m src.main -f '.\data\documents\Example_1.docx' -o results/mapping_result_example1.txt
```

```
python -m src.main -f '.\data\documents\Example_2.docx' -o results/mapping_result_example2.txt
```

## Environment Variables

You can configure the application using these environment variables in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEFAULT_MODEL`: Default model name (default: "gpt-4o")
- `DEFAULT_TEMPERATURE`: Default temperature setting (default: 0.0)
- `DEFAULT_MAX_TOKENS`: Default maximum tokens (default: None)
- `DATA_DIR`: Data directory path (default: "data")
- `RESULTS_DIR`: Results directory path (default: "results")
- `EXAMPLE_FILE`: Example annotation file name (default: "annotations/example_annotation.txt")
- `LOG_LEVEL`: Logging level (default: "INFO")

## Evaluation

The application includes an evaluation module to compare the generated mapping results against ground truth annotations.

### Evaluation Features

- Extracts claims and citations from generated text
- Compares them with ground truth annotations
- Calculates coverage metrics and timestamp distribution
- Generates detailed comparison reports

### Usage

Run evaluation after generating mapping results:

```
python -m src.eval --generated results/mapping_result_example1.txt --ground-truth data/ground_truth/Example_1_human_annotations.csv --output results/evaluation_example1.csv
```

### Command Line Options

When running evaluation:

- `--generated`, `-g`: Path to the generated mapping result file
- `--ground-truth`, `-gt`: Path to the ground truth CSV file
- `--output`, `-o`: Path to save the comparison CSV file
- `--example`, `-e`: Example number (1 or 2) to use default paths

### Evaluation Metrics

The evaluation produces the following metrics:

- Number of claims in both generated output and ground truth
- Number of citations in the generated output
- Number of unique timestamps in both files
- Timestamp coverage percentage
- Detailed timestamp distribution comparison
