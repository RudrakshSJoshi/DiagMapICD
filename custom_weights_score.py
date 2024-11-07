import json
import math

# Define a set of common stop words to ignore
STOP_WORDS = {
    "and", "or", "if", "in", "of", "the", "to", "is", "a", "an", "for", "on", "with",
    "as", "by", "at", "it", "that", "this", "are", "was", "were", "be", "but", "not",
    "from", "about", "which", "all", "these", "their", "its", "has", "have", "can", "without"
}

INSIGNIFICANT_WORDS = { 
    "site", "sites", "specified", "due", "up", "person", "s", "parts",
    "during", "including", "any", "need"
}

EXCLUDE_WORDS = STOP_WORDS.union(INSIGNIFICANT_WORDS)

def func(count):
    temp = math.log(1 + count)
    if count <= 100:
        temp = temp / 4
    return temp

def load_global_frequencies(global_frequency_path):
    # Load global frequency occurrences from the text file, excluding EXCLUDE_WORDS
    global_frequencies = {}
    with open(global_frequency_path, 'r') as file:
        for line in file:
            word, count = line.split(': ')
            word = word.strip()
            if word not in EXCLUDE_WORDS:  # Exclude unwanted words
                global_frequencies[word] = int(count.strip())
    return global_frequencies

def calculate_relative_frequencies(current_json_path, global_frequency_path, output_json_path):
    # Load current ICD-10 word frequencies
    with open(current_json_path, 'r') as json_file:
        icd10_frequencies = json.load(json_file)

    # Load global frequencies
    global_frequencies = load_global_frequencies(global_frequency_path)

    # Create a new dictionary for relative frequencies
    relative_frequencies = {}

    # Calculate relative frequencies, excluding EXCLUDE_WORDS
    for subclass_id, word_counts in icd10_frequencies.items():
        relative_frequencies[subclass_id] = {}
        for word, count in word_counts.items():
            if word not in EXCLUDE_WORDS:  # Skip excluded words
                global_count = global_frequencies.get(word, 1)  # Use 1 to avoid division by zero
                relative_frequencies[subclass_id][word] = count / func(global_count)

    # Save the relative frequencies to a new JSON file
    with open(output_json_path, 'w') as output_file:
        json.dump(relative_frequencies, output_file, indent=4)

def main():
    current_json_path = 'icd10_word_frequencies_updated.json'  # Path to the input ICD-10 JSON file
    global_frequency_path = 'global_frequency_occurrence.txt'  # Path to the global frequency text file
    output_json_path = 'icd10_word_frequencies_custom.json'  # Path to the output JSON file

    calculate_relative_frequencies(current_json_path, global_frequency_path, output_json_path)
    print(f"Relative frequencies saved to {output_json_path}")

# Example usage
if __name__ == "__main__":
    main()
