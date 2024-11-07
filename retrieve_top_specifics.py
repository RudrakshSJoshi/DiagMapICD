import json
import re
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.metrics import edit_distance

# Initialize required components
stemmer = PorterStemmer()

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

            # Add to match count if the Levenshtein score is above a threshold (0.8)
            if lev_score > 0.8:
                match_count += 1

    return match_count / total_tokens if total_tokens > 0 else 1.0

def build_new_json(top_results, icd10_data):
    new_results = {}
    for diag_id, diagnoses in top_results.items():
        new_results[diag_id] = []
        for diagnosis_entry in diagnoses:
            diagnosis = diagnosis_entry["diagnosis"]
            codes = diagnosis_entry["codes"]

            new_codes = []
            for code, code_data in codes.items():
                score = code_data["score"]
                
                # Skip codes with a score of 0
                if score == 0:
                    continue

                # Add main code with description from top_results
                main_code_entry = {
                    "code": code,
                    "description": code_data["description"]
                }
                new_codes.append(main_code_entry)

                # Get specifics from icd10_data and filter by similarity to the diagnosis
                specifics = icd10_data.get(code, {}).get("specifics", {})
                specific_entries = [
                    (specific_code, specific_description)
                    for specific_code, specific_description in specifics.items()
                ]

                # Sort specific codes by similarity and select top 2
                if specific_entries:
                    specific_entries = sorted(
                        specific_entries,
                        key=lambda x: compute_similarity_score(diagnosis, x[1]),
                        reverse=True
                    )[:2]

                    # Add specific codes with descriptions
                    new_codes.extend([
                        {"code": specific_code, "description": specific_description}
                        for specific_code, specific_description in specific_entries
                    ])

            new_results[diag_id].append({
                "diagnosis": diagnosis,
                "codes": new_codes
            })
    return new_results

# Example usage:
# Load the JSON files
with open("top_subclass_results_ln_weighted_4_100_updGlobal.json") as f:
    top_results = json.load(f)
with open("icd10_data.json") as f:
    icd10_data = json.load(f)

# Process the JSON data
new_json_data = build_new_json(top_results, icd10_data)

# Save the output
with open("reduced_match_results.json", "w") as f:
    json.dump(new_json_data, f, indent=2)
