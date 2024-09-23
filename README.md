# Swiss-Prot Embeddings

Want to analyze some proteins, but lack embeddings? Want to perform vector similarity search? Want a context of known proteins embeddings? Look no further!

This repository is a dataset of [Reviewed Swiss-Prot Proteins](https://www.uniprot.org/help/downloads). Each protein I compute the embeddings for [ESM2](https://github.com/facebookresearch/esm) (6 layer model), [ProteinCLIP](https://github.com/wukevin/proteinclip), and 2D projection of ProteinCLIP with ParametricUMAP (for visualization).

About 500k proteins and their embeddings in total. For this repo, I filtered proteins such that they were < 3000 residues. The larger proteins took too long to embed and I am GPU poor (sorry no Titin for you).

**Visualize Dataset**: I provide a small web interface that visualizes the proteins in 2D  (like https://esmatlas.com/ and https://atlas.nomic.ai/). What's new? ProteinCLIP aims to embed proteins in functional space, so here we map out the regions functionally.

## Credit

All credit for the data goes to https://www.uniprot.org/ and https://www.expasy.org/resources/uniprotkb-swiss-prot and to the original authors of each protein. I directly took the data from them.

Large pieces of code were copied from https://github.com/wukevin/proteinclip to embed both ESM and ProteinCLIP. Without their pretrained models and code, I could not have produced the embeddings.

And credit to Fair ESM for the pretrained ESM2 models https://github.com/facebookresearch/esm.

## References

- https://www.uniprot.org/help/downloads
- https://github.com/wukevin/proteinclip
- https://github.com/facebookresearch/esm
- https://umap-learn.readthedocs.io/
- https://atlas.nomic.ai/
