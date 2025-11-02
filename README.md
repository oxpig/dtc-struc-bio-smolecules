# Structure-Based Drug Discovery Workshop

### Designing a Zika Protease Binder

---

## 0. Environment setup (REINVENT4 quick start)

We'll be using **REINVENT4**, an open-source generative design tool for small molecules. REINVENT4 can sample and optimise molecules toward a custom multi-parameter score (drug-likeness, properties, etc.), and it exposes a `reinvent` command-line interface that we call from the notebooks using a TOML config. ([GitHub][1])

Follow these steps in a terminal before running the notebooks:

```bash
# 1. Get the code
git clone https://github.com/MolecularAI/REINVENT4.git
cd REINVENT4

# 2. Create and activate a clean environment with Python 3.10
conda create --name reinvent4 python=3.10
conda activate reinvent4

# 3. Install REINVENT4 for CPU
python install.py cpu

# 4. Sanity check
reinvent --help
```

* REINVENT4 is developed and validated on Linux, requires Python ≥3.10, and supports CPU-only runs (GPU is helpful but not required for our RL/scoring use case). ([GitHub][1])
* The installer adds a `reinvent` CLI. You run it with a config file, e.g.:

  ```bash
  reinvent -l run.log config.toml
  ```

  This is exactly what we'll do in the notebooks. ([GitHub][1])

### Pretrained priors

REINVENT4 uses pretrained "prior" models. You'll point to these priors in your TOML (for example as `prior_file = "libinvent.prior"`). All public prior models are distributed on Zenodo by the REINVENT4 authors. ([GitHub][1])

For this workshop you should download the provided prior checkpoints (from the Zenodo record we give you) and place them in your working directory, e.g.:

```bash
# example: download the published priors
wget https://zenodo.org/records/15641297/files/libinvent.prior
```

These priors are the starting generative models you will sample/optimize against your scoring function.

---

## 1. Workshop goal

The goal of this workshop is to walk through a **full structure-based drug discovery workflow** against the Zika virus NS2B–NS3 protease:

1. Start from an experimental viral protease structure (PDB ID: 7I9O, deposited 23 Apr 2025). 7I9O is a crystal structure of the Zika virus NS2B–NS3 protease bound to small-molecule inhibitors from the ASAP Discovery Consortium, solved at ~1.96 Å resolution. This structure defines a real ligandable pocket in the active site. ([RCSB Protein Data Bank][2])
2. Understand the initial hit / scaffold and its properties.
3. Use generative modelling (REINVENT4) to propose improved analogues.
4. Use docking and protein–ligand interaction analysis to assess whether candidates actually sit in the protease active site the way we want.

Why this target:
The Zika virus NS2B–NS3 protease is the viral serine protease that processes (cleaves) the ZIKV polyprotein into functional proteins. That cleavage step is essential for viral replication, so inhibiting this protease is a direct antiviral strategy. ([ResearchGate][3])

**Your final deliverable:**
Design **one** compound you believe would bind this protease better than the original hit, is chemically reasonable, and is worth proposing for synthesis.

You must justify that choice using:

* ligand-based reasoning (properties, liabilities),
* generative model score,
* docking pose / interactions in the 7I9O pocket. ([RCSB Protein Data Bank][2])

---

## 2. Notebook overview

### `1_intro_to_rdkit.ipynb`

Focus: **ligand-based analysis with RDKit**

* Load and visualise molecules from SMILES.
* Inspect the given "hit" / scaffold.
* Calculate key medicinal chemistry properties (molecular weight, cLogP, polar surface area, etc.).
* Apply simple filtering to remove obviously bad ideas.

By the end of Notebook 1 you should be able to look at a SMILES and say: "Is this even remotely drug-like, or is it instantly disqualified?"

---

### `2_run_reinvent.ipynb`

Focus: **generative design with REINVENT4**

What you'll do here:

* Edit a TOML config (e.g. `zika.toml`) to define a **scoring function**.
  This score encodes what "good" means for our Zika protease project (size window, acceptable polarity, etc.). REINVENT4 is built to optimise multi-component scores via reinforcement learning and sampling. ([GitHub][1])
* Run `reinvent` from inside the notebook. This generates new candidate molecules.
* Collect the output CSV (the model's proposed compounds + their scores).
* Do first-pass triage of those molecules in Python: throw out junk, keep interesting ones.

The goal of Notebook 2 is to become comfortable driving REINVENT4 end-to-end: define the score → run the model → interpret the output.

---

### `3_docking_and_interactions.ipynb`

Focus: **structure-based design**

Here we move from "this looks drug-like on paper" to "does it actually bind the protease pocket?"

* You'll take a filtered subset (you cannot dock everything; assume a budget of ~100 molecules max).
* Dock those molecules into the active site of the Zika virus NS2B–NS3 protease using the crystal structure 7I9O. 7I9O captures the protease with bound small-molecule inhibitors at ~1.96 Å resolution, so it gives us a physically reasonable binding site. ([RCSB Protein Data Bank][2])
* Inspect protein–ligand interactions: hydrogen bonds, hydrophobic contacts, shape complementarity, etc.

By the end of Notebook 3, you should be able to say which designs actually look like plausible protease inhibitors rather than just "nice SMILES strings."

---

### `4_cure_zika.ipynb`

Focus: **decision and justification**

This is the capstone (work in progress):

* Combine everything — property profile, generative score, docking pose quality, interactions in 7I9O — and argue for **one** final compound.
* That compound is your proposed lead to hand off to a medicinal chemist for synthesis and follow-up testing against Zika virus NS2B–NS3 protease, an essential viral protease target with no approved Zika antivirals today. ([RCSB Protein Data Bank][2])

---

## 3. End-to-end discovery pipeline in this project

You will follow (and simulate) a very typical early antiviral hit-to-lead pipeline:

1. **Hit understanding (Notebook 1)**

   * Look at the initial hit/scaffold that was found to bind in the protease pocket.
   * Check basic drug-like properties and liabilities.

2. **Idea generation (Notebook 2)**

   * Use REINVENT4 and a custom scoring function to generate new analogues.
   * Shape the scoring function to reflect what you think a "good protease inhibitor lead" looks like (physchem limits, etc.). ([GitHub][1])
   * Sample molecules and collect them into a candidate list.

3. **Triage / downselection (Notebook 2 → 3)**

   * You do **not** get to dock thousands of molecules.
   * Filter by:

     * obvious toxicity / nonsense chemistry,
     * redundancy (pick diverse chemotypes instead of 50 near-duplicates),
     * sanity of properties (not outrageously big or greasy).
   * Keep a focused panel (~100) for structure-based evaluation.

4. **Structure-based prioritisation (Notebook 3)**

   * Dock that focused panel into the Zika NS2B–NS3 protease structure (7I9O, 1.96 Å; protease in complex with small-molecule inhibitors). ([RCSB Protein Data Bank][2])
   * Inspect binding modes and interactions in the active site, which is the catalytic cleft the virus uses to process its polyprotein. ([ResearchGate][3])
   * Score/rank based on: does it actually engage the pocket like an inhibitor?

5. **Lead nomination (Notebook 4)**

   * Select **one final compound**.
   * Justify why this is the best next-step design for a Zika protease inhibitor (biologically relevant target, plausible binding mode, okay properties, believable synthetic path).

This pipeline is how you go from "interesting fragment in a crystal structure" to "here is a concrete small molecule I want a chemist to make."

---

## TL;DR

* Install REINVENT4 in a fresh Conda env (`python install.py cpu`) and grab the published prior checkpoints from Zenodo. ([GitHub][1])
* Notebook 1: use RDKit to understand the starting hit and basic medicinal chemistry properties.
* Notebook 2: use REINVENT4 to define a scoring function, generate candidate molecules, and triage them. ([GitHub][1])
* Notebook 3: dock the best ~100 ideas into the Zika virus NS2B–NS3 protease crystal structure (PDB 7I9O, 1.96 Å, inhibitors bound) and analyse protein–ligand interactions. ([RCSB Protein Data Bank][2])
* Notebook 4: choose **one** compound you believe is a viable Zika protease inhibitor lead and defend that choice.

[1]: https://github.com/MolecularAI/REINVENT4 "GitHub - MolecularAI/REINVENT4: AI molecular design tool for de novo design, scaffold hopping, R-group replacement, linker design and molecule optimization."
[2]: https://www.rcsb.org/structure/7i9o?utm_source=chatgpt.com "7I9O: Group deposition of ZIKV NS2B-NS3 protease in ..."
[3]: https://www.researchgate.net/publication/396319053_Combined_crystallographic_fragment_screening_and_deep_mutational_scanning_enable_discovery_of_Zika_virus_NS2B-NS3_protease_inhibitors?utm_source=chatgpt.com "(PDF) Combined crystallographic fragment screening and ..."
