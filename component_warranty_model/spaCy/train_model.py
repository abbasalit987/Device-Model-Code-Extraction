import spacy
import random
import pandas as pd
import re
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags

def load_nlp_model():
    nlp = spacy.load("en_core_web_sm")

    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add the 'MODEL' label for entity recognition
    ner.add_label("MODEL")
    
    return nlp

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

def check_alignment(text, entities, nlp):
    doc = nlp.make_doc(text)
    biluo_tags = offsets_to_biluo_tags(doc, entities)
    print("Alignment check:", biluo_tags)

def train_model(data_path, sheet_name, nlp, training_data, unmatched_data):

    df = pd.read_excel(data_path, sheet_name=sheet_name)

    for _, row in df.iterrows():
        text = row['Model Description']
        extracted_model = row['Model Code'] if 'Model Code' in row else row['extracted_model']  # Adjust column name if necessary

        entities = extract_model_spans(text, extracted_model)

        # Check alignment before appending to training data
        if entities:
            check_alignment(text, entities, nlp)
            annotations = {"entities": entities}
            doc = nlp.make_doc(text)
            training_data.append(Example.from_dict(doc, annotations))
        else:
            unmatched_data.append({
                "text": text,
                "extracted_model": extracted_model,
                "reason": "No matching spans found"
            })

def save_unmatched_data(unmatched_data, file_path):
    unmatched_df = pd.DataFrame(unmatched_data)
    unmatched_df.to_excel(file_path, index=False)

def main():
    # Initialize pre-trained model
    nlp = load_nlp_model()

    # Lists to store training data and unmatched cases
    training_data = []
    unmatched_data = []

    # Replace with the actual path to your dataset and sheet name
    data_path = "your_dataset_path_here.xlsx"
    sheet_name = "Sheet1" 
    
    train_model(data_path, sheet_name, nlp, training_data, unmatched_data)

    # Save unmatched data for analysis
    save_unmatched_data(unmatched_data, "unmatched_cases.xlsx")

    # Set up the optimizer
    optimizer = nlp.resume_training()

    # Training loop
    for epoch in range(10):
        random.shuffle(training_data)
        for batch in spacy.util.minibatch(training_data, size=2):
            nlp.update(batch)

    # Save the fine-tuned model
    nlp.to_disk("fine_tuned_model")
    print("Training completed successfully!")

if __name__ == "__main__":
    main()
