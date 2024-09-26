# credit to https://github.com/wukevin. most if not all of this code is copied from the files below
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/esm_wrapper.py
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/model_utils.py
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/gpt.py

import esm
import torch.nn as nn
import torch
import numpy as np
from functools import lru_cache

from pathlib import Path

ESM_CALLABLES = {
    48: esm.pretrained.esm2_t48_15B_UR50D,
    36: esm.pretrained.esm2_t36_3B_UR50D,
    33: esm.pretrained.esm2_t33_650M_UR50D,
    30: esm.pretrained.esm2_t30_150M_UR50D,
    12: esm.pretrained.esm2_t12_35M_UR50D,
    6: esm.pretrained.esm2_t6_8M_UR50D,
}


@lru_cache(maxsize=2)
def get_model(model_size: int) -> tuple[nn.Module, esm.Alphabet]:
    """Return model and alphabet for a given model size."""
    model, alphabet = ESM_CALLABLES[model_size]()
    model.eval()
    return model, alphabet


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


@lru_cache(maxsize=2)
def load_proteinclip(model_path="proteinclip_esm2_6.onnx") -> ONNXModel:
    return ONNXModel(model_path)


def embed_proteinclip(seq, esm2, alphabet, pclip, layer=6, device="cpu"):
    esm_repr = embed_sequence(seq, esm2, alphabet, layer, device)
    esm_repr /= np.linalg.norm(esm_repr)
    pclip_repr = pclip.predict(esm_repr)
    return pclip_repr


def embed_proteinclip_6(seq, device="cpu"):
    size = 6
    esm2, alphabet = get_model(size)
    pclip = load_proteinclip(f"src/proteinclip_esm2_{size}.onnx")
    return embed_proteinclip(seq, esm2, alphabet, pclip, size, device)
