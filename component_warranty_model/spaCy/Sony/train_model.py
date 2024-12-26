import spacy
import random
import pandas as pd
import re
from spacy.training.example import Example
from spacy.matcher import Matcher
from openpyxl import load_workbook
from spacy.training import offsets_to_biluo_tags

nlp = spacy.load("en_core_web_sm")

if "ner" not in nlp.pipe_names:
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner, last=True)
else:
    ner = nlp.get_pipe("ner")

ner.add_label("MODEL")

df = pd.read_excel("component_warranty_model/Data/Sony/extracted_models_sony.xlsx", sheet_name='Extracted Models 004')

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

def check_alignment(text, entities):
    doc = nlp.make_doc(text)
    biluo_tags = offsets_to_biluo_tags(doc, entities)
    print("Alignment check:", biluo_tags)

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
