import pandas as pd
import re
from datetime import datetime
import os
import spacy
from openpyxl import load_workbook

# Define regex patterns
sony_regex_patterns = {
    "Bravia OLED" : r"^(KD|XR)?[\s-]*\d{2}[\s-]*[aA]\d{1,4}[a-zA-Z0-9\-()+]*$",
    "32 inch" : r"^([A-Za-z]{2,4}?[\s-]*)?32[\s-]*[A-Za-z]{1,2}\d{1,4}[a-zA-Z0-9\-()+]*$",
    "43 inch & above" : r"^([A-Za-z]{2,4}?[\s-]*)?(4[3-9]|[5-9]\d{1,3}|[1-9]\d{3,})[\s-]*[A-Za-z]{1,2}\d{1,4}[a-zA-Z0-9\-()+]*$",
    "XR" : r"^XR[\s-]*[a-zA-Z0-9\-()+]*$",
    "LED" : r"^(KD|KDL|XR|KLV|K|UA)?[\s-]*\d{2}[\s-]*[xwrzspcXWRZSPU]{1,2}\d{1,4}[a-zA-Z0-9\-()+]*$",
    "A80J" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A80J[a-zA-Z0-9\-()+]*$",
    "A80K" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A80K[a-zA-Z0-9\-()+]*$",
    "A80K" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A80L[a-zA-Z0-9\-()+]*$",
    "A95K" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A95K[a-zA-Z0-9\-()+]*$",
    "A95L" : r"^([A-Za-z]{2,4}?[\s-]*)?\d{2,4}A95L[a-zA-Z0-9\-()+]*$",
}
# File paths
input_file_path = "component_warranty_model/Data/Sony/extracted_models_sony.xlsx"
input_data_sheet_name = "Sample Data 006"
output_data_sheet_name = "Extracted Models 008"

# Load the spaCy model
nlp = spacy.load("component_warranty_model/spaCy/Sony/fine_tune_model")


# Function to extract model code from text using spaCy
def extract_model(text):
    if not isinstance(text, str):
        text = str(text)  # Convert non-string values to string
    doc = nlp(text)
    models = [ent.text for ent in doc.ents if ent.label_ == "MODEL"]
    return models[0] if models else None


# Function to match tags using regex patterns
def match_tags(model_code):
    tags = [
        tag
        for tag, pattern in sony_regex_patterns.items()
        if (model_code and re.match(pattern, str(model_code.strip().replace(" ", ""))))
    ]
    return tags


# Load the data from Excel
df = pd.read_excel(input_file_path, sheet_name=input_data_sheet_name)

# Extract model codes using spaCy
df["Model Code"] = df["Model Description"].apply(extract_model)

# Match tags using regex patterns
df["Tags"] = df["Model Code"].apply(lambda x: match_tags(x))

# Select required columns
df = df[["Model Description", "Model Code", "Tags"]]


# Save results to one sheet in a single Excel file
def save_to_excel(file_path, sheet_name, data):
    try:
        if os.path.exists(file_path):
            # Load existing workbook and append sheet
            book = load_workbook(file_path)
            with pd.ExcelWriter(file_path, engine="openpyxl", mode="a") as writer:
                writer._book = book
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Appended data to sheet: {sheet_name}")
        else:
            # Create new file if it doesn't exist
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Created new file with sheet: {sheet_name}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


# Save to a timestamped sheet
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_to_excel(input_file_path, output_data_sheet_name, df)

# Print the first few rows for verification
print(df.head())
