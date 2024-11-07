import os
import time
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Placeholder for the Google model instantiation to avoid API calls
google_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)

def classify_all_diagnoses(input_json_path, output_json_path, log_txt_path):
    # Load JSON data
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    # Initialize output structure and diagnostic log file
    output_data = {}
    with open(log_txt_path, 'w') as log_file:

        for patient_id, diagnoses in data.items():
            output_data[patient_id] = []
            diagnosis_batches = [diagnoses[i:i + 20] for i in range(0, len(diagnoses), 20)]
            total_batches = len(diagnosis_batches)

            for batch_idx, batch in enumerate(diagnosis_batches, start=1):
                # Display batch processing progress
                print(f"Processing Patient {patient_id}, Batch {batch_idx}/{total_batches}")

                # Prepare prompt and message for the LLM
                        # Prepare prompt and message for the LLM
                prompt = (
                    f"You are an expert diagnosis classifier. You will receive {len(batch)} diagnoses, each with specific codes. "
                    'If no code is found, output "No Match Found", and put suitable reasons in the "reason" field.\n\n'
                    "Select only the most relevant code for each diagnosis. Output each result in the format:\n"
                    'id: <patient_id> ; diagnosis: "<diagnosis>" ; code: "<selected code>" ; reason: "<reason>"\n\n'
                    "Return results as a single string with each entry separated by '\\n' with no extra information.\n\n"
                    "Each diagnosis in the input will be enclosed by '----' for separation; this is only in the input, not in the output. "
                    "Use '\\n' to separate each diagnosis in the output.\n\n"
                    "Sample Input:\n"
                    "id: 1; diagnosis: Personal history of malignant melanoma of skin; codes: { \n"
                    '    "C43": "Malignant Melanoma Of Skin",\n'
                    '    "C43.8": "Malignant Neoplasm: Overlapping Malignant Melanoma Of Skin",\n'
                    '    "C43.9": "Malignant Neoplasm: Malignant Melanoma Of Skin, Unspecified",\n'
                    '    "D03": "Melanoma In Situ",\n'
                    '    "D03.3": "Melanoma In Situ Of Other And Unspecified Parts Of Face",\n'
                    '    "D03.0": "Melanoma In Situ Of Lip",\n'
                    '    "Z85": "Personal History Of Malignant Neoplasm",\n'
                    '    "Z85.3": "Personal History Of Malignant Neoplasm Of Breast",\n'
                    '    "Z85.0": "Personal History Of Malignant Neoplasm Of Digestive Organs"\n'
                    "}\n"
                    "Sample Output:\n"
                    'id: 1; diagnosis: Personal history of malignant melanoma of skin; code: C43.9; reason: As C43 is malignant melanoma of skin, and is unspecified, so C43.9 suits best.\n\n'
                    f'You make sure that you output {len(batch)} results only, and the above is a sample, not to be confused with actual results.\n\n'
                    'This line is proof that the above is a sample, and anything written after this is actual query.\n\n'
                    'Below are the diagnosis and possible codes:\n'
                )   

                # Add actual diagnoses to the prompt
                for entry in batch:
                    diagnosis = entry['diagnosis']
                    codes = entry['codes']
                    prompt += f"----\nid: {patient_id}; diagnosis: '{diagnosis}'; codes: {{\n"
                    for code, description in codes.items():
                        prompt += f'    "{code}": "{description}",\n'
                    prompt = prompt.rstrip(",\n") + "}\n----\n\n"

                # Send the prompt to the LLM with a 1-second delay between calls
                time.sleep(1)
                messages = [{"role": "user", "content": prompt}]
                response = google_model.invoke(messages)
                fetched_response = response.content.strip()
                # print(fetched_response)

                # Parse and validate response
                response_lines = fetched_response.split("\n")
                if len(response_lines) != len(batch):
                    # Log discrepancy and save input/output details if count mismatch occurs
                    log_file.write(f"Discrepancy for Patient {patient_id}, Batch {batch_idx}\n")
                    log_file.write(f"Expected Diagnoses Count: {len(batch)}\n")
                    log_file.write(f"Received Response:\n{fetched_response}\n\n")
                    print(f"Discrepancy for Patient {patient_id}, Batch {batch_idx}")
                    continue
                else:
                    print(f"Success for for Patient {patient_id}, Batch {batch_idx}")

                # Process each response line and update output_data
                for response_line in response_lines:
                    parts = response_line.split(";")
                    
                    # Ensure there are exactly 4 parts to avoid IndexError
                    if len(parts) != 4:
                        log_file.write(f"Unexpected format for line: {response_line}\n")
                        continue  # Skip this line if the format is incorrect
                    
                    try:
                        # Extract each part and remove surrounding whitespaces
                        id_part = parts[0].split(":")[1].strip()
                        diagnosis_part = parts[1].split(":")[1].strip().strip('"')
                        code_part = parts[2].split(":")[1].strip().strip('"')
                        reason_part = parts[3].split(":")[1].strip().strip('"')

                        # Add the cleaned data to output_data
                        output_data[id_part].append({
                            "diagnosis": diagnosis_part,
                            "code": code_part,
                            "reason": reason_part
                        })
                    except IndexError:
                        log_file.write(f"IndexError encountered for line: {response_line}\n")
                        continue

    # Save final output data to JSON
    with open(output_json_path, 'w') as output_file:
        json.dump(output_data, output_file, indent=4)
    print("Classification completed and output saved.")

# Specify paths for your files
input_json_path = "fetchable.json"
output_json_path = "dataset_result.json"
log_txt_path = "diagnostic_log.txt"

# Run the classification function
classify_all_diagnoses(input_json_path, output_json_path, log_txt_path)
