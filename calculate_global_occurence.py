import json
from collections import defaultdict

def compute_global_frequencies(json_file_path):
    global_frequencies = defaultdict(int)

    # Read the word frequencies from the provided JSON file
    with open(json_file_path, 'r') as file:
        word_frequencies = json.load(file)

        # Accumulate word frequencies globally
        for subclass_id, freq_dict in word_frequencies.items():
            for word, count in freq_dict.items():
                global_frequencies[word] += count

    return global_frequencies

def save_global_frequencies_to_txt(global_frequencies, output_file_path):
    # Sort the global frequencies in descending order based on occurrences
    sorted_frequencies = sorted(global_frequencies.items(), key=lambda x: x[1], reverse=True)

    # Write to the output text file
    with open(output_file_path, 'w') as file:
        for word, count in sorted_frequencies:
            file.write(f"{word}: {count}\n")

def main(json_file_path):
    global_frequencies = compute_global_frequencies(json_file_path)
    save_global_frequencies_to_txt(global_frequencies, 'global_frequency_occurrence.txt')

# Example usage
if __name__ == "__main__":
    json_file_path = "icd10_word_frequencies.json"
    main(json_file_path)
