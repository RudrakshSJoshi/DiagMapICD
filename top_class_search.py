import json
import re

# Define a set of common stop words to ignore
STOP_WORDS = {
    "and", "or", "if", "in", "of", "the", "to", "is", "a", "an", "for", "on", "with",
    "as", "by", "at", "it", "that", "this", "are", "was", "were", "be", "but", "not",
    "from", "about", "which", "all", "these", "their", "its", "has", "have", "can"
}

def preprocess_input(input_string):
    # Normalize the input: lowercase and remove punctuation
    words = re.findall(r'\b\w+\b', input_string.lower())
    # Filter out stop words and use a list comprehension to keep only unique words in order of appearance
    unique_filtered_words = []
    for word in words:
        if word not in STOP_WORDS and word not in unique_filtered_words:
            unique_filtered_words.append(word)
    return unique_filtered_words

def compute_scores(input_words, word_frequencies):
    scores = {}

    for subclass_id, freq_dict in word_frequencies.items():
        score = 0
        for word in input_words:
            if word in freq_dict:
                score += freq_dict[word]  # Increment score by the frequency value
        scores[subclass_id] = score

    return scores

def get_top_k_subclasses(scores, icd10_data, top_k=3):
    # Sort subclasses by score in descending order
    sorted_subclasses = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    # Get top_k subclasses with their descriptions and scores
    top_k_results = {}
    for subclass_id, score in sorted_subclasses[:top_k]:
        description = icd10_data[subclass_id]["description"]
        top_k_results[subclass_id] = {
            "score": score,
            "description": description
        }

    return top_k_results

def main(input_json_path, output_json_path, top_k=3):
    # Read the word frequencies from JSON
    with open('icd10_word_frequencies_custom.json', 'r') as freq_file:
        word_frequencies = json.load(freq_file)

    # Read the ICD-10 data from JSON
    with open('icd10_data.json', 'r') as data_file:
        icd10_data = json.load(data_file)

    # Read the diagnoses from the input JSON
    with open(input_json_path, 'r') as input_file:
        diagnoses_data = json.load(input_file)

    # Prepare the results dictionary
    results = {}

    # Process each diagnosis
    for key, diagnoses in diagnoses_data.items():
        results[key] = []
        for diagnosis in diagnoses:
            # Preprocess the input
            input_words = preprocess_input(diagnosis)

            # Compute scores for each subclass
            scores = compute_scores(input_words, word_frequencies)

            # Get the top_k subclasses based on scores
            top_k_results = get_top_k_subclasses(scores, icd10_data, top_k)

            # Store the results in the desired format
            diagnosis_result = {
                "diagnosis": diagnosis,
                "codes": top_k_results
            }
            results[key].append(diagnosis_result)

    # Save results to the output JSON file
    with open(output_json_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    print(f"Top subclasses saved to {output_json_path}")

# Example usage
if __name__ == "__main__":
    input_json_path = 'process_input.json'  # Path to the input diagnosis JSON file
    output_json_path = 'top_subclass_results.json'  # Path to the output JSON file
    main(input_json_path, output_json_path, 3)
