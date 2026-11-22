# NeuroImmune-Virtual-Biotech (`v2.0`)

Source code, figure source tables, data provenance manifests, and audit receipts accompanying the manuscript:

> **Dynamic cellular specificity predicts inflammatory lock-in and clinical translation in acute brain injury**

This repository accompanies the manuscript submission (mirroring **Additional file 1** source tables and **Additional file 3** `Additional_file_3_Supplementary_Software_v2.0.zip`), covering the **NeuroImmune-Virtual-Biotech** analytical pipeline, the **vGlia-Niche** multicellular ODE dynamical simulator, figure generation scripts, and automated verification gates.

## Repository Structure

```text
NeuroImmune_Virtual_Biotech/
├── README.md
├── LICENSE
├── .gitignore
├── accession_metadata_authenticity_gate.py                        # Automated NCBI GEO & ClinicalTrials.gov metadata authenticity gate
├── neuroimmune_biotech/
│   ├── __init__.py                                                # Core simulation package exports
│   └── vglia_niche_simulator.py                                   # vGlia-Niche 5-variable Hill-type coupled ODE dynamical simulator
├── scripts/
│   ├── 00_extract_real_geo_cohorts.py                             # Raw NCBI GEO cohort extraction across 10 public datasets
│   ├── 01_pubmed_benchmark_and_230trials_tau_retrospective.py     # ClinicalTrials.gov 230-trial retrospective & dynamic tau(t) pipeline
│   ├── 02_build_flagship_5_figures.py                             # Main Figures 1-5 generation (600 DPI PNG/PDF/SVG)
│   ├── 03a_write_en_manuscript.py                                 # English manuscript assembly & reference parity
│   ├── 03b_write_zh_manuscript.py                                 # Chinese review manuscript assembly
│   ├── 03c_compile_docx_and_run_gates.py                          # DOCX compilation and formatting/parity gates
│   ├── 04_comprehensive_gap_audit.py                              # End-to-end 4-gate provenance, figure & numerical parity audit
│   ├── 05_build_submission_package.py                             # Submission package builder (v1.0)
│   ├── 05_run_rebuttal_sensitivity_and_loco.py                    # Sensitivity analyses, 16-fold LORO / 4-fold LOCO CV & 1,000-LHS ODE runs
│   ├── 06_build_sciadv_submission_package.py                      # Submission package builder (v2.0)
│   ├── 06_write_rebuttal_letter_and_update_status.py              # Revision audit & consistency verification
│   ├── 07_agentic_trace_and_icu_chrono_validation.py              # Multi-agent deliberation traces, 2x2 protocol chrono-window & GSE63808 audit
│   ├── 08_build_extended_data_4_figures.py                        # Extended Data / Supplementary Figures 1-4 generation
│   ├── figure_clean_aesthetic_gate.py                             # Publication figure AST & pixel quality verification gate
│   ├── gate.py                                                    # Preflight, canary, retry-limit & resource estimation gate utilities
│   └── scientific_text_sanitizer.py                               # LaTeX/Markdown-to-native-DOCX scientific typography sanitizer
├── tables/
│   ├── Table1_230Trials_Modality_and_Tau_Tier_Summary.csv         # Main Table 1 (Fig. 1 source data)
│   ├── Table2_Top25_Tier1_Targets_MultiCohort_Ledger.csv          # Main Table 2 (Fig. 4 & Fig. 5 source data)
│   ├── Table3_SixGate_Ablation_and_Benchmark_Comparison.csv       # Main Table 3 (Fig. 3 source data)
│   ├── TableS1_230_ClinicalTrials_MultiAgent_Audit.csv            # Supplementary Table S1 (N = 230 trials, Fig. 1 source data)
│   ├── TableS2_133Genes_Dynamic_Tau_Trajectories.csv              # Supplementary Table S2 (133 candidates, Fig. 2 & Fig. 3 source data)
│   ├── TableS3_10_GEO_Cohorts_Architecture_and_Validation_Summary.csv # Supplementary Table S3 (10 GEO cohorts, Fig. 2 source data)
│   └── TableS4_Agentic_CrossDivision_Deliberation_Traces.csv      # Supplementary Table S4 (12 cross-division deliberation traces)
└── data/
    ├── CLINICALTRIALS_PRISMA_FUNNEL_RECEIPT.json                  # ClinicalTrials.gov PRISMA 370 -> 230 screening receipt
    ├── CTGOV_OFFICIAL_VERBATIM_CACHE.json                         # Official ClinicalTrials.gov REST API v2 verbatim title/status cache
    ├── CTGOV_PROTOCOL_ELIGIBILITY_230_CACHE.json                  # ClinicalTrials.gov 230-trial protocol eligibility & window cache
    ├── DATA_PROVENANCE_MANIFEST.json                              # SHA-256 checksums for all 10 isolated derived datasets (10/10 verified)
    ├── Division4_ClinicalTrialsGov_Live_TBI_Neuroimmune_Trials.csv # Live 230-trial ClinicalTrials.gov registry table
    ├── Division4_Retrospective_Trial_Failure_and_Precision_Ledger.csv # Historical TBI/neuroimmune trial benchmark ledger
    ├── Division6_Protocol_ChronoWindow_Audit_230Trials.csv        # Protocol initiation-window & CWAS audit across 230 trials
    ├── GEO_EXHAUSTIVE_CENSUS_RECEIPT.json                         # Exhaustive 92-series NCBI GEO cohort census receipt
    ├── GSE180862_sc_gene_celltype_dotplot_matrix.csv              # Murine hippocampal TBI scRNA-seq cell-type expression matrix (Fig. 2)
    ├── GSE180862_sc_gene_primary_celltype_assignment.csv          # Baseline 24-cluster parenchymal primary cell-type assignment
    ├── GSE63808_129Patients_Hysteresis_Separatrix_Audit.csv       # N = 129 human surgical hippocampus separatrix audit (Supplementary Fig. S4)
    ├── GSE63808_human_129patients_glia_vs_neuron_scores.csv       # N = 129 human surgical hippocampus glia vs. neuron scores (Fig. 2)
    ├── Phase1_Virtual_CSO_Target_Priority_Ledger_133Genes.csv     # 133-candidate multi-division priority ledger
    ├── Phase3_vGliaNiche_1000LHS_ODE_Sensitivity.npz              # 1,000-run Latin-hypercube 5-ODE parameter perturbation archive
    ├── Phase3_vGliaNiche_16Point_LORO_LOCO_Validation.csv         # 16-readout LORO-CV and LOCO-CV calibration table (Fig. 4)
    ├── Phase3_vGliaNiche_72hr_Trajectories.csv                    # 72-h 5-ODE state trajectories across 8 regimens (Fig. 4 & Fig. 5)
    ├── Phase3_vGliaNiche_CellBehavior_Grammar_Rules.json          # vGlia-Niche multicellular Hill-type behavioral grammar rules
    ├── Phase3_vGliaNiche_ChronoTrial_Summary_vs_PublicCohorts.csv # vGlia-Niche chrono-trial summary vs. public cohorts (Fig. 4 & Fig. 5)
    ├── SixGate_UpSet_Intersection_Summary.json                    # Boolean 6-gate UpSet intersection summary (Supplementary Fig. S3)
    ├── cns_agent_papers_metadata.json                             # Curated benchmark literature metadata
    ├── flagship_v2_f1_f2_d2_summary.json                          # Multi-cohort audit & cross-species validation summary
    ├── rebuttal_sensitivity_and_loco_stats.json                   # Sensitivity, LORO/LOCO CV, and LHS ODE summary statistics
    └── trial_230_retrospective_stats.json                         # Retrospective trial failure & dynamic tau(t) statistics
```

## Public Data Sources

All analyses rely exclusively on publicly accessible datasets:

- **NCBI GEO transcriptomic cohorts (10 cohorts)**: `GSE180862`, `GSE269748`, `GSE247339`, `GSE277487`, `GSE226207`, `GSE302863`, `GSE319769`, `GSE330624`, `GSE209552`, and human surgical hippocampus cohort `GSE63808` (N = 129).
- **ClinicalTrials.gov**: Interventional TBI & neuroinflammation registry cohort (N = 230 screened via PRISMA funnel; receipt in `data/CLINICALTRIALS_PRISMA_FUNNEL_RECEIPT.json`).

SHA-256 verification checksums for all 10 isolated derived tables in `data/DATA_PROVENANCE_MANIFEST.json` match the files in `data/` 100% (10/10).

## Software Environment

The analysis, simulation, and plotting scripts are implemented in **Python 3** using standard scientific computing libraries:

- `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`, `seaborn`, `python-docx`

> **Note on local paths**: Several pipeline scripts record the original local build paths (`BASE_DIR` / `EXTERNAL_RAW_BASE`) from the authors' workstation. Pre-extracted derived matrices, ODE trajectories, and source tables are provided directly in `data/` and `tables/`; to re-run end-to-end from raw GEO downloads (`scripts/00_extract_real_geo_cohorts.py`), point `BASE_DIR` and `EXTERNAL_RAW_BASE` to your local directory containing the downloaded NCBI GEO series files.

## License

This project is released under the [MIT License](LICENSE).
