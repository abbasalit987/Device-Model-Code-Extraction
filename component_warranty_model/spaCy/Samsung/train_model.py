import spacy
import random
import pandas as pd
import difflib
import re

from spacy.training.example import Example

# Load the pre-trained model
nlp = spacy.load("en_core_web_sm")

# Add NER pipeline if it doesn't exist
if "ner" not in nlp.pipe_names:
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner, last=True)
else:
    ner = nlp.get_pipe("ner")

# Add the 'MODEL' label
ner.add_label("MODEL")

df = pd.read_excel("component_warranty_model/Data/Samsung/extracted_models_samsung.xlsx", sheet_name='Training Data')

# Function to split text using multiple delimiters
def advanced_split(text):
    return re.split(r'[ "\'/-]', text)  # Splits by space, double quotes, single quotes, hyphen, or slash

# Lists to store matched and unmatched cases
training_data = []
unmatched_data = []

for _, row in df.iterrows():
    text = row['Model Description']
    extracted_model = row['extracted_model']
    annotation_label = "MODEL"  # E.g., "MODEL"

    # Split the text using the advanced split function
    text_tokens = advanced_split(text)
    
    # Try to find the closest match position
    match = difflib.get_close_matches(extracted_model, text_tokens, n=1, cutoff=0.5)  # Adjust cutoff for flexibility

    if match:
        # Calculate start and end indices of the closest match
        matched_model = match[0]
        start_idx = text.find(matched_model)
        end_idx = start_idx + len(matched_model)

        if start_idx != -1:
            annotations = {
                "entities": [(start_idx, end_idx, annotation_label)]
            }
            training_data.append(Example.from_dict(nlp.make_doc(text), annotations))
        else:
            unmatched_data.append({
                "text": text,
                "extracted_model": extracted_model,
                "reason": "Partial match found but could not calculate indices"
            })
    else:
        # Add to training data with placeholder annotation for unmatched cases
        annotations = {
            "entities": []  # No entities annotated for unmatched cases
        }
        training_data.append(Example.from_dict(nlp.make_doc(text), annotations))
        
        # Add unmatched case to separate list
        unmatched_data.append({
            "text": text,
            "extracted_model": extracted_model,
            "reason": "No match found"
        })

# Save unmatched data for analysis
unmatched_df = pd.DataFrame(unmatched_data)
unmatched_df.to_excel("component_warranty_model/Data/Samsung/unmatched_cases.xlsx", index=False)

# Set up the optimizer
optimizer = nlp.resume_training()

# Training loop
for epoch in range(10):
    random.shuffle(training_data)
    for batch in spacy.util.minibatch(training_data, size=2):
        nlp.update(batch)

# Save the fine-tuned model
nlp.to_disk("component_warranty_model/spaCy/Samsung/fine_tune_model")
