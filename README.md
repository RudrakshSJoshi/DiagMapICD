# DiagMapICD: Advanced Diagnosis to ICD10 Code Mapper

DiagMapICD is a robust and refined tool designed to map diagnosis descriptions accurately to ICD-10 codes. Using optimized search algorithms, statistical scoring mechanisms, and LLM validation, DiagMapICD achieves high accuracy even with unsupervised datasets. By leveraging structured data processing and frequency analysis, DiagMapICD helps healthcare systems and researchers streamline diagnosis coding with exceptional precision.

---

## Project Workflow

### Initial Inputs
- `code-description pairs.txt`: Contains ICD-10 codes and their descriptions.
- `Diagnoses_List.csv`: A CSV of diagnosis descriptions to be mapped to ICD-10 codes.

### Step-by-Step Workflow

#### 1. Convert CSV to JSON
**Script:** `preprocess_input_data.py`  
**Input:** `Diagnoses_List.csv`  
**Output:** `Diagnoses_JSON.json`  
**Description:** Converts the diagnoses CSV to JSON for enhanced readability and processing.

#### 2. Create ICD10 Structured JSON
**Script:** `set_database.py`  
**Input:** `code-description pairs.txt`  
**Output:** `icd10_data.json`  
**Description:** Transforms code-description pairs into a structured JSON format with classes and specifics defined for easier retrieval and analysis.

#### 3. Calculate Word Occurrences per Class
**Script:** `calculate_class_occurence.py`  
**Input:** `icd10_data.json`  
**Output:** `icd10_word_frequencies.json`  
**Description:** Counts word occurrences within each class (including class name and description) to establish a foundational scoring mechanism.

#### 4. Calculate Global Word Occurrence
**Script:** `calculate_global_occurence.py`  
**Input:** `icd10_word_frequencies.json`  
**Output:** `global_frequency_occurrence.txt`  
**Description:** Computes the total occurrences of each term across all classes, storing this data to refine scoring weights.

#### 5. Apply Custom Scoring Mechanism
**Script:** `custom_weights_score.py`  
**Inputs:** `icd10_word_frequencies.json`, `global_frequency_occurrence.txt`  
**Output:** `icd10_word_frequencies_custom.json`  
**Description:** Utilizes a tf-idf-inspired approach to create an inverse document frequency (IDF) score, adjusting for common words with a logarithmic base-4 scaling. Unique, low-frequency terms (occurrences ≤ 100) are further weighted to maximize their relevance. 

---

This custom scoring mechanism is designed to improve classification accuracy by weighting word relevance across classes using various scaling approaches. Here’s a breakdown of each approach:

**Linear Scaling:**  
In the initial model, a simple linear scaling was used, where the score of a word was divided by its global frequency across all classes. This approach worked effectively for unique terms but underperformed in cases where high-frequency, non-specific terms dominated the dataset, resulting in an accuracy of **83%**.

**Logarithmic Scaling (Log-Base-4):**  
To reduce the influence of high-frequency words, the approach was adjusted to use logarithmic scaling with base 4. The new score for each word was computed by dividing the initial score by `log4(1 + global frequency)`. This log-based scaling closed the gap between high-frequency and low-frequency terms, boosting accuracy to **92%** by enhancing sensitivity to unique words while mitigating the overpowering effect of common terms.

**Custom Scaling:**  
Building on the logarithmic approach, a custom scaling technique was introduced to further improve classification. For words with a global frequency of 100 or fewer, the score was multiplied by 4 to prioritize terms likely to be unique. This additional weighting ensured that rare, context-specific terms carried greater influence, while the logarithmic scaling continued to adjust for other terms. This refined approach achieved the highest accuracy, reaching **97%** by more effectively balancing the relevance of words across varying frequencies.

---

#### 6. Identify Top Classes per Query
**Script:** `top_class_search.py`  
**Inputs:** `Diagnoses_JSON.json`, `icd10_word_frequencies_custom.json`  
**Output:** `top_subclass_results.json`  
**Description:** Identifies the top three most relevant classes per diagnosis query, filtering out cases with a score of zero.

#### 7. Extract Relevant Codes from Each Class
**Script:** `retrieve_top_specifics.py`  
**Input:** `top_subclass_results.json`  
**Output:** `reduced_match_results.json`  
**Description:** Retrieves three details per class: the class name and top two matching results, utilizing a simple string-matching algorithm for refinement.

#### 8. Convert JSON to LLM-Compatible Format
**Script:** `json_convert.py`  
**Input:** `reduced_match_results.json`  
**Output:** `converted_input.json`  
**Description:** Reformats JSON for compatibility with the LLM, enabling smooth data transfer and response parsing.

#### 9. Invoke LLM and Save Final Results
**Script:** `invoke_LLM.py`  
**Input:** `converted_input.json`  
**Outputs:** `dataset_result.json`, `diagnostic_log.txt`  
**Description:** Sends batches of 20 diagnoses to the LLM and retrieves validated ICD-10 mappings. Any parsing errors are recorded in `diagnostic_log.txt`.

---

## Workflow Diagram

Here is a simplified representation of the data flow and file structure in DiagMapICD:

```plaintext
┌─────────────────────────────────────────────────────────────┐
│                       Inputs                                │
│  Initial Files:                                             │
│  - code-description pairs.txt (icd10 dataset)               │
│  - Diagnoses_List.csv (input dataset)                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Convert Diagnoses List to JSON                      │
│ Inputs  -> Diagnoses_List.csv                               │
│ Code    -> preprocess_input_data.py                         │
│ Outputs -> Diagnoses_JSON.json                              │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Convert Code-Description Pairs to Structured JSON   │
│ Inputs  -> code-description pairs.txt                       │
│ Code    -> set_database.py                                  │
│ Outputs -> icd10_data.json                                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Calculate Word Occurrences per Class                │
│ Inputs  -> icd10_data.json                                  │
│ Code    -> calculate_class_occurence.py                     │
│ Outputs -> icd10_word_frequencies.json                      │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Calculate Global Word Occurrences                   │
│ Inputs  -> icd10_word_frequencies.json                      │
│ Code    -> calculate_global_occurence.py                    │
│ Outputs -> global_frequency_occurrence.txt                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Apply Custom Scoring Mechanism                      │
│ Inputs  -> icd10_word_frequencies.json,                     │
│            global_frequency_occurrence.txt                  │
│ Code    -> custom_weights_score.py                          │
│ Outputs -> icd10_word_frequencies_custom.json               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Find Top Relevant Classes                           │
│ Inputs  -> Diagnoses_JSON.json,                             │
│            icd10_word_frequencies_custom.json               │
│ Code    -> top_class_search.py                              │
│ Outputs -> top_subclass_results.json                        │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 7: Retrieve Top Specific Codes from Classes            │
│ Inputs  -> top_subclass_results.json                        │
│ Code    -> retrieve_top_specifics.py                        │
│ Outputs -> reduced_match_results.json                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 8: Convert Results to LLM-Compatible JSON Format       │
│ Inputs  -> reduced_match_results.json                       │
│ Code    -> json_convert.py                                  │
│ Outputs -> converted_input.json                             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 9: Send Data to LLM and Retrieve Classification Output │
│ Inputs  -> converted_input.json                             │
│ Code    -> invoke_LLM.py                                    │
│ Outputs -> dataset_result.json,                             │
│            diagnostic_log.txt                               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                       Outputs                               │
│  Generated Files:                                           │
│  - dataset_result.json (output file)                        │
│  - Diagnoses_List.csv (error log file)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## User Specific Query Fetcher

### Overview
This is a custom user query searching program, that takes user input (diagnosis) and finds the top 3 most relevant searches found.

### Usage Instructions
1. Ensure the `icd10_word_frequencies_custom.json` file is in the same directory as `query_search.py`. This file is essential, as it contains the frequency data used for scoring and determining the relevance of classes.
   
2. Run `query_search.py`. You will be prompted to enter a diagnosis description.

3. After entering a description, the program will process it and display the top 3 ICD-10 classes, each with a description and relevant specific codes retrieved based on relevance.

---

## Environment Setup

### Overview
To run `invoke_LLM.py`, you’ll need to set up the environment. Follow these steps to get started:

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

Your environment is now ready. You can run `invoke_LLM.py` in this setup.

---