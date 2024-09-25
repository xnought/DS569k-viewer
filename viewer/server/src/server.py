import uvicorn
import pandas as pd
import numpy as np
from utils import init_fastapi_app, disable_cors, CamelModel
import os
from protein_clip import load_proteinclip, get_model, embed_sequence


def load_569k(src):
    print("Loading Embeddings Dataset")
    df = pd.read_parquet(os.path.join("..", "..", "data", src))
    df["i"] = range(len(df))
    print("Loaded Embeddings Dataset")
    return df


def load_models():
    esm2, alphabet = get_model(6)
    pclip = load_proteinclip(6)
    return esm2, alphabet, pclip


app = init_fastapi_app()
disable_cors(app, ["*"])

df = load_569k("569k-protein-embeddings.parquet")
idx = np.vstack(df["embedding"].to_numpy())
esm2, alphabet, pclip = load_models()


def embed_pclip(seq, esm2, alphabet, pclip):
    esm_repr = embed_sequence(seq, esm2, alphabet, 6)
    esm_repr /= np.linalg.norm(esm_repr)
    pclip_repr = pclip.predict(esm_repr)
    return pclip_repr


class SimilarityQuery(CamelModel):
    sequence: str
    top_k: int
    class_filters: list[str] | None = None
    phylum_filters: list[str] | None = None


class ProteinData(CamelModel):
    accession: list[str]
    protein_name: list[str]
    organism_name: list[str]
    sequence_length: list[int]
    ncbi_taxonomy_class: list[str | None]
    ncbi_taxonomy_phylum: list[str | None]
    similarity: list[float]


def filter_df(df, class_filters, phylum_filters):
    filtered_df = df
    if class_filters is not None:
        filtered_df = filtered_df[
            filtered_df["ncbi_taxonomy_class"].isin(class_filters)
        ]
    if phylum_filters is not None:
        filtered_df = filtered_df[
            filtered_df["ncbi_taxonomy_phylum"].isin(phylum_filters)
        ]
    return filtered_df


@app.post("/proteinclip", response_model=ProteinData)
def compute_similarity(body: SimilarityQuery):
    global idx, pclip, alphabet, esm2, df

    # first filter the dataframe
    fdf = filter_df(df, body.class_filters, body.phylum_filters)
    fidx = idx[fdf["i"].tolist(), :]  # filter down the idx too

    # compute cosine similarity with sequence vs all swiss-prot
    pclip_repr = embed_pclip(body.sequence, esm2, alphabet, pclip).reshape(-1, 1)
    cosine_sim = fidx @ pclip_repr  # since both are normed

    top_k = range(len(fidx))
    if len(fidx) > body.top_k:
        top_k = np.argpartition(cosine_sim.reshape(-1), -body.top_k)[-body.top_k :]

    # convert to payload from the metadata
    top_k_df = fdf.iloc[top_k]
    return ProteinData(
        accession=top_k_df["accession"],
        protein_name=top_k_df["protein_name"],
        organism_name=top_k_df["organism_name"],
        sequence_length=top_k_df["sequence_length"],
        ncbi_taxonomy_class=top_k_df["ncbi_taxonomy_class"],
        ncbi_taxonomy_phylum=top_k_df["ncbi_taxonomy_phylum"],
        similarity=cosine_sim[top_k].reshape(-1).tolist(),
    )


class TaxonomyInfo(CamelModel):
    classes: list[str]
    phyla: list[str]


@app.get("/taxonomy-info", response_model=TaxonomyInfo)
def taxonomy_info():
    global df
    classes = df["ncbi_taxonomy_class"].dropna().unique().tolist()
    phyla = df["ncbi_taxonomy_phylum"].dropna().unique().tolist()
    return TaxonomyInfo(phyla=phyla, classes=classes)


if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000)
