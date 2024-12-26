import spacy
import pandas as pd
from openpyxl import load_workbook

# Load the fine-tuned spaCy model
nlp = spacy.load("component_warranty_model/spaCy/LG/fine_tune_model")

input_file_path = "component_warranty_model/Data/LG/extracted_models_lg.xlsx"
sheet_name = "Sample Data 001"
output_file_path = "component_warranty_model/Data/LG/extracted_models_lg.xlsx"
output_sheet_name = "Extracted Models 001"

df = pd.read_excel(input_file_path, sheet_name=sheet_name)

# Function to extract model from text
def extract_model(text):
    if not isinstance(text, str):
        text = str(text)
    
    doc = nlp(text)
    models = [ent.text for ent in doc.ents if ent.label_ == "MODEL"]
    return models[0] if models else None

df['Model Code'] = df['Model Description'].apply(extract_model)

def save_to_new_sheet(file_path, sheet_name, data):
    try:
        book = load_workbook(file_path)
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a") as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Data written to new sheet: {sheet_name}")
    except FileNotFoundError:
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"File created with sheet: {sheet_name}")

save_to_new_sheet(output_file_path, output_sheet_name, df)

print(df.head())
