from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings1 = model.encode("UA43AU7700 samsung")
# embeddings2 = model.encode("SAMSUNG UA43AU7700 - 43\" LED")
embeddings2 = model.encode("SAMSUNG UA43AU7700 - LED")
similarity = util.cos_sim(embeddings1, embeddings2)
print(similarity)
