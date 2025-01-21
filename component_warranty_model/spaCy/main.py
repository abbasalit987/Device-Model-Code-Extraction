import spacy
import random
import pandas as pd
import re
import uvicorn
from spacy.training.example import Example
from spacy.training import offsets_to_biluo_tags
from spacy.tokenizer import Tokenizer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class TrainRequest(BaseModel):
    brand: str
    training_type: str = "resume"


def extract_model_spans(text, extracted_model):
    """
    Matches extracted model codes within text using regex for flexible matching.
    Handles cases with numbers, spaces, and alphanumeric model codes.
    """
    if not isinstance(text, str) or not isinstance(extracted_model, str):
        return []

    # Build regex pattern for flexible matching
    pattern = re.escape(extracted_model).replace(r"\-", r"[-\s]*")
    pattern = pattern.replace(r"\.", r"[.\s]*")
    pattern = pattern.replace(r"\(", r"[\(\s]*")
    pattern = pattern.replace(r"\)", r"[\)\s]*")
    pattern = pattern.replace(r"\:", r"[\:\s]*")
    pattern = pattern.replace(r"\s", r"[\s]*")
    pattern = pattern.replace(r"\#", r"[\s]*")
    pattern = pattern.replace(r"\|", r"[\s]*")
    pattern = pattern.replace(r"\+", r"[\s]*")

    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        start_idx = match.start()
        end_idx = match.end()
        return [(start_idx, end_idx, "MODEL")]
    return []


def calculate_training_params(training_data_size):
    """
    Dynamically calculate epoch and batch size based on training data size.
    """
    if training_data_size <= 500:
        return 8, 50
    elif training_data_size <= 5000:
        return 32, 20
    else:
        return 128, 10


def load_training_data(file_path, sheet_name):
    """
    Load and preprocess training data from an Excel file.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)


def prepare_training_data(nlp, data):
    """
    Prepare spaCy-compatible training data from a DataFrame.
    """
    training_data = []
    unmatched_data = []

    for _, row in data.iterrows():
        text = row["Model Description"]
        extracted_model = row["Model Code"]

        entities = extract_model_spans(text, extracted_model)

        if entities:
            doc = nlp.make_doc(text)
            biluo_tags = offsets_to_biluo_tags(doc, entities)
            print("Alignment check:", biluo_tags)
            annotations = {"entities": entities}
            training_data.append(Example.from_dict(doc, annotations))
        else:
            unmatched_data.append(
                {
                    "text": text,
                    "extracted_model": extracted_model,
                    "reason": "No matching spans found",
                }
            )

    return training_data, unmatched_data


def save_unmatched_data(unmatched_data, file_path):
    """
    Save unmatched data to an Excel file for review.
    """
    unmatched_df = pd.DataFrame(unmatched_data)
    unmatched_df.to_excel(file_path, index=False)


def configure_tokenizer(nlp):
    """
    Configure a custom tokenizer for handling special characters.
    """
    infix_re = re.compile(r"[.\-/():#|+]")
    nlp.tokenizer = Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)


def train_ner_model(brand, training_type="resume"):
    """
    Train a spaCy NER model with custom data for a given brand.
    """
    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")
    configure_tokenizer(nlp)

    # Set up the NER pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe("ner")

    ner.add_label("MODEL")

    # Load training data
    file_path = (
        f"component_warranty_model/Data/{brand}/extracted_models_{brand.lower()}.xlsx"
    )
    sheet_name = "Extracted Models 004"
    df = load_training_data(file_path, sheet_name)

    # Prepare training data
    training_data, unmatched_data = prepare_training_data(nlp, df)

    # Save unmatched data
    unmatched_file_path = f"component_warranty_model/Data/{brand}/unmatched_cases.xlsx"
    save_unmatched_data(unmatched_data, unmatched_file_path)

    # Set up optimizer and training parameters
    optimizer = nlp.resume_training()
    batch_size, epochs = calculate_training_params(len(training_data))

    print(f"Training data size: {len(training_data)}")
    print(f"Batch size: {batch_size}, Epochs: {epochs}")

    # Training loop
    for epoch in range(epochs):
        random.shuffle(training_data)
        for batch in spacy.util.minibatch(training_data, size=batch_size):
            nlp.update(batch, sgd=optimizer)

    # Save the fine-tuned model
    output_dir = f"component_warranty_model/spaCy/{brand}/fine_tune_model"
    nlp.to_disk(output_dir)
    print(f"Training completed successfully for {brand} Models!")


@app.post("/train")
async def train_endpoint(request: TrainRequest):
    try:
        train_ner_model(request.brand, request.training_type)
        return {
            "message": f"Training completed successfully for {request.brand} Models!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9500, reload=True)

# Example usage:
# Run FastAPI and send POST requests to /train with JSON payload:
# {
#     "brand": "Samsung",
#     "training_type": "resume"
# }
