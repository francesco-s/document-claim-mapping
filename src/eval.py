import re
import pandas as pd
from collections import Counter
import os
import argparse

def extract_claims_and_citations_from_generated_text(file_content):
    """Extract claims and citations from the generated output file."""
    # Extract the generated text part (before "### Source List")
    if "### Source List" in file_content:
        generated_text = file_content.split("### Source List")[0]
        sources = file_content.split("### Source List")[1]
    else:
        generated_text = file_content
        sources = ""
    
    # Find all citations in the generated text
    citations = re.findall(r'\[\d+\]', generated_text)
    citation_numbers = [re.search(r'\[(\d+)\]', citation).group(1) for citation in citations]
    
    # Extract claims with a more robust approach
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', generated_text)
    
    claims_with_citations = []
    for sentence in sentences:
        # Find citations in this sentence
        citations_in_sentence = re.findall(r'\[(\d+)\]', sentence)
        
        if citations_in_sentence:
            # If there are citations, split the sentence based on citations
            parts = re.split(r'(\[\d+\])', sentence)
            
            # Reconstruct claims associated with each citation
            current_claim = ""
            for part in parts:
                if re.match(r'\[\d+\]', part):
                    # This part is a citation, save the current claim
                    citation_num = re.search(r'\[(\d+)\]', part).group(1)
                    if current_claim:
                        claims_with_citations.append((current_claim.strip() + " " + part, citation_num))
                        current_claim = ""
                else:
                    # This part is text
                    current_claim += part
    
    # Extract timestamps from sources
    timestamps = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', sources)
    
    # Create a mapping from citations to timestamps
    citation_to_timestamp = {}
    for line in sources.split('\n'):
        citation_match = re.search(r'\[(\d+)\]', line)
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', line)
        if citation_match and timestamp_match:
            citation_num = citation_match.group(1)
            timestamp = timestamp_match.group(1)
            citation_to_timestamp[citation_num] = timestamp
    
    # Organize claims with their citations and timestamps
    claims_result = []
    for claim, citation_num in claims_with_citations:
        claims_result.append({
            'claim': claim,
            'citation_num': citation_num,
            'timestamp': citation_to_timestamp.get(citation_num, "")
        })
    
    return claims_result, citations, timestamps

def extract_claims_and_citations_from_ground_truth(file_content):
    """Extract claims and timestamps from the ground truth CSV file."""
    # Extract rows from the table (ignoring the header)
    lines = file_content.strip().split('\n')[1:]
    
    claims = []
    timestamps = []
    
    for line in lines:
        parts = line.split(';')
        if len(parts) > 2:
            claim = parts[1].strip('"')
            news_item = parts[2].strip('"')
            
            # Extract timestamp from the news
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', news_item)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                timestamps.append(timestamp)
                claims.append(claim)
    
    return claims, timestamps

def evaluate_mapping(generated_file_path, ground_truth_file_path, output_csv=None):
    """Compare the generated file with ground truth and produce evaluation metrics."""
    # Read file contents
    with open(generated_file_path, 'r', encoding='utf-8') as f1:
        generated_content = f1.read()
    
    with open(ground_truth_file_path, 'r', encoding='utf-8') as f2:
        ground_truth_content = f2.read()
    
    # Analyze the generated file
    claims_gen, citations_gen, timestamps_gen = extract_claims_and_citations_from_generated_text(generated_content)
    
    # Analyze the ground truth file
    claims_gt, timestamps_gt = extract_claims_and_citations_from_ground_truth(ground_truth_content)
    
    # Count occurrences of each timestamp
    timestamp_count_gen = Counter(timestamps_gen)
    timestamp_count_gt = Counter(timestamps_gt)
    
    # Create a dataframe for comparison
    comparison = pd.DataFrame({
        'Timestamp': sorted(set(timestamps_gen) | set(timestamps_gt)),
        'Occurrences_Generated': [timestamp_count_gen.get(ts, 0) for ts in sorted(set(timestamps_gen) | set(timestamps_gt))],
        'Occurrences_GroundTruth': [timestamp_count_gt.get(ts, 0) for ts in sorted(set(timestamps_gen) | set(timestamps_gt))]
    })
    
    # Calculate coverage metrics
    unique_timestamps_gen = set(timestamps_gen)
    unique_timestamps_gt = set(timestamps_gt)
    common_timestamps = unique_timestamps_gen.intersection(unique_timestamps_gt)
    
    coverage_percentage = (len(common_timestamps) / len(unique_timestamps_gt)) * 100 if unique_timestamps_gt else 0
    
    results = {
        'Number_of_claims_in_Generated': len(claims_gen),
        'Number_of_claims_in_GroundTruth': len(claims_gt),
        'Number_of_citations_in_Generated': len(citations_gen),
        'Number_of_unique_timestamps_in_Generated': len(unique_timestamps_gen),
        'Number_of_unique_timestamps_in_GroundTruth': len(unique_timestamps_gt),
        'Number_of_common_timestamps': len(common_timestamps),
        'Coverage_percentage': coverage_percentage,
        'Detailed_comparison': comparison
    }
    
    if output_csv:
        comparison.to_csv(output_csv, index=False)
    
    return results

def print_evaluation_results(results):
    """Print the evaluation results in a formatted way."""
    print("\n===== EVALUATION RESULTS =====")
    print(f"Number of claims in Generated file: {results['Number_of_claims_in_Generated']}")
    print(f"Number of claims in Ground Truth: {results['Number_of_claims_in_GroundTruth']}")
    print(f"Number of citations in Generated file: {results['Number_of_citations_in_Generated']}")
    print(f"Number of unique timestamps in Generated file: {results['Number_of_unique_timestamps_in_Generated']}")
    print(f"Number of unique timestamps in Ground Truth: {results['Number_of_unique_timestamps_in_GroundTruth']}")
    print(f"Number of common timestamps: {results['Number_of_common_timestamps']}")
    print(f"Coverage percentage: {results['Coverage_percentage']:.2f}%")
    print("\nDetailed comparison saved to CSV file.")
    print("==============================\n")

def evaluate(args=None):
    """Main function to evaluate mapping results against ground truth."""
    parser = argparse.ArgumentParser(description='Evaluate document claim mapping results')
    parser.add_argument('--generated', '-g', type=str, default=None, 
                        help='Path to the generated mapping result file')
    parser.add_argument('--ground-truth', '-gt', type=str, default=None,
                        help='Path to the ground truth CSV file')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Path to save the comparison CSV file')
    parser.add_argument('--example', '-e', type=int, default=None,
                        help='Example number (1 or 2) to use default paths')
    
    # Parse arguments
    if args is None:
        args = parser.parse_args()
    
    # If example number is provided, use default paths
    if args.example:
        example_num = args.example
        generated_file = f'results/mapping_result_example{example_num}.txt'
        ground_truth_file = f'data/ground_truth/Example_{example_num}_human_annotations.csv'
        output_csv = f'results/evaluation_example{example_num}.csv'
    else:
        # Use provided paths
        generated_file = args.generated
        ground_truth_file = args.ground_truth
        output_csv = args.output or 'results/evaluation_comparison.csv'
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # Run evaluation
    results = evaluate_mapping(generated_file, ground_truth_file, output_csv)
    print_evaluation_results(results)
    
    return results

if __name__ == "__main__":
    evaluate()