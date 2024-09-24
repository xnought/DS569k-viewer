import uvicorn
import pandas as pd
import numpy as np
from utils import init_fastapi_app, disable_cors, CamelModel
import os
from protein_clip import load_proteinclip, get_model, embed_sequence


def load_569k():
    print("Loading Embeddings Dataset")
    df = pd.read_parquet(
        os.path.join("..", "..", "data", "swissprot-embeddings-small.parquet")
    )
    print("Loaded Embeddings Dataset")
    return df


def load_models():
    esm2, alphabet = get_model(6)
    pclip = load_proteinclip(6)
    return esm2, alphabet, pclip


app = init_fastapi_app()
disable_cors(app, ["*"])

df = load_569k()
idx = np.array(df["proteinclip_embed_esm2_6"].tolist())
esm2, alphabet, pclip = load_models()


def embed_pclip(seq, esm2, alphabet, pclip):
    esm_repr = embed_sequence(seq, esm2, alphabet, 6)
    esm_repr /= np.linalg.norm(esm_repr)
    pclip_repr = pclip.predict(esm_repr)
    return pclip_repr


class ProteinCLIPQuery(CamelModel):
    sequence: str
    top_k: int


class EmbeddingsData(CamelModel):
    accession: list[str]
    protein_name: list[str]
    organism_name: list[str]
    sequence_length: list[int]
    similarity: list[float]


@app.post("/proteinclip", response_model=EmbeddingsData)
def compute_similarity(body: ProteinCLIPQuery):
    global idx, pclip, alphabet, esm2, df

    # compute cosine similarity with sequence vs all swiss-prot
    pclip_repr = embed_pclip(body.sequence, esm2, alphabet, pclip).reshape(-1, 1)
    cosine_sim = idx @ pclip_repr  # since both are normed
    top_k = np.argpartition(cosine_sim.reshape(-1), -body.top_k)[-body.top_k :]

    # convert to payload from the metadata
    top_k_df = df.iloc[top_k]
    return EmbeddingsData(
        accession=top_k_df["accession"],
        protein_name=top_k_df["protein_name"],
        organism_name=top_k_df["organism_name"],
        sequence_length=top_k_df["sequence_length"],
        similarity=cosine_sim[top_k].reshape(-1).tolist(),
    )


if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000)
