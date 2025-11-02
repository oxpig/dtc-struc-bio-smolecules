# Structure-based Small Molecule Drug Design

### Designing a Zika Protease Binder

## 0. Environment setup

### Create `SMDD_env` environment

```bash
conda env create -f SMDD_env.yaml
conda activate SMDD_env
```

### Install REINVENT4

For generating compounds we will use REINVENT4:

```bash
git clone https://github.com/MolecularAI/REINVENT4.git
cd REINVENT4
conda activate SMDD_env
python install.py cpu
reinvent --help
```

## 1. Workshop goal

Design a compound that binds Zika virus NS2B–NS3 protease better than the original hit. We use the crystal structure 7I9O as our target. Justify your choice using property analysis, generative model scores, and docking interactions.

## 2. Notebook overview

### `1_intro_to_rdkit.ipynb`

Ligand-based analysis with RDKit: load molecules, calculate properties (MW, logP, TPSA), and filter for drug-likeness.

### `2_run_reinvent.ipynb`

Generative design with REINVENT4: define a scoring function in TOML, generate candidate molecules, and triage the results.

### `3_zika_example_workflow.ipynb`

Structure-based design: dock molecules into the Zika protease structure (7I9O) and analyze protein–ligand interactions.

### `4_cure_zika.ipynb`

Cure Zika!: combine all analyses to select **10 compounds** and justify your choice.

## 3. Discovery pipeline

1. **Hit understanding**: Analyze the starting scaffold and its properties.
2. **Idea generation**: Use LibINVENT to generate new analogues with a custom scoring function.
3. **Triage**: Filter by toxicity and other properties (~100 molecules).
4. **Docking**: Dock into the Zika NS2B–NS3 protease structure (7I9O).
5. **Compound selection**: Select and justify 10 of the best compounds.

[1]: https://github.com/MolecularAI/REINVENT4 "GitHub - MolecularAI/REINVENT4: AI molecular design tool for de novo design, scaffold hopping, R-group replacement, linker design and molecule optimization."
[2]: https://www.rcsb.org/structure/7i9o?utm_source=chatgpt.com "7I9O: Group deposition of ZIKV NS2B-NS3 protease in ..."
[3]: https://www.researchgate.net/publication/396319053_Combined_crystallographic_fragment_screening_and_deep_mutational_scanning_enable_discovery_of_Zika_virus_NS2B-NS3_protease_inhibitors?utm_source=chatgpt.com "(PDF) Combined crystallographic fragment screening and ..."
