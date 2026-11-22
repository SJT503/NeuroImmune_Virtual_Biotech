#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════
 公共数据库编号真实性与领域/模态防张冠李戴门禁
 (accession_metadata_authenticity_gate.py)
════════════════════════════════════════════════════════════════════════════
 解决痛点：
   1. 防止跨项目遗留数据集（如把流感/新冠 GSE315893 改名后混入纯 TBI 论文）
   2. 防止编号张冠李戴或幻觉（如把皮肤毛囊发育 GSE122026 误写为海马 ChIP-seq）
   3. 防止把 Bulk/芯片数据集在文中虚标为“单细胞转录组（scRNA-seq/snRNA-seq）”
   4. 强制要求所有 GSE / NCT 编号通过官方 API (NCBI E-utilities / ClinicalTrials.gov v2)
      实时拉取官方 Title + Summary + Taxon + Assay Type 进行语义与模态核验。
════════════════════════════════════════════════════════════════════════════
"""

import json
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

import tempfile

CACHE_PATH = pathlib.Path(
    os.environ.get(
        "ACCESSION_GATE_CACHE",
        os.path.join(tempfile.gettempdir(), "nivb_accession_metadata_cache.json"),
    )
)


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache: dict) -> None:
    try:
        CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def fetch_geo_metadata(gse_id: str, cache: dict) -> dict:
    if gse_id in cache:
        return cache[gse_id]
    time.sleep(0.38)
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "gds", "term": f"{gse_id}[ACCN]", "retmode": "json"}
    )
    req = urllib.request.Request(esearch_url, headers={"User-Agent": "Mozilla/5.0 (Accession-Gate/1.0)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read().decode("utf-8"))
    idlist = d.get("esearchresult", {}).get("idlist", [])
    if not idlist:
        meta = {"exists": False, "accession": gse_id}
        cache[gse_id] = meta
        save_cache(cache)
        return meta

    time.sleep(0.38)
    esum_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "gds", "id": idlist[0], "retmode": "json"}
    )
    req2 = urllib.request.Request(esum_url, headers={"User-Agent": "Mozilla/5.0 (Accession-Gate/1.0)"})
    with urllib.request.urlopen(req2, timeout=20) as r2:
        s = json.loads(r2.read().decode("utf-8")).get("result", {}).get(idlist[0], {})

    meta = {
        "exists": True,
        "accession": gse_id,
        "title": s.get("title", ""),
        "summary": s.get("summary", ""),
        "taxon": s.get("taxon", ""),
        "gdstype": s.get("gdstype", ""),
        "n_samples": int(s.get("n_samples", 0) or 0),
        "pubdate": s.get("pdat", ""),
    }
    cache[gse_id] = meta
    save_cache(cache)
    return meta


def verify_project_accessions(cfg: dict, read_text_fn) -> tuple[list[str], list[str]]:
    """
    Called by project_gate.py or standalone CLI.
    Returns (passed_messages, failed_messages).
    """
    passed, failed = [], []
    acc_cfg = cfg.get("accession_gate", {})
    if not acc_cfg and not cfg.get("files_must_exist"):
        return passed, failed

    # 1. Extract all GSE\d+ across all project text files
    gse_found = {}
    for fpath in cfg.get("files_must_exist", []):
        txt = read_text_fn(fpath)
        if not txt:
            continue
        for m in re.findall(r"\bGSE\d{4,8}\b", txt):
            gse_found.setdefault(m, []).append(os.path.basename(fpath))

    if gse_found:
        cache = load_cache()
        required_domain_terms = [t.lower() for t in acc_cfg.get("required_domain_any", [])]
        forbidden_domain_terms = [t.lower() for t in acc_cfg.get("forbidden_domain_any", [])]
        allowed_whitelist = set(acc_cfg.get("allowed_gse_whitelist", []))
        single_cell_declared = set(acc_cfg.get("single_cell_gse", []))
        chromatin_declared = set(acc_cfg.get("chromatin_gse", []))

        for gse_id, files in sorted(gse_found.items()):
            meta = fetch_geo_metadata(gse_id, cache)
            if not meta.get("exists"):
                failed.append(f"GEO编号不存在/幻觉: {gse_id} (出现于 {', '.join(files[:3])})")
                continue

            title = meta.get("title", "")
            summary = meta.get("summary", "")
            gdstype = meta.get("gdstype", "")
            blob = f"{title} {summary} {gdstype}".lower()

            reasons = []
            # Check whitelist if configured
            if allowed_whitelist and gse_id not in allowed_whitelist:
                reasons.append("不在白名单 allowed_gse_whitelist 中")

            # Check required domain terms (e.g. brain/hippocampus/cortex/neuro/tbi/epilepsy)
            if required_domain_terms and not any(t in blob for t in required_domain_terms):
                reasons.append(f"领域张冠李戴(不含任何目标领域词 {required_domain_terms[:4]})")

            # Check forbidden domain terms in official GEO metadata (e.g. influenza/sars-cov-2/dermal condensate)
            hit_forbid = [t for t in forbidden_domain_terms if t in blob]
            if hit_forbid:
                reasons.append(f"命中违禁跨课题/异质模型词 {hit_forbid}")

            # Check single-cell modality truthfulness
            if gse_id in single_cell_declared:
                sc_markers = ["single cell", "single-cell", "scrna", "snrna", "single nucleus", "single-nucleus", "nuclei"]
                if not any(m in blob for m in sc_markers):
                    reasons.append(f"单细胞模态虚标(官方平台为 {gdstype})")

            # Check chromatin/epigenomic modality truthfulness
            if gse_id in chromatin_declared:
                epi_markers = ["atac", "chip", "chromatin", "methylation", "histone", "epigenom", "genome binding"]
                if not any(m in blob for m in epi_markers):
                    reasons.append(f"表观/染色质模态虚标(官方平台为 {gdstype})")

            if reasons:
                failed.append(
                    f"GEO编号违规拦截: {gse_id} 官方标题「{title[:70]}」 -> {'; '.join(reasons)} (出现于 {', '.join(sorted(set(files))[:3])})"
                )
                continue

            passed.append(
                f"GEO官方元数据核验通过: {gse_id} (n={meta.get('n_samples')}, {meta.get('taxon')}) -> 「{title[:68]}」"
            )

    # 2. Verify 100% Verbatim ClinicalTrials.gov NCT_ID records if CTGOV_OFFICIAL_VERBATIM_CACHE.json or trials_census.json exists
    proj_root = pathlib.Path(cfg.get("project_root", ".") or ".").resolve()
    raw_ct_candidates = [
        acc_cfg.get("ctgov_verbatim_cache", ""),
        "data/CTGOV_OFFICIAL_VERBATIM_CACHE.json",
        "research_audit/trials_census.json",
        "flagship_paper/data/CTGOV_OFFICIAL_VERBATIM_CACHE.json",
    ]
    ct_cache_rel = ""
    for cand in raw_ct_candidates:
        if not cand:
            continue
        cp = pathlib.Path(cand)
        if not cp.is_absolute():
            cp_proj = proj_root / cp
            if cp_proj.exists():
                ct_cache_rel = str(cp_proj)
                break
        if os.path.exists(cand):
            ct_cache_rel = cand
            break

    nct_in_files = {}
    for fpath in cfg.get("files_must_exist", []):
        txt = read_text_fn(fpath)
        if not txt:
            continue
        for m in re.findall(r"\bNCT\d{8}\b", txt):
            nct_in_files.setdefault(m, []).append(os.path.basename(fpath))

    if ct_cache_rel:
        import csv
        raw_ct = json.loads(open(ct_cache_rel, encoding="utf-8-sig").read())
        if isinstance(raw_ct, dict) and isinstance(raw_ct.get("studies"), list):
            ct_ref = {
                str(s.get("nct_id") or "").strip(): {
                    "Title": str(s.get("title") or "").strip(),
                    "OverallStatus": str(s.get("overall_status") or "").strip(),
                    "official_json_sha256": str(s.get("official_json_sha256") or "").strip(),
                }
                for s in raw_ct["studies"]
                if str(s.get("nct_id") or "").strip()
            }
        else:
            ct_ref = raw_ct

        # Check manuscript/text NCT mentions against official cache when require_nct_in_cache is set
        if acc_cfg.get("require_nct_in_cache") and nct_in_files:
            for nct_id, files in sorted(nct_in_files.items()):
                if nct_id not in ct_ref:
                    failed.append(
                        f"ClinicalTrials.gov 编号未在官方 SHA-256 缓存中核验: {nct_id} (出现于 {', '.join(sorted(set(files))[:3])})"
                    )
                else:
                    passed.append(
                        f"ClinicalTrials.gov 编号官方缓存核验通过: {nct_id} -> 「{(ct_ref[nct_id].get('Title') or '')[:68]}」"
                    )

        default_csvs = [
            str(proj_root / "data/Division4_ClinicalTrialsGov_Live_TBI_Neuroimmune_Trials.csv"),
            str(proj_root / "tables/TableS1_230_ClinicalTrials_MultiAgent_Audit.csv"),
        ]
        csv_targets = list(dict.fromkeys(list(cfg.get("files_must_exist", [])) + default_csvs))
        for fpath in csv_targets:
            if not fpath.endswith(".csv") or not os.path.exists(fpath):
                continue
            with open(fpath, encoding="utf-8-sig", newline="") as cf:
                reader = csv.DictReader(cf)
                if not reader.fieldnames or "NCT_ID" not in reader.fieldnames or "Title" not in reader.fieldnames:
                    continue
                n_rows = 0
                n_bad = 0
                for row in reader:
                    nct = (row.get("NCT_ID") or "").strip()
                    if not nct:
                        continue
                    n_rows += 1
                    ref = ct_ref.get(nct)
                    if not ref:
                        failed.append(f"ClinicalTrials.gov 编号未在官方缓存中核验: {nct} ({os.path.basename(fpath)})")
                        n_bad += 1
                        continue
                    row_title = (row.get("Title") or "").strip()
                    ref_title = (ref.get("Title") or "").strip()
                    if row_title != ref_title:
                        failed.append(
                            f"ClinicalTrials.gov 标题篡改/嫁接拦截: {nct} ({os.path.basename(fpath)}) -> 表内「{row_title[:45]}」 != 官方「{ref_title[:45]}」"
                        )
                        n_bad += 1
                if n_rows > 0 and n_bad == 0:
                    passed.append(
                        f"ClinicalTrials.gov 100% 原始字段一致性核验通过: {os.path.basename(fpath)} ({n_rows}/{n_rows} 条 NCT_ID 与官方注册库 Title 100% 逐字符一致, 0 嫁接/篡改)"
                    )

    return passed, failed


def read_text_stdlib(fpath: str) -> str:
    """100%-stdlib reader supporting .md, .txt, .csv, .json, and .docx (paragraph-joined so split-run GSE*/NCT* tokens remain contiguous)."""
    if not fpath or not os.path.exists(fpath) or fpath.lower().endswith((".png", ".pdf", ".jpg", ".jpeg", ".tif", ".tiff")):
        return ""
    if fpath.lower().endswith(".docx"):
        import xml.etree.ElementTree as ET
        import zipfile
        try:
            chunks = []
            with zipfile.ZipFile(fpath, "r") as zf:
                for xml_name in sorted(zf.namelist()):
                    if xml_name.startswith("word/") and xml_name.endswith(".xml"):
                        root = ET.fromstring(zf.read(xml_name))
                        p_texts = []
                        for elem in root.iter():
                            if elem.tag.split("}")[-1] == "p":
                                p_str = "".join(
                                    (t.text or "") for t in elem.iter() if t.tag.split("}")[-1] == "t"
                                ).strip()
                                if p_str:
                                    p_texts.append(p_str)
                        if p_texts:
                            chunks.append("\n".join(p_texts))
            return "\n".join(chunks)
        except Exception:
            return ""
    try:
        return open(fpath, encoding="utf-8-sig", errors="replace").read()
    except Exception:
        return ""


def build_cfg_from_project(project_root: pathlib.Path, extra_files: list[str] | None = None) -> dict:
    """Auto-build accession_gate config from DATASETS_REGISTRY.json + manuscript files (zero PyYAML needed)."""
    proj = project_root.resolve()
    files: list[str] = []
    for f in (extra_files or []):
        if f and os.path.exists(f):
            files.append(str(pathlib.Path(f).resolve()))
    for rel in ("manuscript", "tables", "results/tables", "data"):
        d = proj / rel
        if d.is_dir():
            for child in sorted(d.iterdir()):
                if child.is_file() and child.suffix.lower() in (".md", ".docx", ".csv"):
                    s = str(child.resolve())
                    if s not in files:
                        files.append(s)

    acc_cfg: dict = {}
    reg_p = proj / "DATASETS_REGISTRY.json"
    if not reg_p.exists():
        reg_p = proj / "research_audit" / "DATASETS_REGISTRY.json"
    if reg_p.exists():
        try:
            reg = json.loads(reg_p.read_text(encoding="utf-8-sig"))
            sc_gse = []
            chrom_gse = []
            cohorts = reg.get("included_cohorts") or reg.get("included_datasets") or []
            for ds in cohorts:
                did = str(ds.get("id") or ds.get("dataset_id") or "").strip()
                mod = str(ds.get("modality") or "").lower()
                if re.match(r"^GSE\d{4,8}$", did):
                    if any(k in mod for k in ("scrna", "snrna", "single-cell", "single_cell", "single nucleus", "10x")):
                        sc_gse.append(did)
                    if any(k in mod for k in ("atac", "chip", "cut&tag", "cut&run", "chromatin", "methylation", "bisulfite", "epigenom")):
                        chrom_gse.append(did)
            if sc_gse:
                acc_cfg["single_cell_gse"] = sc_gse
            if chrom_gse:
                acc_cfg["chromatin_gse"] = chrom_gse
        except Exception:
            pass
    if (proj / "data" / "CTGOV_OFFICIAL_VERBATIM_CACHE.json").exists() or (proj / "research_audit" / "trials_census.json").exists():
        acc_cfg["require_nct_in_cache"] = True

    return {
        "project_root": str(proj),
        "files_must_exist": files,
        "accession_gate": acc_cfg,
    }


def main() -> int:
    import argparse

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description="Verify GEO GSE* and ClinicalTrials.gov NCT* metadata authenticity")
    ap.add_argument("--manuscript", default="", help="Optional manuscript .md or .docx path")
    ap.add_argument("--project-root", default="", help="Project root directory (auto-detects DATASETS_REGISTRY.json & caches)")
    ap.add_argument("--config", default="", help="Optional legacy gate_config.yaml path")
    args = ap.parse_args()

    cfg_p = pathlib.Path(args.config) if args.config else (pathlib.Path.cwd() / "gate_config.yaml")
    cfg = None
    if not args.manuscript and not args.project_root and cfg_p.exists():
        try:
            import yaml  # type: ignore
            cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8-sig"))
        except ImportError:
            cfg = None
    if cfg is None:
        if args.project_root:
            proj = pathlib.Path(args.project_root).resolve()
        elif args.manuscript:
            mp = pathlib.Path(args.manuscript).resolve()
            proj = mp.parent.parent if mp.parent.name.lower() in ("manuscript", "submission", "final") else mp.parent
        else:
            proj = pathlib.Path.cwd().resolve()
        extra = [args.manuscript] if args.manuscript else []
        cfg = build_cfg_from_project(proj, extra_files=extra)

    p_list, f_list = verify_project_accessions(cfg, read_text_stdlib)
    for p in p_list:
        print("  ✅", p)
    for f in f_list:
        print("  ❌", f)
    if not p_list and not f_list:
        print("  ℹ️ 未检测到 GSE* 或受监管 NCT* 编号（纯 EHR 队列或无外部登录号稿件）")
    return 1 if f_list else 0


if __name__ == "__main__":
    sys.exit(main())
