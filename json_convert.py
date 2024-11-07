import json

def convert_format(input_json_path, output_json_path):
    # Load the input JSON data
    with open(input_json_path, 'r') as input_file:
        input_data = json.load(input_file)

    # Prepare the results structure
    results = {}

    # Iterate through each diagnosis
    for key, diagnoses in input_data.items():
        results[key] = []  # Initialize a list for each key
        for diagnosis in diagnoses:
            diagnosis_result = {
                "diagnosis": diagnosis["diagnosis"],
                "codes": {}
            }
            for code_entry in diagnosis['codes']:
                code = code_entry['code']
                description = code_entry['description']
                # Normalize the description (capitalize appropriately)
                normalized_description = ' '.join(word.capitalize() for word in description.split())
                diagnosis_result["codes"][code] = normalized_description

            results[key].append(diagnosis_result)

    # Save the results to the output JSON file
    with open(output_json_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)

    print(f"Converted format saved to {output_json_path}")

# Example usage
if __name__ == "__main__":
    input_json_path = 'reduced_match_results.json'  # Path to the input JSON file
    output_json_path = 'converted_input.json'  # Path to the output JSON file
    convert_format(input_json_path, output_json_path)
