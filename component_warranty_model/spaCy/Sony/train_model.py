import spacy
import random
import pandas as pd
import re
from spacy.training.example import Example
from spacy.matcher import Matcher
from openpyxl import load_workbook
from spacy.training import offsets_to_biluo_tags

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

# Load your data
df = pd.read_excel("component_warranty_model/Data/Sony/extracted_models_sony.xlsx", sheet_name='Extracted Models 003')

# Enhanced Span Matching Function with Regex
def extract_model_spans(text, extracted_model):
    """
    Matches extracted model codes within text using regex for flexible matching.
    """
    if not isinstance(text, str) or not isinstance(extracted_model, str):
        return []
    
    # Escape special regex characters and allow dashes or spaces for matching
    pattern = re.escape(extracted_model).replace(r'\-', r'[-\s]*')  # Allow '-' and spaces
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        start_idx = match.start()
        end_idx = match.end()
        return [(start_idx, end_idx, "MODEL")]
    return []

# Function to check entity alignment
def check_alignment(text, entities):
    doc = nlp.make_doc(text)
    biluo_tags = offsets_to_biluo_tags(doc, entities)
    print("Alignment check:", biluo_tags)

# Lists to store training data and unmatched cases
training_data = []
unmatched_data = []

# Process each row in the DataFrame
for _, row in df.iterrows():
    text = row['Model Description']
    extracted_model = row['Model Code']

    # Get entity spans using enhanced regex matching
    entities = extract_model_spans(text, extracted_model)

    # Check alignment before appending to training data
    if entities:
        check_alignment(text, entities)  # This will print the alignment check for each entity
        annotations = {"entities": entities}
        doc = nlp.make_doc(text)
        training_data.append(Example.from_dict(doc, annotations))
    else:
        unmatched_data.append({
            "text": text,
            "extracted_model": extracted_model,
            "reason": "No matching spans found"
        })

# Save unmatched data for analysis
unmatched_df = pd.DataFrame(unmatched_data)
unmatched_df.to_excel("component_warranty_model/Data/Sony/unmatched_cases.xlsx", index=False)

# Set up the optimizer
optimizer = nlp.resume_training()

# Training loop
for epoch in range(10):
    random.shuffle(training_data)
    for batch in spacy.util.minibatch(training_data, size=2):
        nlp.update(batch, sgd=optimizer)

# Save the fine-tuned model
nlp.to_disk("component_warranty_model/spaCy/Sony/fine_tune_model")
print("Training completed successfully!")
