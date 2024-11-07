import json
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.metrics import edit_distance

# Initialize required components
stemmer = PorterStemmer()

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

def normalize_token(token):
    return re.sub(r'[^a-zA-Z]', '', token.lower())

def compute_similarity_score(str1, str2):
    tokens1 = [normalize_token(token) for token in word_tokenize(str1)]
    tokens2 = [normalize_token(token) for token in word_tokenize(str2)]
    
    match_count = 0
    total_tokens = len(tokens1) + len(tokens2)

    for token1 in tokens1:
        for token2 in tokens2:
            lev_distance = edit_distance(token1, token2)
            lev_score = 1 - (lev_distance / max(len(token1), len(token2))) if max(len(token1), len(token2)) > 0 else 1

            if lev_score > 0.8:
                match_count += 1

    return match_count / total_tokens if total_tokens > 0 else 1.0

def compute_scores(input_words, word_frequencies):
    scores = {}

    for subclass_id, freq_dict in word_frequencies.items():
        score = 0
        for word in input_words:
            if word in freq_dict:
                score += freq_dict[word]
        scores[subclass_id] = score

    return scores

def get_top_k_subclasses(scores, icd10_data, top_k=3):
    sorted_subclasses = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    top_k_results = {}
    for subclass_id, score in sorted_subclasses[:top_k]:
        description = icd10_data[subclass_id]["description"]
        specifics = icd10_data[subclass_id].get("specifics", {})

        specific_codes = [
            {
                "code": specific_code,
                "description": specific_description,
                "similarity_score": compute_similarity_score(specific_description, description)
            }
            for specific_code, specific_description in specifics.items()
        ]

        top_k_results[subclass_id] = {
            "score": score,
            "description": description,
            "specifics": specific_codes
        }

    return top_k_results

def main():
    # Load the word frequencies from JSON
    with open('icd10_word_frequencies_custom.json', 'r') as freq_file:
        word_frequencies = json.load(freq_file)

    # Load the ICD-10 data from JSON
    with open('icd10_data.json', 'r') as data_file:
        icd10_data = json.load(data_file)

    # Take diagnosis input from the user
    diagnosis = input("Enter a diagnosis description: ")

    # Preprocess the input
    input_words = preprocess_input(diagnosis)

    # Compute scores for each subclass
    scores = compute_scores(input_words, word_frequencies)

    # Get the top 3 subclasses based on scores
    top_k_results = get_top_k_subclasses(scores, icd10_data, top_k=3)

    # Print the results
    print("\n---\nTop 3 ICD-10 Classes for the given diagnosis:\n---")
    for subclass_id, info in top_k_results.items():
        print(f"Class ID: {subclass_id}")
        print(f"Description: {info['description']}")
        print(f"Score: {info['score']}")
        print("-----")

    # Print the specifics
    print("\n---\nPossible Results:\n---")
    for subclass_id, info in top_k_results.items():
        print(f"Class ID: {subclass_id} - Description: {info['description']}")
        print("---")
        for specific in info['specifics']:
            print(f"  Code: {specific['code']} - Description: {specific['description']}")
        print("-----")

# Run the program
if __name__ == "__main__":
    main()
