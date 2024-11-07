import json
import re
from collections import Counter

# Define a set of common stop words to ignore
STOP_WORDS = {
    "and", "or", "if", "in", "of", "the", "to", "is", "a", "an", "for", "on", "with",
    "as", "by", "at", "it", "that", "this", "are", "was", "were", "be", "but", "not",
    "from", "about", "which", "all", "these", "their", "its", "has", "have", "can"
}

def compute_word_frequencies(icd10_data):
    frequencies = {}

    for subclass_id, data in icd10_data.items():
        # Combine subclass description and specifics into a single string
        combined_text = data["description"] + " " + " ".join(data["specifics"].values())
        
        # Normalize the text: lowercase and remove punctuation
        words = re.findall(r'\b\w+\b', combined_text.lower())
        
        # Filter out stop words
        filtered_words = [word for word in words if word not in STOP_WORDS]
        
        # Count the occurrences of each word
        word_count = Counter(filtered_words)
        
        # Store the frequency dictionary in the result
        frequencies[subclass_id] = dict(word_count)

    return frequencies

def main(json_file_path):
    # Read the existing ICD-10 JSON data
    with open(json_file_path, 'r') as json_file:
        icd10_data = json.load(json_file)

    # Compute the word frequencies
    word_frequencies = compute_word_frequencies(icd10_data)

    # Save the word frequencies to a new JSON file
    with open('icd10_word_frequencies.json', 'w') as freq_json_file:
        json.dump(word_frequencies, freq_json_file, indent=4)

# Example usage
if __name__ == "__main__":
    json_file_path = 'icd10_data.json'
    main(json_file_path)
