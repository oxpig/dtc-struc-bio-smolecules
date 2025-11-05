#!/usr/bin/env python3
# Compare hydrogen-bond and related interactions between a resolved inhibitor and designed ligands, including counts against catalytic/subsite residues.

import argparse
import re
from pathlib import Path
import pandas as pd

def normalize_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        cols = [".".join(map(str, c)).strip() for c in df.columns.values]
    else:
        cols = [str(c).strip() for c in df.columns.values]
    return [re.sub(r"\s+", " ", c) for c in cols]

def ensure_bool(df):
    df2 = df.copy().replace({
        "True": True, "False": False, "true": True, "false": False,
        "1": True, "0": False
    })
    try:
        return df2.astype(bool)
    except Exception:
        return df2.applymap(lambda x: bool(x) if pd.notna(x) else False)

def normalize_df_rows(df_raw):
    df = df_raw.copy()
    df.columns = normalize_columns(df_raw)
    # Only transpose if it's a single row AND the columns don't look like interaction columns
    # (interaction columns typically have dots and interaction keywords)
    if df.shape[0] == 1 and df.shape[1] > 1:
        # Check if columns look like they contain interaction information
        has_interaction_format = any(
            ("." in str(col) and any(kw.lower() in str(col).lower() 
             for kw in ["HBDonor", "HBAcceptor", "Ionic", "Cationic", "VdW", "Hydrophobic", "PiStacking"]))
            for col in df.columns
        )
        if not has_interaction_format:
            df = df.T
            df.columns = ["value"]
    return ensure_bool(df)

def extract_residue(colname, interaction_keywords):
    s = colname.replace(",", ".").replace(":", ".").replace("  ", " ").strip()
    for kw in interaction_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", s, flags=re.IGNORECASE):
            left = re.split(rf"\b{re.escape(kw)}\b", s, flags=re.IGNORECASE)[0].strip().rstrip(".").replace(" ", ".")
            toks = [t for t in re.split(r"[.\s]+", left) if t]
            if len(toks) >= 2:
                cand = "".join(toks[-2:])
                return normalize_residue_token(cand) or normalize_residue_token(toks[-1])
            if toks:
                return normalize_residue_token(toks[-1])
    toks = [t for t in re.split(r"[.\s]+", s) if t]
    for i in range(len(toks)-1):
        if toks[i].isalpha() and toks[i+1].isdigit():
            return normalize_residue_token(toks[i] + toks[i+1])
    m = re.search(r"([A-Za-z]{3,})(\d+)", s)
    if m:
        return normalize_residue_token(m.group(1) + m.group(2))
    return None

def normalize_residue_token(token):
    tok = re.sub(r"[^\w]", "", str(token))
    m = re.match(r"^([A-Za-z]{3,})(\d+)", tok)
    if m:
        return f"{m.group(1).upper()}{m.group(2)}"
    m2 = re.match(r"^([A-Za-z]{1,3})(\d+)", tok)
    if m2:
        return f"{m2.group(1).upper()}{m2.group(2)}"
    return None

def load_table(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() in (".parquet", ".pq"):
        return pd.read_parquet(path)
    df = pd.read_csv(path, index_col=0)
    
    # Check if this is the special CSV structure with protein/interaction rows
    if "protein" in df.index and "interaction" in df.index:
        # Reconstruct column names from protein and interaction rows
        protein_row = df.loc["protein"]
        interaction_row = df.loc["interaction"]
        
        # Create new column names: "PROTEIN_RESIDUE.INTERACTION_TYPE"
        # Use positional indexing since columns might have duplicate names
        new_columns = []
        for i in range(len(df.columns)):
            protein = str(protein_row.iloc[i]).strip() if i < len(protein_row) else ""
            interaction = str(interaction_row.iloc[i]).strip() if i < len(interaction_row) else ""
            if protein and interaction and interaction not in ["", "nan", "None"]:
                new_columns.append(f"{protein}.{interaction}")
            elif protein:
                new_columns.append(protein)
            else:
                new_columns.append(str(df.columns[i]))
        
        df.columns = new_columns
        
        # Remove metadata rows (ligand, protein, interaction, Frame) and keep only frame data rows
        metadata_rows = ["ligand", "protein", "interaction", "Frame"]
        frame_rows = [idx for idx in df.index if idx not in metadata_rows]
        df = df.loc[frame_rows]
    
    return df

def get_mol_names_from_sdf(sdfpath: Path):
    from rdkit.Chem import SDMolSupplier
    names = []
    for mol in SDMolSupplier(str(sdfpath), removeHs=False):
        if mol is not None:
            names.append(mol.GetProp("_Name") if mol.HasProp("_Name") else "unknown")
        else:
            names.append("None")
    return names

def summarize_designed(df_designed_bool, mol_names, interaction_keywords, subsites):
    pattern = "|".join(interaction_keywords)
    hb_cols = [c for c in df_designed_bool.columns if re.search(pattern, c, flags=re.IGNORECASE)]
    n_rows = df_designed_bool.shape[0]
    rows = []
    for i in range(n_rows):
        name = mol_names[i] if i < len(mol_names) else f"mol_{i}"
        row = df_designed_bool.iloc[i]
        active = row[hb_cols][row[hb_cols] == True].index.tolist() if hb_cols else []
        residues = []
        for col in active:
            r = extract_residue(col, interaction_keywords)
            residues.append(r or col)
        residues = sorted({r for r in residues if r})
        counts = {}
        for subname, members in subsites.items():
            members_set = set(members)
            cnt = sum(1 for r in residues if r in members_set)
            counts[f"count_{subname}"] = cnt
            counts[f"hit_{subname}"] = bool(cnt)
        rows.append({
            "molecule": name,
            "h_bond_count": len(active),
            "h_bond_residues": ", ".join(residues) if residues else "None",
            **counts
        })
    return pd.DataFrame(rows)

def summarize_resolved(df_resolved_bool, interaction_keywords, subsites):
    pattern = "|".join(interaction_keywords)
    hb_cols = [c for c in df_resolved_bool.columns if re.search(pattern, c, flags=re.IGNORECASE)]
    if not hb_cols or df_resolved_bool.shape[0] == 0:
        return {"count":0,"residues":[],"counts":{k:0 for k in subsites}}
    idx = df_resolved_bool.index[0]
    row = df_resolved_bool.loc[idx]
    active = row[hb_cols][row[hb_cols] == True].index.tolist()
    residues = []
    for col in active:
        r = extract_residue(col, interaction_keywords)
        residues.append(r or col)
    residues = sorted({r for r in residues if r})
    counts = {}
    for subname, members in subsites.items():
        members_set = set(members)
        cnt = sum(1 for r in residues if r in members_set)
        counts[subname] = cnt
    return {"count":len(active),"residues":residues,"counts":counts}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolved", required=True)
    parser.add_argument("--designed", required=True)
    parser.add_argument("--designed-sdf", help="used to extract molecule names if provided")
    parser.add_argument("--output-prefix", default="comparison")
    args = parser.parse_args()

    subsites = {
        "Catalytic": ["HIS51","ASP75","SER135"],
        "S1": ["ASP129","TYR130","PRO131","SER135","TYR150","GLY151","ASN152","TYR161"],
        "S2": ["SER81","ASP83"],
        "S1'": ["HIS51","VAL52","ALA132","GLY133"]
    }

    interaction_keywords = ['HBDonor','HBAcceptor','Ionic','Cationic']

    resolved_raw = load_table(Path(args.resolved))
    df_resolved_bool = normalize_df_rows(resolved_raw)
    res_summary = summarize_resolved(df_resolved_bool, interaction_keywords, subsites)

    df_des_raw = load_table(Path(args.designed))
    df_des_bool = normalize_df_rows(df_des_raw)

    mol_names = []
    if args.designed_sdf:
        try:
            mol_names = get_mol_names_from_sdf(Path(args.designed_sdf))
        except Exception:
            mol_names = []

    if not mol_names:
        mol_names = [f"mol_{i}" for i in range(df_des_bool.shape[0])]

    comparison_df = summarize_designed(df_des_bool, mol_names, interaction_keywords, subsites)

    resolved_row = {
        "molecule": "resolved_inhibitor",
        "h_bond_count": res_summary["count"],
        "h_bond_residues": ", ".join(res_summary["residues"]) if res_summary["residues"] else "None",
        **{f"count_{k}": v for k,v in res_summary["counts"].items()},
        **{f"hit_{k}": (v>0) for k,v in res_summary["counts"].items()}
    }
    comparison_df = pd.concat([pd.DataFrame([resolved_row]), comparison_df], ignore_index=True)

    out_csv = Path(f"{args.output_prefix}.csv")
    comparison_df.to_csv(out_csv, index=False)
    print("Wrote:", out_csv)
    print(comparison_df.to_string(index=False))

if __name__ == "__main__":
    main()
