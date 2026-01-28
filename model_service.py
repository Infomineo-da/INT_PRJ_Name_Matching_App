from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()

# Load model once on startup
MODEL_PATH = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/app/models")
model = SentenceTransformer('all-mpnet-base-v2', cache_folder=MODEL_PATH)

class MatchRequest(BaseModel):
    queries: List[str]
    corpus: List[str]
    threshold: float

@app.post("/match")
async def match(req: MatchRequest):
    # 1. Generate Embeddings
    query_emb = model.encode(req.queries, convert_to_tensor=True)
    corpus_emb = model.encode(req.corpus, convert_to_tensor=True)

    # 2. Reciprocal Search Logic (Moved here to save network bandwidth)
    forward = util.semantic_search(query_emb, corpus_emb, top_k=1)
    reverse = util.semantic_search(corpus_emb, query_emb, top_k=1)

    reverse_lookup = {idx: res[0]['corpus_id'] for idx, res in enumerate(reverse) if res}

    matches = []
    for q_idx, res in enumerate(forward):
        if res:
            c_idx = res[0]['corpus_id']
            score = round(float(res[0]['score']) * 100, 2)
            if reverse_lookup.get(c_idx) == q_idx and score >= req.threshold:
                matches.append({"df1_index": q_idx, "df2_index": c_idx, "match_score": score})

    return matches

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)