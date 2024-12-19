from transformers import pipeline

# Load the pre-trained NER pipeline
ner = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")

# Input text
text = "SAMSUNG UA43AU7700 - 43\" LED and QN90D available now."
entities = ner(text)

# Combine subword tokens into full words
def combine_tokens(ner_results):
    combined_entities = []
    current_word = ""
    current_entity = None

    for token in ner_results:
        word = token["word"]
        if word.startswith("##"):  # Subword token
            current_word += word[2:]
        else:
            if current_word:  # Append the previous entity if it exists
                combined_entities.append({"entity": current_entity, "word": current_word})
            current_word = word
            current_entity = token["entity"]

    # Append the last token
    if current_word:
        combined_entities.append({"entity": current_entity, "word": current_word})

    return combined_entities

# Process and print the results
processed_entities = combine_tokens(entities)
print(processed_entities)
