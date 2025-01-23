import spacy
import random
import pandas as pd
import re
import uvicorn
import io
from spacy.training import Example, offsets_to_biluo_tags
from spacy.tokenizer import Tokenizer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Models for Request Validation
class TrainRequest(BaseModel):
    s3_obj: dict
    brand: str
    training_type: str = "resume"


class ExtractModelRequest(BaseModel):
    device_details: dict = {}
    s3_obj: dict = {}


# Utility Functions
def configure_tokenizer(nlp):
    """Configure custom tokenizer for special characters."""
    nlp.tokenizer = Tokenizer(
        nlp.vocab, infix_finditer=re.compile(r"[.\-/():#|+]").finditer
    )


def extract_model_spans(text, extracted_model):
    """Extract model spans using regex."""
    if not isinstance(text, str) or not isinstance(extracted_model, str):
        return []
    pattern = (
        re.escape(extracted_model).replace(r"\-", r"[-\s]*").replace(r"\.", r"[.\s]*")
    )
    pattern = re.sub(r"([#\|+()])", r"[\1\s]*", pattern)
    match = re.search(pattern, text, re.IGNORECASE)
    return [(match.start(), match.end(), "MODEL")] if match else []


def prepare_training_data(nlp, df):
    """Prepare spaCy-compatible training data."""
    training_data, unmatched_data = [], []

    for _, row in df.iterrows():
        text, extracted_model = row["Model Description"], row["Model Code"]
        entities = extract_model_spans(text, extracted_model)

        if entities:
            doc = nlp.make_doc(text)
            training_data.append(Example.from_dict(doc, {"entities": entities}))
        else:
            unmatched_data.append({"text": text, "extracted_model": extracted_model})

    return training_data, unmatched_data


def train_ner_model(s3_obj, training_type="resume"):
    """Train spaCy NER models for each brand."""
    training_data_df = pd.read_excel(io.BytesIO(s3_obj["Body"].read()))

    grouped_by_brand = training_data_df.groupby("Brand")

    for brand, brand_data in grouped_by_brand:
        try:
            model_path = f"component_warranty_model/spaCy/{brand}/fine_tune_model"
            nlp = (
                spacy.load("en_core_web_sm")
                if training_type != "resume"
                else spacy.load(model_path)
            )
            configure_tokenizer(nlp)
            ner = (
                nlp.create_pipe("ner")
                if "ner" not in nlp.pipe_names
                else nlp.get_pipe("ner")
            )
            ner.add_label("MODEL")

            training_data, unmatched_data = prepare_training_data(nlp, brand_data)

            pd.DataFrame(unmatched_data).to_excel(
                f"component_warranty_model/Data/{brand}/unmatched_cases.xlsx",
                index=False,
            )

            optimizer = (
                nlp.resume_training()
                if training_type == "resume"
                else nlp.begin_training()
            )
            batch_size, epochs = calculate_training_params(len(training_data))

            # Training loop
            for epoch in range(epochs):
                random.shuffle(training_data)
                for batch in spacy.util.minibatch(training_data, size=batch_size):
                    nlp.update(batch, sgd=optimizer)

            nlp.to_disk(model_path)
            print(f"Training completed for {brand}!")

        except Exception as e:
            print(f"Failed to train model for brand '{brand}': {str(e)}")


def calculate_training_params(size):
    """Determine batch size and epochs based on data size."""
    if size <= 500:
        return 8, 50
    elif size <= 5000:
        return 32, 20
    return 128, 10


def process_dataframe(df):
    """Group and process DataFrame by brand."""
    grouped = df.groupby("BRAND")
    processed_dfs = []

    for brand, group_df in grouped:
        try:
            nlp = spacy.load(f"component_warranty_model/spaCy/{brand}/fine_tune_model")
            group_df["Model Code"] = group_df["Model Description"].apply(
                lambda desc: [
                    ent.text for ent in nlp(desc).ents if ent.label_ == "MODEL"
                ]
            )
            processed_dfs.append(group_df)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load model for brand '{brand}': {str(e)}",
            )

    return pd.concat(processed_dfs).sort_values(by=["BRAND", "Model Description"])


# FastAPI Endpoints
@app.post("/train")
async def train_endpoint(request: TrainRequest):
    try:
        train_ner_model(request.s3_obj, request.training_type)
        return {"message": f"Training completed for the data input!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/extract")
def extract_model_codes(request: ExtractModelRequest):
    try:
        if request.device_details:
            brand, model_desc = (
                request.device_details["brand"],
                request.device_details["model"],
            )
            nlp = spacy.load(f"component_warranty_model/spaCy/{brand}/fine_tune_model")
            identified_models = [
                ent.text for ent in nlp(model_desc).ents if ent.label_ == "MODEL"
            ]
            return {"status": "success", "entities": identified_models or []}

        if request.s3_obj:
            extract_data_df = pd.read_excel(io.BytesIO(request.s3_obj["Body"].read()))
            if not {"Brand", "Model Description"}.issubset(extract_data_df.columns):
                raise HTTPException(
                    status_code=400,
                    detail="The DataFrame must have 'Brand' and 'Model Description' columns.",
                )

            result_df = process_dataframe(extract_data_df)
            return {
                "status": "success",
                "message": "Model codes extracted successfully.",
                "extracted_data": result_df.to_dict(orient="records"),
            }

        raise HTTPException(
            status_code=400, detail="Either device_details or s3_obj must be provided."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Hello! Welcome to Model Code Extraction Portal"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9500, reload=True)
