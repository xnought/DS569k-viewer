# All credit to the code I've copied from
# https://github.com/wukevin/proteinclip/blob/main/proteinclip/esm_wrapper.py
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


def embed(sequence, model, alphabet, embed_layer=5):
    batch_converter = alphabet.get_batch_converter()

    _, _, tokens = batch_converter([("", sequence)])
    with torch.no_grad():
        results = model(tokens, repr_layers=[embed_layer], return_contacts=False)
    token_representations = results["representations"][embed_layer]
    rep = token_representations[0, 1 : 1 + len(sequence)].cpu().numpy()
    rep = rep.mean(0)

    return rep


VENOME = "/Users/donnybertucci/datasets/venome"


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
