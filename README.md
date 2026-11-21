# NeuroImmune-Virtual-Biotech (`v2.0`)

Source code, figure source tables, data provenance manifests, and audit receipts accompanying the manuscript:

> **Dynamic cellular specificity predicts inflammatory lock-in and clinical translation in acute brain injury**

This repository accompanies the manuscript submission (mirroring **Additional file 1** source tables and **Additional file 3** `Additional_file_3_Supplementary_Software_v2.0.zip`), covering the **NeuroImmune-Virtual-Biotech** analytical pipeline, the **vGlia-Niche** multicellular ODE world model, figure generation scripts, and automated audit gates.

## Repository Structure

```text
NeuroImmune_Virtual_Biotech/
├── README.md
├── LICENSE
├── .gitignore
├── scripts/
│   ├── 00_extract_real_geo_cohorts.py                         # Raw NCBI GEO cohort extraction across 10 public datasets
│   ├── 01_pubmed_benchmark_and_230trials_tau_retrospective.py # ClinicalTrials.gov 230-trial retrospective & dynamic tau(t) pipeline
│   ├── 02_build_flagship_5_figures.py                         # Main Figures 1-5 generation (600 DPI PNG/PDF/SVG)
│   ├── 03a_write_en_manuscript.py                             # English manuscript assembly & reference parity
│   ├── 03b_write_zh_manuscript.py                             # Chinese review manuscript assembly
│   ├── 03c_compile_docx_and_run_gates.py                      # DOCX compilation and formatting/parity gates
│   ├── 04_comprehensive_gap_audit.py                          # End-to-end 4-gate provenance, figure & numerical parity audit
│   ├── 05_build_submission_package.py                         # Submission package builder (v1.0)
│   ├── 05_run_rebuttal_sensitivity_and_loco.py                # Sensitivity analyses, 16-fold LORO / 4-fold LOCO CV & 1,000-LHS ODE runs
│   ├── 06_build_sciadv_submission_package.py                  # Submission package builder (v2.0)
│   ├── 06_write_rebuttal_letter_and_update_status.py          # Revision audit & consistency verification
│   ├── 07_agentic_trace_and_icu_chrono_validation.py          # Multi-agent deliberation traces, 2x2 protocol chrono-window & GSE63808 audit
│   └── 08_build_extended_data_4_figures.py                    # Extended Data / Supplementary Figures 1-4 generation
├── tables/
│   ├── Table1_230Trials_Modality_and_Tau_Tier_Summary.csv               # Main Table 1 (Fig. 1 source data)
│   ├── Table2_Top25_Tier1_Targets_MultiCohort_Ledger.csv                # Main Table 2 (Fig. 4 & Fig. 5 source data)
│   ├── Table3_SixGate_Ablation_and_Benchmark_Comparison.csv             # Main Table 3 (Fig. 3 source data)
│   ├── TableS1_230_ClinicalTrials_MultiAgent_Audit.csv                  # Supplementary Table S1 (N = 230 trials, Fig. 1 source data)
│   ├── TableS2_133Genes_Dynamic_Tau_Trajectories.csv                    # Supplementary Table S2 (133 candidates, Fig. 2 & Fig. 3 source data)
│   ├── TableS3_10_GEO_Cohorts_Architecture_and_Validation_Summary.csv   # Supplementary Table S3 (10 GEO cohorts, Fig. 2 source data)
│   └── TableS4_Agentic_CrossDivision_Deliberation_Traces.csv            # Supplementary Table S4 (12 cross-division deliberation traces)
└── data/
    ├── DATA_PROVENANCE_MANIFEST.json                                    # SHA-256 checksums for isolated public datasets
    ├── CLINICALTRIALS_PRISMA_FUNNEL_RECEIPT.json                        # ClinicalTrials.gov PRISMA 370 -> 230 screening receipt
    ├── GEO_EXHAUSTIVE_CENSUS_RECEIPT.json                               # Exhaustive NCBI GEO cohort census receipt
    ├── trial_230_retrospective_stats.json                               # Retrospective trial failure & dynamic tau(t) statistics
    ├── rebuttal_sensitivity_and_loco_stats.json                         # Sensitivity, LORO/LOCO CV, and LHS ODE summary statistics
    ├── flagship_v2_f1_f2_d2_summary.json                                # Dry-lab audit & cross-species validation summary
    ├── GSE63808_human_129patients_glia_vs_neuron_scores.csv             # N = 129 human surgical hippocampus glia vs. neuron scores (Fig. 2)
    ├── GSE63808_129Patients_Hysteresis_Separatrix_Audit.csv             # N = 129 human surgical hippocampus separatrix audit
    ├── Phase3_vGliaNiche_ChronoTrial_Summary_vs_PublicCohorts.csv       # vGlia-Niche chrono-trial summary vs. public cohorts (Fig. 4 & Fig. 5)
    └── Phase3_vGliaNiche_CellBehavior_Grammar_Rules.json                # vGlia-Niche multicellular Hill-type behavioral grammar rules
```

## Public Data Sources

All analyses rely exclusively on publicly accessible datasets:

- **NCBI GEO transcriptomic cohorts (10 cohorts)**: `GSE180862`, `GSE269748`, `GSE247339`, `GSE277487`, `GSE226207`, `GSE302863`, `GSE319769`, `GSE330624`, `GSE209552`, and human surgical hippocampus cohort `GSE63808` (N = 129).
- **ClinicalTrials.gov**: Interventional TBI & neuroinflammation registry cohort (N = 230 screened via PRISMA funnel; receipt in `data/CLINICALTRIALS_PRISMA_FUNNEL_RECEIPT.json`).

SHA-256 verification checksums for intermediate derived tables are recorded in `data/DATA_PROVENANCE_MANIFEST.json`.

## Software Environment

The analysis and plotting scripts are implemented in **Python 3** using standard scientific computing libraries:

- `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`, `seaborn`, `python-docx`

> **Note on local paths**: Several scripts reference original local build directories (e.g., `BASE_DIR` / `EXTERNAL_RAW_BASE`) from the authors' workstation. To re-run end-to-end from raw GEO downloads, update `BASE_DIR` and `EXTERNAL_RAW_BASE` to point to your local directory containing the downloaded NCBI GEO raw files.

## License

This project is released under the [MIT License](LICENSE).
