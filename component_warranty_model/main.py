import spacy
import random
import pandas as pd
import re
import uvicorn
from spacy.training import Example, offsets_to_biluo_tags
from spacy.tokenizer import Tokenizer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class TrainRequest(BaseModel):
    brand: str
    training_type: str = "resume"


def extract_model_spans(text, extracted_model):
    """Matches model codes in text using regex."""
    if not isinstance(text, str) or not isinstance(extracted_model, str):
        return []

    pattern = (
        re.escape(extracted_model).replace(r"\-", r"[-\s]*").replace(r"\.", r"[.\s]*")
    )
    pattern = re.sub(r"([#\|+()])", r"[\1\s]*", pattern)
    match = re.search(pattern, text, re.IGNORECASE)
    return [(match.start(), match.end(), "MODEL")] if match else []


def calculate_training_params(size):
    """Calculate batch size and epochs based on training data size."""
    if size <= 500:
        return 8, 50
    elif size <= 5000:
        return 32, 20
    return 128, 10


def prepare_training_data(nlp, df):
    """Prepare spaCy-compatible training data and print alignment using BILOU tags."""
    unmatched_data = []
    training_data = []

    for _, row in df.iterrows():
        text = row["Model Description"]
        extracted_model = row["Model Code"]

        # Extract entity spans
        entities = extract_model_spans(text, extracted_model)

        if entities:
            # Create a Doc and convert to BILOU tags
            doc = nlp.make_doc(text)
            biluo_tags = offsets_to_biluo_tags(doc, entities)

            # Print the alignment check
            print(f"Text: {text}")
            print(f"BILOU tags: {biluo_tags}")

            # Create the Example and append it
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


def save_unmatched_data(data, brand):
    """Save unmatched data to an Excel file."""
    pd.DataFrame(data).to_excel(
        f"component_warranty_model/Data/{brand}/unmatched_cases.xlsx", index=False
    )


def configure_tokenizer(nlp):
    """Configure custom tokenizer for special characters."""
    nlp.tokenizer = Tokenizer(
        nlp.vocab, infix_finditer=re.compile(r"[.\-/():#|+]").finditer
    )


def train_ner_model(brand, training_type="resume"):
    """Train spaCy NER model for a given brand."""
    nlp = (
        spacy.load("en_core_web_sm")
        if training_type != "resume"
        else spacy.load(f"component_warranty_model/spaCy/{brand}/fine_tune_model")
    )

    # Disable unnecessary components
    nlp.disable_pipes(
        "lemmatizer", "tagger", "parser", "ner"
    )  # Disable all but NER (if you're training)

    # Configure tokenizer for special characters
    configure_tokenizer(nlp)

    ner = nlp.create_pipe("ner") if "ner" not in nlp.pipe_names else nlp.get_pipe("ner")
    ner.add_label("MODEL")

    # Load and prepare data
    df = pd.read_excel(
        f"component_warranty_model/Data/{brand}/extracted_models_{brand.lower()}.xlsx",
        sheet_name="Extracted Models 004",
    )
    training_data, unmatched_data = prepare_training_data(nlp, df)

    save_unmatched_data(unmatched_data, brand)

    # Set up optimizer
    optimizer = (
        nlp.resume_training() if training_type == "resume" else nlp.begin_training()
    )
    batch_size, epochs = calculate_training_params(len(training_data))

    print(
        f"Training data size: {len(training_data)} | Batch size: {batch_size} | Epochs: {epochs}"
    )

    # Training loop
    for epoch in range(epochs):
        random.shuffle(training_data)
        for batch in spacy.util.minibatch(training_data, size=batch_size):
            nlp.update(batch, sgd=optimizer)

    # Save fine-tuned model
    nlp.to_disk(f"component_warranty_model/spaCy/{brand}/fine_tune_model")
    print(f"Training completed for {brand}!")


@app.post("/train")
async def train_endpoint(request: TrainRequest):
    try:
        train_ner_model(request.brand, request.training_type)
        return {"message": f"Training completed for {request.brand}!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9500, reload=True)

# Example usage:
# POST to /train with payload:
# { "brand": "Samsung", "training_type": "resume" }
