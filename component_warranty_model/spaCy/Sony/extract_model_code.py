import spacy
import pandas as pd
from openpyxl import load_workbook

# Load the fine-tuned spaCy model
nlp = spacy.load("component_warranty_model/spaCy/Sony/fine_tune_model")

# Load the Excel file containing the list of texts
input_file_path = "component_warranty_model/Data/Sony/extracted_models_sony.xlsx"
sheet_name = "Sample Data 004"
output_file_path = "component_warranty_model/Data/Sony/extracted_models_sony.xlsx"
output_sheet_name = "Extracted Models 004"

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

# Apply the function to each row in the 'Model Description' column
df['Model Code'] = df['Model Description'].apply(extract_model)

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
