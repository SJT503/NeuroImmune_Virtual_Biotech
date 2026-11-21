from gate import gate, pass_gate, canary_gate, retry_limit
import os
import sys
import gzip
import glob
import json
import time
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd
from scipy import sparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
RAW_GEO_DIR = os.path.join(BASE_DIR, "data", "raw_geo")
TABLES_DIR = os.path.join(BASE_DIR, "tables")
EXTERNAL_RAW_BASE = r"D:\2026-04-24\new-chat-2\TBI_astrocyte_scst_project\raw_data"

# Canonical gene aliases between 2024 MGI symbols and 2018 RefSeq Drop-seq symbols
GENE_ALIASES = {
    "Selenom": ["Selenom", "Selm"],
    "Bicral": ["Bicral", "2900097C17Rik", "Gltscr1l"],
    "3000002C10Rik": ["3000002C10Rik", "Plpp6", "Ppapdc2"],
    "Gm2762": ["Gm2762", "Ccl21a", "Ccl21b"],
    "Gm35339": ["Gm35339", "Ifi208", "Pyhin1"],
    "Il6r": ["Il6r", "Il6ra", "IL6R"],
    "Scn2a": ["Scn2a", "Scn2a1", "SCN2A"],
}

# Lineage markers for single-cell cell-type classification and mandatory Purity Gate
LINEAGE_MARKERS_MOUSE = {
    "ASC": ["Aqp4", "Gfap", "Slc1a2", "Slc1a3", "Aldh1l1", "Gja1"],
    "MG": ["Hexb", "Csf1r", "Cx3cr1", "C1qa", "C1qb", "Tyrobp", "Itgam"],
    "ODC": ["Plp1", "Mbp", "Mog", "Mobp", "Mag", "Cnp"],
    "OPC": ["Pdgfra", "Cspg4", "Olig1", "Olig2"],
    "NEU": ["Snap25", "Syt1", "Rbfox3", "Slc17a7", "Gad1", "Gad2", "Syn1"],
    "END": ["Cldn5", "Flt1", "Pecam1", "Ly6c1"],
    "PER": ["Pdgfrb", "Rgs5", "Acta2", "Tagln"],
    "CPE_EPEN": ["Ttr", "Folr1", "Prlr", "Foxj1", "Ccdc153"],
}

LINEAGE_MARKERS_HUMAN = {
    k: [g.upper() for g in v] for k, v in LINEAGE_MARKERS_MOUSE.items()
}


def get_target_gene_universe():
    """Return the complete universe of candidate, clinical trial, purity, and module genes."""
    p1_path = os.path.join(BASE_DIR, "data", "Phase1_Virtual_CSO_Target_Priority_Ledger_133Genes.csv")
    cand_genes = []
    if os.path.exists(p1_path):
        df_p1 = pd.read_csv(p1_path)
        g_col = "gene_name" if "gene_name" in df_p1.columns else df_p1.columns[0]
        cand_genes = df_p1[g_col].dropna().astype(str).tolist()
        if "Human_Symbol" in df_p1.columns:
            for _, r in df_p1.iterrows():
                mg = str(r[g_col]).strip()
                hg = str(r["Human_Symbol"]).strip()
                existing = GENE_ALIASES.get(mg, [mg])
                for cand in [mg, mg.upper(), hg, hg.upper()]:
                    if cand and cand != "nan" and cand not in existing:
                        existing.append(cand)
                GENE_ALIASES[mg] = existing

    # Clinical trial target genes (for Table S1 drug/biologic target specificity)
    clinical_genes = [
        "Nr3c1", "Pgr", "Esr1", "Ar", "Grin1", "Grin2a", "Grin2b", "Gria1", "Gria2",
        "Gabra1", "Gabra2", "Gabrb2", "Gabrg2", "Sv2a", "Scn1a", "Scn2a", "Scn3a", "Scn8a",
        "Scn9a", "Kcnq2", "Kcnq3", "Cacna1c", "Cacna1b", "Cacna2d1", "Hcn1",
        "Tlr4", "Tlr2", "Nlrp3", "Il1b", "Il1r1", "Il6", "Il6r", "Tnf", "Tnfrsf1a",
        "Ccr2", "Ccr5", "Cx3cr1", "Csf1r", "Cybb", "Nos1", "Nos2", "Nos3", "Ptgs2", "Ptgs1",
        "Hmox1", "Nfe2l2", "Pparg", "Sirt1", "Prkaa1", "Mtor", "Akt1", "Gsk3b",
        "Folh1", "Slc1a2", "Slc1a3", "Glul", "Gjb6", "Aqp4", "Kcnj10", "S100b", "Gfap",
        "Plin4", "Rnf112", "Abcc8", "Trpm4", "P2rx7", "P2ry12", "Adora1", "Adora2a",
        "Bdnf", "Ntrk2", "Ngf", "Igf1", "Igf1r", "Ghr", "Epor", "Vegfa", "Kdr", "Angpt1", "Tek",
        "Mmp9", "Mmp2", "Timp1", "C1qa", "C3", "C5", "C5ar1", "Serping1", "F2", "F10", "Plg", "Plat",
        "Drd2", "Drd1", "Slc6a3", "Slc6a4", "Slc6a2", "Htr1a", "Htr2a", "Adrb1", "Adrb2", "Adra2a",
        "Chrna7", "Chrm1", "Oprm1", "Oprk1", "Sigmar1", "Cnr1", "Cnr2", "Faah",
        "S1pr1", "S1pr5", "Itga4", "Cd68", "Trem2", "Tyrobp", "Ly86", "Lcn2", "Vim", "C3",
        "Camk2a", "Syn1", "Dlg4", "Rbfox3", "Snap25", "Syt1", "Slc17a7", "Gad1", "Gad2",
        "Ccdc103", "Alkbh5", "Canx", "Hspa5", "Ttr", "Folr1", "Prlr", "Foxj1",
        "Casp3", "Bax", "Bcl2", "Ripk1", "Ripk3", "Mlkl", "Gsdmd", "Parp1", "Ppia", "Ppif",
        "Ednrb", "Mapk14", "Hmgcr", "Pde5a", "Casp1", "Gclc", "Chka", "Pcyt1a", "Ache",
        "Trpv1", "Glp1r", "Bdkrb2", "Tacr1", "Ntrk1", "Pgrmc1", "Pgrmc2", "Hdac1",
        "Hdac2", "Abat", "Jak2", "Stat5b", "Ppp3ca",
    ]
    purity_genes = [g for lst in LINEAGE_MARKERS_MOUSE.values() for g in lst]
    alias_genes = [a for lst in GENE_ALIASES.values() for a in lst]

    mouse_set = sorted(set(cand_genes + clinical_genes + purity_genes + alias_genes))
    return cand_genes, mouse_set


def read_features_list(feat_path):
    """Read gene symbols from features.tsv.gz or genes.tsv.gz."""
    genes = []
    with gzip.open(feat_path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\r\n").split("\t")
            if len(parts) >= 2 and parts[1]:
                genes.append(parts[1].strip())
            else:
                genes.append(parts[0].strip())
    return genes


def parse_single_mtx_sample(task):
    """
    Worker function: read a single 10x/Drop-seq .mtx.gz + features.tsv.gz file,
    compute:
      1. Sample-level pseudobulk UMI counts and log2(CPM + 1) for target genes
      2. Cell-type lineage assignment (ASC, MG, ODC, OPC, NEU, END, PER, CPE_EPEN)
      3. Cell-type mean log1p(CP10K) expression for target genes + purity markers
    """
    sample_id = task["sample_id"]
    mtx_path = task["mtx_path"]
    feat_path = task["feat_path"]
    is_human = task.get("is_human", False)
    target_genes_mouse = task["target_genes_mouse"]
    gene_aliases = task.get("gene_aliases", GENE_ALIASES)

    genes = read_features_list(feat_path)
    n_genes = len(genes)

    # Map uppercase/mouse symbols to row indices (0-based)
    gene_upper_to_indices = {}
    for idx, g in enumerate(genes):
        gu = g.upper()
        if gu not in gene_upper_to_indices:
            gene_upper_to_indices[gu] = [idx]
        else:
            gene_upper_to_indices[gu].append(idx)

    # Read MTX header
    with gzip.open(mtx_path, "rt", encoding="utf-8", errors="replace") as f:
        skip = 0
        dims = None
        for i, line in enumerate(f):
            if not line.startswith("%"):
                dims = [int(x) for x in line.strip().split()]
                skip = i + 1
                break

    n_rows, n_cols, n_nnz = dims[0], dims[1], dims[2]
    df_coo = pd.read_csv(
        mtx_path,
        sep=r"\s+",
        skiprows=skip,
        names=["r", "c", "v"],
        dtype={"r": np.int32, "c": np.int32, "v": np.float32},
        engine="c",
    )

    mat = sparse.csr_matrix(
        (df_coo["v"].values, (df_coo["r"].values - 1, df_coo["c"].values - 1)),
        shape=(n_rows, n_cols),
        dtype=np.float32,
    )

    # Filter cells with >= 100 total UMIs
    col_sums = np.asarray(mat.sum(axis=0)).ravel()
    valid_cells = col_sums >= 100
    if valid_cells.sum() >= 20:
        mat = mat[:, valid_cells]
        col_sums = col_sums[valid_cells]
    n_valid_cells = mat.shape[1]

    # 1. Sample-level pseudobulk log2(CPM + 1)
    gene_sums = np.asarray(mat.sum(axis=1)).ravel()
    total_umis = float(gene_sums.sum()) if gene_sums.sum() > 0 else 1.0

    # Resolve each target mouse gene (handling aliases and human uppercase)
    resolved_rows = {}
    for mg in target_genes_mouse:
        candidates = gene_aliases.get(mg, [mg])
        matched_idx = []
        for cand in candidates:
            cu = cand.upper()
            if cu in gene_upper_to_indices:
                matched_idx.extend(gene_upper_to_indices[cu])
                break
        if matched_idx:
            resolved_rows[mg] = matched_idx

    pseudobulk_log2cpm = {}
    for mg, idxs in resolved_rows.items():
        umi_val = float(gene_sums[idxs].sum())
        cpm = umi_val / total_umis * 1e6
        pseudobulk_log2cpm[mg] = float(np.log2(cpm + 1.0))

    # 2. Cell-type lineage assignment on single cells via log1p(CP10K) of canonical markers
    inv_lib = 1e4 / np.maximum(col_sums, 1.0)
    lineage_dict = LINEAGE_MARKERS_HUMAN if is_human else LINEAGE_MARKERS_MOUSE
    lineage_names = list(lineage_dict.keys())
    lineage_scores = np.zeros((len(lineage_names), n_valid_cells), dtype=np.float32)

    for l_idx, l_name in enumerate(lineage_names):
        m_idxs = []
        for m_gene in lineage_dict[l_name]:
            mu = m_gene.upper()
            if mu in gene_upper_to_indices:
                m_idxs.extend(gene_upper_to_indices[mu])
        if m_idxs:
            sub = mat[m_idxs, :].toarray() * inv_lib[None, :]
            lineage_scores[l_idx, :] = np.log1p(sub).mean(axis=0)

    best_lineage = np.argmax(lineage_scores, axis=0)
    max_score = np.max(lineage_scores, axis=0)

    # Doublet & ambient-RNA exclusion for pure cell-type reference profiles (critical for snRNA-seq):
    # Ensure glial reference cells have primary marker > Snap25, and neuronal cells have Snap25 > Aqp4
    def get_gene_log1p(g_sym):
        idxs = []
        for cand in gene_aliases.get(g_sym, [g_sym]):
            cu = cand.upper()
            if cu in gene_upper_to_indices:
                idxs.extend(gene_upper_to_indices[cu])
                break
        if not idxs:
            return np.zeros(n_valid_cells, dtype=np.float32)
        sub = mat[idxs, :].toarray() * inv_lib[None, :]
        return np.log1p(sub).mean(axis=0)

    aqp4_vec = get_gene_log1p("Aqp4")
    hexb_vec = get_gene_log1p("Hexb")
    plp1_vec = get_gene_log1p("Plp1")
    snap25_vec = get_gene_log1p("Snap25")

    celltype_counts = {}
    celltype_gene_sums = {}
    all_needed_rows = sorted({i for idxs in resolved_rows.values() for i in idxs})
    row_to_pos = {r_i: pos for pos, r_i in enumerate(all_needed_rows)}

    for l_idx, l_name in enumerate(lineage_names):
        mask = (best_lineage == l_idx) & (max_score > 0)
        if l_name == "ASC":
            pure_mask = mask & (aqp4_vec > snap25_vec * 1.5)
            if pure_mask.sum() >= 5:
                mask = pure_mask
        elif l_name == "MG":
            pure_mask = mask & (hexb_vec > snap25_vec * 1.5)
            if pure_mask.sum() >= 5:
                mask = pure_mask
        elif l_name == "ODC":
            pure_mask = mask & (plp1_vec > snap25_vec * 1.5)
            if pure_mask.sum() >= 5:
                mask = pure_mask
        elif l_name == "NEU":
            pure_mask = mask & (snap25_vec > aqp4_vec * 1.5)
            if pure_mask.sum() >= 5:
                mask = pure_mask

        cnt = int(mask.sum())
        celltype_counts[l_name] = cnt
        if cnt > 0:
            sub_inv = inv_lib[mask]
            sub_mat = mat[all_needed_rows, :][:, mask].toarray() * sub_inv[None, :]
            sub_log = np.log1p(sub_mat).mean(axis=1)
            ct_means = {}
            for mg, idxs in resolved_rows.items():
                ct_means[mg] = float(np.mean([sub_log[row_to_pos[i]] for i in idxs]))
            celltype_gene_sums[l_name] = ct_means

    return {
        "sample_id": sample_id,
        "n_cells": n_valid_cells,
        "total_umis": total_umis,
        "pseudobulk_log2cpm": pseudobulk_log2cpm,
        "celltype_counts": celltype_counts,
        "celltype_means": celltype_gene_sums,
    }


def compute_yanai_tau_from_vector(vals):
    """Exact Yanai et al. (2005) tissue/cell-type specificity index tau."""
    arr = np.asarray(vals, dtype=np.float64)
    arr = np.maximum(arr, 0.0)
    n = len(arr)
    if n <= 1:
        return 0.0
    m = np.max(arr)
    if m <= 1e-12:
        return 0.0
    return float(np.sum(1.0 - (arr / m)) / (n - 1))


def verify_single_cell_purity_gate(cohort_name, ct_matrix_df):
    """
    Mandatory Single-Cell Input Purity Gate per 00_core_gates_and_prohibitions.md:
      - Astrocyte (ASC): Aqp4 / Snap25 >= 3
      - Microglia (MG): Hexb / Snap25 >= 3
      - Oligodendrocyte (ODC): Plp1 / Snap25 >= 3
      - Neuron (NEU): Snap25 / Aqp4 >= 3
    """
    eps = 1e-6
    asc_ratio = float((ct_matrix_df.loc["Aqp4", "ASC"] + eps) / (ct_matrix_df.loc["Snap25", "ASC"] + eps))
    mg_ratio = float((ct_matrix_df.loc["Hexb", "MG"] + eps) / (ct_matrix_df.loc["Snap25", "MG"] + eps))
    odc_ratio = float((ct_matrix_df.loc["Plp1", "ODC"] + eps) / (ct_matrix_df.loc["Snap25", "ODC"] + eps))
    neu_ratio = float((ct_matrix_df.loc["Snap25", "NEU"] + eps) / (ct_matrix_df.loc["Aqp4", "NEU"] + eps))

    print(
        f"  [PURITY GATE {cohort_name}] "
        f"ASC(Aqp4/Snap25)={asc_ratio:.2f}x | "
        f"MG(Hexb/Snap25)={mg_ratio:.2f}x | "
        f"ODC(Plp1/Snap25)={odc_ratio:.2f}x | "
        f"NEU(Snap25/Aqp4)={neu_ratio:.2f}x"
    )
    if min(asc_ratio, mg_ratio, odc_ratio, neu_ratio) < 3.0:
        raise RuntimeError(
            f"PURITY FAIL in {cohort_name}: ratios = ASC {asc_ratio:.2f}, MG {mg_ratio:.2f}, ODC {odc_ratio:.2f}, NEU {neu_ratio:.2f} (< 3.0)"
        )
    return {
        "ASC_Aqp4_vs_Snap25": round(asc_ratio, 3),
        "MG_Hexb_vs_Snap25": round(mg_ratio, 3),
        "ODC_Plp1_vs_Snap25": round(odc_ratio, 3),
        "NEU_Snap25_vs_Aqp4": round(neu_ratio, 3),
        "Status": "PASS (>= 3.0x)",
    }


def extract_gse180862(target_genes_mouse):
    """
    Process GSE180862 Hippocampus Drop-seq (29,013 cells across Sham, 24h TBI, 7d TBI
    and 26 official NeuronCellTypes) + Cortex Drop-seq + Cortex 24h HN.
    """
    print("\n=== [1/10] Extracting GSE180862 (Hippocampus 29,013 cells + Cortex) ===")
    meta_path = os.path.join(RAW_GEO_DIR, "GSE180862_DropSeq.Hippocampus.7days.24hrs.TBI.Sham.metaData.tsv.gz")
    feat_path = os.path.join(RAW_GEO_DIR, "GSE180862_DropSeq.Hippocampus.7days.24hrs.TBI.Sham.features.tsv.gz")
    mtx_path = os.path.join(RAW_GEO_DIR, "GSE180862_DropSeq.Hippocampus.7days.24hrs.TBI.Sham.digital_expression.mtx.gz")

    meta = pd.read_csv(meta_path, sep="\t", index_col=0)
    genes = read_features_list(feat_path)
    gene_upper_to_idx = {g.upper(): i for i, g in enumerate(genes)}

    with gzip.open(mtx_path, "rt") as f:
        for i, line in enumerate(f):
            if not line.startswith("%"):
                dims = [int(x) for x in line.strip().split()]
                skip = i + 1
                break

    df_coo = pd.read_csv(
        mtx_path,
        sep=r"\s+",
        skiprows=skip,
        names=["r", "c", "v"],
        dtype={"r": np.int32, "c": np.int32, "v": np.float32},
        engine="c",
    )
    mat = sparse.csr_matrix(
        (df_coo["v"].values, (df_coo["r"].values - 1, df_coo["c"].values - 1)),
        shape=(dims[0], dims[1]),
        dtype=np.float32,
    )

    col_sums = np.asarray(mat.sum(axis=0)).ravel()
    inv_lib = 1e4 / np.maximum(col_sums, 1.0)

    # Mandatory Purity Gate on official GSE180862 NeuronCellType annotations
    ct_col = meta["NeuronCellType"].astype(str).values
    neu_subtypes_180 = ["DG", "CA1d", "CA1v", "CA1i", "CA2", "CA3d", "CA3v", "SUB", "INT", "C-R", "NRGN", "LHX9", "NDNF", "RELN"]
    major_map = {
        "ASC": ct_col == "ASC",
        "MG": ct_col == "MG",
        "ODC": ct_col == "ODC",
        "NEU": np.isin(ct_col, neu_subtypes_180),
    }
    purity_rows = ["Aqp4", "Hexb", "Plp1", "Snap25"]
    p_idxs = [gene_upper_to_idx[g.upper()] for g in purity_rows]
    p_df = pd.DataFrame(index=purity_rows, columns=["ASC", "MG", "ODC", "NEU"], dtype=float)
    for m_name, mask in major_map.items():
        sub = mat[p_idxs, :][:, mask].toarray() * inv_lib[mask][None, :]
        p_df[m_name] = np.log1p(sub).mean(axis=1)
    purity_receipt = verify_single_cell_purity_gate("GSE180862_Hippocampus", p_df)

    # Compute exact single-cell Yanai tau across:
    # - 26 total cell types (t0 Sham, t1 24h TBI, t2 7d TBI, and pooled)
    # - 24 parenchymal cell types (excluding CPE and EPEN per Gate 1)
    all_cts_26 = sorted(meta["NeuronCellType"].unique())
    paren_cts_24 = [c for c in all_cts_26 if c not in ("CPE", "EPEN")]

    tp_col_name = "Timepoint" if "Timepoint" in meta.columns else "TimePoint"
    cond_col_name = "Condition" if "Condition" in meta.columns else "Tissue"
    tp_masks = {
        "All": np.ones(len(meta), dtype=bool),
        "t0_Sham": meta[cond_col_name].astype(str).values == "Sham",
        "t1_24h": (meta[cond_col_name].astype(str).values == "TBI") & (meta[tp_col_name].astype(str).values == "24hrs"),
        "t2_7d": (meta[cond_col_name].astype(str).values == "TBI") & (meta[tp_col_name].astype(str).values == "7days"),
    }

    # Resolve row indices for all target_genes_mouse
    resolved_idx = {}
    for mg in target_genes_mouse:
        for cand in GENE_ALIASES.get(mg, [mg]):
            if cand.upper() in gene_upper_to_idx:
                resolved_idx[mg] = gene_upper_to_idx[cand.upper()]
                break

    needed_rows = sorted(set(resolved_idx.values()))
    row_to_pos = {r: pos for pos, r in enumerate(needed_rows)}
    sub_mat_needed = mat[needed_rows, :]

    # Compute cell-type mean log1p(CP10K) for each timepoint and cell type
    ct_time_means = {}
    for tp_name, tp_mask in tp_masks.items():
        ct_mat = np.zeros((len(needed_rows), len(all_cts_26)), dtype=np.float64)
        for c_i, ct in enumerate(all_cts_26):
            m = tp_mask & (ct_col == ct)
            if m.sum() > 0:
                arr = sub_mat_needed[:, m].toarray() * inv_lib[m][None, :]
                ct_mat[:, c_i] = np.log1p(arr).mean(axis=1)
        ct_time_means[tp_name] = pd.DataFrame(ct_mat, index=needed_rows, columns=all_cts_26)

    neu_cols_present = [c for c in neu_subtypes_180 if c in all_cts_26]
    # Build comprehensive real tau trajectory table for GSE180862
    tau_records = []
    for mg in target_genes_mouse:
        if mg not in resolved_idx:
            continue
        r_idx = resolved_idx[mg]
        rec = {"Gene_Symbol": mg, "RefSeq_Matched_Symbol": genes[r_idx]}
        for tp_name in ["All", "t0_Sham", "t1_24h", "t2_7d"]:
            vec_26 = ct_time_means[tp_name].loc[r_idx, all_cts_26].values
            vec_24 = ct_time_means[tp_name].loc[r_idx, paren_cts_24].values
            rec[f"Tau26_{tp_name}"] = round(compute_yanai_tau_from_vector(vec_26), 4)
            rec[f"Tau24_{tp_name}"] = round(compute_yanai_tau_from_vector(vec_24), 4)
            # Dominant cell type in 26 and 24
            rec[f"TopCT26_{tp_name}"] = all_cts_26[int(np.argmax(vec_26))] if np.max(vec_26) > 0 else "None"
            rec[f"TopCT24_{tp_name}"] = paren_cts_24[int(np.argmax(vec_24))] if np.max(vec_24) > 0 else "None"
            # Major lineage expression at each timepoint
            rec[f"Expr_MG_{tp_name}"] = round(float(ct_time_means[tp_name].loc[r_idx, "MG"]), 5)
            rec[f"Expr_ASC_{tp_name}"] = round(float(ct_time_means[tp_name].loc[r_idx, "ASC"]), 5)
            rec[f"Expr_NEU_{tp_name}"] = round(float(ct_time_means[tp_name].loc[r_idx, neu_cols_present].mean()), 5)
            rec[f"Expr_CPE_EPEN_{tp_name}"] = round(float(ct_time_means[tp_name].loc[r_idx, ["CPE", "EPEN"]].max()), 5)
        tau_records.append(rec)

    df_tau = pd.DataFrame(tau_records)
    df_tau.to_csv(os.path.join(RAW_GEO_DIR, "GSE180862_hippocampus_real_tau_trajectories.csv"), index=False)

    # Also compute sample-level pseudobulk log2(CPM+1) across the 12 biological replicates in Hippocampus Drop-seq
    samples_hip = sorted(meta["Sample"].unique())
    pb_records = []
    for s_name in samples_hip:
        s_mask = meta["Sample"].astype(str).values == s_name
        tp = str(meta.loc[s_mask, tp_col_name].iloc[0])
        tis = str(meta.loc[s_mask, cond_col_name].iloc[0])
        g_sums = np.asarray(mat[:, s_mask].sum(axis=1)).ravel()
        tot = float(g_sums.sum()) if g_sums.sum() > 0 else 1.0
        row_dict = {
            "Sample_ID": f"Hip_{s_name}",
            "Condition": "Sham" if tis == "Sham" else f"TBI_{tp}",
            "Binary_Label": 0 if tis == "Sham" else 1,
            "Timepoint": tp,
            "Region": "Hippocampus",
            "N_Cells": int(s_mask.sum()),
        }
        for mg, r_idx in resolved_idx.items():
            row_dict[mg] = round(float(np.log2(g_sums[r_idx] / tot * 1e6 + 1.0)), 5)
        pb_records.append(row_dict)

    # Also check Cortex 24hrs HN (Humanin neuroprotective treatment vs TBI vs Sham) if available
    hn_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE180862")
    hn_meta_p = os.path.join(hn_dir, "GSE180862_DropSeq.Cortex.24hrs.TBI.HN.metaData.tsv.gz")
    hn_feat_p = os.path.join(hn_dir, "GSE180862_DropSeq.Cortex.24hrs.TBI.HN.features.tsv.gz")
    hn_mtx_p = os.path.join(hn_dir, "GSE180862_DropSeq.Cortex.24hrs.TBI.HN.digital_expression.mtx.gz")
    if os.path.exists(hn_mtx_p):
        hn_meta = pd.read_csv(hn_meta_p, sep="\t", index_col=0)
        hn_genes = read_features_list(hn_feat_p)
        hn_g2i = {g.upper(): i for i, g in enumerate(hn_genes)}
        with gzip.open(hn_mtx_p, "rt") as f:
            for i, line in enumerate(f):
                if not line.startswith("%"):
                    hn_dims = [int(x) for x in line.strip().split()]
                    hn_skip = i + 1
                    break
        hn_coo = pd.read_csv(
            hn_mtx_p, sep=r"\s+", skiprows=hn_skip, names=["r", "c", "v"],
            dtype={"r": np.int32, "c": np.int32, "v": np.float32}, engine="c"
        )
        hn_mat = sparse.csr_matrix(
            (hn_coo["v"].values, (hn_coo["r"].values - 1, hn_coo["c"].values - 1)),
            shape=(hn_dims[0], hn_dims[1]), dtype=np.float32
        )
        for s_name in sorted(hn_meta["Sample"].unique()):
            s_mask = hn_meta["Sample"].astype(str).values == s_name
            tis = str(hn_meta.loc[s_mask, "Tissue"].iloc[0]) if "Tissue" in hn_meta.columns else s_name
            g_sums = np.asarray(hn_mat[:, s_mask].sum(axis=1)).ravel()
            tot = float(g_sums.sum()) if g_sums.sum() > 0 else 1.0
            cond = "Sham" if "Sham" in s_name else ("TBI_HN_24h" if "HN" in s_name else "TBI_24hrs")
            row_dict = {
                "Sample_ID": f"Ctx_{s_name}",
                "Condition": cond,
                "Binary_Label": 0 if "Sham" in s_name else 1,
                "Timepoint": "24hrs",
                "Region": "Cortex",
                "N_Cells": int(s_mask.sum()),
            }
            for mg in target_genes_mouse:
                for cand in GENE_ALIASES.get(mg, [mg]):
                    if cand.upper() in hn_g2i:
                        row_dict[mg] = round(float(np.log2(g_sums[hn_g2i[cand.upper()]] / tot * 1e6 + 1.0)), 5)
                        break
            pb_records.append(row_dict)

    df_pb = pd.DataFrame(pb_records)
    df_pb.to_csv(os.path.join(RAW_GEO_DIR, "GSE180862_sample_pseudobulk_log2cpm.csv"), index=False)
    print(f"  Saved GSE180862: {len(df_tau)} genes real tau trajectories, {len(df_pb)} sample pseudobulks.")
    return {
        "Cohort": "GSE180862",
        "N_Samples": len(df_pb),
        "N_Cells_Hippocampus": int(mat.shape[1]),
        "Purity_Gate": purity_receipt,
    }


def run_parallel_mtx_cohort(cohort_name, tasks, sample_meta_map, target_genes_mouse, is_human=False):
    """Run parallel MTX extraction across all samples in a single-cell cohort, verify Purity Gate, and save CSVs."""
    pb_out_path = os.path.join(RAW_GEO_DIR, f"{cohort_name}_sample_pseudobulk_log2cpm.csv")
    ct_out_path = os.path.join(RAW_GEO_DIR, f"{cohort_name}_celltype_tau_summary.csv")
    if os.path.exists(pb_out_path) and os.path.exists(ct_out_path):
        df_pb_cached = pd.read_csv(pb_out_path)
        df_ct_cached = pd.read_csv(ct_out_path).set_index("Gene_Symbol")
        if len(df_pb_cached) == len(tasks) and len(df_ct_cached) >= 400:
            ct_check = pd.DataFrame({
                "ASC": df_ct_cached["Expr_ASC"],
                "MG": df_ct_cached["Expr_MG"],
                "ODC": df_ct_cached["Expr_ODC"],
                "NEU": df_ct_cached["Expr_NEU"],
            })
            purity_receipt = verify_single_cell_purity_gate(f"{cohort_name} (Cached)", ct_check)
            return {
                "Cohort": cohort_name,
                "N_Samples": int(len(df_pb_cached)),
                "N_Cells": int(df_pb_cached["N_Cells"].sum()),
                "Purity_Gate": purity_receipt,
            }

    t0 = time.time()
    print(f"\n=== Extracting {cohort_name} ({len(tasks)} single-cell MTX samples) ===")
    for t in tasks:
        t["target_genes_mouse"] = target_genes_mouse
        t["is_human"] = is_human
        t["gene_aliases"] = GENE_ALIASES

    results = []
    with ProcessPoolExecutor(max_workers=min(8, len(tasks))) as ex:
        futs = {ex.submit(parse_single_mtx_sample, t): t["sample_id"] for t in tasks}
        for fut in as_completed(futs):
            res = fut.result()
            results.append(res)

    results.sort(key=lambda x: x["sample_id"])
    total_cells = sum(r["n_cells"] for r in results)

    # 1. Build sample-level pseudobulk table
    pb_rows = []
    for r in results:
        sid = r["sample_id"]
        meta_info = sample_meta_map[sid]
        row = {
            "Sample_ID": sid,
            "Condition": meta_info["Condition"],
            "Binary_Label": meta_info["Binary_Label"],
            "Timepoint": meta_info.get("Timepoint", "NA"),
            "Region": meta_info.get("Region", "CNS"),
            "N_Cells": r["n_cells"],
        }
        row.update({k: round(v, 5) for k, v in r["pseudobulk_log2cpm"].items()})
        pb_rows.append(row)

    df_pb = pd.DataFrame(pb_rows)
    df_pb.to_csv(os.path.join(RAW_GEO_DIR, f"{cohort_name}_sample_pseudobulk_log2cpm.csv"), index=False)

    # 2. Aggregate cell-type expression weighted by cell count across all samples (and by condition)
    lineages = ["ASC", "MG", "ODC", "OPC", "NEU", "END", "PER", "CPE_EPEN"]
    paren_lineages = ["ASC", "MG", "ODC", "OPC", "NEU", "END", "PER"]

    ct_df = pd.DataFrame(0.0, index=target_genes_mouse, columns=lineages)
    ct_weights = {l: 0 for l in lineages}
    for r in results:
        for l in lineages:
            cnt = r["celltype_counts"].get(l, 0)
            if cnt > 0 and l in r["celltype_means"]:
                ct_weights[l] += cnt
                for mg, val in r["celltype_means"][l].items():
                    ct_df.loc[mg, l] += val * cnt

    for l in lineages:
        if ct_weights[l] > 0:
            ct_df[l] /= float(ct_weights[l])

    purity_receipt = verify_single_cell_purity_gate(cohort_name, ct_df)

    # Compute empirical single-cell Yanai tau across parenchymal lineages in this cohort
    tau_rows = []
    for mg in target_genes_mouse:
        vec_all = ct_df.loc[mg, lineages].values
        vec_paren = ct_df.loc[mg, paren_lineages].values
        tau_rows.append({
            "Gene_Symbol": mg,
            f"{cohort_name}_Tau_AllLineages": round(compute_yanai_tau_from_vector(vec_all), 4),
            f"{cohort_name}_Tau_Parenchymal": round(compute_yanai_tau_from_vector(vec_paren), 4),
            f"{cohort_name}_TopLineage": paren_lineages[int(np.argmax(vec_paren))] if np.max(vec_paren) > 0 else "None",
            "Expr_ASC": round(float(ct_df.loc[mg, "ASC"]), 5),
            "Expr_MG": round(float(ct_df.loc[mg, "MG"]), 5),
            "Expr_ODC": round(float(ct_df.loc[mg, "ODC"]), 5),
            "Expr_NEU": round(float(ct_df.loc[mg, "NEU"]), 5),
            "Expr_CPE_EPEN": round(float(ct_df.loc[mg, "CPE_EPEN"]), 5),
        })
    df_ct_tau = pd.DataFrame(tau_rows)
    df_ct_tau.to_csv(os.path.join(RAW_GEO_DIR, f"{cohort_name}_celltype_tau_summary.csv"), index=False)

    print(f"  Completed {cohort_name} in {time.time()-t0:.1f}s: {len(results)} samples, {total_cells:,} cells.")
    return {
        "Cohort": cohort_name,
        "N_Samples": len(results),
        "N_Cells": total_cells,
        "CellType_Counts": ct_weights,
        "Purity_Gate": purity_receipt,
    }


def build_all_cohort_tasks(target_genes_mouse):
    receipts = []

    # 1. GSE180862
    receipts.append(extract_gse180862(target_genes_mouse))

    # 2. GSE269748 (36 GSM samples in _raw_tar_extract)
    gse269_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE269748", "_raw_tar_extract")
    # Parse official titles from GSE269748_series_matrix.txt.gz
    gse269_titles = {}
    with gzip.open(os.path.join(RAW_GEO_DIR, "GSE269748_series_matrix.txt.gz"), "rt", encoding="utf-8") as f:
        titles, accs = [], []
        for line in f:
            if line.startswith("!Sample_title"):
                titles = [x.strip('"') for x in line.strip().split("\t")[1:]]
            elif line.startswith("!Sample_geo_accession"):
                accs = [x.strip('"') for x in line.strip().split("\t")[1:]]
        for a, t in zip(accs, titles):
            gse269_titles[a] = t

    tasks_269, meta_269 = [], {}
    for mtx_p in sorted(glob.glob(os.path.join(gse269_dir, "*_matrix.mtx.gz"))):
        bn = os.path.basename(mtx_p)
        gsm = bn.split("_")[0]
        feat_p = mtx_p.replace("_matrix.mtx.gz", "_features.tsv.gz")
        title = gse269_titles.get(gsm, bn)
        is_naive = ("Naïve" in title) or ("Naive" in title)
        if "6 month" in title:
            tp = "6m"
        elif "7 day" in title:
            tp = "7d"
        else:
            tp = "24h"
        cond = "Naive" if is_naive else ("rCHI_24h" if "repetitive" in title else ("CCI_HS_24h" if "HS" in title else f"CCI_{tp}"))
        tasks_269.append({"sample_id": gsm, "mtx_path": mtx_p, "feat_path": feat_p})
        meta_269[gsm] = {"Condition": cond, "Binary_Label": 0 if is_naive else 1, "Timepoint": tp, "Region": "Cortex_Hippocampus"}
    receipts.append(run_parallel_mtx_cohort("GSE269748", tasks_269, meta_269, target_genes_mouse, is_human=False))

    # 3. GSE247339 (41 GSM samples across Sham, TBI+Veh, TBI+T4 at 24h, 7d, 21d in Hippocampus & Cortex)
    gse247_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE247339")
    tasks_247, meta_247 = [], {}
    for mtx_p in sorted(glob.glob(os.path.join(gse247_dir, "*.matrix.mtx.gz"))):
        bn = os.path.basename(mtx_p)
        gsm = bn.split("_")[0]
        feat_p = mtx_p.replace(".matrix.mtx.gz", ".genes.tsv.gz")
        region = "Hippocampus" if ("_h" in bn or "Hipp" in bn) else "Cortex"
        tp = "24h" if "24" in bn else ("7d" if "7" in bn else "21d")
        if "Sham" in bn or "sham" in bn:
            cond = "Sham"
            lbl = 0
        elif "T4" in bn:
            cond = f"TBI_T4_{tp}"
            lbl = 2  # Treated arm (0=Sham, 1=Untreated TBI, 2=TBI+Early T4 Rx)
        else:
            cond = f"TBI_Veh_{tp}"
            lbl = 1
        tasks_247.append({"sample_id": gsm, "mtx_path": mtx_p, "feat_path": feat_p})
        meta_247[gsm] = {"Condition": cond, "Binary_Label": lbl, "Timepoint": tp, "Region": region}
    receipts.append(run_parallel_mtx_cohort("GSE247339", tasks_247, meta_247, target_genes_mouse, is_human=False))

    # 4. GSE277487 (12 GSM samples across Ctrl, 6h, 2d, 4d)
    gse277_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE277487")
    tasks_277, meta_277 = [], {}
    for mtx_p in sorted(glob.glob(os.path.join(gse277_dir, "*_matrix.mtx.gz"))):
        bn = os.path.basename(mtx_p)
        gsm = bn.split("_")[0]
        feat_p = mtx_p.replace("_matrix.mtx.gz", "_features.tsv.gz")
        if "Ctrl" in bn:
            cond, lbl, tp = "Control", 0, "0h"
        elif "group1" in bn:
            cond, lbl, tp = "STBI_6h", 1, "6h"
        elif "group2" in bn:
            cond, lbl, tp = "STBI_2d", 1, "2d"
        else:
            cond, lbl, tp = "STBI_4d", 1, "4d"
        tasks_277.append({"sample_id": gsm, "mtx_path": mtx_p, "feat_path": feat_p})
        meta_277[gsm] = {"Condition": cond, "Binary_Label": lbl, "Timepoint": tp, "Region": "Cortex"}
    receipts.append(run_parallel_mtx_cohort("GSE277487", tasks_277, meta_277, target_genes_mouse, is_human=False))

    # 5. GSE226207 (15 GSM samples across Intact, 3dpi/5dpi CTRL, 3dpi/5dpi INH)
    gse226_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE226207")
    gse226_titles = {}
    for fn in ["GSE226207-GPL21103_series_matrix.txt.gz", "GSE226207-GPL24247_series_matrix.txt.gz"]:
        with gzip.open(os.path.join(RAW_GEO_DIR, fn), "rt", encoding="utf-8") as f:
            titles, accs = [], []
            for line in f:
                if line.startswith("!Sample_title"):
                    titles = [x.strip('"') for x in line.strip().split("\t")[1:]]
                elif line.startswith("!Sample_geo_accession"):
                    accs = [x.strip('"') for x in line.strip().split("\t")[1:]]
            for a, t in zip(accs, titles):
                gse226_titles[a] = t

    tasks_226, meta_226 = [], {}
    for mtx_p in sorted(glob.glob(os.path.join(gse226_dir, "*_matrix.mtx.gz"))):
        bn = os.path.basename(mtx_p)
        gsm = bn.split("_")[0]
        feat_p = mtx_p.replace("_matrix.mtx.gz", "_features.tsv.gz")
        title = gse226_titles.get(gsm, bn)
        if "Intact" in title:
            cond, lbl, tp = "Intact", 0, "0d"
        elif "3dpi_CTRL" in title:
            cond, lbl, tp = "TBI_CTRL_3dpi", 1, "3d"
        elif "5dpi_CTRL" in title:
            cond, lbl, tp = "TBI_CTRL_5dpi", 1, "5d"
        elif "3dpi_INH" in title:
            cond, lbl, tp = "TBI_INH_3dpi", 2, "3d"
        else:
            cond, lbl, tp = "TBI_INH_5dpi", 2, "5d"
        tasks_226.append({"sample_id": gsm, "mtx_path": mtx_p, "feat_path": feat_p})
        meta_226[gsm] = {"Condition": cond, "Binary_Label": lbl, "Timepoint": tp, "Region": "Cortex"}
    receipts.append(run_parallel_mtx_cohort("GSE226207", tasks_226, meta_226, target_genes_mouse, is_human=False))

    # 6. GSE302863 (5 GSM samples across Sham, TBI 1d, 3d, 7d, 14d)
    gse302_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE302863")
    tasks_302, meta_302 = [], {}
    for mtx_p in sorted(glob.glob(os.path.join(gse302_dir, "*_matrix.mtx.gz"))):
        bn = os.path.basename(mtx_p)
        gsm = bn.split("_")[0]
        feat_p = mtx_p.replace("_matrix.mtx.gz", "_genes.tsv.gz")
        if "sham" in bn.lower():
            cond, lbl, tp = "Sham", 0, "0d"
        else:
            tp = bn.split("_")[1].replace("TBI", "") + "d"
            cond, lbl = f"TBI_{tp}", 1
        tasks_302.append({"sample_id": gsm, "mtx_path": mtx_p, "feat_path": feat_p})
        meta_302[gsm] = {"Condition": cond, "Binary_Label": lbl, "Timepoint": tp, "Region": "Cortex_Hippocampus"}
    receipts.append(run_parallel_mtx_cohort("GSE302863", tasks_302, meta_302, target_genes_mouse, is_human=False))

    # 7. GSE209552 (17 human acute severe TBI vs Control snRNA-seq samples)
    gse209_dir = os.path.join(EXTERNAL_RAW_BASE, "GSE209552", "extracted_all")
    gse209_hours = {
        "GSM6376803": ("Control", 0, "0h"),
        "GSM6376804": ("Control", 0, "0h"),
        "GSM6376805": ("Control", 0, "0h"),
        "GSM6376806": ("Control", 0, "0h"),
        "GSM6376807": ("Control", 0, "0h"),
        "GSM6376811": ("TBI_Acute_4h", 1, "4h"),
        "GSM6376812": ("TBI_Acute_9h", 1, "9h"),
        "GSM6376813": ("TBI_Subacute_84h", 1, "84h"),
        "GSM6376814": ("TBI_Subacute_180h", 1, "180h"),
        "GSM6376815": ("TBI_Acute_24h", 1, "24h"),
        "GSM6376816": ("TBI_Subacute_42h", 1, "42h"),
        "GSM6376817": ("TBI_Subacute_57h", 1, "57h"),
        "GSM6376818": ("TBI_Subacute_192h", 1, "192h"),
        "GSM6376819": ("TBI_Subacute_106h", 1, "106h"),
        "GSM6376820": ("TBI_Acute_9h", 1, "9h"),
        "GSM6376821": ("TBI_Acute_4h", 1, "4h"),
        "GSM6376822": ("TBI_Acute_4h", 1, "4h"),
    }
    tasks_209, meta_209 = [], {}
    for mtx_p in sorted(glob.glob(os.path.join(gse209_dir, "*_matrix.mtx.gz"))):
        bn = os.path.basename(mtx_p)
        gsm = bn.split("_")[0]
        feat_p = mtx_p.replace("_matrix.mtx.gz", "_features.tsv.gz")
        cond, lbl, tp = gse209_hours[gsm]
        tasks_209.append({"sample_id": gsm, "mtx_path": mtx_p, "feat_path": feat_p})
        meta_209[gsm] = {"Condition": cond, "Binary_Label": lbl, "Timepoint": tp, "Region": "Human_Cortex"}
    receipts.append(run_parallel_mtx_cohort("GSE209552", tasks_209, meta_209, target_genes_mouse, is_human=True))

    # 8. GSE319769 (36 hippocampal RNA-seq samples across Day 3, Day 7, Day 14 KA vs Saline)
    print("\n=== [8/10] Extracting GSE319769 (36 Hippocampal Bulk RNA-seq Samples) ===")
    df_319 = pd.read_csv(os.path.join(RAW_GEO_DIR, "GSE319769_raw_counts.txt.gz"), sep="\t", index_col=0)
    sample_cols_319 = [c for c in df_319.columns if c.startswith("iaka") or c.startswith("iasl")]
    g2i_319 = {str(g).upper(): i for i, g in enumerate(df_319.index.values)}
    counts_319 = df_319[sample_cols_319].values.astype(np.float64)
    col_sums_319 = np.maximum(counts_319.sum(axis=0), 1.0)
    log2cpm_319 = np.log2(counts_319 / col_sums_319[None, :] * 1e6 + 1.0)

    rows_319 = []
    for s_idx, s_name in enumerate(sample_cols_319):
        is_ka = s_name.startswith("iaka")
        tp_m = re.search(r"ia(?:ka|sl)(\d+)_", s_name)
        tp = f"D{tp_m.group(1)}" if tp_m else "NA"
        row = {
            "Sample_ID": s_name,
            "Condition": f"KA_{tp}" if is_ka else f"Saline_{tp}",
            "Binary_Label": 1 if is_ka else 0,
            "Timepoint": tp,
            "Region": "Hippocampus",
        }
        for mg in target_genes_mouse:
            for cand in GENE_ALIASES.get(mg, [mg]):
                if cand.upper() in g2i_319:
                    row[mg] = round(float(log2cpm_319[g2i_319[cand.upper()], s_idx]), 5)
                    break
        rows_319.append(row)
    pd.DataFrame(rows_319).to_csv(os.path.join(RAW_GEO_DIR, "GSE319769_sample_log2cpm.csv"), index=False)
    receipts.append({"Cohort": "GSE319769", "N_Samples": len(rows_319), "Type": "Bulk_RNAseq_Hippocampus"})

    # 9. GSE330624 (32 FANS-sorted NeuN+ Neuron and NeuN- Glia hippocampal RNA-seq samples)
    print("\n=== [9/10] Extracting GSE330624 (32 FANS NeuN+/NeuN- Hippocampal Samples) ===")
    df_330 = pd.read_csv(os.path.join(RAW_GEO_DIR, "GSE330624_counts_with_symbol.csv"))
    samp_330 = pd.read_csv(os.path.join(RAW_GEO_DIR, "GSE330624_samples.csv"))
    sample_cols_330 = samp_330["Sample"].tolist()
    counts_330 = df_330[sample_cols_330].values.astype(np.float64)
    col_sums_330 = np.maximum(counts_330.sum(axis=0), 1.0)
    log2cpm_330 = np.log2(counts_330 / col_sums_330[None, :] * 1e6 + 1.0)

    g2i_330 = {}
    for i, sym in enumerate(df_330["Symbol"].astype(str).values):
        su = sym.upper()
        if su not in g2i_330:
            g2i_330[su] = i

    rows_330 = []
    for s_idx, s_row in samp_330.iterrows():
        s_name = s_row["Sample"]
        is_ka = s_row["Treatment"] == "KA"
        tp = s_row["Timepoint"]
        tis = s_row["Tissue"]  # Neuron or Glia
        row = {
            "Sample_ID": s_name,
            "Condition": f"{s_row['Treatment']}_{tp}_{tis}",
            "Binary_Label": 1 if is_ka else 0,
            "Timepoint": tp,
            "Fraction": tis,
            "Region": "Hippocampus",
        }
        for mg in target_genes_mouse:
            for cand in GENE_ALIASES.get(mg, [mg]):
                if cand.upper() in g2i_330:
                    row[mg] = round(float(log2cpm_330[g2i_330[cand.upper()], s_idx]), 5)
                    break
        rows_330.append(row)
    pd.DataFrame(rows_330).to_csv(os.path.join(RAW_GEO_DIR, "GSE330624_sample_log2cpm.csv"), index=False)
    receipts.append({"Cohort": "GSE330624", "N_Samples": len(rows_330), "Type": "FANS_NeuN_Hippocampus"})

    # 10. GSE63808 (129 Official NCBI GEO Human Surgical Hippocampus Samples GSM1565578-GSM1565706)
    print("\n=== [10/10] Extracting GSE63808 (129 Official NCBI GEO Human Hippocampal Biopsies) ===")
    adf_path = os.path.join(RAW_GEO_DIR, "A-MEXP-1171.adf.txt")
    probe_to_gene = {}
    with open(adf_path, "r", encoding="utf-8", errors="ignore") as f:
        hdr = None
        i_name, i_hugo = 0, 5
        for line in f:
            if line.startswith("Block Column\t"):
                hdr = line.rstrip("\r\n").split("\t")
                i_name = hdr.index("Reporter Name")
                i_hugo = hdr.index("Reporter Database Entry[hugo]")
                continue
            if hdr:
                parts = line.rstrip("\r\n").split("\t")
                if len(parts) > max(i_name, i_hugo) and parts[i_name].startswith("ILMN_"):
                    hugo = parts[i_hugo].strip().upper()
                    if hugo:
                        probe_to_gene[parts[i_name].strip()] = hugo

    sm_path = os.path.join(RAW_GEO_DIR, "GSE63808_series_matrix.txt.gz")
    titles_638, accs_638 = [], []
    probe_ids_638, probe_rows_638 = [], []
    with gzip.open(sm_path, "rt", encoding="utf-8", errors="ignore") as f:
        in_table = False
        for line in f:
            if line.startswith("!Sample_title\t"):
                titles_638 = [x.strip('"') for x in line.rstrip("\r\n").split("\t")[1:]]
            elif line.startswith("!Sample_geo_accession\t"):
                accs_638 = [x.strip('"') for x in line.rstrip("\r\n").split("\t")[1:]]
            elif line.startswith("!series_matrix_table_begin"):
                in_table = True
                _ = next(f)
                continue
            elif line.startswith("!series_matrix_table_end"):
                break
            elif in_table:
                parts = line.rstrip("\r\n").split("\t")
                pid = parts[0].strip('"')
                if pid in probe_to_gene:
                    try:
                        vals = [float(x) for x in parts[1:]]
                        probe_ids_638.append(pid)
                        probe_rows_638.append(vals)
                    except ValueError:
                        pass

    df_probes_638 = pd.DataFrame(probe_rows_638, index=probe_ids_638, columns=accs_638)
    df_probes_638["Gene_Symbol"] = [probe_to_gene[p] for p in probe_ids_638]
    df_probes_638["_mean"] = df_probes_638[accs_638].mean(axis=1)
    # Select highest-expressed representative probe per HUGO symbol (matching 13_ml_funnel_and_human_conservation.py)
    df_638_genes = (
        df_probes_638.sort_values("_mean", ascending=False)
        .drop_duplicates(subset=["Gene_Symbol"], keep="first")
        .set_index("Gene_Symbol")[accs_638]
    )

    # Exact Glial UP (13 detected genes) and Neuronal DN (12 detected genes) panels from 13_ml_funnel_and_human_conservation.py
    glia_panel = [g for g in ["TLR4", "RELB", "TNFAIP3", "C3AR1", "C5AR1", "C1R", "LGALS1", "SOCS3", "KIAA1881", "FOLH1", "NTRK2", "HSPA5", "PDLIM1", "TLE3"] if g in df_638_genes.index and g != "FOLH1"]
    neu_panel = [g for g in ["ZNF179", "SCN3B", "KCNC3", "KCNJ6", "RYR2", "GRIK2", "C1QL2", "GRIN2A", "CAMK2B", "ELK1", "SYT7", "DBN1"] if g in df_638_genes.index]

    def row_zscore(sub_df):
        m = sub_df.mean(axis=1)
        s = sub_df.std(axis=1) + 1e-9
        return sub_df.sub(m, axis=0).div(s, axis=0)

    glia_z = row_zscore(df_638_genes.loc[glia_panel]).mean(axis=0)
    neu_z = row_zscore(df_638_genes.loc[neu_panel]).mean(axis=0)
    q75 = float(np.percentile(glia_z.values, 75.0))
    q25 = float(np.percentile(neu_z.values, 25.0))

    rows_638 = []
    for s_idx, gsm in enumerate(accs_638):
        gz = float(glia_z[gsm])
        nz = float(neu_z[gsm])
        row = {
            "Patient_ID": gsm,
            "Sample_Title": titles_638[s_idx],
            "Glial_Neuroimmune_UP_Score": round(gz, 6),
            "Neuronal_Channel_Synaptic_DN_Score": round(nz, 6),
            "Glia_Activation_Z": round(gz, 6),
            "Neuronal_Gate_Z": round(nz, 6),
            "High_Glia_Threshold": round(q75, 5),
            "Neuronal_Collapse_Threshold": round(q25, 5),
            "Binary_Label": 1 if gz >= q75 else 0,
            "Collapsed_Label": 1 if nz <= q25 else 0,
        }
        for mg in target_genes_mouse:
            for cand in GENE_ALIASES.get(mg, [mg]):
                cu = cand.upper()
                if cu in df_638_genes.index:
                    row[mg] = round(float(df_638_genes.loc[cu, gsm]), 5)
                    break
        rows_638.append(row)

    df_638_out = pd.DataFrame(rows_638)
    df_638_out.to_csv(os.path.join(RAW_GEO_DIR, "GSE63808_official_129samples_scores_and_targets.csv"), index=False)
    df_638_out[["Patient_ID", "Sample_Title", "Glial_Neuroimmune_UP_Score", "Neuronal_Channel_Synaptic_DN_Score", "Glia_Activation_Z", "Neuronal_Gate_Z", "High_Glia_Threshold", "Neuronal_Collapse_Threshold"]].to_csv(
        os.path.join(TABLES_DIR, "GSE63808_human_129patients_glia_vs_neuron_scores.csv"), index=False
    )
    df_638_out[["Patient_ID", "Sample_Title", "Glial_Neuroimmune_UP_Score", "Neuronal_Channel_Synaptic_DN_Score", "Glia_Activation_Z", "Neuronal_Gate_Z", "High_Glia_Threshold", "Neuronal_Collapse_Threshold"]].to_csv(
        os.path.join(BASE_DIR, "data", "GSE63808_human_129patients_glia_vs_neuron_scores.csv"), index=False
    )
    receipts.append({"Cohort": "GSE63808", "N_Samples": len(rows_638), "Type": "Human_Surgical_Hippocampus_Microarray"})

    with open(os.path.join(RAW_GEO_DIR, "MultiCohort_10GSE_Purity_and_Sample_Audit_Receipt.json"), "w", encoding="utf-8") as f:
        json.dump(receipts, f, indent=2, ensure_ascii=False)
    print("\n✅ All 10 Raw GEO Cohorts Extracted and Verified Successfully!")
    return receipts


@retry_limit(2)
def main():
    pass_gate(SCRIPT_DIR)
    gate(__file__)
    cand_genes, target_genes_mouse = canary_gate(
        lambda: get_target_gene_universe(),
        description="Load 133 candidate + clinical trial + purity marker gene universe",
        min_output_size=2,
    )
    print(f"Target gene universe size: {len(target_genes_mouse)} mouse/human ortholog symbols ({len(cand_genes)} Phase-1 candidates)")
    build_all_cohort_tasks(target_genes_mouse)


if __name__ == "__main__":
    main()
