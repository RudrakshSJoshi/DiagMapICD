import json
import re

def create_icd10_json(txt_file_path):
    icd10_dict = {}
    current_subclass = None
    subclass_count = 0

    # Define regex patterns for subclass and specifics, ensuring they end with a tab
    subclass_pattern = re.compile(r'^[A-Z]\d{2}\b\t')  # Matches lines like "A00\t"
    specific_pattern = re.compile(r'^[A-Z]\d{2}\.\d+\t')  # Matches lines like "A00.0\t"

    # Open a separate file to store subclass IDs and descriptions
    with open('subclass_descriptions.txt', 'w') as subclass_file, open(txt_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Check if line matches subclass pattern (e.g., "A00 Cholera")
            subclass_match = subclass_pattern.match(line)
            if subclass_match:
                subclass_id = subclass_match.group().strip()  # Remove any trailing tab
                # Extract description after subclass ID
                description_start = line.find(subclass_id) + len(subclass_id)
                description = line[description_start:].strip()
                
                # Add subclass to dictionary if not already present
                if subclass_id not in icd10_dict:
                    icd10_dict[subclass_id] = {
                        "description": description,
                        "specifics": {}
                    }
                    
                    # Write subclass ID and description to text file with space instead of tab
                    subclass_file.write(f"{subclass_id} {description}\n")
                    subclass_count += 1

                # Update the current subclass context
                current_subclass = subclass_id
            
            # Check if line matches specific pattern (e.g., "A00.0 Cholera due to Vibrio cholerae 01, biovar cholerae")
            elif current_subclass and specific_pattern.match(line):
                specific_id_match = specific_pattern.match(line)
                specific_id = specific_id_match.group().strip()  # Remove any trailing tab
                
                # Extract description after specific ID
                description_start = line.find(specific_id) + len(specific_id)
                description = line[description_start:].strip()
                
                # Add specific to the current subclass's specifics dictionary
                icd10_dict[current_subclass]["specifics"][specific_id] = description

    # Print the count of subclasses written to the text file
    print(f"Total subclass count: {subclass_count}")
    
    return icd10_dict

def main(txt_file_path):
    icd10_json = create_icd10_json(txt_file_path)
    
    # Save to a JSON file without any tab characters
    with open('icd10_data.json', 'w') as json_file:
        json.dump(icd10_json, json_file, indent=4)

# Example usage
if __name__ == "__main__":
    txt_file_path = 'code-description pairs.txt'
    main(txt_file_path)
