# credit to https://github.com/wukevin. most if not all of this code is copied from the files below
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/esm_wrapper.py
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/model_utils.py
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/gpt.py

import esm
import torch.nn as nn
import torch
import numpy as np
from Bio import SeqIO
from tqdm import tqdm
import matplotlib.pyplot as plt
from Bio.SeqUtils import seq1
from io import StringIO
from Bio.PDB import PDBParser
import os
import re
import functools
from typing import *

import openai

import json
from pathlib import Path
from typing import Any, Dict, Literal

ESM_CALLABLES = {
    48: esm.pretrained.esm2_t48_15B_UR50D,
    36: esm.pretrained.esm2_t36_3B_UR50D,
    33: esm.pretrained.esm2_t33_650M_UR50D,
    30: esm.pretrained.esm2_t30_150M_UR50D,
    12: esm.pretrained.esm2_t12_35M_UR50D,
    6: esm.pretrained.esm2_t6_8M_UR50D,
}


def get_model(model_size: int) -> tuple[nn.Module, esm.Alphabet]:
    """Return model and alphabet for a given model size."""
    model, alphabet = ESM_CALLABLES[model_size]()
    model.eval()
    return model, alphabet


def read_fasta(filename):
    fa = SeqIO.parse(filename, "fasta")
    sequences = []
    ids = []
    for i in fa:
        ids.append(i.id)
        sequences.append(str(i.seq))
    return list(zip(ids, sequences))


def batch_embed_sequence(batch, model, alphabet, embed_layer=5, device="cpu"):
    batch_converter = alphabet.get_batch_converter()

    _, _, tokens = batch_converter(
        [(i, s.replace("*", "<mask>")) for i, s in enumerate(batch)]
    )
    with torch.no_grad():
        results = model(
            tokens.to(device), repr_layers=[embed_layer], return_contacts=False
        )
    token_representations = results["representations"][embed_layer]

    # then convert the batch into an array of embeddings
    reprs = []
    batch_lens = (tokens != alphabet.padding_idx).sum(1)
    for i, tokens_len in enumerate(batch_lens):
        rep = token_representations[i, 1 : tokens_len - 1].cpu().numpy().mean(0)
        reprs.append(rep)

    return reprs


def embed_sequence(sequence, model, alphabet, embed_layer=5, device="cpu"):
    batch_converter = alphabet.get_batch_converter()

    _, _, tokens = batch_converter([("", sequence.replace("*", "<mask>"))])
    with torch.no_grad():
        results = model(
            tokens.to(device), repr_layers=[embed_layer], return_contacts=False
        )
    token_representations = results["representations"][embed_layer]
    rep = token_representations[0, 1 : 1 + len(sequence)].cpu().numpy()
    rep = rep.mean(0)

    return rep


def amino_acids(structure, one_letter_code=True):
    return "".join(
        [
            seq1(residue.resname) if one_letter_code else residue.resname
            for residue in structure.get_residues()
        ]
    )


def read_fasta_from_pdbs(path):
    if not os.path.exists(path):
        raise Exception(path + " does not exist")

    files = os.listdir(path)
    sequences = []
    ids = []
    for f in files:
        parser = PDBParser()
        structure = parser.get_structure(id=None, file=os.path.join(path, f))
        ids.append(f)
        sequences.append(amino_acids(structure))

    return list(zip(ids, sequences))


MODEL_DIR = Path(__file__).parent.parent / "pretrained"


class ONNXModel:
    """Wrapper for an ONNX model to provide a more familiar interface."""

    def __init__(self, path):
        import onnxruntime as ort

        self.model = ort.InferenceSession(path, providers=["CPUExecutionProvider"])

    def predict(self, x: np.ndarray, apply_norm: bool = True):
        """If apply_norm is specified, then apply a norm before feeding into model."""
        assert x.ndim == 1
        if apply_norm:
            x /= np.linalg.norm(x)
        if x.dtype != np.float32:
            x = x.astype(np.float32)
        return self.model.run(None, {"input": x[None, :]})[0].squeeze()

    def predict_batch(self, x: np.ndarray, apply_norm: bool = True):
        assert x.ndim == 2
        if apply_norm:
            x /= np.linalg.norm(x, axis=1)[:, None]
        if x.dtype != np.float32:
            x = x.astype(np.float32)
        return self.model.run(None, {"input": x})[0]


def load_proteinclip(model_size: int | None = None) -> ONNXModel:
    """Load the ProteinCLIP model for the given protein language model."""
    assert MODEL_DIR.is_dir()
    assert model_size is not None, "ESM model requires a size."
    assert model_size in [6, 12, 30, 33, 36], f"Invalid ESM model size: {model_size}"

    model_path = MODEL_DIR / f"proteinclip_esm2_{model_size}.onnx"
    return ONNXModel(model_path)


def embed_text(s: str, key, model="text-embedding-3-large") -> np.ndarray:
    """Get the embeddings for the given string s."""
    CLIENT = openai.OpenAI(api_key=key)
    s = s.strip()  # Remove leading and trailing whitespace
    embed = CLIENT.embeddings.create(input=[s], model=model).data[0].embedding
    return np.array(embed)
