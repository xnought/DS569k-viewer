# DS569k-viewer

**Similar protein search interface for the [DS569k](https://huggingface.co/datasets/donnyb/569k-protein-embeddings) dataset.**

First install https://github.com/astral-sh/uv then run

```bash
cd viewer
cd server
uv venv
uv sync
uv run src/server.py
```

to install backend packages.

Then in another terminal, use https://pnpm.io/ to install and run the frontend

```bash
cd ..
cd website
pnpm install
pnpm dev
```

Then open http://localhost:5173.


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
