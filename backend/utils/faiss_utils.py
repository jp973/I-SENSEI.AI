# backend\utils\faiss_utils.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("D:/I-SENSEI.AI/models/all-MiniLM-L6-v2-local")
# Global FAISS index (in-memory)
index = faiss.IndexFlatL2(384)  # 384 = dimension of the MiniLM embedding
stored_questions = []

def embed(text):
    return model.encode([text])[0]

def add_to_index(question):
    vector = embed(question)
    index.add(np.array([vector], dtype=np.float32))
    stored_questions.append(question)

def is_similar(question, threshold=0.8):
    if index.ntotal == 0:
        return False
    vector = embed(question).astype("float32")
    D, _ = index.search(np.array([vector]), k=1)
    # D is distance, convert to similarity
    similarity = 1 - D[0][0] / 4  # adjust based on MiniLM vector norm
    return similarity >= threshold
