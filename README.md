# Swiss-Prot Embeddings

Want to analyze some proteins, but lack embeddings? Want to perform vector similarity search? Want a context of known proteins embeddings? Look no further!

This repository is a dataset of [Reviewed Swiss-Prot Proteins](https://www.uniprot.org/help/downloads). Each protein I compute the embeddings for [ESM2](https://github.com/facebookresearch/esm) (6 layer model) and [ProteinCLIP](https://github.com/wukevin/proteinclip).

About 500k proteins and their embeddings in total. For this repo, I filtered proteins such that they were < 3000 residues. The larger proteins took too long to embed and I am GPU poor (sorry no Titin for you).

**Embedding Viewer**: To view this dataset, I provide a small interface that maps out the 2D embeddings. You can enter your own fasta sequence to automatically embed your own protein.

## Credit

All credit for the data goes to https://www.uniprot.org/ and https://www.expasy.org/resources/uniprotkb-swiss-prot and to the original authors of each protein. I directly took the data from them.

Large pieces of code were copied from https://github.com/wukevin/proteinclip to embed both ESM and ProteinCLIP. Without their pretrained models and code, I could not have produced the embeddings.

And credit to Fair ESM for the pretrained ESM2 models https://github.com/facebookresearch/esm.

## References

- https://www.uniprot.org/help/downloads
- https://github.com/wukevin/proteinclip
- https://github.com/facebookresearch/esm
- https://umap-learn.readthedocs.io/
