import pandas as pd
import re
from datetime import datetime
import os
import spacy
from openpyxl import load_workbook

# Define regex patterns
lg_oled_pattern_01 = r"^(LG)?[\s-]*\d{2}[\s-]*[Ee][A-Za-z][a-zA-Z0-9\-()+]*$"
lg_oled_pattern_02 = (
    r"^(OLED)?[\s-]*\d{2}[\s-]*[BCEGWZRbcegwzr][A-Za-z0-9][a-zA-Z0-9\-()+]*$"
)
lg_oled_77_to_97_inch_pattern_01 = (
    r"^(LG)?[\s-]*(7[7-9]|8\d{1}|9[0-7])[\s-]*[Ee][A-Za-z][a-zA-Z0-9\-()+]*$"
)
lg_oled_77_to_97_inch_pattern_02 = r"^(OLED)?[\s-]*(7[7-9]|8\d{1}|9[0-7])[\s-]*[BCEGWZRbcegwzr][A-Za-z0-9][a-zA-Z0-9\-()+]*$"

lg_regex_patterns = {
    "OLED": f"{lg_oled_pattern_01}|{lg_oled_pattern_02}",
    "32 inch & above": r"^([A-Za-z]{2,4})?[\s-]*(3[2-9]|[4-9]\d{1,3}|[1-9]\d{3,})[\s-]*[a-zA-Z0-9\-()+]*$",
    "70 inch & above 4K LED": r"^([A-Za-z]{2,4})?[\s-]*(7[0-9]|[8-9]\d{1,3}|[1-9]\d{3,})[\s-]*U[a-zA-Z0-9\-()+]*$",
    "QNED": r"^\d{2,3}QNED[a-zA-Z0-9\-()+]*$",
    "77 - 97 inch OLED": f"{lg_oled_77_to_97_inch_pattern_01}|{lg_oled_77_to_97_inch_pattern_02}",
}

# File paths
input_file_path = "component_warranty_model/Data/LG/extracted_models_lg.xlsx"
input_data_sheet_name = "Sample Data 005"
output_data_sheet_name = "Extracted Models 005"

# Load the spaCy model
nlp = spacy.load("component_warranty_model/spaCy/LG/fine_tune_model")


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
        for tag, pattern in lg_regex_patterns.items()
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
