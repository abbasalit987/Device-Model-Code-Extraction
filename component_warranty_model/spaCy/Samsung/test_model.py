import spacy

# Load the fine-tuned model
nlp = spacy.load("component_warranty_model/spaCy/fine_tune_model")

# Test the model
test_text = "Samsung LED 138CM 55LS03AA QLED"
doc = nlp(test_text)

# Print the entities recognized by the model
for ent in doc.ents:
    print(ent.text, ent.label_)
