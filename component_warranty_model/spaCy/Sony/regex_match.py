import spacy
from rapidfuzz import fuzz
import re
import pandas as pd
from spacy.language import Language

input_file_path = "component_warranty_model/Data/Sony/extracted_models_sony.xlsx"

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

# Load spaCy pipeline
nlp = spacy.blank("en")

# Add custom attribute for tags
spacy.tokens.Doc.set_extension("tags", default=[], force=True)

# Register the component in spaCy pipeline with pattern configuration
nlp.add_pipe("fuzzy_regex_matcher", last=True, config={"patterns": patterns, "threshold": FUZZY_THRESHOLD})

# Function to process and categorize model codes
def categorize_model_code_with_fuzzy_matching(model_code):
    # Ensure the model_code is a string
    model_code_str = str(model_code) if model_code is not None else ""
    
    # Process the model code using spaCy
    doc = nlp(model_code_str)
    return doc._.tags

# Load Excel file
df = pd.read_excel(input_file_path, sheet_name='Extracted Models 004')

# Convert NaN values in 'Model Code' to empty string
df['Model Code'] = df['Model Code'].fillna('')

# Apply categorization to all model codes
df['Model Tags'] = df['Model Code'].apply(categorize_model_code_with_fuzzy_matching)

# Save the results to the same Excel file and sheet
with pd.ExcelWriter(input_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='Extracted Models 004', index=False)

print("Categorization complete! Results saved to the same file and sheet.")
