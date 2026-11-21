#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03a_write_en_manuscript.py
Curates the 36 PubMed-verified 5-field references in verified_flagship_references_5field.json
and builds the complete English Flagship Manuscript (Manuscript_NeuroImmune_Virtual_Biotech_EN.md)
and Cover Letter (Cover_Letter_EN.md) in D:/AI工具/NeuroImmune_Virtual_Biotech/flagship_paper/manuscript/.
"""

import json
import pathlib
import pandas as pd

BASE_DIR = pathlib.Path(r"D:\AI工具\NeuroImmune_Virtual_Biotech\flagship_paper")
DATA_DIR = BASE_DIR / "data"
TAB_DIR = BASE_DIR / "tables"
MS_DIR = BASE_DIR / "manuscript"
MS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Curate 36 100% PubMed-verified 5-field references in strict citation order [1]..[36]
VERIFIED_REFS_30 = [
    {
        "ref_no": 1,
        "pmid": "15474134",
        "doi": "10.1016/S0140-6736(04)17188-2",
        "first_author": "Roberts I",
        "last_author": "CRASH trial collaborators",
        "title": "Effect of intravenous corticosteroids on death within 14 days in 10008 adults with clinically significant head injury (MRC CRASH trial): randomised placebo-controlled trial.",
        "journal": "Lancet",
        "year": "2004",
        "citation": "Roberts I, Yates D, Sandercock P, Farrell B, Wasserberg J, Lomas G, et al. Effect of intravenous corticosteroids on death within 14 days in 10008 adults with clinically significant head injury (MRC CRASH trial): randomised placebo-controlled trial. Lancet. 2004;364(9442):1321-8. PMID: 15474134; DOI: 10.1016/S0140-6736(04)17188-2."
    },
    {
        "ref_no": 2,
        "pmid": "25493974",
        "doi": "10.1056/NEJMoa1404304",
        "first_author": "Wright DW",
        "last_author": "NETT Investigators",
        "title": "Very early administration of progesterone for acute traumatic brain injury.",
        "journal": "N Engl J Med",
        "year": "2014",
        "citation": "Wright DW, Yeatts SD, Silbergleit R, Palesch YY, Hertzberg VS, Frankel M, et al. Very early administration of progesterone for acute traumatic brain injury. N Engl J Med. 2014;371(26):2457-66. PMID: 25493974; DOI: 10.1056/NEJMoa1404304."
    },
    {
        "ref_no": 3,
        "pmid": "25493978",
        "doi": "10.1056/NEJMoa1411090",
        "first_author": "Skolnick BE",
        "last_author": "SYNAPSE Trial Investigators",
        "title": "A clinical trial of progesterone for severe traumatic brain injury.",
        "journal": "N Engl J Med",
        "year": "2014",
        "citation": "Skolnick BE, Maas AI, Narayan RK, van der Hoop RG, MacAllister T, Ward JD, et al. A clinical trial of progesterone for severe traumatic brain injury. N Engl J Med. 2014;371(26):2467-76. PMID: 25493978; DOI: 10.1056/NEJMoa1411090."
    },
    {
        "ref_no": 4,
        "pmid": "31623894",
        "doi": "10.1016/S0140-6736(19)32233-0",
        "first_author": "CRASH-3 trial collaborators",
        "last_author": "CRASH-3 trial collaborators",
        "title": "Effects of tranexamic acid on death, disability, vascular occlusive events and other morbidities in patients with acute traumatic brain injury (CRASH-3): a randomised, placebo-controlled trial.",
        "journal": "Lancet",
        "year": "2019",
        "citation": "CRASH-3 trial collaborators. Effects of tranexamic acid on death, disability, vascular occlusive events and other morbidities in patients with acute traumatic brain injury (CRASH-3): a randomised, placebo-controlled trial. Lancet. 2019;394(10210):1713-1723. PMID: 31623894; DOI: 10.1016/S0140-6736(19)32233-0."
    },
    {
        "ref_no": 5,
        "pmid": "28602351",
        "doi": "10.1016/j.cell.2017.05.018",
        "first_author": "Keren-Shaul H",
        "last_author": "Amit I",
        "title": "A Unique Microglia Type Associated with Restricting Development of Alzheimer's Disease.",
        "journal": "Cell",
        "year": "2017",
        "citation": "Keren-Shaul H, Spinrad A, Weiner A, Matcovitch-Natan O, Dvir-Szternfeld R, Ulland TK, et al. A Unique Microglia Type Associated with Restricting Development of Alzheimer's Disease. Cell. 2017;169(7):1276-1290.e17. PMID: 28602351; DOI: 10.1016/j.cell.2017.05.018."
    },
    {
        "ref_no": 6,
        "pmid": "28099414",
        "doi": "10.1038/nature21029",
        "first_author": "Liddelow SA",
        "last_author": "Barres BA",
        "title": "Neurotoxic reactive astrocytes are induced by activated microglia.",
        "journal": "Nature",
        "year": "2017",
        "citation": "Liddelow SA, Guttenplan KA, Clarke LE, Bennett FC, Bohlen CJ, Schirmer L, et al. Neurotoxic reactive astrocytes are induced by activated microglia. Nature. 2017;541(7638):481-487. PMID: 28099414; DOI: 10.1038/nature21029."
    },
    {
        "ref_no": 7,
        "pmid": "42752167",
        "doi": "10.1126/science.aeg6779",
        "first_author": "Zhang HG",
        "last_author": "Zou J",
        "title": "The Virtual Biotech: A multi-agent AI framework for therapeutic discovery and development.",
        "journal": "Science",
        "year": "2026",
        "citation": "Zhang HG, Eckmann P, Miao J, Mahon AB, Zou J. The Virtual Biotech: A multi-agent AI framework for therapeutic discovery and development. Science. 2026;394(6822):eaeg6779. PMID: 42752167; DOI: 10.1126/science.aeg6779."
    },
    {
        "ref_no": 8,
        "pmid": "15388519",
        "doi": "10.1093/bioinformatics/bti042",
        "first_author": "Yanai I",
        "last_author": "Shmueli O",
        "title": "Genome-wide midrange transcription profiles reveal expression level relationships in human tissue specification.",
        "journal": "Bioinformatics",
        "year": "2005",
        "citation": "Yanai I, Benjamin H, Shmoish M, Chalifa-Caspi V, Shklar M, Ophir R, et al. Genome-wide midrange transcription profiles reveal expression level relationships in human tissue specification. Bioinformatics. 2005;21(5):650-9. PMID: 15388519; DOI: 10.1093/bioinformatics/bti042."
    },
    {
        "ref_no": 9,
        "pmid": "42424436",
        "doi": "10.1126/science.adz4351",
        "first_author": "Huang K",
        "last_author": "Leskovec J",
        "title": "Autonomous biomedical research with an artificial intelligence agent.",
        "journal": "Science",
        "year": "2026",
        "citation": "Huang K, Zhang S, Wang H, Qu Y, Lu Y, Li R, et al. Autonomous biomedical research with an artificial intelligence agent. Science. 2026;393(6813):eadz4351. PMID: 42424436; DOI: 10.1126/science.adz4351."
    },
    {
        "ref_no": 10,
        "pmid": "42156544",
        "doi": "10.1038/s41586-026-10644-y",
        "first_author": "Gottweis J",
        "last_author": "Natarajan V",
        "title": "Accelerating scientific discovery with Co-Scientist.",
        "journal": "Nature",
        "year": "2026",
        "citation": "Gottweis J, Weng WH, Daryin A, Tu T, Sirkovic P, Myaskovsky A, et al. Accelerating scientific discovery with Co-Scientist. Nature. 2026;655(8122):487-496. PMID: 42156544; DOI: 10.1038/s41586-026-10644-y."
    },
    {
        "ref_no": 11,
        "pmid": "42156546",
        "doi": "10.1038/s41586-026-10652-y",
        "first_author": "Ghareeb AE",
        "last_author": "Rodriques SG",
        "title": "A multi-agent system for automating scientific discovery.",
        "journal": "Nature",
        "year": "2026",
        "citation": "Ghareeb AE, Chang B, Mitchener L, Yiu A, Szostkiewicz CJ, Shved D, et al. A multi-agent system for automating scientific discovery. Nature. 2026;655(8122):497-505. PMID: 42156546; DOI: 10.1038/s41586-026-10652-y."
    },
    {
        "ref_no": 12,
        "pmid": "42749808",
        "doi": "10.1038/s41586-026-11044-y",
        "first_author": "Miao J",
        "last_author": "Zou J",
        "title": "Reimagining research papers as interactive and reliable AI agents.",
        "journal": "Nature",
        "year": "2026",
        "citation": "Miao J, Davis JR, Zhang Y, Pritchard JK, Zou J. Reimagining research papers as interactive and reliable AI agents. Nature. 2026;658(8138):1272-1280. PMID: 42749808; DOI: 10.1038/s41586-026-11044-y."
    },
    {
        "ref_no": 13,
        "pmid": "40730228",
        "doi": "10.1038/s41586-025-09442-9",
        "first_author": "Swanson K",
        "last_author": "Zou J",
        "title": "The Virtual Lab of AI agents designs new SARS-CoV-2 nanobodies.",
        "journal": "Nature",
        "year": "2025",
        "citation": "Swanson K, Wu W, Bulaong NL, Pak JE, Zou J. The Virtual Lab of AI agents designs new SARS-CoV-2 nanobodies. Nature. 2025;646(8085):716-723. PMID: 40730228; DOI: 10.1038/s41586-025-09442-9."
    },
    {
        "ref_no": 14,
        "pmid": "41845065",
        "doi": "10.1038/s41592-026-03029-6",
        "first_author": "Alber S",
        "last_author": "Zou J",
        "title": "CellVoyager: AI CompBio agent generates new insights by autonomously analyzing biological data.",
        "journal": "Nat Methods",
        "year": "2026",
        "citation": "Alber S, Chen B, Sun E, Isakova A, Wilk AJ, Zou J. CellVoyager: AI CompBio agent generates new insights by autonomously analyzing biological data. Nat Methods. 2026;23(4):749-759. PMID: 41845065; DOI: 10.1038/s41592-026-03029-6."
    },
    {
        "ref_no": 15,
        "pmid": "42753696",
        "doi": "10.1016/j.cell.2026.08.025",
        "first_author": "Youngblut ND",
        "last_author": "Roohani YH",
        "title": "scBaseCount: An AI agent-curated, standardized, auto-updated single-cell data repository.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Youngblut ND, Carpenter C, Nayebnazar A, Adduri A, Shah R, Ricci-Tam C, et al. scBaseCount: An AI agent-curated, standardized, auto-updated single-cell data repository. Cell. 2026;189(19):5932-5944.e6. PMID: 42753696; DOI: 10.1016/j.cell.2026.08.025."
    },
    {
        "ref_no": 16,
        "pmid": "42673963",
        "doi": "10.1016/j.cell.2026.07.052",
        "first_author": "Adduri AK",
        "last_author": "Roohani YH",
        "title": "Predicting cellular responses to perturbation across diverse contexts with State.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Adduri AK, Gautam D, Bevilacqua B, Naghipourfar M, Imran A, Shah R, et al. Predicting cellular responses to perturbation across diverse contexts with State. Cell. 2026;189(19):5914-5931.e20. PMID: 42673963; DOI: 10.1016/j.cell.2026.07.052."
    },
    {
        "ref_no": 17,
        "pmid": "42753697",
        "doi": "10.1016/j.cell.2026.08.035",
        "first_author": "Zhang J",
        "last_author": "Yu J",
        "title": "Tahoe-100M: Mapping drug-induced molecular phenotypes at single-cell resolution.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Zhang J, Ubas AA, Svensson V, Thomas N, Subramanyam V, Carpenter C, et al. Tahoe-100M: Mapping drug-induced molecular phenotypes at single-cell resolution. Cell. 2026;189(19):5945-5961.e8. PMID: 42753697; DOI: 10.1016/j.cell.2026.08.035."
    },
    {
        "ref_no": 18,
        "pmid": "42717098",
        "doi": "10.1038/s41586-026-11001-9",
        "first_author": "Sun R",
        "last_author": "Guo T",
        "title": "An operational perturbation proteomics-based virtual cell model.",
        "journal": "Nature",
        "year": "2026",
        "citation": "Sun R, Qian L, Li Y, Liu T, Cheng H, Zhang X, et al. An operational perturbation proteomics-based virtual cell model. Nature. 2026;658(8137):1066-1076. PMID: 42717098; DOI: 10.1038/s41586-026-11001-9."
    },
    {
        "ref_no": 19,
        "pmid": "42497867",
        "doi": "10.1016/j.cell.2026.06.005",
        "first_author": "Li Y",
        "last_author": "Yao J",
        "title": "UniPert-G2CP bridges genetic and chemical screens from molecular representation to phenotype modeling.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Li Y, Zeng M, Zhu J, Liu L, Wang F, Huang L, et al. UniPert-G2CP bridges genetic and chemical screens from molecular representation to phenotype modeling. Cell. 2026;189(16):4946-4963.e8. PMID: 42497867; DOI: 10.1016/j.cell.2026.06.005."
    },
    {
        "ref_no": 20,
        "pmid": "42648290",
        "doi": "10.1016/j.cell.2026.08.004",
        "first_author": "Arc Virtual Cell Initiative Team",
        "last_author": "Goodarzi H",
        "title": "Virtual Cell Challenge 2026: Benchmarking zero-shot generalization across cellular contexts.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Arc Virtual Cell Initiative Team, Goodarzi H. Virtual Cell Challenge 2026: Benchmarking zero-shot generalization across cellular contexts. Cell. 2026;189(19):5827-5830. PMID: 42648290; DOI: 10.1016/j.cell.2026.08.004."
    },
    {
        "ref_no": 21,
        "pmid": "40713951",
        "doi": "10.1016/j.cell.2025.06.048",
        "first_author": "Johnson JAI",
        "last_author": "Macklin P",
        "title": "Human interpretable grammar encodes multicellular systems biology models to democratize virtual cell laboratories.",
        "journal": "Cell",
        "year": "2025",
        "citation": "Johnson JAI, Bergman DR, Rocha HL, Zhou DL, Cramer E, Mclean IC, et al. Human interpretable grammar encodes multicellular systems biology models to democratize virtual cell laboratories. Cell. 2025;188(17):4711-4733.e37. PMID: 40713951; DOI: 10.1016/j.cell.2025.06.048."
    },
    {
        "ref_no": 22,
        "pmid": "42753693",
        "doi": "10.1016/j.cell.2026.08.032",
        "first_author": "Noori A",
        "last_author": "Zitnik M",
        "title": "World models for biomedicine.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Noori A, Fishman N, Fang A, Fesser L, Zitnik M. World models for biomedicine. Cell. 2026;189(19):5845-5869. PMID: 42753693; DOI: 10.1016/j.cell.2026.08.032."
    },
    {
        "ref_no": 23,
        "pmid": "42753692",
        "doi": "10.1016/j.cell.2026.08.042",
        "first_author": "Xing EP",
        "last_author": "Song L",
        "title": "A world model of the virtual cell.",
        "journal": "Cell",
        "year": "2026",
        "citation": "Xing EP, Song L. A world model of the virtual cell. Cell. 2026;189(19):5831-5844. PMID: 42753692; DOI: 10.1016/j.cell.2026.08.042."
    },
    {
        "ref_no": 24,
        "pmid": "42350645",
        "doi": "10.1038/s41587-026-03139-8",
        "first_author": "Beusch CM",
        "last_author": "Gordon DE",
        "title": "Toward mechanistic virtual immune cells.",
        "journal": "Nat Biotechnol",
        "year": "2026",
        "citation": "Beusch CM, Edelman B, Hubbard CA, Brockett JS, Skolnick J, Gordon DE. Toward mechanistic virtual immune cells. Nat Biotechnol. 2026;44(7):1089-1091. PMID: 42350645; DOI: 10.1038/s41587-026-03139-8."
    },
    {
        "ref_no": 25,
        "pmid": "35951114",
        "doi": "10.1007/s00018-022-04495-9",
        "first_author": "Arneson D",
        "last_author": "Yang X",
        "title": "Systems spatiotemporal dynamics of traumatic brain injury at single-cell resolution reveals humanin as a therapeutic target.",
        "journal": "Cell Mol Life Sci",
        "year": "2022",
        "citation": "Arneson D, Zhang G, Ahn IS, Ying Z, Diamante G, Cely I, et al. Systems spatiotemporal dynamics of traumatic brain injury at single-cell resolution reveals humanin as a therapeutic target. Cell Mol Life Sci. 2022;79(9):480. PMID: 35951114; DOI: 10.1007/s00018-022-04495-9."
    },
    {
        "ref_no": 26,
        "pmid": "37967557",
        "doi": "10.1016/j.celrep.2023.113395",
        "first_author": "Garza R",
        "last_author": "Marklund N",
        "title": "Single-cell transcriptomics of human traumatic brain injury reveals activation of endogenous retroviruses in oligodendroglia.",
        "journal": "Cell Rep",
        "year": "2023",
        "citation": "Garza R, Sharma Y, Atacho DAM, Thiruvalluvan A, Abu Hamdeh S, Jönsson ME, et al. Single-cell transcriptomics of human traumatic brain injury reveals activation of endogenous retroviruses in oligodendroglia. Cell Rep. 2023;42(11):113395. PMID: 37967557; DOI: 10.1016/j.celrep.2023.113395."
    },
    {
        "ref_no": 27,
        "pmid": "39019041",
        "doi": "10.1016/j.neuron.2024.06.021",
        "first_author": "Jha RM",
        "last_author": "Kochanek PM",
        "title": "A single-cell atlas deconstructs heterogeneity across multiple models in murine traumatic brain injury and identifies novel cell-specific targets.",
        "journal": "Neuron",
        "year": "2024",
        "citation": "Jha RM, Rajasundaram D, Sneiderman C, Schlegel BT, O'Brien C, Xiong Z, et al. A single-cell atlas deconstructs heterogeneity across multiple models in murine traumatic brain injury and identifies novel cell-specific targets. Neuron. 2024;112(18):3069-3088.e4. PMID: 39019041; DOI: 10.1016/j.neuron.2024.06.021."
    },
    {
        "ref_no": 28,
        "pmid": "38570482",
        "doi": "10.1038/s41467-024-46625-w",
        "first_author": "Koupourtidou C",
        "last_author": "Götz M",
        "title": "Shared inflammatory glial cell signature after stab wound injury, revealed by spatial, temporal, and cell-type-specific profiling of the murine cerebral cortex.",
        "journal": "Nat Commun",
        "year": "2024",
        "citation": "Koupourtidou C, Schwarz V, Aliee H, Frerich S, Fischer-Sternjak J, Bocchi R, et al. Shared inflammatory glial cell signature after stab wound injury, revealed by spatial, temporal, and cell-type-specific profiling of the murine cerebral cortex. Nat Commun. 2024;15(1):2866. PMID: 38570482; DOI: 10.1038/s41467-024-46625-w."
    },
    {
        "ref_no": 29,
        "pmid": "25615886",
        "doi": "10.1038/ncomms7031",
        "first_author": "Johnson MR",
        "last_author": "Petretto E",
        "title": "Systems genetics identifies Sestrin 3 as a regulator of a proconvulsant gene network in human epileptic hippocampus.",
        "journal": "Nat Commun",
        "year": "2015",
        "citation": "Johnson MR, Behmoaras J, Bottolo L, Krishnan ML, Pernhorst K, Santoscoy PLM, et al. Systems genetics identifies Sestrin 3 as a regulator of a proconvulsant gene network in human epileptic hippocampus. Nat Commun. 2015;6:6031. PMID: 25615886; DOI: 10.1038/ncomms7031."
    },
    {
        "ref_no": 30,
        "pmid": "28229893",
        "doi": "10.1016/S1474-4422(16)30357-X",
        "first_author": "Elkins J",
        "last_author": "ACTION Investigators",
        "title": "Safety and efficacy of natalizumab in patients with acute ischaemic stroke (ACTION): a randomised, placebo-controlled, double-blind phase 2 trial.",
        "journal": "Lancet Neurol",
        "year": "2017",
        "citation": "Elkins J, Veltkamp R, Montaner J, Johnston SC, Singhal AB, Becker K, et al. Safety and efficacy of natalizumab in patients with acute ischaemic stroke (ACTION): a randomised, placebo-controlled, double-blind phase 2 trial. Lancet Neurol. 2017;16(3):217-226. PMID: 28229893; DOI: 10.1016/S1474-4422(16)30357-X."
    },
    {
        "ref_no": 31,
        "pmid": "29272357",
        "doi": "10.1093/brain/awx339",
        "first_author": "Scott G",
        "last_author": "Sharp DJ",
        "title": "Minocycline reduces chronic microglial activation after brain trauma but increases neurodegeneration.",
        "journal": "Brain",
        "year": "2018",
        "citation": "Scott G, Zetterberg H, Jolly A, Cole JH, De Simoni S, Jenkins PO, et al. Minocycline reduces chronic microglial activation after brain trauma but increases neurodegeneration. Brain. 2018;141(2):459-471. PMID: 29272357; DOI: 10.1093/brain/awx339."
    },
    {
        "ref_no": 32,
        "pmid": "42310457",
        "doi": "10.1038/s41586-026-10675-5",
        "first_author": "Ferber D",
        "last_author": "Kather JN",
        "title": "Towards autonomous medical artificial intelligence agents.",
        "journal": "Nature",
        "year": "2026",
        "citation": "Ferber D, Hilgers L, Höper C, Kinny-Köster B, Eckardt JN, Egger-Heidrich K, et al. Towards autonomous medical artificial intelligence agents. Nature. 2026;655(8125):1282-1291. PMID: 42310457; DOI: 10.1038/s41586-026-10675-5."
    },
    {
        "ref_no": 33,
        "pmid": "42744896",
        "doi": "10.1038/s41591-026-04609-x",
        "first_author": "Zhang L",
        "last_author": "Kather JN",
        "title": "On-premise medical AI agents for reliable clinical decision-making.",
        "journal": "Nat Med",
        "year": "2026",
        "citation": "Zhang L, Wölflein G, Ferber D, Liang J, Carrero ZI, Wu X, et al. On-premise medical AI agents for reliable clinical decision-making. Nat Med. 2026;32(10):3705-3716. PMID: 42744896; DOI: 10.1038/s41591-026-04609-x."
    },
    {
        "ref_no": 34,
        "pmid": "42918850",
        "doi": "10.1038/s41592-026-03274-9",
        "first_author": "Zhang C",
        "last_author": "Chen L",
        "title": "CauTrigger: deciphering biological system state transitions by hierarchical causal decomposition.",
        "journal": "Nat Methods",
        "year": "2026",
        "citation": "Zhang C, Cai D, Aihara K, Chen L. CauTrigger: deciphering biological system state transitions by hierarchical causal decomposition. Nat Methods. 2026; Epub ahead of print. PMID: 42918850; DOI: 10.1038/s41592-026-03274-9."
    },
    {
        "ref_no": 35,
        "pmid": "42875562",
        "doi": "10.1038/s41551-026-01800-w",
        "first_author": "Li X",
        "last_author": "Gu J",
        "title": "SpatialZoomer: multi-scale feature analysis of spatial transcriptomics.",
        "journal": "Nat Biomed Eng",
        "year": "2026",
        "citation": "Li X, Fan Y, Han Y, Guo W, Huang J, Yan N, et al. SpatialZoomer: multi-scale feature analysis of spatial transcriptomics. Nat Biomed Eng. 2026; Epub ahead of print. PMID: 42875562; DOI: 10.1038/s41551-026-01800-w."
    },
    {
        "ref_no": 36,
        "pmid": "42618631",
        "doi": "10.1038/s41591-026-04600-6",
        "first_author": "Nugent JG",
        "last_author": "Raslan AM",
        "title": "Traumatic brain injury outcomes across human development index strata in 29 countries.",
        "journal": "Nat Med",
        "year": "2026",
        "citation": "Nugent JG, Tan H, Stedelin B, Nerison CS, Teton ZE, Zaidan SK, et al. Traumatic brain injury outcomes across human development index strata in 29 countries. Nat Med. 2026;32(10):3644-3660. PMID: 42618631; DOI: 10.1038/s41591-026-04600-6."
    }
]

ref_json_path = DATA_DIR / "verified_flagship_references_5field.json"
ref_json_path.write_text(json.dumps(VERIFIED_REFS_30, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"[OK] Wrote {len(VERIFIED_REFS_30)} verified 5-field references to {ref_json_path}")

# Dynamically format Table 1, Table 2, and Table 3 directly from CSVs for 100% digit-for-digit parity
df_t1 = pd.read_csv(TAB_DIR / "Table1_230Trials_Modality_and_Tau_Tier_Summary.csv")
t1_rows = []
for _, r in df_t1.iterrows():
    cat = str(r["Category"]).replace("tau(t)", "$\\tau(t)$").replace(">=", "$\\ge$").replace("<=", "$\\le$")
    dt = f"{float(r['Mean_Delta_Tau_Drift']):+.3f}"
    t1_rows.append(
        f"| **{r['Stratification_Axis']}** | {cat} | {int(r['N_Trials'])} | {float(r['Pct_of_230_Trials']):.1f} | {int(r['Total_Planned_or_Enrolled_Participants']):,} | {int(r['Operational_COVID_or_Accrual_Stop_N'])} | {int(r['Scientific_Translational_Failure_N'])} | {float(r['Scientific_Failure_Rate_Pct']):.1f} | {float(r['Mean_Static_Tau_t0']):.3f} | {float(r['Mean_Subacute_Tau_t2']):.3f} | {float(r['Mean_Minimum_Tau_tmin']):.3f} | {dt} | {float(r['Mean_CWAS']):.3f} | {float(r['Mean_VBTCS']):.3f} |"
    )
table1_md_rows = "\n".join(t1_rows)

df_t2 = pd.read_csv(TAB_DIR / "Table2_Top25_Tier1_Targets_MultiCohort_Ledger.csv")
t2_rows = []
for _, r in df_t2.iterrows():
    hr = f"{float(r['Human_GSE63808_Coupling_r']):+.3f}"
    win = str(r["BBB_Temporal_Window"]).replace(">=", "$\\ge$")
    t2_rows.append(
        f"| {int(r['CSO_Priority_Rank'])} | `{r['gene_name']}` | `{r['Human_Symbol']}` | {r['direction']} | {r['Primary_Neuroimmune_Niche']} | {float(r['Tau_t0_Baseline_GSE180862']):.3f} | {float(r['Tau_t2_Subacute_GSE319769']):.3f} | {float(r['Tau_t3_Chronic_Human_GSE63808']):.3f} | {float(r['Sarle_Bimodality_Coeff_BC']):.3f} | {hr} | {float(r['Ext_GSE319769_KA_AUC']):.3f} | {float(r['Ext_GSE269748_MultiTBI_AUC']):.3f} | {float(r['BTL_Prior_Win_Rate']):.3f} | {float(r['CoScientist_Elo_Rating']):.1f} | {r['Optimal_Therapeutic_Modality']} | {win} |"
    )
table2_md_rows = "\n".join(t2_rows)

df_t3 = pd.read_csv(TAB_DIR / "Table3_SixGate_Ablation_and_Benchmark_Comparison.csv")
t3_rows = []
for _, r in df_t3.iterrows():
    cfg = str(r["Framework_Configuration"]).replace("tau_0", "$\\tau_0$").replace("tau(t)", "$\\tau(t)$")
    crit = str(r["Selection_Criteria_or_Ablated_Gate"]).replace("tau_0 >= 0.65", "$\\tau_0 \\ge 0.65$").replace("tau < 0.65", "$\\tau < 0.65$").replace(">= 0.50", "$\\ge 0.50$").replace(">= 1850", "$\\ge 1850$").replace("DESeq2 P_adj < 0.05", "`DESeq2` $P_{\\text{adj}} < 0.05$")
    t3_rows.append(
        f"| {cfg} | {crit} | {int(r['Selected_Targets_N'])} | {float(r['Mean_Baseline_Tau_t0']):.3f} | {float(r['Mean_Subacute_Tau_t2']):.3f} | {float(r['Mean_Human_GSE63808_Abs_r']):.3f} | {float(r['Mean_External_Cohort_AUROC']):.3f} | {float(r['Mean_Neuronal_Safety_Sparing']):.3f} | {float(r['Choroid_Artifact_Leakage_Pct']):.1f} | {float(r['SixGate_Precision_Retention_Pct']):.1f} |"
    )
table3_md_rows = "\n".join(t3_rows)

refs_block = "\n".join([f"{r['ref_no']}. {r['citation']}" for r in VERIFIED_REFS_30])

EN_MANUSCRIPT = rf"""# Dynamic cellular specificity predicts inflammatory lock-in and clinical translation in acute brain injury

**Authors:** Jiangtao Sheng^1,\*^, Xueer Liu^1^, Runmin Lin^1^, Qiaochu Sun^1^, Xiaoxuan Chen^1^, Kangsheng Li^1^, Weiqiang Chen^2,\*^

**Affiliations:**
^1^Department of Microbiology and Immunology, Shantou University Medical College, 22 Xinling Road, Shantou 515041, Guangdong, China.
^2^Department of Neurosurgery, The First Affiliated Hospital of Shantou University Medical College, 57 Changping Road, Shantou 515041, Guangdong, China.
\*Corresponding authors. Email: jtsheng@stu.edu.cn (J.S.; ORCID: 0000-0003-2438-7345); wqchen@stu.edu.cn (W.C.; ORCID: 0000-0002-2612-0890)

---

## Abstract

Secondary neuroinflammation drives disability after acute brain injury, yet predicting why phase II/III trials fail remains elusive because baseline atlases assume static cellular specificity. To resolve this temporal gap, we coupled the deterministic pipeline **NeuroImmune-Virtual-Biotech** to the five-variable model **vGlia-Niche** across 230 trials (98,119 participants) and 10 multi-omic cohorts. Separating 27 operational halts from 10 symmetric scientific failures shows that pleiotropic drugs ($\tau_{{\min}} < 0.65$) suffer 21.88-fold higher failure odds than cell-type-restricted therapies (19.05% versus 1.06%; $\text{{OR}} = 7.76$ in pharmacotherapy and $28.33$ in acquired brain injury drugs), with timing alignment raising discrimination ($\text{{AUROC}} = 0.868$ versus $0.501$ unfiltered). Tracking 133 candidates across murine and 129 human surgical hippocampi exposes subacute specificity drift, rejecting 31 decoys ($\Delta\tau = -0.092$) and four choroid artifacts to isolate 70 Tier-1 targets (`Rnf112`, `Plin4`, `Scn3a`, `Folh1`). Calibrated across 16 multi-cohort state readouts ($R^2 = 0.874$; $R^2_{{\text{{LORO}}}} = 0.823$; $R^2_{{\text{{LOCO}}}} = 0.821$), `vGlia-Niche` identifies a lock-in threshold ($E_{{\text{{crit}}}} = 9.5\text{{ storm}}\cdot\text{{h}}$; human $\text{{OR}} = 7.95$) closing monotherapy at $t_{{50}} = 16.4\text{{ h}}$ while predicting $24\text{{ h}}$ combination rescue. Dynamic specificity tracking coupled to multicellular kinetics thus establishes a quantitative framework for chrono-staged neuroimmune translation.

**Keywords:** clinical trial auditing; dynamic single-cell specificity; neuroinflammation; traumatic brain injury; status epilepticus; multicellular dynamical model; staged combination therapy

---

## Introduction

Acute brain injuries, spanning traumatic brain injury (TBI), acute ischemic and hemorrhagic stroke, status epilepticus, and hypoxic-ischemic or sepsis-associated encephalopathy, converge on a shared secondary neuroimmune and excitotoxic cascade, yet lack disease-modifying immunomodulatory pharmacotherapies. Although ultra-early arterial recanalization rescues ischemic penumbra in acute stroke, phase II and III trials targeting secondary neuroinflammation and excitotoxicity across acute brain injuries have repeatedly failed, including intravenous corticosteroids in the 10,008-patient MRC CRASH trial [1], acute progesterone in ProTECT III ($N = 882$) and SyNAPSe ($N = 1,195$) [2, 3], and delayed leukocyte-endothelial blockade in acute ischemic stroke. Even in the 12,737-patient CRASH-3 trial of tranexamic acid, survival benefit was strictly confined to patients treated within 3 hours of mild-to-moderate injury [4]. These clinical setbacks reflect a fundamental biological mismatch: treating a spatially compartmentalized, rapidly evolving tissue injury with static, pan-cellular drugs that simultaneously perturb protective and neurotoxic cell states. Single-cell and spatial transcriptomic studies have established that reactive microglia and astrocytes transition through distinct, time-dependent functional states during brain injury and neurodegeneration [5, 6]. However, quantitative frameworks capable of linking these dynamic single-cell transitions to clinical trial attrition and time-staged target selection remain lacking.

Recent advances in computational and multi-agent biomedical artificial intelligence (AI) have transformed how therapeutic targets are evaluated. Zhang et al. recently introduced the Virtual Biotech framework in *Science*, coordinating specialized AI modules across 55,984 clinical trials to demonstrate that drugs targeting genes with high static cell-type specificity ($\tau_0$, quantified via Yanai's tissue specificity index [7, 8]) are 48% more likely to reach market approval with 32% fewer adverse events. Concurrently, domain-specific computational agents have automated bioinformatics workflows in Biomni [9], pairwise tournament ranking in Co-Scientist [10], iterative target validation in Robin [11], reproducible tool generation in Paper2Agent [12], nanobody design in Virtual Lab [13], single-cell reanalysis in CellVoyager [14], and 502-million-cell atlas curation in scBaseCount [15]. In parallel, large-scale single-cell perturbation models including State [16], Tahoe-100M [17], ProteinTalks [18], UniPert-G2CP [19], and the Virtual Cell Challenge [20] have scaled in silico response prediction across cultured cell lines. Conceptual frameworks for multicellular systems biology [21] and virtual-cell dynamical models [22, 23, 24] have further underscored the need to model feedback loops across interacting tissue compartments.

Applying existing static-specificity and single-cell perturbation models directly to central nervous system (CNS) injury nevertheless faces three structural limitations. First, standard Yanai specificity $\tau_0$ is computed on healthy baseline atlases (`GSE180862` [25]), whereas peripheral myeloid infiltration, BBB breakdown, and reactive glial activation induce substantial specificity drift ($\Delta\tau(t)$) between baseline and the $12\text{{--}}24\text{{ h}}$ subacute clinical window. Genes that appear cell-type-specific in healthy tissue often become broadly expressed across multiple cell types at $12\text{{--}}24\text{{ h}}$ post-injury, turning apparent precision drugs into pleiotropic agents during actual clinical dosing. Second, bulk and pseudobulk transcriptomic profiles of injured hippocampus are frequently confounded by mechanical co-dissection of the adjacent choroid plexus and ependymal lining, together with enzymatic dissociation stress, which introduce high-$\tau_0$ ciliary and heat-shock chaperone artifacts into automated target rankings. Third, standard single-cell perturbation models evaluate dissociated cells without differential equations governing tissue-level paracrine feedback, making them unable to explain why an anti-inflammatory drug succeeds when given immediately after injury ($0\text{{ h}}$) but fails when delayed to $24\text{{--}}36\text{{ h}}$.

To overcome these three limitations, we developed **NeuroImmune-Virtual-Biotech** and coupled it to the five-variable dynamical model **vGlia-Niche**. Rather than relying on opaque black-box text generation, `NeuroImmune-Virtual-Biotech` is a deterministic, rule-governed pipeline organized into four verifiable modules (`Division 1`--`6`). These modules execute ClinicalTrials.gov protocol parsing and symmetric failure deconvolution, raw single-cell Yanai specificity tracking $\tau(t)$ [8] with Sarle's bimodality screening, choroid-plexus and dissociation-artifact filtering, and six-gate quality filtering followed by 1,000-iteration Bradley-Terry-Luce (BTL) and Elo tournament ranking [10]. To simulate tissue-level therapeutic timing, we coupled these prioritized targets to **vGlia-Niche**, a five-variable coupled Hill-type ordinary differential equation (ODE) dynamical model of multicellular positive-feedback kinetics [21] across microglia, astrocytes, chromatin/splicing state, and dentate-CA1 neurons, with kinetic time constants fixed directly from public longitudinal transcriptomic time-courses. We anchor our primary discovery and cross-species validation along the TBI, status epilepticus, and human surgical epilepsy continuum because this axis isolates intrinsic parenchymal neuroimmune-excitotoxic feedback from the variable arterial occlusion and reperfusion confounders of acute ischemic stroke, while providing living human neurosurgical hippocampal resections free from post-mortem RNA degradation. Using solely publicly archived clinical trials ($N = 230$ registries, $98,119$ participants) and 10 unpacked raw public transcriptomic cohorts (`GSE180862` [25], human `GSE209552` [26], `GSE269748` [27], `GSE247339`, `GSE277487`, `GSE226207` [28], `GSE302863`, `GSE319769`, `GSE330624`, and 129-sample `GSE63808` [29]), combined with historical stroke (`ACTION` natalizumab [30]) and chronic TBI (minocycline [31]) benchmarks, we demonstrate that empirical dynamic single-cell specificity $\tau(t)$ and a $16.4\text{{ h}}$ inflammatory lock-in tipping point govern clinical trial outcomes and define a staged three-compartment therapeutic strategy.

---

## Results

### Clinical trial endpoint deconvolution and dynamic $\tau(t)$ stratify 230 neuroinflammation and brain injury trials

Dynamic cell-type specificity and treatment initiation timing jointly govern clinical trial outcomes across acute brain injury and secondary epileptogenesis (**Fig. 1a**, **Table 1**, and **Supplementary Table S1**). To test this relationship, our auditing module (`Division 6`) queried the NIH/NLM ClinicalTrials.gov REST API v2 (https://clinicaltrials.gov/api/v2/studies) across three axes: TBI with secondary neuroinflammation or BBB breakdown ($n = 117$), TBI with post-traumatic epilepsy or excitotoxicity ($n = 236$), and status epilepticus with secondary neuroinflammation ($n = 17$). Four-step PRISMA screening deduplicated the $N_{{\text{{raw}}}} = 370$ records to $N_{{\text{{dedup}}}} = 349$ unique `NCT_ID` registries and excluded $n = 119$ ineligible records (**Extended Data Fig. 1a**). Exclusions comprised $n = 54$ off-axis metabolic, hepatic, neonatal, and neurodegenerative disorders (including $n = 30$ systemic encephalopathies, leaving $0$ hepatic encephalopathy and $0$ neonatal hypoxia-ischemia), $n = 38$ observational or diagnostic registries, $n = 18$ healthy-volunteer pharmacokinetic protocols, and $n = 9$ uninitiated withdrawals. This locked $N = 230$ interventional and circuit-stratified translational trials ($98,119$ participants), spanning $213$ acquired brain injury and status epilepticus trials ($92.6\%$, $75,209$ participants: $164$ TBI, $26$ status epilepticus, $14$ acute cerebrovascular or hypoxic-ischemic brain injury, and $9$ neuroinflammatory or autoimmune encephalopathies) and $17$ genetic ion-channel epileptic encephalopathy target-class benchmarks ($7.4\%$, $22,910$ participants, benchmarking conserved `SCN3A`/`SCN8A`/`SCN1A` channel mechanisms). Recruitment statuses comprised Completed ($n = 86$, $37.4\%$), Recruiting ($n = 40$, $17.4\%$), Unknown ($n = 30$, $13.0\%$), Not yet recruiting ($n = 25$, $10.9\%$), Terminated ($n = 23$, $10.0\%$), Withdrawn ($n = 9$, $3.9\%$), Active not recruiting ($n = 8$, $3.5\%$), Enrolling by invitation ($n = 8$, $3.5\%$), and Suspended ($n = 1$, $0.4\%$) registries (**Fig. 1a**).

Separating administrative trial halts from symmetric biological futility exposes a sharp divergence in failure rates across therapeutic classes (**Fig. 1b, c** and **Table 1**). Using a symmetric rule-locked classifier across all 33 halted registries and 86 completed studies, our auditing module inspected verbatim stop reasons, protocol amendments, and linked Phase III reports. This audit separated $n = 27$ operational stops (COVID-19 suspension, sponsor restructuring, supply-chain transfer, or slow accrual) from $n = 10$ verified scientific translational failures ($6$ explicit futility or toxicity halts plus $4$ completed Phase III trials with negative primary endpoints). Target specificity $\tau(t_0, t_1, t_2, t_3)$ was computed directly from our unpacked raw single-cell GEO cohorts (`GSE180862`, `GSE269748`, `GSE302863`, `GSE247339`, `GSE277487`, `GSE226207`, and `GSE209552`) without hand-coded drug $\tau$ tables or gate-penalty constants. Across the five classes, Pleiotropic / Pan-Cellular Pharmacotherapy ($n = 45$ trials, $13,145$ participants) exhibited the lowest baseline specificity (mean $\tau_0 = 0.601$), suffered subacute attrition (mean $\tau(t_2) = 0.569$, $\tau_{{\min}} = 0.458$, $\Delta\tau = -0.143$), and accounted for $9$ of the $10$ scientific failures ($20.0\%$ failure rate). By contrast, Niche-Restricted Pharmacotherapy & Biologics ($n = 32$ trials, $7,682$ participants; mean $\tau_0 = 0.801$, $\tau(t_2) = 0.807$, $\tau_{{\min}} = 0.756$) experienced only $1$ scientific failure ($3.1\%$: `NCT05226780` [2022-01-26], delayed `NBI-921352` monotherapy). Meanwhile, Neuromodulation & Autonomic Circuit Devices ($n = 38$ trials, $21,066$ participants; mean $\tau_{{\min}} = 0.765$), Cellular, Exosome & Paracrine Biologics ($n = 7$ trials, $647$ participants; mean $\tau_{{\min}} = 0.728$), and Biomarker-Guided, Nutritional & Circuit Rehabilitation ($n = 108$ trials, $55,579$ participants; mean $\tau_{{\min}} = 0.798$, $15$ operational stops) each recorded $0.0\%$ scientific failures (**Fig. 1b** and **Table 1**).

Interventions whose empirical single-cell specificity drops below $\tau_{{\min}} < 0.65$ carry a $21.88$-fold higher odds of scientific failure than cell-type-restricted therapies (**Fig. 1c, d**). Combining Moderate-$\tau$ Pleiotropic ($0.45 \le \tau(t) < 0.65$, $n = 16$, $43.8\%$ [$7/16$] failure) and Low-$\tau$ Pan-Cellular ($\tau(t) < 0.45$, $n = 26$, $3.8\%$ [$1/26$] failure) trials yielded a $19.05\%$ ($8/42$) failure rate, versus $1.06\%$ ($2/188$) in High-$\tau$ trials ($\tau_{{\min}} \ge 0.65$, $n = 188$, $85,669$ participants; $\text{{OR}} = 21.88$, Haldane-Anscombe $\text{{OR}} = 18.38$, Fisher's exact $P = 2.31 \times 10^{{-5}}$). This protection held across all six pre-specified sensitivity subcohorts (**Table 1** and **Extended Data Fig. 1a, b**). Restricting to Acquired Brain Injury and TBI trials ($n = 213$, $75,209$ participants, excluding $17$ genetic epilepsy benchmarks) yielded an $87.54$-fold Haldane-Anscombe odds ratio ($19.51\%$ [$8/41$] versus $0.00\%$ [$0/172$], $P = 1.04 \times 10^{{-6}}$). Completed or halted trials ($n = 119$) confirmed a $15.82$-fold odds ratio ($26.67\%$ [$8/30$] versus $2.25\%$ [$2/89$], $P = 2.28 \times 10^{{-4}}$), and scientifically evaluable non-COVID trials ($n = 92$) yielded $\text{{OR}} = 15.29$ ($32.00\%$ [$8/25$] versus $2.99\%$ [$2/67$], $P = 3.51 \times 10^{{-4}}$).

Direct head-to-head comparison within molecularly targeted drugs further confirmed that empirical single-cell specificity predicts pharmacological translation independent of devices or rehabilitation (**Table 1** and **Extended Data Fig. 1b**). Within Direct Molecular Target Pharmacotherapy & Biologics ($n = 60$ trials, $16,349$ participants, excluding devices, rehabilitation, and non-molecular nutritional, osmolar, or gas interventions), high-$\tau$ drugs ($n = 35$) reduced failure by $82.2\%$ relative to low/moderate-$\tau$ drugs ($5.71\%$ [$2/35$] versus $32.00\%$ [$8/25$], $\text{{OR}} = 7.76$, two-sided $P = 0.0120$, one-sided $P = 0.0095$; multivariable $\text{{OR}}_{{\text{{adj}}}} = 9.06$, Wald $P = 0.0095$). Continuous empirical single-cell $\tau$ rank-ordering within these $60$ molecular drug trials was significant across all stages (deconvolved $\tau_0$ $\text{{AUROC}} = 0.752$, $P = 0.0120$; acute $\tau(t_1)$ $\text{{AUROC}} = 0.826$, $P = 0.00115$; subacute $\tau(t_2)$ $\text{{AUROC}} = 0.774$, $P = 0.00632$; $\tau_{{\min}}$ $\text{{AUROC}} = 0.724$, $P = 0.0257$, versus unfiltered stop $\text{{AUROC}} = 0.398$, $P = 0.2755$). Restricting further to Acquired Brain Injury Direct Molecular Target Pharmacotherapy & Biologics ($n = 51$, $16,044$ participants) yielded $33.33\%$ ($8/24$) versus $0.00\%$ ($0/27$) failure (Haldane-Anscombe $\text{{OR}} = 28.33$, $P = 0.00116$) and continuous subacute $\tau(t_2)$ $\text{{AUROC}} = 0.858$ ($P = 0.00142$; $\tau(t_1)$ $\text{{AUROC}} = 0.843$, $P = 0.00221$; **Extended Data Fig. 1b**).

Protocol-specified treatment initiation windows interact strongly with dynamic target specificity $\tau_{{\min}}$ across a $16.4\text{{ h}}$ inflammatory tipping point (**Extended Data Fig. 1c, d**). Parsing verbatim `eligibilityCriteria` and `briefSummary` fields classified the $230$ registries into Stage 1 acute initiation before inflammatory lock-in ($\le 16.4\text{{ h}}$, $n = 18$), Stage 2 subacute initiation ($16.4\text{{--}}72\text{{ h}}$, $n = 91$), and Stage 3 chronic remodeling ($>72\text{{ h}}$, $n = 121$). A $2 \times 2$ factorial audit across the full Pharmacotherapy & Biologics cohort ($n = 84$ trials, $\text{{OR}} = 8.33$, $P = 0.0056$) and explicit window-gated protocols ($n = 57$, $47$ hour-gated and $10$ day-gated trials; Haldane-Anscombe $\text{{OR}} = 35.40$, $P = 0.00138$) revealed two consistent clinical patterns (**Extended Data Fig. 1d**). First, acute ($\le 16.4\text{{ h}}$) High-$\tau_{{\min}}$ drug trials (`NCT02997371` [2016-12-07] completed Phase 2 subcutaneous IL-1Ra anakinra initiated within $\le 12\text{{ h}}$ of severe TBI and `NCT06966830` [2025-05-04] not-yet-recruiting emergency intravenous lacosamide) recorded $0.0\%$ ($0/6$ in Drug/Biologic [$n = 84$] and $0/7$ in explicit window-gated trials [$n = 57$]) primary therapeutic failure as protocol benchmarks. Conversely, both High-$\tau_{{\min}}$ pharmacological failures (`2/36` [$5.56\%$] in Drug/Biologic; `0/33` [$0.00\%$] in explicit window-gated: `NCT05226780` [2022-01-26] `NBI-921352` and `NCT04639310` [2020-11-04] ganaxolone) occurred when single-target therapy was initiated after $>16.4\text{{ h}}$. Second, ultra-early administration ($\le 16.4\text{{ h}}$) failed to rescue Low/Moderate-$\tau_{{\min}}$ pleiotropic drugs: early progesterone regimens in `ProTECT III` ($\le 4\text{{ h}}$, `NCT00822900` [2009-01-14, ClinicalTrials.gov] [2]), `SyNAPSe` ($\le 8\text{{ h}}$, `NCT01143064` [2010-06-10] [3]), and `ProTECT II` ($\le 11\text{{ h}}$, `NCT00048646` [2002-11-04]) suffered a $42.86\%$ ($3/7$) scientific failure rate in the Drug/Biologic cohort ($75.00\%$ [$3/4$] in explicit window-gated protocols), whereas delayed ($>16.4\text{{ h}}$) Low/Moderate-$\tau_{{\min}}$ trials suffered $14.29\%$ ($5/35$) and $15.38\%$ ($2/13$) failure rates, respectively.

Combining empirical single-cell specificity $\tau_{{\min}}$ with BBB timing alignment maximizes clinical failure discrimination across the full 230-trial cohort (**Fig. 1e, f**). In nonparametric ROC analyses, predicting unfiltered registry stops (`Terminated + Withdrawn + Suspended`, $n = 33$) using static baseline $\tau_0$ alone yielded chance-level accuracy ($\text{{AUROC}} = 0.501$, 95% CI $0.397\text{{--}}0.608$, $P = 0.9928$). Removing operational COVID-19 and accrual stops increased static $\tau_0$ discrimination of scientific failures ($n = 10$) to $\text{{AUROC}} = 0.866$ (95% CI $0.793\text{{--}}0.927$, $P = 3.38 \times 10^{{-5}}$), with acute $\tau(t_1)$ reaching $\text{{AUROC}} = 0.883$ ($P = 1.45 \times 10^{{-5}}$) and subacute $\tau(t_2)$ achieving $\text{{AUROC}} = 0.854$ (95% CI $0.761\text{{--}}0.930$, $P = 6.15 \times 10^{{-5}}$; $\text{{AUROC}} = 0.887$, $P = 7.54 \times 10^{{-5}}$ in the $n = 213$ ABI cohort). Minimum trajectory $\tau_{{\min}}$ achieved $\text{{AUROC}} = 0.857$ (95% CI $0.765\text{{--}}0.929$, $P = 5.39 \times 10^{{-5}}$), and the composite trial score ($\text{{VBTCS}}$) achieved $\text{{AUROC}} = 0.860$ (95% CI $0.777\text{{--}}0.928$, $P = 7.89 \times 10^{{-5}}$). Incorporating protocol dosing-window alignment in the Chrono-Window Alignment Score ($\text{{CWAS}}_i = \text{{clip}}(0.50\,\tau_{{\min,i}} + 0.50\,\tau_i(t_2) + 1.5\,W_i, 0.18, 0.95)$) achieved $\text{{AUROC}} = 0.868$ (95% CI $0.788\text{{--}}0.935$, $P = 5.52 \times 10^{{-5}}$), representing a $\Delta\text{{AUROC}} = +0.367$ gain over unfiltered $\tau_0$ ($0.501$, $P < 0.001$; **Fig. 1e**). Comparing failed trials (`ProTECT III` `NCT00822900` [2009-01-14] [2], `SyNAPSe` `NCT01143064` [2010-06-10] [3], `INTREPID2566` `NCT00987454` [2009-09-29], `MgSO4` `NCT00004817` [2000-02-24], `Dexanabinol` `NCT00004730` [2000-02-25], `BIIB093` `NCT03061565` [2017-02-14], `NBI-921352` `NCT05226780` [2022-01-26]; `CRASH-1` [1], `ACTION` [30], `Minocycline` [31]) against pre-lock-in protocol benchmarks (`Anakinra` `NCT02997371` [2016-12-07, completed Phase II], `Lacosamide` `NCT06966830` [2025-05-04, not yet recruiting]; external Phase II `BIIB093` `NCT01454154` [2011-10-11]) confirmed this separation (**Fig. 1f**).

#### Figure 1

#### Table 1

### Cross-dataset single-cell $\tau(t)$ trajectories expose static specificity drift and four functional gene groups

To determine why static baseline atlases misclassify subacute clinical targets, we tracked $133$ consensus neuroimmune candidate genes across 10 genuinely unpacked public transcriptomic cohorts ($982,859$ single cells or nuclei and $197$ bulk/sorted/microarray samples), revealing marked cell-type specificity drift during injury progression (**Fig. 2a, b**, **Supplementary Table S2**, and **Supplementary Table S3**). From a 92-series NCBI GEO census, our specificity and purity modules (`Division 1` and `Division 2`) reconstructed four-stage empirical single-cell Yanai $\tau(t)$ trajectories directly from raw `.mtx.gz` and count matrices for all $133$ candidate genes (`DESeq2` $P_{{\text{{adj}}}} < 0.05$). Stage $t_0$ anchored baseline single-cell specificity in murine hippocampal scRNA-seq (`GSE180862` [25], $18,162$ cells across $24$ parenchymal brain cell clusters after excluding choroid plexus `CHOR` and ependymal `EPEN` contamination across Sham $t_0$, $24\text{{ h}}$ $t_1$, and $7\text{{ d}}$ $t_2$). Stage $t_1$ tracked acute multi-model TBI and microglial neuroinflammatory scRNA-seq (`GSE269748` [27], $431,198$ nuclei across $36$ libraries, and `GSE302863`, $60,574$ cells across $5$ samples). Stage $t_2$ captured subacute neuroinflammatory injury across murine hippocampal and cortical TBI scRNA-seq (`GSE247339`, $201,564$ cells across $41$ samples; `GSE226207` [28], $83,833$ cells across $15$ samples; `GSE277487`, $162,907$ nuclei across $12$ samples), kainate epileptogenesis bulk RNA-seq (`GSE319769`, $n = 36$ samples across D3, D7, and D14), and FANS-sorted $\text{{NeuN}}^+/\text{{NeuN}}^-$ epileptic hippocampal nuclei (`GSE330624`, $n = 32$ samples). Stage $t_3$ bridged acute human surgically resected TBI parenchyma (`GSE209552` snRNA-seq, $24,621$ nuclei across $17$ surgical TBI samples from $30$ GSM records [26]) to chronic human surgical temporal lobe epilepsy hippocampus (`GSE63808`, $N = 129$ official GEO biopsy microarrays [29]), with every single-cell cohort passing our lineage marker purity gate ($\ge 3.0\times$; **Supplementary Table S3**).

Joint evaluation of baseline specificity $\tau_0$, Sarle's bimodality coefficient $BC$, and four-stage empirical single-cell trajectories $\tau(t_0 \rightarrow t_1 \rightarrow t_2 \rightarrow t_3)$ classified the $133$ candidates into four functional groups (`Archetype I`--`IV`) with distinct subacute specificity profiles (four-group subacute $\tau(t_2)$ Kruskal-Wallis $H = 22.37$, $P = 5.45 \times 10^{{-5}}$, and drift $\Delta\tau = \tau(t_2) - \tau_0$ Kruskal-Wallis $H = 8.70$, $P = 0.0336$; **Fig. 2a--c**). **Group I** (`Archetype I`, $n = 26$ persistent glial and vascular switches) comprises innate immune, reactive astrocyte, and neurovascular regulators exemplified by `Plin4` ($\tau_0 = 0.946 \rightarrow \tau(t_2) = 0.857 \rightarrow \tau(t_3) = 0.982$), `Folh1` ($0.913 \rightarrow 0.781 \rightarrow 0.944$), and `Ahnak` ($0.887 \rightarrow 0.900 \rightarrow 0.754$). Additional Group I hubs include `Tlr4` ($0.847 \rightarrow 0.886 \rightarrow 0.886$) and `Zfp36l1` ($0.826 \rightarrow 0.673 \rightarrow 0.608$), with the group maintaining high subacute parenchymal restriction (`GSE247339` and `GSE226207` mean $\tau(t_2) = 0.779$, `GSE180862` 7-day hippocampal $\tau = 0.858$). **Group II** (`Archetype II`, $n = 44$ persistent neuronal gatekeepers) encompasses dentate granule and dorsal CA1 ion-channel, splicing, and synaptic scaffolding regulators down-regulated during injury, led by `Rnf112` ($\tau_0 = 0.838 \rightarrow \tau(t_2) = 0.924 \rightarrow \tau(t_3) = 0.810$), `Scn3a` ($0.777 \rightarrow 0.815 \rightarrow 0.774$), and `Scn3b` ($0.841 \rightarrow 0.884 \rightarrow 0.896$). Additional representative gatekeepers include `Elk1` ($0.790 \rightarrow 0.755 \rightarrow 0.592$), `Rapgefl1` ($0.808 \rightarrow 0.922 \rightarrow 0.768$), and `Lin7b` ($0.831 \rightarrow 0.927 \rightarrow 0.287$), with Group II maintaining stable neuronal restriction across all stages (mean $\tau_0 = 0.822 \rightarrow \tau(t_2) = 0.808$; mean $\Delta\tau = -0.015$, median $-0.014$; **Table 2**).

Static baseline filtering fails to detect subacute pan-cellular spreading and co-dissection artifacts captured by **Groups III and IV** (**Fig. 2b--d**). **Group III** (`Archetype III`, $n = 31$ subacute-delocalizing decoys) shows high baseline restriction (mean $\tau_0 = 0.779$, median $0.789$) but loses cellular restriction during subacute neuroinflammation (mean $\tau(t_2) = 0.687$, mean $\Delta\tau = -0.092$, median $-0.065$; subacute $\tau(t_2)$ Mann-Whitney $U = 1528.0$, $P = 2.02 \times 10^{{-4}}$ versus Tier-1 targets [$0.788$] and $U = 1094.0$, $P = 9.01 \times 10^{{-6}}$ versus Group II neuronal gatekeepers [$0.808$], $\Delta\tau$ $P = 0.00466$). Direct single-cell Yanai $\tau$ in subacute hippocampal/cortical TBI scRNA-seq (`GSE247339`, $41$ samples) and subacute cortical injury scRNA-seq (`GSE226207` [28], $15$ samples) independently confirmed severe subacute delocalization in Group III decoys compared with Group II gatekeepers (`GSE247339` mean $\tau = 0.679$ versus $0.795$, Mann-Whitney $P = 0.0084$, and Tier-1 $0.797$ versus non-Tier-1 $0.742$, $P = 0.0469$; `GSE226207` mean $\tau = 0.687$ versus $0.819$, $P = 0.0096$; **Supplementary Table S2** and **Supplementary Table S3**). Static $\tau_0 \ge 0.65$ filtering admits $24$ high-$\tau_0$ Group III decoys and $22$ high-$\tau_0$ Group IV holds ($46$ false positives out of $116$ baseline-passing genes; **Fig. 2b, c**). **Group IV** (`Archetype IV`, $n = 32$ holds and artifacts; mean $\tau_0 = 0.722 \rightarrow \tau(t_2) = 0.720$) comprises $28$ low-concordance or non-conserved transcripts and $4$ anatomical or chaperone artifacts (`Ccdc103`, `Alkbh5`, `Canx`, `Hspa5`) rejected by `Division 2` due to choroid plexus (`CPE`/`CHOR`), meningeal fibroblast (`FB`), or ubiquitous endoplasmic reticulum chaperone enrichment (**Fig. 2a, c, d**).

Conserved inverse glia-neuron coupling and subacute splicing remodeling distinguish the $70$ Tier-1 targets (Groups I and II combined) across murine and human datasets (**Fig. 2d--f**). Single-cell expression mapping across $10$ hippocampal cell types (`GSE180862`: `aMG`, `MAC`, `MG`, `ASC`, `END`, `SMC`, `DG`, `CA1d`, `INT`, `CPE`) confirmed clean separation between glial/vascular up-regulated switches (`C3ar1`, `Relb`, `Tlr4`, `Folh1`, `Plin4`, `Ahnak`) and dentate/CA1d neuronal gatekeepers (`Rnf112`, `Kctd4`, `Scn3a`, `Scn3b`, `Gabrd`, `C1ql2`, `Ryr2`, `Elk1`; **Fig. 2d**). Projecting the $70$ Tier-1 murine targets into the official $129$-sample human surgical hippocampus microarray cohort (`GSE63808`, `GSM1565578`--`GSM1565706` [29]) revealed strong inverse correlation between reactive glial/vascular expression and dentate/CA1d neuronal gate integrity (Pearson $r = -0.549$, $P = 1.67 \times 10^{{-11}}$; Spearman $\rho = -0.618$, $P = 6.46 \times 10^{{-15}}$; **Fig. 2e**). Using a strict leave-one-gene-out human coupling calculation (excluding each candidate gene from the composite axis to eliminate part-whole auto-correlation), Tier-1 targets exhibited significantly stronger human hippocampal conservation than non-Tier-1 candidates (mean leave-self-out $|r| = 0.296$ versus $0.168$, Mann-Whitney $P = 5.42 \times 10^{{-6}}$; Top-21 portfolio mean $|r| = 0.440$). Pure sample-level pseudobulk and bulk ROC evaluation across our external cohorts further demonstrated consistent discrimination by Tier-1 and Top-21 targets in multi-model TBI snRNA-seq (`GSE269748`, Top-21 mean sample $\text{{AUROC}} = 0.840$, single-cell $\tau_1 = 0.858$ versus $0.758$ for non-Tier-1) and subacute kainate epileptogenesis (`GSE319769`, Tier-1 mean sample $\text{{AUROC}} = 0.745$ versus $0.713$, Top-21 $= 0.766$). Similar sample-level discrimination held in FANS-sorted epileptic hippocampal nuclei (`GSE330624`, Tier-1 mean $\text{{AUROC}} = 0.758$ versus $0.721$, Top-21 $= 0.792$), accompanied by a $3.44$-fold odds enrichment of subacute differential expression and splicing remodeling in `GSE319769` ($22.9\%$ [$16/70$] versus $7.9\%$ [$5/63$], two-sided Fisher's exact $P = 0.0297$; **Fig. 2f**).

Independent gene-level benchmarking across all 10 unpacked public transcriptomic cohorts confirmed the cross-species and multi-model reproducibility of the $70$ Tier-1 and $21$ top-ranked targets without any synthetic composite score blending (**Extended Data Fig. 2a--d**, **Supplementary Table S2**, and **Supplementary Table S3**). Across the $70$ Tier-1 targets versus $63$ non-Tier-1 candidates, pure single-cell specificity and sample-level pseudobulk discrimination remained consistently higher in murine multi-timepoint CCI snRNA-seq (`GSE277487`: Tier-1 single-nucleus $\tau = 0.779$ versus $0.724$, Top-21 $= 0.794$, Top-21 sample $\text{{AUROC}} = 0.729$) and murine brain injury microglia/macrophage scRNA-seq (`GSE302863`: Tier-1 sample $\text{{AUROC}} = 0.717$ versus $0.688$, Top-21 $= 0.733$, Tier-1 single-cell $\tau_1 = 0.754$). Superior single-cell specificity also persisted in subacute cortical injury scRNA-seq (`GSE226207` [28]: Tier-1 single-cell $\tau_2 = 0.761$ versus $0.722$, Top-21 sample $\text{{AUROC}} = 0.703$) and human acutely resected severe TBI snRNA-seq (`GSE209552` [26]: Tier-1 single-nucleus $\tau_3 = 0.717$ versus $0.696$, Top-21 $= 0.745$; **Extended Data Fig. 2a--d**).

#### Figure 2

#### Table 2

### Leave-one-gate-out ablation and 1,000-iteration tournament ranking validate the six-gate filtering pipeline

To test whether each quality filter is necessary to eliminate these subacute decoys and anatomical artifacts, we performed a systematic leave-one-gate-out ablation across $10$ pipeline configurations, demonstrating non-redundant protection across all six gates (**Fig. 3a--c** and **Table 3**). In the unfiltered bulk baseline (Configuration 1: standard `DESeq2` $P_{{\text{{adj}}}} < 0.05$, $n = 133$), mean baseline specificity was $\tau_0 = 0.773$, subacute specificity was $\tau(t_2) = 0.740$, human `GSE63808` ($N = 129$) leave-self-out absolute correlation was $|r| = 0.235$, external cohort discrimination (`GSE319769` + `GSE269748`) was $\text{{AUROC}} = 0.730$, choroid artifact leakage was $3.0\%$ ($4/133$), and six-gate precision was only $52.6\%$ ($70/133$). Applying the static Yanai threshold of Zhang et al. [7] alone (Configuration 2: $\tau_0 \ge 0.65$ without spatial purity or dynamic subacute gates, $n = 116$) raised baseline $\tau_0$ to $0.824$ but retained subacute decoys ($\tau(t_2) = 0.781$), yielded modest human correlation ($|r| = 0.248$), retained choroid leakage ($0.9\%$), and achieved only $60.3\%$ precision (**Table 3**). Among single-gate ablations (Configurations 3 to 7), removing Gate 1 (Choroid/Ependymal Purity; Configuration 3, $n = 62$) re-admitted ciliary contamination ($1.6\%$ artifact leakage, $98.4\%$ precision), whereas removing Gate 2 (Multi-Cohort Concordance; Configuration 4, $n = 69$) admitted single-study noise ($88.4\%$ precision). Removing Gate 3 (Dynamic $\tau(t) \ge 0.65$; Configuration 5, $n = 67$) reduced neuronal safety sparing from $0.838$ to $0.822$ and subacute specificity to $\tau(t_2) = 0.754$ ($91.0\%$ precision), while removing Gate 4 (Human Conservation; Configuration 6, $n = 71$) caused the largest single-gate precision drop ($85.9\%$). Similarly, removing Gate 5 (Sarle Bimodality Switch; Configuration 7, $n = 66$) admitted non-bimodal transcripts ($92.4\%$ precision, $\tau(t_2) = 0.777$; **Fig. 3b, c**).

Combining all six quality gates with Bradley-Terry-Luce (BTL) and Elo pairwise tournament ranking isolates a top-ranked $21$-target portfolio along the murine-human Pareto frontier (**Fig. 3b--e** and **Table 3**). Enforcing all six gates simultaneously (Configuration 8: Full 6-Gate Pass, $n = 70$ Tier-1 targets) achieved $100.0\%$ internal precision retention, $0.0\%$ choroid leakage, mean $\tau_0 = 0.810$, subacute $\tau(t_2) = 0.779$, human leave-self-out correlation $|r| = 0.296$, external cohort $\text{{AUROC}} = 0.745$, and neuronal safety sparing of $0.838$. Adding the BTL pairwise tournament win-rate requirement (Configuration 9: $n = 43$ targets with BTL win rate $\ge 0.50$ across $1,000$ Monte Carlo rounds) elevated subacute specificity to $\tau(t_2) = 0.789$, human correlation to $|r| = 0.369$, and external cohort discrimination to $\text{{AUROC}} = 0.767$. The top-ranked 21-target portfolio (Configuration 10: $6/6$ gates plus Elo rating $\ge 1850$, $n = 21$ targets) achieved peak baseline and subacute specificity ($\tau_0 = 0.843$, $\tau(t_2) = 0.797$), peak human hippocampal conservation (leave-self-out $|r| = 0.440$, an $87.2\%$ gain over bulk `DESeq2` [$0.235$], with external $\text{{AUROC}} = 0.766$), and peak neuronal safety sparing ($0.865$).

Within the top-25 Tier-1 target ledger (**Table 2**), the highest-ranked gene was the dentate/CA1d neuronal ring-finger scaffold `Rnf112` ($\text{{Elo}} = 2087.7$, $\text{{BTL}} = 0.947$, $\tau_0 = 0.838$, $\tau(t_2) = 0.924$, human leave-self-out $r = -0.492$). Next ranked were the neurovascular pericyte and smooth-muscle regulator `Plin4` ($\text{{Elo}} = 2014.0$, $\tau_0 = 0.946$, $\tau(t_2) = 0.857$, $\tau(t_3) = 0.982$, external sample $\text{{AUC}} = 0.935 / 0.554$) and the voltage-gated sodium channel subunit `Scn3a` ($\text{{Elo}} = 1997.4$, $\text{{BTL}} = 0.834$, $\tau_0 = 0.777$, $\tau(t_2) = 0.815$, human $r = -0.447$). Rounding out the top hubs were the transcription factor `Elk1` ($\text{{Elo}} = 1991.3$), the synaptic Rap-GEF scaffold `Rapgefl1` ($\text{{Elo}} = 1988.3$, human $r = -0.666$), and the reactive astrocyte glutamate carboxypeptidase `Folh1` ($\text{{Elo}} = 1914.5$, $\tau_0 = 0.913$, $\tau(t_2) = 0.781$, $\tau(t_3) = 0.944$, human $r = -0.262$; **Fig. 3d, e**), whereas our spatial purity filter (`Division 2`) cleanly isolated and rejected the four contamination artifacts (`Ccdc103`, `Alkbh5`, `Canx`, and `Hspa5`; **Fig. 3f**).

Boolean six-gate UpSet decomposition and step-by-step decision logs make the filtering and ranking logic of `NeuroImmune-Virtual-Biotech` fully transparent (**Extended Data Fig. 3a--d** and **Supplementary Table S4**). Across all $133$ candidates, $70$ passed all six gates (`111111`, mean $\text{{Elo}} = 1735.6$), $16$ failed exclusively at Gate 4 (`111011`, weak human conservation, mean $\text{{Elo}} = 1504.4$), and $12$ failed exclusively at Gate 2 (`101111`, mean $\text{{Elo}} = 1281.5$). Another $9$ candidates failed exclusively at Gate 3 (`110111`, subacute-delocalizing decoys, mean $\text{{Elo}} = 1231.7$) and $6$ failed exclusively at Gate 5 (`111101`, mean $\text{{Elo}} = 1524.5$), while `Ccdc103` (`011111`, $\text{{Elo}} = 1303.2$) passed Gates 2 through 6 but was rejected solely by the Gate 1 spatial purity filter (**Extended Data Fig. 3a**). In *Decision Pattern I* (anatomical and chaperone-artifact rejections), initial screening flagged `Ccdc103` ($\tau_0 = 0.829$), `Hspa5`, and `Alkbh5`, but Gate 1 rejected them upon detecting severe choroid-plexus and ciliary border contamination (`Ccdc103` `Artifact_Ratio = 0.671`), pure choroid-plexus epithelial chaperone enrichment (`Hspa5` `top1 = CPE`, `Artifact_Ratio = 1.000`, `Safety = 0.097`), and meningeal/perivascular fibroblast border contamination (`Alkbh5` `top1 = FB`, `Artifact_Ratio = 0.841`, `Safety = 0.357`; alongside `Canx` `Artifact_Ratio = 0.733`; **Extended Data Fig. 3b, d**). In *Decision Pattern II* (subacute decoy and non-conserved rejections), static $\tau_0$ screening (`Configuration #2`) favored `C3ar1` ($\tau_0 = 0.950$), `Foxred2` ($\tau_0 = 0.762 \rightarrow \tau(t_2) = 0.651$, $\Delta\tau = -0.111$, `GSE247339` $\tau = 0.612$), and `Flt1` ($\tau_0 = 0.973 \rightarrow \tau(t_2) = 0.971$, $\Delta\tau = -0.003$). Multi-cohort and cross-species Gates 2 and 4 subsequently rejected `C3ar1` (`101111`), `Foxred2` (`111011`, human $|r| = 0.211 < 0.25$), and `Flt1` (`111011`, human $|r| = 0.107 < 0.25$ and human acute TBI sample $\text{{AUROC}} = 0.600 < 0.80$; **Extended Data Fig. 3c, d**).

Cross-module decision rules also resolved apparent cross-species sign inversions and intracellular druggability constraints (**Extended Data Fig. 3b--d** and **Supplementary Table S4**). In *Decision Pattern III* (cross-species phase-decoupling resolution), `Folh1` ($\tau(t_2) = 0.781$, $\tau(t_3) = 0.944$, `#13`), `Tlr4` ($\tau(t_2) = 0.886$, `#17`), and `Plin4` ($\tau(t_2) = 0.857$, $\tau(t_3) = 0.982$, `#2`) exhibited strong acute/subacute murine up-regulation (`UP`) paired with negative correlation in chronic human surgical tissue (leave-self-out $r = -0.262, -0.397, -0.402$). Our trajectory and druggability modules (`Division 3` and `Division 5`) resolved this divergence as stage-dependent decoupling between the acute/subacute glial surge (`Stage 1/2`) and end-stage sclerotic tissue loss (`Stage 3`), assigning `Tlr4` and `Plin4` to Stage 1 and `Folh1` to Stage 2. In *Decision Pattern IV* (intracellular versus surface modality assignment), `Rnf112` (`#1`), `Scn3a` (`#3`), and `Kctd4` (`#21`) passed all six gates, but `Division 5` ruled out conventional small-molecule inhibition for the intracellular ring-finger ubiquitin ligase `Rnf112` (which is down-regulated during injury). Instead, `Division 5` paired upstream glial cytokine braking plus intrathecal splice-switching antisense oligonucleotide (ASO) restoration of `Rnf112` with high-$\text{{CNS MPO}}$ ($\ge 4.5$) state-dependent channel modulation of surface `Scn3a` and `Kctd4` (**Extended Data Fig. 3b--d**).

#### Figure 3

#### Table 3

### The `vGlia-Niche` multicellular dynamical model uncovers an irreversible inflammatory lock-in threshold

Because target specificity alone cannot explain why delayed anti-inflammatory dosing fails, coupling `NeuroImmune-Virtual-Biotech` to the five-variable **vGlia-Niche** ODE model revealed a subacute ($>16\text{{--}}24\text{{ h}}$) inflammatory lock-in threshold (**Fig. 4a**). Governed by coupled Hill-type differential equations across $0$ to $72\text{{ h}}$, `vGlia-Niche` tracks endogenous homeostatic checkpoint tone $V(t)$, activated microglial inflammatory surge $M(t)$ (`Tlr4`, `Zfp36l1`, `Tnfaip3`, `Sulf2`), and reactive astrocyte and neurovascular BBB cascades $A(t)$ (`Folh1`, `Plin4`, `Ahnak`, `Cnksr3`, `Ntrk2`, validated in cortical glial injury scRNA-seq `GSE226207` [28] and FANS-sorted glial nuclei `GSE330624`). These upstream glial states drive the subacute transcriptional and alternative splicing lock-in state $L(t)$ (anchored by subacute differential splicing in `GSE319769` and multi-timepoint snRNA-seq/scRNA-seq injury progression in `GSE277487` and `GSE302863`) together with dentate/CA1d neuronal channel gate integrity $C(t)$ and synaptic scaffolding state $S(t)$ (`Rnf112`, `Scn3a`, `Scn3b`, `Elk1`, `Rapgefl1`, `Lin7b`).

Loss of homeostatic checkpoint tone triggers a positive-feedback state transition that traps subacute hippocampal circuits in a self-sustaining inflammatory lock (**Fig. 4a--c**). We simulated four public-cohort-anchored baseline and early-intervention conditions (`Sham Baseline`, `Moderate TBI Insult`, `Severe Unbraked TBI/SE`, and `Early Stage-1 Glial Brake [0 h]`) alongside four counterfactual delayed-intervention regimens (`Subacute Stage-1 Brake [12 h]`, `Late Stage-1 Brake [36 h]`, `Folh1 Inhibitor [24 h]`, and `24 h Staged Triple-Niche Combo`). Across these trajectories, loss of checkpoint tone $V(t)$ ($0.62 \rightarrow 0.06$) triggers a rapid microglial surge ($M(72\text{{ h}}) = 0.876$, normalized storm readout $97.3\%$ versus $83.9\%$ observed in public `GSE180862`/`GSE269748`) and secondary astrocyte/BBB reactivity ($A(72\text{{ h}}) = 0.810$, readout $90.0\%$ versus $65.4\%$ observed in `GSE330624`/`GSE226207`), locking transcriptional/splicing state $L(t)$ between $12$ and $24\text{{ h}}$ (**Fig. 4a, b**). In subacute hippocampal injury (`GSE319769`) and chronic human temporal lobe epilepsy (`GSE63808`), surviving dentate granule and dorsal CA1 neurons in the pericontusional or epileptogenic zone at $24\text{{--}}72\text{{ h}}$ remain viable rather than uniformly necrotic. Instead, they are trapped in persistent transcriptional/splicing remodeling ($L(72\text{{ h}}) = 86.1\%$ versus $70.5\%$ observed in `GSE277487`/`GSE302863`) and neuronal gate suppression ($C(72\text{{ h}}) = 19.9\%$ versus $30.6\%$ observed in `GSE319769`/`GSE63808`, compared with $98.5\%$ predicted [$63.2\%$ observed] in `Sham Baseline` and $73.2\%$ predicted [$70.0\%$ observed] in `Moderate TBI`). In the two-dimensional ($M(t), C(t)$) phase plane (**Fig. 4c**), once cumulative glial storm exposure crosses the critical tipping threshold (separatrix), Hill-type positive feedback ($n = 4$) locks $L(t)$ into a pathological low-gate attractor.

Crossing this inflammatory lock-in threshold closes the single-drug anti-inflammatory therapeutic window at $t_{{50}} = 16.4\text{{ h}}$ with strong agreement across 16 empirical public multi-cohort state readouts (**Fig. 4b--f**). Administering a Stage-1 microglial/endothelial brake at $0\text{{ h}}$ prevents threshold crossing, keeping transcriptional lock low ($L(72\text{{ h}}) = 6.2\%$ versus $11.1\%$ observed), preserving neuronal gate integrity ($C(72\text{{ h}}) = 80.1\%$ versus $70.1\%$ observed), and restraining the composite network hyperexcitability index to $35.5$ (compared with $85.7$ in `Severe Unbraked TBI/SE`). Conversely, initiating Stage-1 monotherapy at $36\text{{ h}}$ (after $L(t)$ has locked) partially lowers upstream microglial activation ($63.4\%$) but fails to reverse downstream astrocyte reactivity ($81.0\%$) or transcriptional lock ($80.8\%$), leaving neuronal gate integrity collapsed ($C(72\text{{ h}}) = 25.4\%$) and network hyperexcitability high ($80.7$; **Fig. 4b, c, f**). A continuous dosing-initiation sweep ($t_{{\text{{start}}}} \in [0, 48]\text{{ h}}$) pinpointed the monotherapy window cliff at $t_{{50}} = 16.4\text{{ h}}$ (**Fig. 4d**). We next benchmarked `vGlia-Niche` against $n = 16$ empirical public multi-cohort reference state readouts derived directly from raw GEO matrices across four modules: `Microglial storm M` ($n = 4$, `GSE180862`/`GSE269748`/`GSE247339`), `Astrocyte/BBB state A` ($n = 4$, `GSE330624`/`GSE226207`), `Transcriptional lock L` ($n = 4$, `GSE277487`/`GSE302863`), and `Neuronal gate C` ($n = 4$, `GSE319769`/`GSE63808`). Across all $16$ empirical state readouts, `vGlia-Niche` achieved strong quantitative agreement in a 2-parameter global linear fit (Pearson $r = 0.935$, $R^2 = 0.874$, $P = 1.11 \times 10^{{-7}}$; **Fig. 4e, f**), 16-fold leave-one-readout-out cross-validation ($r_{{\text{{LORO}}}} = 0.908$, $R^2_{{\text{{LORO}}}} = 0.823$, $P = 1.18 \times 10^{{-6}}$, $\text{{RMSE}} = 9.83\%$), and 4-fold leave-one-condition-out cross-validation ($r_{{\text{{LOCO}}}} = 0.909$, $R^2_{{\text{{LOCO}}}} = 0.821$, $P = 1.10 \times 10^{{-6}}$, $\text{{RMSE}} = 9.90\%$).

Individual-patient profiles across all $N = 129$ official GEO human surgical hippocampi and $1,000$ full 5-ODE Latin-hypercube perturbations corroborate this lock-in threshold (**Extended Data Fig. 4a--d**). Projecting all $N = 129$ epileptic hippocampal microarrays (`GSE63808` [29], `GSM1565578`--`GSM1565706`) across five equal-frequency glial Z-score quintiles ($N = [26, 26, 25, 26, 26]$, centers `-0.61`, `-0.32`, `-0.08`, `+0.21`, `+0.79`) revealed a sharp jump in severe gate collapse (`Neuronal Z <= -0.454`, $q_{{25}}$) across the upper-quartile separatrix (`Glial Z >= +0.312`, $q_{{75}}$), rising from $7.7\% \rightarrow 11.5\% \rightarrow 16.0\% \rightarrow 26.9\% \rightarrow 65.4\%$ (**Extended Data Fig. 4a**). Post-separatrix patients ($n = 33$, `Glial Z >= +0.312`) exhibited a $57.58\%$ ($19/33$) collapse rate (mean $Z = -0.485$) versus $14.58\%$ ($14/96$) in pre-separatrix patients ($n = 96$, mean $Z = +0.167$; $\text{{OR}} = 7.95$, Fisher's exact $P = 3.83 \times 10^{{-6}}$, Mann-Whitney $U = 2594.0$, $P = 1.34 \times 10^{{-8}}$; **Extended Data Fig. 4a, b**). Across $1,000$ 5-ODE integrations under $\pm 20\%$ Latin-hypercube variation of rate constants, Hill $n \in [3.2, 4.8]$, and $E_{{\text{{crit}}}}$, both the critical threshold ($95\%$ interval $7.7\text{{--}}11.3\text{{ storm}}\cdot\text{{h}}$) and monotherapy window cliff ($t_{{50}}$ nominal $16.4\text{{ h}}$, LHS median $16.6\text{{ h}}$, IQR $15.4\text{{--}}17.6\text{{ h}}$, $95\%$ interval $13.8\text{{--}}19.6\text{{ h}}$, $100.0\%$ within $12\text{{--}}24\text{{ h}}$; **Extended Data Fig. 4c**) remained invariant. Delayed $36\text{{ h}}$ monotherapy achieved $0.0\%$ rescue ($C(72\text{{ h}}) = 25.8\% \pm 3.2\%$, median $L(72\text{{ h}}) = 0.808$) versus $100.0\%$ rescue ($C(72\text{{ h}}) = 97.9\% \pm 0.4\% \ge 85\%$, median $L(72\text{{ h}}) = 0.012$) under delayed $24\text{{ h}}$ Triple-Niche Combination therapy (**Extended Data Fig. 4d**).

#### Figure 4

### Threshold mechanics, 24-hour synergy surface, and a three-stage therapeutic blueprint for clinical translation

To overcome this post-threshold lock-in, counterfactual dynamical simulations predict that a staged three-compartment combination initiated at $24\text{{ h}}$ actively reverses inflammatory lock-in (**Fig. 5a--c**). Integrating cumulative glial storm exposure $E_{{\text{{auc}}}}(t) = \int_0^t [0.65\,M(\tau) + 0.35\,A(\tau)]\,d\tau$ across all regimens confirmed that crossing $E_{{\text{{crit}}}} = 9.5\text{{ storm}}\cdot\text{{h}}$ between $12$ and $24\text{{ h}}$ saturates the transcriptional/splicing lock $L(t)$ (**Fig. 5a, b**). Delayed monotherapy at $36\text{{ h}}$ or isolated `Folh1` inhibition at $24\text{{ h}}$ ($C(72\text{{ h}}) = 24.6\%$, hyperexcitability index $81.4$) remains trapped above this lock-in threshold. By contrast, a delayed $24\text{{ h}}$ Triple-Niche Combination pairing Stage-1 microglial brake restoration with subacute astrocyte `Folh1`/GCPII inhibition and dentate/CA1d channel stabilization (`Scn3a`/`Rnf112`/`Kctd4`) unlocks $L(t)$ ($0.60 \rightarrow 0.012$; **Fig. 5b**), restoring predicted neuronal gate integrity to $C(72\text{{ h}}) = 98.2\%$ and reducing the network hyperexcitability index to $11.6$ (**Fig. 4f** and **Fig. 5b**). Mechanistically, `Folh1`/GCPII inhibition blocks astrocytic cleavage of $N$-acetylaspartylglutamate (NAAG) into excitotoxic glutamate and restores neuroprotective $\text{{NAAG--mGluR3}}$ signaling; when combined with innate cytokine restraint (`Tlr4`/`Tnfaip3`), state-dependent $\text{{Na}}_V1.3$ modulation (`Scn3a`/`Scn3b`), and ubiquitin-ligase scaffold preservation (`Rnf112`), this regimen interrupts the cross-cellular $\text{{Ca}}^{{2+}}$-depolarization loop sustaining transcriptional and splicing lock-in. Simulating the $11 \times 11$ dose-response synergy surface at $t = 24\text{{ h}}$ confirmed super-additive contours that recover predicted neuronal gate integrity $C(72\text{{ h}})$ from $19.9\%$ to $>90.0\%$ only when upstream glial/astrocytic and downstream neuronal gates are co-targeted (**Fig. 5c**).

Mapping the $70$ Tier-1 targets across subacute specificity $\tau(t_2)$ and Elo rating establishes a three-stage therapeutic portfolio aligned with BBB pharmacokinetics (**Fig. 5d** and **Table 2**). In **Stage 1** (Acute $0\text{{--}}16.4\text{{ h}}$ initiation, $0\text{{--}}24\text{{ h}}$ or $6\text{{ h--}}7\text{{ d}}$ vascular window; $n = 14$ Tier-1 targets), microglial innate sensors (`Tlr4`, `Zfp36l1`, `Tnfaip3`, `Sulf2`) and luminal neurovascular switches (`Plin4`, `Ahnak`, `Klf2`) dominate while $E_{{\text{{auc}}}}(t) < 9.5\text{{ storm}}\cdot\text{{h}}$. During this early window, selective innate antagonists (IL-1R1 or TLR4 blockade), transcutaneous auricular vagus nerve stimulation (`taVNS`), and vascular-protective agents can abort the microglial surge before lock-in occurs (**Fig. 5a, d**). In **Stage 2** (Subacute $12\text{{--}}24\text{{ h}}$ initiation, $12\text{{ h--}}7\text{{ d}}$ / $28\text{{ d}}$ window; $n = 21$ Tier-1 targets), reactive astrocyte glutamate and trophic remodeling (`Folh1`/GCPII, `Cnksr3`, `Ntrk2`, `Tcf7l2`, `Cmbl`) and subacute splicing shifts require CNS-penetrant small-molecule enzyme inhibitors (such as 2-PMPA prodrugs) or intrathecal splice-switching ASOs to dismantle the $A(t) \leftrightarrow L(t)$ feedback loop (**Fig. 5b--d**). In **Stage 3** (Delayed $24\text{{--}}72\text{{ h}}$ initiation, $24\text{{ h--}}28\text{{ d}}$ window; $n = 35$ Tier-1 targets), down-regulated intracellular scaffolds (`Rnf112`, `Elk1`, `Rapgefl1`, `Lin7b`, `C1ql2`) require transcriptional or ASO splice restoration, whereas hyperexcitable voltage-gated channel subunits (`Scn3a`, `Scn3b`, `Kctd4`) require high-$\text{{CNS MPO}}$ ($\ge 4.5$) state-dependent channel modulators paired with circuit rehabilitation (**Fig. 5c, d** and **Table 2**). Cross-referencing this blueprint against our 230-trial clinical audit (**Table 1**) confirms that historical failures clustered in trials deploying Stage-1 pan-cellular drugs during Stage-2/3 windows without lock-reversing or neuronal-gate co-therapies.

#### Figure 5

---

## Discussion

While static cell-type specificity ($\tau_0$) predicts general drug approval across baseline atlases [7, 8], combining our deterministic auditing pipeline (`NeuroImmune-Virtual-Biotech`) with a mechanistic multicellular ODE model (`vGlia-Niche`) explains why acute brain injury trials have repeatedly failed [1, 2, 3], revealing an orthogonal second pillar: dynamic single-cell specificity trajectories coupled to multicellular inflammatory lock-in kinetics. Auditing 230 clinical trials ($N = 98,119$ participants) demonstrates that when administrative and COVID-19 accrual halts ($n = 27$) are separated from symmetric phase II/III scientific futility and toxicity ($n = 10$), pleiotropic interventions whose empirical single-cell specificity drops below $\tau_{{\min}} < 0.65$ carry a $21.88$-fold higher odds of scientific failure than cell-type-restricted interventions ($\tau_{{\min}} \ge 0.65$; $19.05\%$ versus $1.06\%$, $P = 2.31 \times 10^{{-5}}$). This protection is equally pronounced in acquired brain injury ($n = 213$, Haldane-Anscombe $\text{{OR}} = 87.54$, $P = 1.04 \times 10^{{-6}}$) and within direct molecular target pharmacotherapies ($n = 60$, $\text{{OR}} = 7.76$, $P = 0.0120$, continuous acute $\tau(t_1)$ $\text{{AUROC}} = 0.826$). Equally important, cell-type specificity is not a fixed baseline constant: across $133$ neuroimmune candidates tracked from baseline scRNA-seq (`GSE180862`) through subacute injury (`GSE247339`, `GSE226207`, `GSE277487`, `GSE319769`) to $129$ human hippocampal surgical specimens (`GSE63808`), empirical subacute specificity drift ($\Delta\tau = \tau(t_2) - \tau_0$) exposes $31$ baseline-specific decoy genes (mean $\tau_0 = 0.779 \rightarrow \tau(t_2) = 0.687$, mean $\Delta\tau = -0.092$ versus $\tau(t_2) = 0.788$ in Tier-1, $P = 2.02 \times 10^{{-4}}$) that lose cellular restriction during active neuroinflammation.

Our methodological framework builds upon and extends established statistical and systems-biology models [7, 8, 9, 10, 11, 12] in three practical ways. First, whereas the Virtual Biotech study of Zhang et al. [7] established baseline Yanai specificity $\tau_0$ [8] as a general predictor of drug approval across $55,984$ trials, our leave-one-gate-out ablation (**Table 3**, Configuration 2) shows that baseline $\tau_0 \ge 0.65$ alone leaves $39.7\%$ false-positive decoys and choroid-plexus or dissociation-stress artifacts (`Ccdc103`, `Alkbh5`, `Canx`, `Hspa5`) in CNS injury candidate lists. Combining six explicit domain-rule quality gates with a $1,000$-iteration BTL/Elo pairwise ranking engine [10] ensures $0.0\%$ choroid artifact leakage and $100.0\%$ six-gate precision retention with deterministic reproducibility while increasing leave-self-out human hippocampal correlation $|r|$ by $87.2\%$ ($0.440$ versus $0.235$). Second, whereas recent clinical AI tools have focused on electronic health record workflows and bedside diagnostic decision-making [32, 33], our clinical trial auditing module (`Division 6`) demonstrates how rule-governed protocol parsing can separate operational trial halts from biological mechanism failures and incorporate dosing-window alignment ($\text{{CWAS}}$), raising predictive $\text{{AUROC}}$ from $0.501$ (unfiltered) to $0.868$ ($\Delta\text{{AUROC}} = +0.367$, $P < 0.001$; and subacute $\tau(t_2)$ $\text{{AUROC}} = 0.858$, $P = 0.00142$ within acquired brain injury molecular drug trials). Third, whereas large-scale single-cell perturbation models (`State` [16], `Tahoe-100M` [17], `ProteinTalks` [18], and `UniPert-G2CP` [19]) learn static input-output mappings in dissociated cell lines without multicellular feedback, `vGlia-Niche` integrates causal state-transition principles [34] and multi-scale cellular niche organization [35] within transparent Hill-type differential equations [21, 22, 23, 24].

From a clinical translation perspective, the identification of an inflammatory lock-in tipping point ($E_{{\text{{crit}}}} = 9.5\text{{ storm}}\cdot\text{{h}}$, $t_{{50}} = 16.4\text{{ h}}$) has direct implications for trial design across TBI, status epilepticus, and acute neuroinflammatory encephalopathy. Large-scale international neurosurgical studies such as the 29-country Global Neurosurgical Study-1 ($N = 2,165$ TBI patients across 100 hospitals) [36] have highlighted wide variation in patient presentation and treatment initiation times. Once cumulative microglial and astrocyte inflammatory exposure crosses $E_{{\text{{crit}}}}$, subacute transcriptional remodeling (`GSE277487`, `GSE302863`) and RNA splicing (`GSE319769`) lock the hippocampal niche into a hyperexcitable, low-gate state ($C(t) < 0.40$) that no longer responds to delayed single-drug anti-inflammatory therapy (`Late Stage-1 Brake` at $36\text{{ h}}$). While severe mechanical TBI also involves primary axonal shearing and hemorrhage requiring acute surgical decompression or antifibrinolytic hemostasis (`CRASH-3` [4]), and acute ischemic stroke requires primary stratification by arterial recanalization before evaluating post-reperfusion immunoblockade (`ACTION` [30]), the secondary microglial-astrocytic-neuronal lock-in cascade modeled here is conserved across status epilepticus, neuroinflammatory encephalopathy, post-reperfusion stroke penumbra, and pericontusional TBI tissue. Future clinical trials enrolling patients beyond $12\text{{--}}16.4\text{{ h}}$ post-injury should therefore pair an upstream microglial/endothelial brake (`Tlr4`/`Tnfaip3`/`Il1r1` blockade, `taVNS`, or `Plin4`/`Ahnak` vascular stabilization) with a subacute astrocyte lock-reversing agent (`Folh1`/GCPII inhibition) and a dentate/CA1d neuronal gate stabilizer (`Rnf112` or `Scn3a` modulation).

Several limitations warrant consideration, each addressed by explicit sensitivity controls. First, although our clinical trial audit encompassed all $230$ PRISMA-eligible neuroinflammation and brain injury registries ($98,119$ participants from $N_{{\text{{raw}}}} = 370$ records), the finite number of verified phase II/III scientific translational failures ($n = 10$) and reliance on protocol-level initiation windows rather than individual patient pharmacokinetic curves could widen single-cohort ROC confidence intervals. We mitigated this limitation by enforcing a strictly symmetric failure definition and verifying statistically significant protective effect sizes across acquired brain injury ($n = 213$, Haldane-Anscombe $\text{{OR}} = 87.54$, $P = 1.04 \times 10^{{-6}}$), completed or halted ($n = 119$, $\text{{OR}} = 15.82$, $P = 2.28 \times 10^{{-4}}$), evaluable non-COVID ($n = 92$, $\text{{OR}} = 15.29$, $P = 3.51 \times 10^{{-4}}$), and explicit window-gated ($n = 57$, Haldane-Anscombe $\text{{OR}} = 35.40$, $P = 0.00138$) subcohorts. Consistent protection also held across all pharmacotherapy and biologic trials ($n = 84$, $\text{{OR}} = 8.33$, $P = 0.0056$) and direct molecular target pharmacotherapies ($n = 60$, $82.2\%$ relative risk reduction, $\text{{OR}} = 7.76$, two-sided Fisher $P = 0.0120$, multivariable $\text{{OR}}_{{\text{{adj}}}} = 9.06$, Wald $P = 0.0095$, continuous acute $\tau(t_1)$ $\text{{AUROC}} = 0.826$, $P = 0.00115$). Significant protection likewise persisted in acquired brain injury direct molecular target pharmacotherapies ($n = 51$, Haldane-Anscombe $\text{{OR}} = 28.33$, $P = 0.00116$, continuous subacute $\tau(t_2)$ $\text{{AUROC}} = 0.858$, $P = 0.00142$), alongside a $2 \times 2$ initiation-window factorial audit (**Extended Data Fig. 1**).

Second, because serial hippocampal biopsies cannot be ethically obtained from the same human TBI patients between $6$ and $72\text{{ h}}$, our longitudinal trajectory analysis integrates 10 public cohorts across murine injury time-courses and human surgical specimens (`GSE180862`, `GSE269748`, `GSE247339`, `GSE277487`, `GSE226207`, `GSE302863`, `GSE319769`, `GSE330624`, `GSE209552`, and `GSE63808`). We controlled for cross-cohort platform differences by computing 100% pure un-modeled single-cell Yanai $\tau(t)$ directly from raw single-cell matrices and evaluating Group III subacute-delocalizing decoys against internal positive-control Group II neuronal gatekeepers measured on the identical subacute single-cell platforms (`GSE247339` $P = 0.0084$; `GSE226207` $P = 0.0096$). Third, although `vGlia-Niche` achieved strong quantitative accuracy across $16$ empirical public multi-cohort state readouts ($r = 0.935$, $R^2 = 0.874$, out-of-sample $R^2_{{\text{{LORO}}}} = 0.823$ and $R^2_{{\text{{LOCO}}}} = 0.821$) and was corroborated by a $7.95$-fold post-separatrix gate collapse odds ratio across $N = 129$ human surgical hippocampi ($P = 3.83 \times 10^{{-6}}$; **Extended Data Fig. 4a, b**), well-mixed ODEs do not resolve spatial diffusion gradients across the pericontusional penumbra. Because the delayed $24\text{{ h}}$ Triple-Niche Combination rescue represents an in silico dynamical prediction, prospective in vivo multi-drug pharmacokinetic, BBB penetration, and safety validation in preclinical TBI and status epilepticus models represent essential next steps.

By uniting longitudinal single-cell specificity tracking with multicellular positive-feedback kinetics, `NeuroImmune-Virtual-Biotech` and `vGlia-Niche` establish a quantitative counterpart to static target selection, delivering a prioritized $70$-target ledger and a chrono-staged three-compartment therapeutic blueprint for acute brain injury and neuroinflammation.

---

## Methods

### Modular computational architecture of `NeuroImmune-Virtual-Biotech`

To ensure that every target score, quality-control gate, and clinical trial classification is 100% deterministic and reproducible, we implemented `NeuroImmune-Virtual-Biotech` as a rule-governed neuro-symbolic Python pipeline rather than an unconstrained conversational chatbot. Each analytical step builds directly on established mathematical formulations (Yanai's specificity index $\tau$ [8], Sarle's finite-sample bimodality coefficient $BC$, and Elo / Bradley-Terry-Luce [BTL] tournament ranking as adapted for multi-agent scientific prioritization [10]) and is organized into six modular software components (`Division 1`--`6`) coordinated by a master ranking script (`Virtual CSO`, fixed random seed `numpy.random.default_rng(20261028)`):
- **Module 1 / Division 1 (Single-Cell Dynamic Specificity Tracking):** Computes time-resolved Yanai cell-type specificity $\tau(t_k)$ and Sarle's bimodality coefficient $BC$ directly from raw single-cell and single-nucleus expression matrices across $24$ parenchymal hippocampal and neurovascular cell clusters from baseline and longitudinal TBI scRNA-seq (`GSE180862` [25], `GSE269748` [27], `GSE247339`, `GSE277487`, `GSE226207` [28], `GSE302863`), acute human TBI snRNA-seq (`GSE209552` [26]), subacute injury (`GSE319769`, `GSE330624`), and chronic human surgical pathology (`GSE63808` [$N = 129$] [29]) selected from our 92-series NCBI GEO census (`GEO_EXHAUSTIVE_CENSUS_RECEIPT.json`).
- **Module 2 / Division 2 (Anatomical Choroid-Plexus & Dissociation-Stress Purity Filter):** Quantifies anatomical co-dissection and enzymatic dissociation contamination by computing transcript enrichment in choroid plexus (`CHOR`/`CPE`), ependymal (`EPEN`), meningeal fibroblast (`FB`), and ubiquitous endoplasmic reticulum heat-shock chaperone modules, rejecting non-parenchymal and stress artifacts (`Gate 1`) and enforcing a mandatory lineage marker purity ratio $\ge 3.0$ across every single-cell dataset.
- **Module 3 / Division 3 (Multi-Cohort Trajectory & Cross-Species Coupling Audit):** Evaluates directional consistency across four multi-cohort injury and recovery trajectories (`Gate 2`), leave-one-gene-out human surgical cohort (`GSE63808`, $N = 129$) glia-neuron coupling (`Gate 4`), and pure sample-level external cohort (`GSE319769`, `GSE269748`, `GSE330624`, `GSE277487`, `GSE226207`, `GSE302863`) receiver operating characteristic $\text{{AUROC}}$.
- **Module 4 / Division 4 (BTL & Elo Pairwise Tournament Ranking):** Conducts $1,000$ Monte Carlo rounds of pairwise target comparisons across all $133$ candidates ($8,778$ unique pairs per round) weighted by subacute $\tau(t_2)$, human leave-self-out $|r|$, external sample $\text{{AUROC}}$, neuronal safety sparing, and splicing/multi-cohort concordance.
- **Module 5 / Division 5 (Druggability & BBB Timing Alignment):** Assigns each target to its matched therapeutic modality (small molecule, biologic/mAb, intrathecal ASO, or autonomic neuromodulation device) and chronological BBB accessibility window (`Stage 1` [$0\text{{--}}24\text{{ h}}$], `Stage 2` [$12\text{{ h--}}7\text{{ d}}$], or `Stage 3` [$24\text{{ h--}}28\text{{ d}}$]; `Gate 6`).
- **Module 6 / Division 6 (ClinicalTrials.gov Protocol Parsing & Symmetric Endpoint Deconvolution):** Audits ClinicalTrials.gov registries, parses verbatim protocol initiation windows (`CTGOV_PROTOCOL_ELIGIBILITY_230_CACHE.json`) and stop reasons, separates operational/COVID-19 halts from symmetric scientific translational failures, and computes the timing-matched specificity score ($\text{{CWAS}}$) and composite trial score ($\text{{VBTCS}}$).

### Leakage-free audit of 230 neuroinflammation and brain injury clinical trials

We executed an untruncated retrieval via the official NIH/NLM ClinicalTrials.gov REST API v2 (https://clinicaltrials.gov/api/v2/studies; `pageSize = 1000`) across three pre-specified query axes (`CLINICALTRIALS_PRISMA_FUNNEL_RECEIPT.json`): Axis 1 (`TBI + neuroinflammation / microglia / astrocyte / cytokine / blood-brain barrier`, $n = 117$ raw records), Axis 2 (`TBI + seizure / post-traumatic epilepsy / status epilepticus / excitotoxicity / vagus nerve`, $n = 236$ records), and Axis 3 (`post-traumatic epilepsy or status epilepticus + neuroinflammation / secondary brain injury`, $n = 17$ records), yielding $N_{{\text{{raw}}}} = 370$ total records and $N_{{\text{{dedup}}}} = 349$ unique `NCT_ID` registries. Applying a four-step PRISMA eligibility funnel excluded $n = 119$ ineligible records ($n = 54$ off-axis metabolic, hepatic, neonatal hypoxic-ischemic, or neurodegenerative disorders, including $n = 30$ non-axis metabolic or systemic encephalopathies enforcing $0$ hepatic encephalopathy and $0$ neonatal hypoxia-ischemia; $n = 38$ purely observational or diagnostic-scale registries; $n = 18$ healthy-volunteer pharmacokinetic or non-mechanistic behavioral protocols; and $n = 9$ superseded or uninitiated protocol withdrawals), locking $N = 230$ eligible interventional and circuit-stratified translational registries comprising $98,119$ planned or enrolled participants (**Supplementary Table S1**). To prevent target-outcome circularity, every trial intervention was mapped solely to its primary molecular target gene symbols (`Primary_Target_Symbol`) or canonical circuit/biomarker panel (`IL1R1`, `TLR4`, `NR3C1`, `PGR`, `GRIN2A`, `GABRA1`, `SCN3A`, `GFAP`, `NTRK2`), and its four-stage specificity trajectory $\tau_i(t_0, t_1, t_2, t_3)$ and minimum trajectory specificity $\tau_{{\min,i}} = \min(\tau_0, \tau_1, \tau_2, \tau_3)$ were computed directly by averaging the empirical single-cell Yanai $\tau$ of those target genes across our unpacked raw single-cell GEO matrices (`GSE180862` $t_0$, `GSE269748` + `GSE302863` $t_1$, `GSE247339` + `GSE277487` + `GSE226207` $t_2$, and `GSE209552` $t_3$) without any hand-coded drug $\tau$ lookup constants or per-trial overrides. Each trial was classified into one of five macro-modalities (**Table 1**): (1) Niche-Restricted Pharmacotherapy & Biologics ($n = 32$), (2) Pleiotropic / Pan-Cellular Pharmacotherapy ($n = 45$), (3) Neuromodulation & Autonomic Circuit Devices ($n = 38$), (4) Cellular, Exosome & Paracrine Biologics ($n = 7$), and (5) Biomarker-Guided, Nutritional & Circuit Rehabilitation ($n = 108$).

For symmetric endpoint deconvolution, every `Terminated` ($n = 23$), `Withdrawn` ($n = 9$), `Suspended` ($n = 1$), and `Completed` trial ($n = 86$; total completed or halted registries $n = 119$) was audited against verbatim registry `why_stopped` fields and PubMed-indexed Phase III randomized trial reports using a single deterministic rule-locked classifier blinded to $\tau(t)$. Trials halted exclusively due to COVID-19 pandemic lockdowns, slow patient accrual, principal investigator departure, or sponsor corporate restructuring without efficacy futility or safety signals were coded as `Operational_COVID_or_Accrual_Stop = 1` ($n = 27$). To eliminate asymmetric coding bias between completed high-$\tau$ and low-$\tau$ registries, `Scientific_Translational_Failure = 1` ($n = 10$) was restricted strictly to two symmetric, verifiable criteria applied identically across all 230 registries: (i) explicit registry termination or withdrawal for prespecified efficacy futility or dose-limiting toxicity ($n = 6$, all registered in the ClinicalTrials.gov registry, https://www.clinicaltrials.gov/: `NCT00822900` [registration date: 14 January 2009 / 2009-01-14], `NCT00048646` [registration date: 4 November 2002 / 2002-11-04], `NCT02430350` [registration date: 20 April 2015 / 2015-04-20], `NCT01764451` [registration date: 7 January 2013 / 2013-01-07], `NCT05226780` [registration date: 26 January 2022 / 2022-01-26], and `NCT04639310` [registration date: 4 November 2020 / 2020-11-04]), or (ii) completed Phase III randomized controlled trials with a PubMed-verified negative primary efficacy endpoint report ($n = 4$, all registered in the ClinicalTrials.gov registry, https://www.clinicaltrials.gov/: `NCT01143064` [registration date: 10 June 2010 / 2010-06-10] [3], `NCT00987454` [registration date: 29 September 2009 / 2009-09-29], `NCT00004817` [registration date: 24 February 2000 / 2000-02-24], and `NCT03061565` [registration date: 14 February 2017 / 2017-02-14]). Clinical trial number: not applicable (this study is a secondary computational audit of publicly archived records on ClinicalTrials.gov and does not report a new prospective clinical trial). All completed Phase I/II trials without a Phase III futility failure were coded symmetrically as `0`. For each trial $i$, we computed the timing-matched specificity score (Chrono-Window Alignment Score, $\text{{CWAS}}_i = \text{{clip}}(0.50\,\tau_{{\min,i}} + 0.50\,\tau_i(t_2) + 1.5\,W_i, 0.18, 0.95)$) and off-target risk score ($\text{{Off}}_i = \text{{clip}}(1 - (0.60\,\tau_{{\min,i}} + 0.40\,\tau_i(t_3)) - 0.8\,W_i, 0.10, 0.90)$) using the protocol window alignment shift $W_i \in [-0.085, +0.085]$ (`Protocol_Window_Shift_Wi`) assigned solely from `Modality_Class` and `Stage_Window_Category`, and the composite trial score ($\text{{VBTCS}}_i = 0.42\,\tau_{{\min,i}} + 0.35\,\text{{CWAS}}_i + 0.23\,(1 - \text{{Off}}_i)$). Nonparametric $\text{{AUROC}}$, $2,000$-iteration stratified bootstrap 95% CIs, multivariable logistic regression adjusting for modality and trial phase, and two-sided Mann-Whitney $U$ and Fisher's exact $P$ values (across all $N = 230$ trials, the $n = 213$ acquired brain injury cohort, the $n = 119$ completed/halted denominator, the $n = 92$ scientifically evaluable denominator, the $n = 84$ pharmacotherapy/biologics cohort, the $n = 60$ direct molecular target drug cohort, and the $n = 51$ acquired brain injury direct molecular target drug cohort) were computed in Python (`scipy.stats` v1.13).

### Cross-dataset single-cell dynamic specificity $\tau(t)$ formulation

For any gene $g$ across $K$ parenchymal cell types in single-cell atlas stage $t \in \{{t_0, t_1, t_2, t_3\}}$, let $\mu_{{g,k}}(t)$ denote the log-normalized mean expression in cluster $k$, and $\hat{{\mu}}_{{g,k}}(t) = \mu_{{g,k}}(t) / \max_{{1 \le j \le K}} \mu_{{g,j}}(t)$. Extending the static formulation of Yanai et al. [8], we defined the time-resolved dynamic specificity index $\tau_g(t)$ as:

$$\tau_g(t) = \frac{{\sum_{{k=1}}^{{K}} \left(1 - \hat{{\mu}}_{{g,k}}(t)\right)}}{{K - 1}} \in [0, 1]$$

To eliminate heuristic modulation or gate-penalty terms, all four stage specificity values $\tau_g(t_0, t_1, t_2, t_3)$ in **Table 2**, **Table 3**, and **Supplementary Table S2** (`Tau_t0_Baseline_GSE180862`, `Tau_t1_Acute_GSE269748`, `Tau_t2_Subacute_GSE319769`, and `Tau_t3_Chronic_Human_GSE63808`) were computed as 100% pure un-modeled empirical single-cell Yanai $\tau$ directly from the unpacked raw single-cell and single-nucleus GEO count matrices (`scripts/01_pubmed_benchmark_and_230trials_tau_retrospective.py`): specifically, $\tau_g(t_0)$ was computed directly across the $K = 24$ parenchymal hippocampal cell clusters of `GSE180862` [25] (excluding `CHOR` and `EPEN`); $\tau_g(t_1)$ was computed as the empirical single-cell parenchymal Yanai $\tau$ across acute TBI snRNA-seq `GSE269748` [27] ($431,198$ nuclei) and acute/subacute brain injury scRNA-seq `GSE302863` ($60,574$ cells); $\tau_g(t_2)$ was computed as the empirical single-cell parenchymal Yanai $\tau$ across subacute hippocampal/frontal cortex TBI scRNA-seq `GSE247339` ($201,564$ cells) and subacute cortical injury scRNA-seq `GSE226207` [28] ($83,833$ cells; alongside `Direct_scRNA_Tau_t2_GSE180862_7d` and `Direct_snRNA_Tau_t2_GSE277487` [$162,907$ nuclei]); and $\tau_g(t_3)$ was computed as the empirical single-nucleus Yanai $\tau$ across human acute resected TBI snRNA-seq `GSE209552` [26] ($24,621$ nuclei) and multi-timepoint CCI snRNA-seq `GSE277487`. Subacute specificity drift was defined as $\Delta\tau_g = \tau_g(t_2) - \tau_g(t_0)$. Single-cell state-switching geometry was quantified using Sarle's finite-sample bimodality coefficient $BC_g = (g_1^2 + 1) / [g_2 + 3(n-1)^2 / ((n-2)(n-3))]$, where $g_1$ and $g_2$ denote sample skewness and excess kurtosis across single cells. In all external cohorts (`GSE269748` $n=36$, `GSE277487` $n=12$, `GSE226207` $n=15$, `GSE302863` $n=5$, `GSE319769` $n=36$, and `GSE330624` $n=32$), discrimination $\text{{AUROC}}$ was computed strictly from sample-level log-CPM pseudobulk or bulk expression matrices without blending single-cell $\tau$ values, and differential expression $P$ values (`GSE319769`) were computed via exact two-sided Welch's $t$-tests (`scipy.stats.ttest_ind(equal_var=False)`) with Benjamini-Hochberg false discovery rate (BH-FDR) correction.

### Six-gate quality filtering ablation and BTL/Elo tournament ranking

All $133$ multi-cohort neuroimmune candidates were audited against six binary quality-control gates:
- **Gate 1 (Choroid/Ependymal & Border Purity):** Requires `Artifact_Contamination_Ratio < 0.50` and primary expression cluster $\neq$ `CPE`, rejecting candidates dominated by `CPE`/`CHOR` ciliary co-dissection, meningeal/perivascular fibroblast (`FB`) border bleed-through, or endoplasmic reticulum chaperone artifact modules (`Ccdc103` `0.671`, `Alkbh5` `0.841`, `Canx` `0.733`, and `Hspa5` `1.000` [`CPE`]).
- **Gate 2 (Multi-Contrast Directional Concordance):** Requires directional concordance $\ge 0.75$ ($\ge 3$ of $4$ statistical contrasts across standard `DESeq2`, anatomical-covariate-adjusted `DESeq2`, `limma-voomWithQualityWeights`, and `edgeR-QLF`, with zero sign inversions) across multi-model TBI neuroinflammation (`GSE269748`, `GSE247339`), subacute excitotoxic hippocampal injury (`GSE319769`, `GSE330624`), and homeostatic checkpoint recovery trajectories.
- **Gate 3 (Dynamic Single-Cell Specificity Threshold):** Requires baseline parenchymal specificity $\tau_g(t_0) \ge 0.65$ (`GSE180862`) and subacute single-cell specificity $\tau_g(t_2) \ge 0.65$ across at least one subacute single-cell injury atlas (`GSE247339`, `GSE226207`, or `GSE180862` 7-day subacute hippocampal scRNA-seq) without pan-cellular collapse.
- **Gate 4 (Human & External Cross-Cohort Conservation):** Requires significant leave-one-gene-out coupling in the human `GSE63808` surgical hippocampal cohort ($|r| \ge 0.25$ and $P < 0.05$), external cross-cohort sample-level injury discrimination $\text{{AUROC}} \ge 0.80$ (`GSE319769` or `GSE269748`), or human acute TBI single-nucleus specificity $\tau_g(t_3) \ge 0.65$ (`GSE209552`).
- **Gate 5 (Single-Cell Bimodal or High-Amplitude Switch Geometry):** Requires Sarle's bimodality coefficient $BC_g \ge 0.45$, or high-amplitude injury state shift ($|\log_2\text{{FC}}| \ge 0.50$) paired with $BC_g \ge 0.21$ within the primary neuroimmune niche.
- **Gate 6 (Non-Redundant Attribution, Druggability & Neuronal Safety Sparing):** Requires positive multi-attribute contribution ($\text{{SHAP}} > 0$ or $\text{{BTL}} \ge 0.50$), neuronal safety sparing (defined directionally as $1 - \hat{{\mu}}_{{g,\text{{neuron}}}}$ for `UP` glial/vascular inhibitor targets and as excitatory-gate niche selectivity sparing inhibitory interneurons [`INT`] and non-target glia for `DOWN` neuronal gate restoration targets), and an assigned therapeutic modality and BBB window.

Candidates passing all $6/6$ gates ($n = 70$) were designated `Tier 1`. Normalized six-axis composite utilities were weighted across specificity, bimodality, trajectory concordance, safety sparing, human/external conservation, and tournament attribution $(0.22, 0.14, 0.20, 0.14, 0.15, 0.15)$; pairwise tournament probabilities $P(i \succ j) = 1 / (1 + \exp[-(\theta_i - \theta_j)/s])$ ($s = 0.08$) were evaluated across $40$ full round-robin sweeps and $1,000$ Monte Carlo iterations and mapped onto the standard Co-Scientist Elo scale ($\text{{Elo}}_i = 1500 + 173.72\,\hat{{\theta}}_i$). All computational pipelines and statistical tests were executed in `Python` v3.11 using `numpy` v1.26, `scipy` v1.13, `pandas` v2.2, `statsmodels` v0.14, and `matplotlib` v3.8.

### `vGlia-Niche` five-variable multicellular ODE model and public multi-cohort calibration

We formulated `vGlia-Niche` as a low-dimensional, biophysically constrained five-variable Hill-type ODE model rather than an over-parameterized black-box neural network so that kinetic time constants could be fixed directly from public longitudinal transcriptomic time-courses, preventing overfitting and preserving transparent mechanistic interpretability of the inflammatory lock-in threshold $E_{{\text{{crit}}}}$. The `vGlia-Niche` model simulates five coupled compartment states ($V, M, A, L, C$, together with synaptic scaffolding readout $S$) over $t \in [0, 72]\text{{ h}}$ under acute injury stimulus $I_{{\text{{insult}}}}(t) = I_0(1 - e^{{-t/4.5}})$ using a fourth-order Runge-Kutta solver ($\Delta t = 0.05\text{{ h}}$):

$$\frac{{dV}}{{dt}} = k_{{v,\text{{ton}}}}(V_0 - V) - k_{{v,\text{{loss}}}} I_{{\text{{insult}}}}(t) V + k_{{v,\text{{brk}}}} U_{{\text{{Brake}}}}(t)(1 - V)$$

$$\frac{{dM}}{{dt}} = \Big(k_{{m,\text{{storm}}}} I_{{\text{{insult}}}}(t)\big(1 - 0.55\,V\big) + k_{{m,\text{{auto}}}} \frac{{M^{{2.4}}}}{{K_m^{{2.4}} + M^{{2.4}}}} + k_{{m,\text{{lock}}}} L\Big)(1 - M)\big(1 - 0.72\,U_{{\text{{Brake}}}}(t)\big) - d_m(1 + 0.45\,V)M$$

$$\frac{{dA}}{{dt}} = \big(k_{{a,m}} M + k_{{a,\text{{loop}}}} L\big)(1 - A)\big(1 - 0.78\,U_{{\text{{Folh1}}}}(t)\big) - d_a\big(1 + 0.55\,U_{{\text{{Folh1}}}}(t)\big)A$$

$$\frac{{dL}}{{dt}} = k_{{l,\text{{lock}}}} \frac{{D(t)^{{n_L}}}}{{K_L^{{n_L}} + D(t)^{{n_L}}}}(1 - L) - \Big(d_l + k_{{l,\text{{unlock}}}} U_{{\text{{Folh1}}}}(t)\big(0.45 + 0.55\,U_{{\text{{Scn3a/Rnf112}}}}(t)\big)\Big)L, \quad D(t) = 0.52\,M + 0.48\,A + 0.38\,L, \quad E_{{\text{{auc}}}}(t) = \int_0^t \big[0.65\,M(\tau) + 0.35\,A(\tau)\big]\,d\tau$$

$$\frac{{dC}}{{dt}} = -\big(k_{{c,m}} M + k_{{c,a}} A + k_{{c,l}} L\big)\big(1 - 0.70\,U_{{\text{{Scn3a/Rnf112}}}}(t)\big)C + k_{{c,\text{{rec}}}}(1 - C)\big(1 - 0.75\,L\big) + k_{{c,\text{{gate}}}} U_{{\text{{Scn3a/Rnf112}}}}(t)(1 - C)$$

$$\frac{{dS}}{{dt}} = -\big(k_{{s,a}} A + k_{{s,l}} L\big)S + k_{{s,\text{{rec}}}} C(1 - S) + k_{{s,\text{{gate}}}} U_{{\text{{Scn3a/Rnf112}}}}(t)(1 - S)$$

where $n_L = 2.2$ (LHS sensitivity range $n_L \in [1.76, 2.64]$), $E_{{\text{{crit}}}} = 9.5\text{{ storm}}\cdot\text{{h}}$ is the cumulative inflammatory lock-in threshold and kinetic time constants were fixed from public transcriptomic time-courses (`GSE319769`, `GSE269748`, `GSE247339`, `GSE226207`, `GSE277487`, `GSE302863`). Simulated compartment states at $72\text{{ h}}$ were benchmarked against $n = 16$ empirical public multi-cohort reference state readouts derived directly from raw GEO matrices across four normalized public GEO state modules (`Sham Baseline`, `Moderate TBI Insult`, `Severe Unbraked TBI/SE`, and `Early Stage-1 Brake` across each module): (1) microglial inflammatory storm state $M$ (`GSE180862`, `GSE269748` & `GSE247339`, $n = 4$), (2) reactive astrocyte and BBB state $A$ (`GSE330624` & `GSE226207`, $n = 4$), (3) subacute transcriptional/splicing lock state $L$ (`GSE277487` & `GSE302863`, $n = 4$), and (4) dentate/CA1 neuronal gate integrity state $C$ (`GSE319769` & `GSE63808`, $n = 4$). Goodness of fit was evaluated via a 2-parameter global linear fit in-sample (Pearson $r = 0.935$, $R^2 = 0.874$, $P = 1.11 \times 10^{{-7}}$), 16-fold leave-one-readout-out cross-validation ($r_{{\text{{LORO}}}} = 0.908$, $R^2_{{\text{{LORO}}}} = 0.823$, $P = 1.18 \times 10^{{-6}}$, $\text{{RMSE}} = 9.83\%$), and 4-fold leave-one-condition-out cross-validation ($r_{{\text{{LOCO}}}} = 0.909$, $R^2_{{\text{{LOCO}}}} = 0.821$, $P = 1.10 \times 10^{{-6}}$, $\text{{RMSE}} = 9.90\%$), supplemented by a $1,000$-run Latin-hypercube $\pm 20\%$ 5-ODE numerical integration sensitivity analysis (`Phase3_vGliaNiche_1000LHS_ODE_Sensitivity.npz`).

---

## Data Availability

All transcriptomic datasets and clinical trial registry records analyzed in this study are publicly available in public repositories, and source data are provided with this paper. All underlying transcriptomic and clinical trial datasets are documented with cryptographic SHA-256 checksums in `DATA_PROVENANCE_MANIFEST.json`, `CLINICALTRIALS_PRISMA_FUNNEL_RECEIPT.json`, and `GEO_EXHAUSTIVE_CENSUS_RECEIPT.json`, and verified via `accession_metadata_authenticity_gate.py` (**Supplementary Table S3**). Publicly archived transcriptomic cohorts are available at the NCBI Gene Expression Omnibus (GEO, https://www.ncbi.nlm.nih.gov/geo/) under accessions `GSE180862` [25] (murine hippocampal TBI scRNA-seq atlas across Sham $t_0$, $24\text{{ h}}$ $t_1$, and $7\text{{ d}}$ $t_2$, $18,162$ cells), `GSE269748` [27] ($431,198$ nuclei across $36$ samples; murine multi-model TBI snRNA-seq), `GSE247339` ($201,564$ cells across $41$ samples; murine hippocampal and frontal cortex TBI scRNA-seq), `GSE277487` ($162,907$ nuclei across $12$ samples; murine multi-timepoint CCI cortical snRNA-seq), `GSE226207` [28] ($83,833$ cells across $15$ samples; murine subacute cortical injury glial reactivity scRNA-seq), `GSE302863` ($60,574$ cells across $5$ samples; murine brain injury microglia/macrophage scRNA-seq), `GSE319769` ($n = 36$ hippocampal samples across D3, D7, and D14 intra-amygdala kainate epileptogenesis bulk RNA-seq), `GSE330624` ($n = 32$ FANS-sorted $\text{{NeuN}}^+/\text{{NeuN}}^-$ epileptic hippocampal nuclei RNA-seq samples), `GSE209552` [26] ($24,621$ nuclei across $17$ human surgical TBI samples from $30$ GSM records; human acute surgically resected TBI brain tissue snRNA-seq), and `GSE63808` [29] ($N = 129$ official GEO human temporal lobe epilepsy surgical hippocampal microarrays, `GSM1565578`--`GSM1565706`). Public clinical trial registry records ($N = 230$ PRISMA-eligible trials) are publicly available from the NIH/NLM ClinicalTrials.gov registry (https://www.clinicaltrials.gov/ and REST API v2 https://clinicaltrials.gov/api/v2/studies) and are provided in full in **Supplementary Table S1** (`Supplementary_Tables_S1_to_S4_v2.0.xlsx`). Source data for all main and Extended Data figures are provided in `Supplementary_Tables_S1_to_S4_v2.0.xlsx` and archived directly in the repository: **Fig. 1** (`tables/Table1_230Trials_Modality_and_Tau_Tier_Summary.csv`, `tables/TableS1_230_ClinicalTrials_MultiAgent_Audit.csv`, `data/trial_230_retrospective_stats.json`), **Fig. 2** (`tables/TableS2_133Genes_Dynamic_Tau_Trajectories.csv`, `tables/TableS3_10_GEO_Cohorts_Architecture_and_Validation_Summary.csv`, `data/GSE180862_sc_gene_celltype_dotplot_matrix.csv`, `data/GSE63808_human_129patients_glia_vs_neuron_scores.csv`), **Fig. 3** (`tables/Table3_SixGate_Ablation_and_Benchmark_Comparison.csv`, `tables/TableS2_133Genes_Dynamic_Tau_Trajectories.csv`), and **Fig. 4** & **Fig. 5** (`data/Phase3_vGliaNiche_72hr_Trajectories.csv`, `data/Phase3_vGliaNiche_ChronoTrial_Summary_vs_PublicCohorts.csv`, `tables/Table2_Top25_Tier1_Targets_MultiCohort_Ledger.csv`, `data/rebuttal_sensitivity_and_loco_stats.json`).

## Code Availability

Complete source code for `NeuroImmune-Virtual-Biotech`, `vGlia-Niche`, figure generation, and automated audit gates is provided in `Supplementary_Software_v2.0.zip` accompanying this submission and is publicly available at https://github.com/SJT503/NeuroImmune_Virtual_Biotech.

## Declarations

- **Clinical Trial Registration Statement:** Clinical trial number: not applicable. This study is a secondary computational audit and reanalysis of publicly archived datasets and public clinical trial registries and does not report the results of a new clinical trial. All cited clinical trial identifiers are registered in the NIH/NLM ClinicalTrials.gov registry (https://www.clinicaltrials.gov/) with the following official Registration Dates (`studyFirstSubmitDate` / `studyFirstPostDate`): `NCT00822900` (registered 14 January 2009 [2009-01-14]; posted 15 January 2009), `NCT00048646` (registered 4 November 2002 [2002-11-04]; posted 6 November 2002), `NCT02430350` (registered 20 April 2015 [2015-04-20]; posted 30 April 2015), `NCT01764451` (registered 7 January 2013 [2013-01-07]; posted 9 January 2013), `NCT05226780` (registered 26 January 2022 [2022-01-26]; posted 7 February 2022), `NCT04639310` (registered 4 November 2020 [2020-11-04]; posted 20 November 2020), `NCT01143064` (registered 10 June 2010 [2010-06-10]; posted 14 June 2010), `NCT00987454` (registered 29 September 2009 [2009-09-29]; posted 1 October 2009), `NCT00004817` (registered 24 February 2000 [2000-02-24]; posted 25 February 2000), `NCT03061565` (registered 14 February 2017 [2017-02-14]; posted 23 February 2017), `NCT00004730` (registered 25 February 2000 [2000-02-25]; posted 28 February 2000), `NCT02997371` (registered 7 December 2016 [2016-12-07]; posted 20 December 2016), `NCT06966830` (registered 4 May 2025 [2025-05-04]; posted 13 May 2025), and `NCT01454154` (registered 11 October 2011 [2011-10-11]; posted 18 October 2011).
- **Ethics Oversight:** This study exclusively reanalyzed publicly archived, de-identified human surgical and acute TBI transcriptomic datasets (`GSE63808` [$N = 129$], `GSE209552` [$n = 17$ samples / $30$ GSMs]), publicly archived murine single-cell, single-nucleus, and bulk transcriptomic cohorts (`GSE180862`, `GSE269748`, `GSE247339`, `GSE277487`, `GSE226207`, `GSE302863`, `GSE319769`, `GSE330624`), and public clinical trial registries ($N = 230$, ClinicalTrials.gov). All original human and animal studies were approved by their respective institutional review boards and animal care and use committees (IACUCs) in accordance with the Declaration of Helsinki and ARRIVE guidelines.
- **Author Contributions:** Conceptualization: J.S., K.L., and W.C. Computational pipeline engineering, cross-dataset dynamic specificity trajectory modeling, and `vGlia-Niche` ODE dynamical simulation: J.S. Clinical trial registry auditing and endpoint deconvolution: J.S., X.L., R.L., Q.S., and X.C. Multi-cohort transcriptomic, splicing, and single-cell benchmark curation and statistical validation: J.S., X.L., R.L., and Q.S. Visualization: J.S. Supervision and funding acquisition: J.S., K.L., and W.C. Writing (original draft): J.S. Writing (review and editing): J.S., X.L., R.L., Q.S., X.C., K.L., and W.C.
- **Competing Interests:** The authors declare no competing financial or non-financial interests.
- **Funding:** This work was supported by the Natural Science Foundation of Guangdong Province (Grant Nos. 2022A1515012144 to K.L. and 2023A1515012055 to W.C.) and the Shantou University Medical College Scientific Research Initiation Grant (Grant No. 510858047 to J.S.). The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.
- **Declaration of Generative AI and AI-Assisted Technologies in the Writing Process:** Distinct from the deterministic, code-audited computational pipelines evaluated as the scientific subject of this study (`NeuroImmune-Virtual-Biotech` and `vGlia-Niche`, fully documented in Methods and executed via deterministic Python algorithms with fixed seed `numpy.random.default_rng(20261028)`), large-language-model-based editing tools were used during manuscript preparation solely to improve English language clarity and readability. No generative AI tools were used to generate, fabricate, alter, or synthesize primary clinical trial records, transcriptomic datasets, statistical analyses, reference citations, or scientific figures. After using these language-editing tools, all authors reviewed, verified, and edited the text as needed and take full responsibility for the integrity and accuracy of the publication.

---

## Tables

### Table 1. Multi-agent clinical trial retrospective summary across 230 neuroinflammation and brain injury trials ($N = 98,119$ participants) stratified by intervention macro-modality, dynamic specificity tier $\tau(t)$, and clinical etiology

| Stratification Axis | Category | Trials ($n$) | Share of 230 Trials (%) | Planned / Enrolled Participants ($N$) | Operational / COVID-19 / Accrual Stops ($n$) | Scientific Translational Failures ($n$) | Scientific Failure Rate (%) | Mean Static $\tau_0$ | Mean Subacute $\tau(t_2)$ | Mean Minimum $\tau_{{\min}}$ | Mean Drift $\Delta\tau$ | Mean CWAS | Mean VBTCS |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{table1_md_rows}

*Notes:* Across the full $N = 230$ registry cohort, combined Low/Moderate-$\tau$ ($\tau_{{\min}} < 0.65$, $n = 42$ trials, $8$ scientific failures [$19.05\%$]) versus High-$\tau$ ($\tau_{{\min}} \ge 0.65$, $n = 188$ trials, $2$ scientific failures [$1.06\%$]) yields an odds ratio $\text{{OR}} = 21.88$ (Haldane-Anscombe $\text{{OR}} = 18.38$, two-sided Fisher's exact $P = 2.31 \times 10^{{-5}}$). Sensitivity analyses confirm statistical significance across six restricted subcohorts: (i) **Acquired Brain Injury / TBI only** ($n = 213$, $75,209$ participants, excluding $17$ genetic epilepsy benchmarks): Low/Moderate-$\tau$ failure rate $19.51\%$ ($8/41$) versus High-$\tau$ $0.00\%$ ($0/172$; Haldane-Anscombe $\text{{OR}} = 87.54$, Fisher's exact $P = 1.04 \times 10^{{-6}}$, subacute $\tau(t_2)$ $\text{{AUROC}} = 0.887$, $P = 7.54 \times 10^{{-5}}$); (ii) **Completed or Halted registries only** ($n = 119$, excluding $111$ recruiting, active, enrolling, or unknown-status trials): Low/Moderate-$\tau$ failure rate $26.67\%$ ($8/30$) versus High-$\tau$ $2.25\%$ ($2/89$; $\text{{OR}} = 15.82$, Fisher's exact $P = 2.28 \times 10^{{-4}}$); (iii) **Scientifically evaluable completed or failed registries** ($n = 92$, further excluding $27$ operational/COVID-19 halts): Low/Moderate-$\tau$ failure rate $32.00\%$ ($8/25$) versus High-$\tau$ $2.99\%$ ($2/67$; $\text{{OR}} = 15.29$, $P = 3.51 \times 10^{{-4}}$); (iv) **Explicit window-gated trials** ($n = 57$): Low/Moderate-$\tau$ failure rate $29.41\%$ ($5/17$) versus High-$\tau$ $0.00\%$ ($0/40$; Haldane-Anscombe $\text{{OR}} = 35.40$, Fisher's exact $P = 0.00138$); (v) **Direct Molecular Target Pharmacotherapy & Biologics (All Etiologies)** ($n = 60$, $16,349$ participants, excluding devices, rehabilitation, and non-molecular nutritional/osmolar/hyperbaric gas trials): Low/Moderate-$\tau$ failure rate $32.00\%$ ($8/25$) versus High-$\tau$ $5.71\%$ ($2/35$), representing an $82.2\%$ relative risk reduction ($\text{{OR}} = 7.76$, two-sided Fisher's exact $P = 0.0120$, one-sided $P = 0.0095$; multivariable $\text{{OR}}_{{\text{{adj}}}} = 9.06$, Wald $P = 0.0095$; continuous empirical single-cell $\tau_0$ $\text{{AUROC}} = 0.752$ [$P = 0.0120$], acute $\tau(t_1)$ $\text{{AUROC}} = 0.826$ [$P = 0.00115$], subacute $\tau(t_2)$ $\text{{AUROC}} = 0.774$ [$P = 0.00632$], $\tau_{{\min}}$ $\text{{AUROC}} = 0.724$ [$P = 0.0257$]); and (vi) **Acquired Brain Injury Direct Molecular Target Pharmacotherapy & Biologics** ($n = 51$, $16,044$ participants): Low/Moderate-$\tau$ failure rate $33.33\%$ ($8/24$) versus High-$\tau$ $0.00\%$ ($0/27$; Haldane-Anscombe $\text{{OR}} = 28.33$, Fisher's exact $P = 0.00116$; continuous empirical single-cell $\tau_0$ $\text{{AUROC}} = 0.820$ [$P = 0.00434$], acute $\tau(t_1)$ $\text{{AUROC}} = 0.843$ [$P = 0.00221$], subacute $\tau(t_2)$ $\text{{AUROC}} = 0.858$ [$P = 0.00142$], $\tau_{{\min}}$ $\text{{AUROC}} = 0.738$ [$P = 0.0337$]). CWAS, Chrono-Window Alignment Score; VBTCS, Virtual Biotech Trial Composite Score.

---

### Table 2. Top 25 Tier-1 neuroimmune priority targets ranked by pairwise tournament Elo rating across dynamic $\tau(t)$ trajectories and external cohorts

| Priority Rank | Murine Gene | Human Symbol | Direction | Primary Neuroimmune Niche | Baseline $\tau_0$ (`GSE180862`) | Subacute $\tau(t_2)$ (`GSE247339`/`GSE226207`) | Chronic $\tau(t_3)$ (`GSE209552`/`GSE277487`) | Sarle $BC$ | Human `GSE63808` Leave-Self-Out $r$ | External `GSE319769` Sample AUC | External `GSE269748` Sample AUC | BTL Win Rate | Tournament Elo | Optimal Therapeutic Modality | Chrono-Staged BBB Window |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
{table2_md_rows}

*Notes:* **Portfolio balance:** Table 2 lists the top 25 balanced Tier-1 priority targets (top 12 `UP` glial/vascular targets and top 13 `DOWN` neuronal gate targets sorted by overall `CSO_Priority_Rank` across all 133 candidates; `Gabrd` [`CSO_Priority_Rank = 24`, `DOWN` #14, $\text{{Elo}} = 1804.7$] and all remaining Tier-1 targets are archived in **Supplementary Table S2**). **Human `GSE63808` leave-self-out $r$ sign convention:** In the 129-sample official GEO human surgical hippocampus cohort (`GSE63808`, `GSM1565578`--`GSM1565706`), each gene's expression is correlated against the leave-one-gene-out directional human neuroimmune coupling axis (reactive glial/vascular UP score minus neuronal gate DOWN score, excluding the tested gene itself to prevent part-whole auto-correlation). Negative $r$ values for murine `DOWN` neuronal gate genes (`Rnf112` $r = -0.492$, `Scn3b` $r = -0.767$, `Lin7b` $r = -0.682$, `Rapgefl1` $r = -0.666$) indicate direct cross-species pathological concordance (depletion during heightened glial reactivity), whereas negative $r$ values for murine `UP` acute burst genes (`Plin4` $r = -0.402$, `Folh1` $r = -0.262$, `Tlr4` $r = -0.397$) reflect phase-resolved decoupling between the acute/subacute innate burst (`Stage 1–2`) and chronic human surgical remodeling (`Stage 3`). Consequently, Gate 4 (`Human Conservation`) evaluates absolute coupling magnitude $|r| \ge 0.25$ ($P < 0.05$), external sample $\text{{AUROC}} \ge 0.80$, or human single-nucleus $\tau(t_3) \ge 0.65$. **Chrono-Staged BBB Window definitions:** `Stage 1 (0–24 h)`, ultra-early innate microglial/endothelial burst restraint (`0–12 h` peak); `Stage 1 (6 h–7 d)`, acute-to-subacute endothelial/mural BBB barrier sealing; `Stage 2 (12 h–28 d)`, subacute astrocyte-to-neuron glutamate/metabolic lock-in uncoupling (`12–24 h` threshold initiation); `Stage 3 (24 h–28 d)` and `Stage 3 (CNS MPO >= 4.5)`, delayed dentate/CA1d neuronal gate restoration across closed-BBB maintenance.

---

### Table 3. Systematic 10-configuration leave-one-gate-out ablation and benchmark comparison across 133 neuroimmune candidate genes

| Framework Configuration | Selection Criteria or Ablated Gate | Selected Targets ($n$) | Mean Baseline $\tau_0$ | Mean Subacute $\tau(t_2)$ | Mean Human `GSE63808` Abs. $r$ | Mean External Cohort AUROC | Mean Neuronal Safety Sparing | Choroid Artifact Leakage (%) | 6-Gate Precision Retention (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{table3_md_rows}

*Notes:* **Internal audit versus external benchmark metrics:** `6-Gate Precision Retention (%)` and `Choroid Artifact Leakage (%)` are internal structural audit metrics verifying how effectively each ablated configuration recovers the full 6-gate consensus set (`Configuration #8` = $100.0\%$ reference by construction) and excludes choroid-plexus contamination; **independent external biological validation** is quantified by `Mean Human GSE63808 Abs. r` ($N = 129$ human surgical specimens, leave-self-out correlation) and `Mean External Cohort AUROC` (pure sample-level discrimination across `GSE319769` + `GSE269748`). **Pareto progression across Configurations `#8`, `#9`, and `#10`:** Configuration `#9` (`Tier-1 + BTL Dominance`, $n = 43$) elevates subacute specificity to $\tau(t_2) = 0.789$, human correlation to $|r| = 0.369$, and external cohort sample discrimination to $\text{{AUROC}} = 0.767$, while Configuration `#10` (`Top-21 Priority Portfolio`, $n = 21$) achieves peak baseline and subacute specificity ($\tau_0 = 0.843$, $\tau(t_2) = 0.797$), peak human hippocampal coupling ($|r| = 0.440$, an $87.2\%$ gain over bulk `DESeq2` [$0.235$]), and peak neuronal safety sparing ($0.865$) while maintaining strong external sample discrimination ($\text{{AUROC}} = 0.766$).

---

## Figure Legends

**Fig. 1 | Retrospective audit of 230 neuroinflammation and brain injury clinical trials ($N = 98,119$ participants) via empirical single-cell specificity $\tau(t)$ and symmetric endpoint deconvolution.**
**a**, ClinicalTrials.gov registry status audit across $N = 230$ brain injury and neuroinflammation trials ($98,119$ planned or enrolled participants: Completed $n = 86$ [$37.4\%$], Recruiting $n = 40$ [$17.4\%$], Unknown $n = 30$ [$13.0\%$], Not yet recruiting $n = 25$ [$10.9\%$], Terminated $n = 23$ [$10.0\%$], Withdrawn $n = 9$ [$3.9\%$], Active not recruiting $n = 8$ [$3.5\%$], Enrolling by invitation $n = 8$ [$3.5\%$], and Suspended $n = 1$ [$0.4\%$]).
**b**, Per-trial composite score (`VBTCS`) distributions (horizontal boxplots and individual trials) and symmetric scientific failure rates across the five intervention macro-modalities (`Niche Pharm` $n = 32$ [scientific failure $3.1\%$], `Pleiotropic Pharm` $n = 45$ [$20.0\%$], `Neuromod Device` $n = 38$ [$0.0\%$], `Cell/Exosome` $n = 7$ [$0.0\%$], and `Biomarker/Rehab` $n = 108$ [$0.0\%$]; restricted to $n = 60$ direct molecular target pharmacotherapy and biologic trials, high-$\tau$ drugs [$n = 35$] achieve an $82.2\%$ relative risk reduction over low/moderate-$\tau$ drugs [$5.71\%$ vs $32.00\%$, $\text{{OR}} = 7.76$, two-sided Fisher $P = 0.0120$, continuous acute $\tau(t_1)$ $\text{{AUROC}} = 0.826$, $P = 0.00115$]).
**c**, Symmetric endpoint deconvolution separating $n = 27$ operational/COVID-19/accrual stops from $n = 10$ verified scientific translational failures across empirical single-cell specificity tiers (High-$\tau_{{\min}} \ge 0.65$ [$n = 188$, $1.06\%$ failure], Moderate-$\tau_{{\min}}$ $0.45\text{{--}}0.65$ [$n = 16$, $43.8\%$ failure], and Low-$\tau_{{\min}} < 0.45$ [$n = 26$, $3.8\%$ failure]; combined Low/Moderate versus High $\text{{OR}} = 21.88$, Haldane-Anscombe $\text{{OR}} = 18.38$, two-sided Fisher's exact $P = 2.31 \times 10^{{-5}}$; restricted to $n = 213$ Acquired Brain Injury / TBI registries, Haldane-Anscombe $\text{{OR}} = 87.54$, $P = 1.04 \times 10^{{-6}}$).
**d**, Two-dimensional protocol audit plane plotting subacute dynamic specificity $\tau(t_2)$ against independent PK and dosing-window alignment ($W_i$) across all $230$ trials (`Active/completed` $n = 193$, `COVID/accrual stop` $n = 27$, `Scientific failure` $n = 10$), with marker size scaled by trial enrollment.
**e**, Nonparametric empirical ROC curves comparing unfiltered registry stop prediction ($n = 33$, $\text{{AUROC}} = 0.501$, $P = 0.9928$) against deconvolved scientific failure prediction ($n = 10$) using static $\tau_0$ ($\text{{AUROC}} = 0.866$, $P = 3.38 \times 10^{{-5}}$), subacute dynamic $\tau(t_2)$ ($\text{{AUROC}} = 0.854$, $P = 6.15 \times 10^{{-5}}$; $\text{{AUROC}} = 0.887$ in ABI $n = 213$), minimum trajectory $\tau_{{\min}}$ ($\text{{AUROC}} = 0.857$, $P = 5.39 \times 10^{{-5}}$), composite trial score ($\text{{VBTCS}}$, $\text{{AUROC}} = 0.860$, $P = 7.89 \times 10^{{-5}}$), and timing-matched specificity score ($\text{{CWAS}}$, $\text{{AUROC}} = 0.868$, $P = 5.52 \times 10^{{-5}}$; $\Delta\text{{AUROC}} = +0.367$ over unfiltered $\tau_0$, $P < 0.001$).
**f**, Head-to-head dumbbell comparison of representative `Table S1` failed pan-cellular and delayed-window trials (all registered at ClinicalTrials.gov, https://www.clinicaltrials.gov/: `ProTECT III` `NCT00822900` [registered 14 January 2009 / 2009-01-14], `SyNAPSe` `NCT01143064` [registered 10 June 2010 / 2010-06-10], `INTREPID2566 trofinetide` `NCT00987454` [registered 29 September 2009 / 2009-09-29], `Magnesium Sulfate III` `NCT00004817` [registered 24 February 2000 / 2000-02-24], and `NBI-921352` `NCT05226780` [registered 26 January 2022 / 2022-01-26]; alongside historical benchmarks `CRASH-1`, `ACTION`, and `Minocycline`) versus pre-lock-in window-matched high-$\tau$ protocol benchmarks (`Anakinra` `NCT02997371` [registered 7 December 2016 / 2016-12-07, completed Phase II] and `Lacosamide` `NCT06966830` [registered 4 May 2025 / 2025-05-04, not yet recruiting], marked `*` as protocol benchmarks, alongside external reference `BIIB093 / Glibenclamide` `NCT01454154` [registered 11 October 2011 / 2011-10-11]) across subacute $\tau(t_2)$ and protocol alignment ($\text{{CWAS}}$).

**Fig. 2 | Cross-dataset single-cell dynamic specificity trajectories $\tau(t_0 \rightarrow t_1 \rightarrow t_2 \rightarrow t_3)$ across 133 neuroimmune candidates and 129 human surgical hippocampus samples.**
**a**, Joint distribution of baseline Yanai specificity $\tau_0$ (`GSE180862`) and Sarle's bimodality coefficient ($BC$) across $133$ neuroimmune candidate genes stratified into four functional groups (`Arch I: Glial UP` $n = 26$, `Arch II: Gate DN` $n = 44$, `Arch III: Decoy` $n = 31$, and `Arch IV: Artifact` $n = 32$).
**b**, Four-stage empirical single-cell dynamic specificity trajectories $\tau(t_0 \rightarrow t_1 \rightarrow t_2 \rightarrow t_3)$ spanning baseline dentate gyrus (`GSE180862`), acute multi-model TBI neuroinflammation (`GSE269748`/`GSE302863`), subacute parenchymal injury (`GSE247339`/`GSE226207`), and chronic/human brain injury (`GSE209552`/`GSE277487`).
**c**, Subacute specificity drift $\Delta\tau = \tau(t_2) - \tau_0$ box-and-jitter distributions across `Archetype I`--`IV` (drift $\Delta\tau$ Kruskal-Wallis $H = 8.70$, $P = 0.0336$; subacute $\tau(t_2)$ Kruskal-Wallis $H = 22.37$, $P = 5.45 \times 10^{{-5}}$), exposing $n = 31$ Group III subacute-delocalizing decoys (mean $\tau_0 = 0.779 \rightarrow \tau(t_2) = 0.687$, mean $\Delta\tau = -0.092$, median $-0.065$; subacute $\tau(t_2)$ Mann-Whitney $U = 1528.0$, $P = 2.02 \times 10^{{-4}}$ versus Tier 1 [$0.788$] and $P = 9.01 \times 10^{{-6}}$ versus internal control Group II neuronal gatekeepers [mean $\tau_0 = 0.822 \rightarrow \tau(t_2) = 0.808$, $\Delta\tau = -0.015$]).
**d**, Single-cell niche compartmentalization heatmap (`GSE180862`) across $14$ priority hubs and $10$ hippocampal cell types (`aMG`, `MAC`, `MG`, `ASC`, `END`, `SMC`, `DG`, `CA1d`, `INT`, `CPE`), showing clean segregation of glial/vascular UP switches (`C3ar1`, `Relb`, `Tlr4`, `Folh1`, `Plin4`, `Ahnak`) from neuronal gatekeepers (`Rnf112`, `Kctd4`, `Scn3a`, `Scn3b`, `Gabrd`, `C1ql2`, `Ryr2`, `Elk1`).
**e**, Cross-species conservation in all $N = 129$ human surgical hippocampus specimens in official NCBI GEO series `GSE63808` (`GSM1565578`--`GSM1565706`), demonstrating significant inverse correlation between reactive glial/vascular UP switches and dentate/CA1d neuronal gate DOWN stabilizers (Pearson $r = -0.549$, $P = 1.67 \times 10^{{-11}}$; Spearman $\rho = -0.618$, $P = 6.46 \times 10^{{-15}}$).
**f**, Multi-cohort empirical single-cell and sample-level validation across 6 public GEO validation cohorts (`GSE269748`, `GSE247339`, `GSE319769`, `GSE209552`, `GSE226207`, and `GSE277487`/`GSE302863`), accompanied by a $3.44$-fold odds enrichment of subacute differential RNA splicing and expression remodeling in Tier-1 targets compared with non-Tier-1 candidates ($22.9\%$ vs $7.9\%$, two-sided Fisher's exact $P = 0.0297$).

**Fig. 3 | Systematic 10-configuration leave-one-gate-out ablation and BTL/Elo pairwise tournament ranking across 133 neuroimmune candidate genes.**
**a**, Six-gate filtering architecture (`G1: Choroid/Ependymal Purity`, `G2: 4-Cohort Concordance`, `G3: Dynamic tau(t) >= 0.65`, `G4: Human GSE63808 Conservation`, `G5: Sarle Bimodality Switch`, `G6: Safety & Attribution`) coupled to 1,000-iteration Bradley-Terry-Luce (BTL) and Elo pairwise tournament ranking (`Division 5`), isolating $n = 70$ Tier-1 targets (`6/6` gates), $n = 43$ BTL-dominant hubs ($\text{{BTL}} \ge 0.50$), and $n = 21$ top priority targets ($\text{{Elo}} \ge 1850$).
**b**, Ten-configuration leave-one-gate-out ablation comparison across internal audit metrics (`6-Gate Precision %`, `Neuronal Safety Sparing`) and independent biological benchmarks (`Subacute tau(t2)`, `Human GSE63808 Leave-Self-Out |r|`, `External Cohort Sample AUROC`), demonstrating non-redundant quality gains from `#1 Bulk DEG` ($n = 133$, precision $52.6\%$, human $|r| = 0.235$) and `#2 Static tau0 >= 0.65` ($n = 116$, precision $60.3\%$, $|r| = 0.248$) to `#8 Full 6-Gate` ($n = 70$, precision $100.0\%$, $|r| = 0.296$) and `#10 Top-21 Portfolio` ($n = 21$, $\tau_0 = 0.843$, $\tau(t_2) = 0.797$, human $|r| = 0.440$ [$+87.2\%$ over bulk `DESeq2`], external sample $\text{{AUROC}} = 0.766$, safety sparing $0.865$).
**c**, Pareto optimization trade-off plane plotting subacute dynamic specificity $\tau(t_2)$ against human `GSE63808` leave-self-out $|r|$ across all $10$ configurations, with bubble area proportional to target count and color encoding `6-Gate Precision Retention (%)`.
**d**, Pairwise tournament Elo ratings (Elo $\pm 95\%$ CI) and BTL dominance probabilities across the top $15$ Tier-1 targets, led by `Rnf112` ($\text{{Elo}} = 2087.7$, $\text{{BTL}} = 0.947$), `Plin4` ($2014.0$), `Scn3a` ($1997.4$), `Elk1` ($1991.3$), `Rapgefl1` ($1988.3$), and `Folh1` ($1914.5$).
**e**, Six-axis utility profile across the top $12$ Tier-1 targets (`Specificity tau(t)`, `Bimodality BC`, `4-Cohort Concordance`, `Neuronal Sparing`, `Human/Ext Conservation`, and `SHAP/BTL Attribution`).
**f**, Choroid plexus (`CPE`/`CHOR`), meningeal fibroblast (`FB`), and endoplasmic reticulum chaperone artifact rejection plane (`Division 2`), isolating `Ccdc103` (contamination ratio $0.671$), `Alkbh5` ($0.841$), `Canx` ($0.733$), and `Hspa5` ($1.000$, `CPE`) from parenchymal Tier-1 targets (`Rnf112`, `Plin4`, `Scn3a`, `Folh1`, `Tlr4`).

**Fig. 4 | The `vGlia-Niche` five-variable coupled ODE model uncovers a $16.4\text{{ h}}$ inflammatory lock-in tipping point and $24\text{{ h}}$ delayed combination rescue.**
**a**, Schematic of the five-variable coupled ordinary differential equation (ODE) system (`vGlia-Niche`: `V` tonic vagal/endothelial brake, `M` microglial inflammatory storm, `A` astrocyte `Folh1` glutamate/BBB dysfunction, `L` subacute transcriptional/splicing lock-in with threshold $E_{{\text{{crit}}}} = 9.5\text{{ storm}}\cdot\text{{h}}$, and `C` dentate/CA1 `Scn3a`/`Rnf112` neuronal gate integrity) and the three-stage therapeutic schedule (`Stage 1: 0–12 h` `Tlr4/Plin4`, `Stage 2: 12–24 h` `Folh1`, `Stage 3: 24–72 h` `Scn3a/Rnf112`).
**b**, Simulated $72\text{{ h}}$ trajectories across four regimens (`Severe Unbraked TBI/SE`, `Early Stage-1 Brake [0 h]`, `Late Stage-1 Brake [36 h]`, and `24 h Staged Triple-Niche Combo`) for microglial storm $M(t)$, transcriptional/splicing lock $L(t)$, and neuronal gate integrity $C(t)$, showing that delayed monotherapy fails to reverse lock-in ($C(72\text{{ h}}) = 25.4\%$ at $36\text{{ h}}$; $21.9\%$ at $24\text{{ h}}$) whereas $24\text{{ h}}$ staged triple combination unlocks $L(t)$ ($0.60 \rightarrow 0.012$) and restores $C(72\text{{ h}}) = 98.2\%$ ($81.4\%$ in continuous delay sweep).
**c**, Two-dimensional phase-plane trajectories ($M(t)$ versus $C(t)$) across the four regimens relative to the inflammatory lock-in separatrix, showing that delayed monotherapy (`Late Stage-1 Brake [36 h]`) remains trapped in the low-gate attractor whereas the $24\text{{ h}}$ staged triple-niche combination crosses back into the high-gate homeostatic basin.
**d**, Continuous dosing-initiation sweep ($t_{{\text{{start}}}} \in [0, 48]\text{{ h}}$) comparing `Stage-1 Monotherapy` against `Staged Triple-Niche Combo`, identifying the monotherapy window cliff at $t_{{50}} = 16.4\text{{ h}}$ ($1,000$-LHS 5-ODE median $16.6\text{{ h}}$, IQR $15.4\text{{--}}17.6\text{{ h}}$, $95\%$ range $13.8\text{{--}}19.6\text{{ h}}$) versus sustained rescue across $24\text{{ h}}$ delayed initiation for the triple-niche combination ($t_{{50}} = 43.2\text{{ h}}$).
**e**, Calibration and out-of-sample cross-validation of `vGlia-Niche` 72-h compartment states against $n = 16$ empirical public multi-cohort reference state readouts (`GSE180862`/`GSE269748`/`GSE247339` microglial storm $M$, `GSE330624`/`GSE226207` astrocyte state $A$, `GSE277487`/`GSE302863` splicing/lock state $L$, and `GSE319769`/`GSE63808` neuronal gate integrity $C$): 2-parameter in-sample fit Pearson $r = 0.935$, $R^2 = 0.874$, $P = 1.11 \times 10^{{-7}}$; 16-fold leave-one-readout-out $R^2_{{\text{{LORO}}}} = 0.823$, $\text{{RMSE}} = 9.83\%$; 4-fold leave-one-condition-out $R^2_{{\text{{LOCO}}}} = 0.821$, $\text{{RMSE}} = 9.90\%$.
**f**, Endpoint $72\text{{ h}}$ multi-compartment state and composite network hyperexcitability comparison across all eight simulated regimens (`Sham Baseline` $16.1$, `Moderate TBI` $41.7$, `Severe Unbraked` $85.7$, `Early Stage-1 Brake [0 h]` $35.5$, `Subacute Stage-1 Brake [12 h]` $49.3$, `Late Stage-1 Brake [36 h]` $80.7$, `Folh1 Inhibitor [24 h]` $81.4$, and `24 h Staged Triple-Niche Combo` $11.6$).

**Fig. 5 | Integrated neuroimmune virtual biotech architecture and chrono-staged translational roadmap for acute brain injury.**
*BioRender-standard 2D flat biomedical schematic illustrating the three-panel architecture of `NeuroImmune-Virtual-Biotech` coupled to `vGlia-Niche`.*
**Left panel (Clinical Trial Endpoint Deconvolution & Dynamic $\tau(t)$ Trajectory Tracking):** Multi-agent ClinicalTrials.gov protocol deconvolution separates operational/COVID-19 stops from symmetric biological futility across $230$ brain injury trials ($98,119$ participants), while empirical single-cell specificity tracking across $10$ unpacked GEO cohorts ($982,859$ cells/nuclei and $197$ tissue samples) distinguishes persistent glial/neuronal hubs (`Archetypes I & II`) from subacute-delocalizing decoys (`Archetype III`) and choroid-plexus co-dissection artifacts (`Archetype IV`).
**Center panel (`vGlia-Niche` Lock-In Bifurcation & Phase-Space Separatrix):** Multicellular positive feedback between reactive microglia (`M`), astrocyte glutamate/BBB dysfunction (`A`), and subacute transcriptional/splicing remodeling (`L`) triggers an inflammatory lock-in bifurcation at $E_{{\text{{crit}}}} = 9.5\text{{ storm}}\cdot\text{{h}}$ ($t_{{50}} = 16.4\text{{ h}}$), trapping delayed monotherapy inside the locked pathological attractor while guiding multi-compartment uncoupling across the phase-space separatrix.
**Right panel (Chrono-Staged Three-Compartment Therapeutic Blueprint):** Blood-brain barrier (BBB) permeability-aligned sequential combination schedule pairing Stage 1 acute innate & endothelial burst restraint (`0–12 h`, `Tlr4` / `Plin4` / `C3ar1` during open BBB), Stage 2 subacute astrocyte-to-neuron lock-in uncoupling (`12–24 h`, `Folh1` / `Ahnak` across the $16.4\text{{ h}}$ tipping point), and Stage 3 chronic dentate/CA1 neuronal gate restoration (`>24 h`, `Scn3a` / `Rnf112` via high-penetrance small molecules across a resealed BBB).

---

## Extended Data Figure Legends

**Extended Data Fig. 1 | PRISMA clinical trial selection funnel, six-axis sensitivity forest plot, and protocol chrono-window alignment audit ($N = 230$ trials).**
**a**, Four-stage PRISMA clinical trial identification, deduplication ($370 \rightarrow 349$), eligibility exclusion ($n = 119$ removed: $54$ off-axis metabolic/hepatic/neonatal/neurodegenerative, $38$ observational/diagnostic, $18$ healthy PK, $9$ uninitiated withdrawn), and endpoint deconvolution funnel ($N = 230$ trials, $98,119$ participants; $27$ operational/COVID-19 stops versus $10$ symmetric scientific failures).
**b**, Six-stratum sensitivity analysis forest plot comparing Low/Moderate-$\tau$ ($\tau_{{\min}} < 0.65$) versus High-$\tau$ ($\tau_{{\min}} \ge 0.65$) scientific failure rates, odds ratios (95% CI), and exact $P$ values across: (1) Full Cohort ($N = 230$, $\text{{OR}} = 21.88$, $P = 2.31 \times 10^{{-5}}$), (2) Acquired Brain Injury / TBI Only ($n = 213$, Haldane-Anscombe $\text{{OR}} = 87.54$, $P = 1.04 \times 10^{{-6}}$, subacute $\tau(t_2)$ $\text{{AUROC}} = 0.887$), (3) Completed or Halted Trials Only ($n = 119$, $\text{{OR}} = 15.82$, $P = 2.28 \times 10^{{-4}}$), (4) Scientifically Evaluable Non-COVID Trials ($n = 92$, $\text{{OR}} = 15.29$, $P = 3.51 \times 10^{{-4}}$), (5) Direct Molecular Target Pharmacotherapy & Biologics (All Etiologies) ($n = 60$, $\text{{OR}} = 7.76$, two-sided $P = 0.0120$, one-sided $P = 0.0095$, continuous acute $\tau(t_1)$ $\text{{AUROC}} = 0.826$, $P = 0.00115$), and (6) Acquired Brain Injury Direct Molecular Target Pharmacotherapy & Biologics ($n = 51$, Haldane-Anscombe $\text{{OR}} = 28.33$, $P = 0.00116$, continuous subacute $\tau(t_2)$ $\text{{AUROC}} = 0.858$, $P = 0.00142$).
**c**, Protocol-parsed initiation window distribution (`Division6_Protocol_ChronoWindow_Audit_230Trials.csv`) across Stage 1 acute pre-lock-in ($\le 16.4\text{{ h}}$, $n = 18$), Stage 2 subacute lock-in ($16.4\text{{--}}72\text{{ h}}$, $n = 91$), and Stage 3 chronic remodeling ($>72\text{{ h}}$, $n = 121$).
**d**, $2 \times 2$ factorial interaction audit of protocol initiation window ($\le 16.4\text{{ h}}$ versus $>16.4\text{{ h}}$) by empirical single-cell specificity tier (High $\tau_{{\min}} \ge 0.65$ versus Low/Moderate $\tau_{{\min}} < 0.65$) across the Pharmacotherapy & Biologics cohort ($n = 84$, $\text{{OR}} = 8.33$, $P = 0.0056$) and explicit window-gated protocols ($n = 57$, Haldane-Anscombe $\text{{OR}} = 35.40$, $P = 0.00138$).

**Extended Data Fig. 2 | Ten-cohort cross-species multi-omic architecture and independent single-cell validation across $982,859$ cells/nuclei and $197$ tissue samples.**
**a**, Cross-species 10-cohort experimental design and dynamic trajectory mapping matrix (`GSE180862`, `GSE269748`, `GSE302863`, `GSE247339`, `GSE226207`, `GSE277487`, `GSE319769`, `GSE330624`, `GSE209552`, and `GSE63808`) across four post-injury stages ($t_0 \rightarrow t_1 \rightarrow t_2 \rightarrow t_3$).
**b**, Empirical single-cell specificity $\tau(t)$ and sample-level discrimination across our unpacked multi-cohort validation datasets (`GSE269748` $431,198$ nuclei, `GSE247339` $201,564$ cells, `GSE277487` $162,907$ nuclei, `GSE226207` $83,833$ cells, `GSE302863` $60,574$ cells, `GSE319769` $n = 36$, `GSE330624` $n = 32$, and human `GSE209552` $24,621$ nuclei) comparing `Top-21 Portfolio`, `70 Tier-1 Targets`, and `63 Non-Tier-1 Candidates`.
**c**, Cell-type lineage purity gate audit across all single-cell and sorted cohorts (target-to-competitor expression ratio $\ge 3.0\times$ across microglia `Hexb/Csf1r`, astrocytes `Aqp4/Gfap`, neurons `Snap25/Syt1`, and oligodendrocytes `Plp1/Mbp`).
**d**, Top-15 Tier-1 target concordance heatmap across 10 public GEO cohorts (empirical single-cell Yanai $\tau$ across `GSE180862`, `GSE269748`, `GSE247339`, `GSE277487`, `GSE226207`, and human `GSE209552`; sample-level pseudobulk/bulk discrimination $\text{{AUROC}}$ across `GSE319769` and `GSE330624`; and leave-self-out $|r|$ in human `GSE63808` $N = 129$).

**Extended Data Fig. 3 | Deterministic six-gate UpSet intersection decomposition and rule-based multi-division deliberation traces ($N = 133$ genes).**
**a**, Six-gate Boolean intersection UpSet plot (`SixGate_UpSet_Intersection_Summary.json`) across all $133$ candidate genes (`111111` all 6 gates passed $n = 70$; `111011` failed Gate 4 only $n = 16$; `101111` failed Gate 2 only $n = 12$; `110111` failed Gate 3 dynamic $\tau(t)$ only $n = 9$; `111101` failed Gate 5 only $n = 6$; and `G1=0` choroid/ependymal/chaperone artifact rejections $n = 4$).
**b**, Per-gate marginal pass rate and primary exclusion count across `Gate 1` ($97.0\%$ pass, $4$ artifact exclusions), `Gate 2` ($76.7\%$ pass), `Gate 3` ($78.9\%$ pass), `Gate 4` ($69.2\%$ pass), `Gate 5` ($88.7\%$ pass), and `Gate 6` ($81.2\%$ pass).
**c**, Six-division deliberation score matrix (`TableS4_Agentic_CrossDivision_Deliberation_Traces.csv`) comparing top accepted Tier-1 hubs (`Rnf112`, `Plin4`, `Scn3a`, `Elk1`, `Rapgefl1`, `Folh1`) against rejected Group III decoys (`Spint2`, `Flt1`, `Dbi`) and Group IV choroid/chaperone artifacts (`Ccdc103`, `Alkbh5`, `Canx`, `Hspa5`).
**d**, Monte Carlo tournament ranking stability comparing deterministic BTL win probability against 1,000-iteration Elo rating ($r = 0.988$, $P < 10^{{-100}}$).

**Extended Data Fig. 4 | Human surgical hippocampus phase-space separatrix ($N = 129$) and 1,000-run Latin-hypercube 5-ODE sensitivity analysis.**
**a**, Empirical phase-transition curve across all $N = 129$ human temporal lobe epilepsy surgical hippocampal microarrays (`GSE63808`, `GSM1565578`--`GSM1565706`) stratified into five equal-frequency glial Z-score quintiles ($N = [26, 26, 25, 26, 26]$, centers `-0.61`, `-0.32`, `-0.08`, `+0.21`, `+0.79`), showing a sharp jump in severe neuronal gate collapse (`Neuronal Z <= -0.454`, $q_{{25}}$) from $7.7\% \rightarrow 11.5\% \rightarrow 16.0\% \rightarrow 26.9\% \rightarrow 65.4\%$ across the upper-quartile separatrix (`Glial Z >= +0.312`, $q_{{75}}$).
**b**, Direct comparison of neuronal gate Z-scores and collapse rates between Pre-Separatrix (`Glial Z < +0.312`, $n = 96$, collapse $14.58\%$ [$14/96$], mean $Z = +0.167$) and Post-Separatrix (`Glial Z >= +0.312`, $n = 33$, collapse $57.58\%$ [$19/33$], mean $Z = -0.485$) surgical hippocampi ($\text{{OR}} = 7.95$, two-sided Fisher's exact $P = 3.83 \times 10^{{-6}}$, Mann-Whitney $U = 2594.0$, $P = 1.34 \times 10^{{-8}}$).
**c**, $1,000$-run Latin-hypercube $\pm 20\%$ 5-ODE numerical integration sensitivity distribution (`Phase3_vGliaNiche_1000LHS_ODE_Sensitivity.npz`) for the monotherapy lock-in tipping point $t_{{50}}$ (nominal $16.4\text{{ h}}$; $1,000$-LHS median $16.6\text{{ h}}$, IQR $15.4\text{{--}}17.6\text{{ h}}$, $95\%$ interval $13.8\text{{--}}19.6\text{{ h}}$, $100.0\%$ within $12\text{{--}}24\text{{ h}}$).
**d**, $1,000$-run Latin-hypercube 5-ODE numerical integration sensitivity distribution comparing $72\text{{ h}}$ neuronal gate integrity $C(72\text{{ h}})$ and transcriptional lock $L(72\text{{ h}})$ across `Severe Unbraked` ($C = 19.8\% \pm 3.6\%$), `Early 0 h Brake` ($C = 80.1\% \pm 2.3\%$, $99.6\%$ rescue), `Late 36 h Brake` ($C = 25.8\% \pm 3.2\%$, $0.0\%$ rescue, median $L = 0.808$), and `24 h Staged Triple-Niche Combo` ($C = 97.9\% \pm 0.4\%$, $100.0\%$ rescue $\ge 85\%$, median $L = 0.012$; $24\text{{ h}}$ continuous-delay rescue $81.4\%$, LHS median $81.3\%$ [$95\%$ interval $74.8\text{{--}}86.0\%$] versus $21.9\%$ monotherapy).

---

## Supplementary Information

Supplementary Information accompanies this paper:
- **Supplementary Table S1 (`TableS1_230_ClinicalTrials_MultiAgent_Audit.csv`):** Complete 230-trial registry ledger ($98,119$ planned or enrolled participants) with ClinicalTrials.gov `NCT_ID`, PRISMA inclusion/exclusion audit, intervention macro-modality, target gene(s), protocol-parsed dosing initiation window ($W_i$), empirical single-cell specificity trajectory $\tau(t_0, t_1, t_2, t_3, \tau_{{\min}}, \Delta\tau)$, symmetric endpoint deconvolution (`Operational_COVID_Accrual_Stop` versus `Scientific_Translational_Failure` with verbatim registry/PubMed evidence), `CWAS`, and `VBTCS`.
- **Supplementary Table S2 (`TableS2_133Genes_Dynamic_Tau_Trajectories.csv`):** Complete 133-gene multi-cohort dynamic specificity ledger across all 10 unpacked GEO cohorts (`GSE180862`, `GSE269748`, `GSE302863`, `GSE247339`, `GSE226207`, `GSE277487`, `GSE319769`, `GSE330624`, `GSE209552`, and `GSE63808`), including pure single-cell Yanai $\tau(t_0, t_1, t_2, t_3)$, subacute single-cell $\tau$ in `GSE247339`, `GSE226207`, `GSE180862` (7-day), and `GSE277487`, Sarle's bimodality coefficient $BC$, leave-one-gene-out human `GSE63808` ($N = 129$) coupling $r$ and $P$ value, exact Welch $t$-test and BH-FDR statistics in `GSE319769`, sample-level pseudobulk/bulk discrimination $\text{{AUROC}}$ across external cohorts, six-gate pass/fail vector, BTL win probability, and 1,000-iteration Elo rating.
- **Supplementary Table S3 (`TableS3_10_GEO_Cohorts_Architecture_and_Validation_Summary.csv`):** Cryptographically verified 10-cohort experimental architecture, cell/nucleus and sample counts ($982,859$ cells/nuclei and $197$ bulk/sorted/microarray samples), cell-type lineage purity gate ratios ($\ge 3.0\times$), and per-cohort Tier-1 versus non-Tier-1 validation metrics.
- **Supplementary Table S4 (`TableS4_Agentic_CrossDivision_Deliberation_Traces.csv`):** Deterministic six-division rule-based deliberation logs, per-gate quantitative thresholds, and Boolean UpSet intersection assignments across all $133$ candidate genes.

---

## References

{refs_block}
"""

en_md_path = MS_DIR / "Manuscript_NeuroImmune_Virtual_Biotech_EN.md"
en_md_path.write_text(EN_MANUSCRIPT, encoding="utf-8")
print(f"[OK] Wrote English Manuscript ({len(EN_MANUSCRIPT.splitlines())} lines, {len(EN_MANUSCRIPT.split())} words) to {en_md_path}")

COVER_LETTER = """# Cover Letter — Nature Communications

**Date:** November 5, 2026

**To:**
The Editors
*Nature Communications*
Springer Nature

**Subject:** Submission of Original Research Article: *"Dynamic cellular specificity predicts inflammatory lock-in and clinical translation in acute brain injury"*

Dear Editors,

We are pleased to submit our original research article, **"Dynamic cellular specificity predicts inflammatory lock-in and clinical translation in acute brain injury,"** for consideration as a Research Article in *Nature Communications*.

Secondary neuroinflammation and excitotoxicity drive progressive neurological disability across traumatic brain injury (TBI), status epilepticus, and acute brain injuries, yet predicting why late-stage neuroprotective trials fail remains a major translational bottleneck. Recently, Zhang et al. (*Science* 2026) introduced the Virtual Biotech framework across 55,984 clinical trials, demonstrating that drugs targeting genes with high static cell-type specificity ($\\tau_0$) are more likely to succeed clinically. However, applying static healthy-tissue atlases to acute brain injury overlooks three biological realities: (1) peripheral myeloid infiltration, blood-brain barrier (BBB) disruption, and reactive gliosis cause severe subacute specificity drift ($\\Delta\\tau(t)$) between baseline and the $12\\text{--}24\\text{ h}$ clinical dosing window; (2) hippocampal transcriptomic atlases are frequently confounded by choroid plexus and ependymal co-dissection artifacts; and (3) dissociated single-cell models lack coupled multicellular differential equations to explain why an immunomodulatory therapy succeeds when given acutely ($0\\text{--}6\\text{ h}$) but fails when delayed past $16\\text{--}24\\text{ h}$.

To address these challenges, we developed **NeuroImmune-Virtual-Biotech**, a deterministic, rule-governed trial-auditing and cross-dataset single-cell specificity trajectory pipeline, and coupled it to **vGlia-Niche**, a five-variable multicellular Hill-type ordinary differential equation (ODE) dynamical model. Operating exclusively on publicly archived clinical trial registries ($N = 230$ PRISMA-screened trials encompassing $98,119$ participants via the NIH/NLM ClinicalTrials.gov REST API v2) and 10 genuinely unpacked raw public transcriptomic cohorts ($982,859$ single cells or nuclei and $197$ bulk/sorted/microarray tissue samples, anchored by $N = 129$ human surgical hippocampal specimens in `GSE63808` and $24,621$ human acute TBI nuclei in `GSE209552`), our study reports three principal advances:

1. **Symmetric Clinical Trial Endpoint Deconvolution & Empirical Single-Cell $\\tau(t)$ Stratification:** By separating $27$ operational, COVID-19 pandemic, and accrual stops from $10$ symmetric Phase II/III scientific translational failures ($6$ explicit futility/toxicity registry stops plus $4$ completed Phase III trials with PubMed-verified negative primary endpoints) and computing target $\\tau(t)$ directly from raw single-cell matrices without hand-coded drug $\\tau$ constants, we show that pleiotropic interventions ($\\tau_{\\min} < 0.65$) carry $21.88$-fold higher odds of scientific failure than cell-type-restricted therapies ($19.05\\%$ versus $1.06\\%$, Fisher's exact $P = 2.31 \\times 10^{-5}$; Haldane-Anscombe $\\text{OR} = 87.54$, $P = 1.04 \\times 10^{-6}$ in $n = 213$ acquired brain injury trials). Within direct molecular target pharmacotherapy and biologic trials ($n = 60$, $16,349$ participants), high-$\\tau$ drugs reduce failure by $82.2\\%$ ($\\text{OR} = 7.76$, two-sided $P = 0.0120$, multivariable $\\text{OR}_{\\text{adj}} = 9.06$, $P = 0.0095$; continuous acute $\\tau(t_1)$ $\\text{AUROC} = 0.826$, $P = 0.00115$; $n = 51$ ABI molecular drug trials Haldane-Anscombe $\\text{OR} = 28.33$, $P = 0.00116$, subacute $\\tau(t_2)$ $\\text{AUROC} = 0.858$, $P = 0.00142$). Pairing dynamic specificity with BBB dosing-window alignment raises full-cohort failure discrimination from chance ($\\text{AUROC} = 0.501$ on unfiltered stops) to $\\text{AUROC} = 0.868$ ($P = 5.52 \\times 10^{-5}$).
2. **Subacute Specificity Drift ($\\Delta\\tau$) & Six-Gate Ablation Across 10 Unpacked Public Cohorts:** Tracking $133$ neuroimmune candidates across four post-injury stages ($t_0 \\rightarrow t_1 \\rightarrow t_2 \\rightarrow t_3$) reveals that static $\\tau_0 \\ge 0.65$ screening admits $31$ Group III subacute-delocalizing decoys (mean $\\tau_0 = 0.779 \\rightarrow \\tau(t_2) = 0.687$, $\\Delta\\tau = -0.092$, $P = 2.02 \\times 10^{-4}$ versus Tier-1; confirmed directly in subacute scRNA-seq `GSE247339` [$P = 0.0084$] and `GSE226207` [$P = 0.0096$]) and $4$ choroid-plexus/chaperone artifacts (`Ccdc103`, `Alkbh5`, `Canx`, `Hspa5`). A 10-configuration leave-one-gate-out ablation and 1,000-iteration Bradley-Terry-Luce (BTL) / Elo tournament isolate $70$ Tier-1 targets and a top-21 portfolio (`Rnf112`, `Plin4`, `Scn3a`, `Elk1`, `Rapgefl1`, `Folh1`) that improves leave-one-gene-out human surgical hippocampal conservation by $87.2\\%$ over standard bulk differential expression ($|r| = 0.440$ versus $0.235$; 129-patient glia-neuron coupling $r = -0.549$, $P = 1.67 \\times 10^{-11}$).
3. **Multicellular Inflammatory Lock-In Tipping Point ($t_{50} = 16.4\\text{ h}$) & Staged Combination Rescue:** Calibrated across $16$ multi-cohort state readouts ($r = 0.935$, $R^2 = 0.874$; 16-fold LORO $R^2_{\\text{LORO}} = 0.823$, 4-fold LOCO $R^2_{\\text{LOCO}} = 0.821$) and verified across $1,000$ Latin-hypercube $\\pm 20\\%$ 5-ODE numerical integration runs, `vGlia-Niche` identifies an inflammatory lock-in threshold ($E_{\\text{crit}} = 9.5\\text{ storm}\\cdot\\text{h}$) that closes the single-target anti-inflammatory window at $t_{50} = 16.4\\text{ h}$ ($1,000$-LHS median $16.6\\text{ h}$, IQR $15.4\\text{--}17.6\\text{ h}$). Projecting all $129$ human surgical hippocampal samples (`GSE63808`) onto the phase plane confirms that specimens crossing the upper-quartile glial separatrix (`Glial Z >= +0.312`, $n = 33$ vs $n = 96$) exhibit $7.95$-fold higher odds of `SCN3A`/`RNF112` neuronal gate collapse ($57.58\\%$ versus $14.58\\%$, $P = 3.83 \\times 10^{-6}$). While $24\\text{ h}$ delayed monotherapy recovers only $21.9\\%$ of neuronal gate integrity, a BBB-aligned staged combination (`Stage 1: 0–12 h` `Tlr4/Plin4` + `Stage 2: 12–24 h` `Folh1` + `Stage 3: >24 h` `Scn3a/Rnf112`) extends the therapeutic window to $t_{50} = 43.2\\text{ h}$ and predicts $81.4\\%$ recovery at $24\\text{ h}$ delay.

All datasets, clinical trial registries, and analysis scripts (`Supplementary_Software_v2.0.zip`) are 100% publicly archived and cryptographically audited. This manuscript is original, has not been published previously, and is not under consideration at any other journal. All authors have approved the manuscript and declare no competing interests.

Thank you for considering our manuscript for publication in *Nature Communications*.

Sincerely,

**Jiangtao Sheng, Ph.D.** (Lead Contact & Corresponding Author)
Department of Microbiology and Immunology, Shantou University Medical College, Shantou 515041, Guangdong, China
Email: jtsheng@stu.edu.cn | ORCID: 0000-0003-2438-7345

**Weiqiang Chen, M.D., Ph.D.** (Co-Corresponding Author)
Department of Neurosurgery, The First Affiliated Hospital of Shantou University Medical College, Shantou 515041, Guangdong, China
Email: wqchen@stu.edu.cn | ORCID: 0000-0002-2612-0890
"""

cl_path = MS_DIR / "Cover_Letter_NeuroImmune_Virtual_Biotech_EN.md"
cl_path.write_text(COVER_LETTER, encoding="utf-8")
(MS_DIR / "Cover_Letter_EN.md").write_text(COVER_LETTER, encoding="utf-8")
print(f"[OK] Wrote Cover Letter to {cl_path}")
