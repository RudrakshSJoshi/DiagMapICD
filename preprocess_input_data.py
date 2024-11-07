import csv
import json

def convert_csv_to_json(csv_file_path, json_file_path):
    # Initialize a dictionary to hold the structured data
    structured_data = {}

    # Read the CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Process each row in the CSV
        for index, row in enumerate(csv_reader, start=1):
            # Extract the text from the row, assuming the format is correct
            text_items = eval(row[0])  # Using eval to convert the string representation of the list

            # Save the items in the desired structure
            structured_data[str(index)] = list(set(text_items))  # Convert set back to list

    # Save the structured data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(structured_data, json_file, indent=4)

def main():
    csv_file_path = 'Diagnoses_List.csv'  # Replace with your CSV file path
    json_file_path = 'Diagnoses_JSON.json'  # Output JSON file path

    convert_csv_to_json(csv_file_path, json_file_path)
    print(f"Converted CSV data saved to {json_file_path}")

# Example usage
if __name__ == "__main__":
    main()
