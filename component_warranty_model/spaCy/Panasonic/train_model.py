import spacy
import random
import pandas as pd
import re
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags
from spacy.tokenizer import Tokenizer

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Custom tokenizer to prevent splitting on spaces, hyphens, and other special characters
infix_re = re.compile(r'''[.\-/():#]''')  # Customize for dots, hyphens, colons, parentheses
nlp.tokenizer = Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

# If 'ner' pipe doesn't exist, create one
if "ner" not in nlp.pipe_names:
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner, last=True)
else:
    ner = nlp.get_pipe("ner")

# Add the label to the NER pipeline
ner.add_label("MODEL")

# Load the training data from Excel
df = pd.read_excel("component_warranty_model/Data/Panasonic/extracted_models_panasonic.xlsx", sheet_name='Extracted Models 002')

def extract_model_spans(text, extracted_model):
    """
    Matches extracted model codes within text using regex for flexible matching.
    Handles cases with numbers, spaces, and alphanumeric model codes.
    """
    if not isinstance(text, str) or not isinstance(extracted_model, str):
        return []

    # Pattern to allow matching model code with spaces, numbers, hyphens, and alphanumeric sequences
    pattern = re.escape(extracted_model).replace(r'\-', r'[-\s]*')  # Allow dashes and spaces
    pattern = pattern.replace(r'\.', r'[.\s]*')  # Allow periods and spaces
    pattern = pattern.replace(r'\(', r'[\(\s]*')  # Allow opening parentheses and spaces
    pattern = pattern.replace(r'\)', r'[\)\s]*')  # Allow closing parentheses and spaces
    pattern = pattern.replace(r'\:', r'[\:\s]*')  # Allow colon and spaces
    pattern = pattern.replace(r'\s', r'[\s]*')  # Allow for any spaces between parts
    pattern = pattern.replace(r'\#', r'[\s]*')  # Allow for any numbers between parts

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        start_idx = match.start()
        end_idx = match.end()
        return [(start_idx, end_idx, "MODEL")]
    return []

def check_alignment(text, entities):
    doc = nlp.make_doc(text)
    biluo_tags = offsets_to_biluo_tags(doc, entities)
    print("Alignment check:", biluo_tags)

# Prepare training data and unmatched data
training_data = []
unmatched_data = []

for _, row in df.iterrows():
    text = row['Model Description']
    extracted_model = row['Model Code']

    entities = extract_model_spans(text, extracted_model)

    # Check alignment before appending to training data
    if entities:
        check_alignment(text, entities)
        annotations = {"entities": entities}
        doc = nlp.make_doc(text)
        training_data.append(Example.from_dict(doc, annotations))
    else:
        unmatched_data.append({
            "text": text,
            "extracted_model": extracted_model,
            "reason": "No matching spans found"
        })

# Save unmatched data for further review
unmatched_df = pd.DataFrame(unmatched_data)
unmatched_df.to_excel("component_warranty_model/Data/Panasonic/unmatched_cases.xlsx", index=False)

# Set up the optimizer for training
optimizer = nlp.resume_training()

# Training loop
for epoch in range(10):
    random.shuffle(training_data)
    for batch in spacy.util.minibatch(training_data, size=2):
        nlp.update(batch, sgd=optimizer)

# Save the fine-tuned model
nlp.to_disk("component_warranty_model/spaCy/Panasonic/fine_tune_model")
print("Training completed successfully for Panasonic Models!")
