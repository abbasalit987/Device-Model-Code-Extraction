import spacy
from rapidfuzz import fuzz
import re
import pandas as pd
from spacy.language import Language
from openpyxl import load_workbook

# Define regex patterns for Sony TV series
patterns = {
    "OLED": r"^(XR|KD|KDL)?-?\d{2}A\d+([A-Za-z0-9]*)$",
    "LED": r"^(KD|KDL)?-?(\d{2})([XW])([A-Za-z0-9]*)$",
    "XR": r"^XR-?[A-Za-z0-9]*$",
}

# Threshold for fuzzy matching
FUZZY_THRESHOLD = 70

# Define custom component using @Language.factory
@Language.factory("fuzzy_regex_matcher")
class FuzzyRegexMatcher:
    def __init__(self, nlp, name, patterns, threshold=85):
        self.patterns = patterns
        self.threshold = threshold

    def __call__(self, doc):
        matches = []
        for label, regex in self.patterns.items():
            # Check if the regex matches fully
            if re.fullmatch(regex, doc.text):
                matches.append(label)
            else:
                # Apply fuzzy matching if no exact match
                similarity = fuzz.partial_ratio(doc.text, regex)
                if similarity >= self.threshold:
                    matches.append(label)
        
        # Add matched labels as custom attributes
        doc._.tags = matches if matches else ["Unknown"]
        return doc

# Load the fine-tuned spaCy model
nlp = spacy.load("component_warranty_model/spaCy/Sony/fine_tune_model")

# Add the fuzzy regex matcher component to the pipeline
nlp.add_pipe("fuzzy_regex_matcher", last=True, config={"patterns": patterns, "threshold": FUZZY_THRESHOLD})

# Add custom attribute for tags
spacy.tokens.Doc.set_extension("tags", default=[], force=True)

# Input and output file paths
input_file_path = "component_warranty_model/Data/Sony/extracted_models_sony.xlsx"
sheet_name = "Sample Data 004"
output_file_path = "component_warranty_model/Data/Sony/extracted_models_sony.xlsx"
output_sheet_name = "Extracted Models 004"

# Load Excel file
df = pd.read_excel(input_file_path, sheet_name=sheet_name)

# Function to extract model from text
def extract_model(text):
    # Ensure that the input is a string (convert if necessary)
    if not isinstance(text, str):
        text = str(text)  # Convert non-string values to string (e.g., NaN -> 'nan')
    
    # Process the text with the spaCy model
    doc = nlp(text)
    models = [ent.text for ent in doc.ents if ent.label_ == "MODEL"]  # Extract entities labeled "MODEL"
    return models[0] if models else None  # Return the first model found, or None if no model found

# Function to categorize model codes
def categorize_model_code_with_fuzzy_matching(model_code):
    # Ensure the model_code is a string
    model_code_str = str(model_code) if model_code is not None else ""
    
    # Process the model code using spaCy
    doc = nlp(model_code_str)
    return doc._.tags

# Apply the model extraction and categorization
df['Model Code'] = df['Model Description'].apply(extract_model)  # Extract "MODEL" entities
df['Model Tags'] = df['Model Code'].apply(categorize_model_code_with_fuzzy_matching)  # Categorize models

# Save the results to a new sheet in the existing Excel file
def save_to_new_sheet(file_path, sheet_name, data):
    try:
        # Load the existing workbook
        book = load_workbook(file_path)
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a") as writer:
            writer._book = book  # Use the private `_book` attribute instead of `book`
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Data written to new sheet: {sheet_name}")
    except FileNotFoundError:
        # If the file doesn't exist, create a new one
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"File created with sheet: {sheet_name}")

# Call the function to save the results
save_to_new_sheet(output_file_path, output_sheet_name, df)

# Print the first few rows of the result
print(df.head())
