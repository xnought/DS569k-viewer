import uvicorn
import pandas as pd
import numpy as np
from utils import init_fastapi_app, disable_cors, CamelModel
import os
from embed_proteinclip import embed_proteinclip_6
import wget
from functools import lru_cache


@lru_cache(maxsize=1)
def load_569k(src="DS569k.parquet", devMode=False):
    print("Loading Embeddings Dataset")
    if devMode:
        df = pd.read_parquet(
            os.path.join("..", "..", "data", "15k-protein-embeddings.parquet")
        )  # dev debugging on smaller df
    else:
        if not os.path.exists(src):
            print("Fetching from HF")
            wget.download(
                "https://huggingface.co/datasets/donnyb/DS569k/resolve/main/DS569k.parquet",
                "DS569k.parquet",
            )
        df = pd.read_parquet(src)

    df["i"] = range(len(df))
    print("Loaded Embeddings Dataset")

    return df


app = init_fastapi_app()
disable_cors(app, ["*"])
df = load_569k(devMode=False)
idx = np.vstack(df["embedding"].to_numpy())
classes = df["ncbi_taxonomy_class"].dropna().unique().tolist()
phyla = df["ncbi_taxonomy_phylum"].dropna().unique().tolist()


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
    function: list[str | None]


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
    pclip_repr = embed_proteinclip_6(body.sequence).reshape(-1, 1)
    cosine_sim = fidx @ pclip_repr

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
        function=top_k_df["function"],
    )


class TaxonomyInfo(CamelModel):
    classes: list[str]
    phyla: list[str]


@app.get("/taxonomy-info", response_model=TaxonomyInfo)
def taxonomy_info():
    global classes, phyla
    return TaxonomyInfo(phyla=phyla, classes=classes)


if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=4322)
