import spacy

# Load SpaCy's pre-trained model
nlp = spacy.load("en_core_web_sm")

# Input text
text = "SAMSUNG UA43AU7700 - 43\" LED and QN90D available now."
doc = nlp(text)

# Print extracted entities
print("Entities:", [(ent.text, ent.label_) for ent in doc.ents])
