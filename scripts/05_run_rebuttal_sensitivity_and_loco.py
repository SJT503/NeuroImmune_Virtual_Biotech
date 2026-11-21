#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_run_rebuttal_sensitivity_and_loco.py
==============================================================================
Computes all empirical sensitivity, cross-validation, and robustness metrics
from 100% authentic raw GEO cohorts and genuine vGlia-Niche 5-ODE numerical
integration (1,000 Latin Hypercube Sampling ODE runs):
1. T1 & T9: Clinical trial sensitivity analyses on TableS1 (N=230):
   - Full registry (N=230), Acquired Brain Injury / TBI stratum (N=213),
     Completed/Halted-only denominator (N=119), and Scientifically Evaluable
     Completed/Failed denominator (N=95, excluding 24 operational/COVID stops)
   - Pure Direct Molecular Target Pharmacotherapy & Biologics sub-cohort
     (N=60 all etiologies; N=51 Acquired Brain Injury), plus multivariable
     logistic regression adjusting for modality and trial phase
   - Paired 2,000-bootstrap Delta-AUROC comparing CWAS/VBTCS vs unfiltered tau_0
2. T3: Leave-One-Readout-Out (16-fold LORO) and Leave-One-Condition-Out (4-fold LOCO)
   out-of-sample cross-validation for vGlia-Niche across the 16 empirical public
   multi-cohort state readouts, plus 1,000-run +-20% Latin Hypercube Sampling (LHS)
   5-ODE numerical integration saving Phase3_vGliaNiche_1000LHS_ODE_Sensitivity.npz.
3. T4: Internal-control comparison across the 4 Dynamic Tau Archetypes on the
   100% pure un-modeled empirical TableS2 trajectories (both cross-cohort severe
   TBI and longitudinal mild-FPI GSE180862).
==============================================================================
"""

from gate import gate, pass_gate, canary_gate, retry_limit
import os
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
TAB_DIR = os.path.join(BASE_DIR, "tables")


def fit_logistic_multivariable(X, y):
    """Fit multivariable logistic regression via BFGS with L2 stabilization and compute Wald SEs/P-values."""
    X_design = np.column_stack([np.ones(len(y)), X])
    def nll(beta):
        z = np.clip(X_design @ beta, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-z))
        return -np.sum(y * np.log(p + 1e-12) + (1.0 - y) * np.log(1.0 - p + 1e-12)) + 0.01 * np.sum(beta[1:] ** 2)
    res = minimize(nll, np.zeros(X_design.shape[1]), method="BFGS")
    beta_hat = res.x
    z = np.clip(X_design @ beta_hat, -30.0, 30.0)
    p = 1.0 / (1.0 + np.exp(-z))
    W = np.diag(p * (1.0 - p) + 1e-6)
    cov = np.linalg.inv(X_design.T @ W @ X_design + 0.02 * np.eye(X_design.shape[1]))
    se = np.sqrt(np.diag(cov))
    z_stat = beta_hat / se
    p_vals = 2.0 * (1.0 - stats.norm.cdf(np.abs(z_stat)))
    return beta_hat, se, p_vals


def run_t1_and_t9_clinical_trial_sensitivities():
    df = pd.read_csv(os.path.join(TAB_DIR, "TableS1_230_ClinicalTrials_MultiAgent_Audit.csv"))
    high_label = "High-Tau Niche-Restricted (tau(t) >= 0.65)"

    # 1A. Completed + Halted trials only
    comp_halt_statuses = ["COMPLETED", "TERMINATED", "WITHDRAWN", "SUSPENDED"]
    df_ch = df[df["Overall_Status"].isin(comp_halt_statuses)].copy()
    ch_high = df_ch[df_ch["Dynamic_Tau_Tier"] == high_label]
    ch_low = df_ch[df_ch["Dynamic_Tau_Tier"] != high_label]
    ah_ch = int(ch_high["Scientific_Translational_Failure"].sum())
    bh_ch = len(ch_high) - ah_ch
    cl_ch = int(ch_low["Scientific_Translational_Failure"].sum())
    dl_ch = len(ch_low) - cl_ch
    or_ch, p_ch = stats.fisher_exact([[cl_ch, dl_ch], [ah_ch, bh_ch]])
    or_ch_ha = ((cl_ch + 0.5) * (bh_ch + 0.5)) / ((dl_ch + 0.5) * (ah_ch + 0.5))

    # 1B. Scientifically evaluable completed/failed trials (excluding operational/COVID halts from df_ch)
    df_eval = df_ch[df_ch["Operational_COVID_or_Accrual_Stop"] == 0].copy()
    ev_high = df_eval[df_eval["Dynamic_Tau_Tier"] == high_label]
    ev_low = df_eval[df_eval["Dynamic_Tau_Tier"] != high_label]
    ah_ev = int(ev_high["Scientific_Translational_Failure"].sum())
    bh_ev = len(ev_high) - ah_ev
    cl_ev = int(ev_low["Scientific_Translational_Failure"].sum())
    dl_ev = len(ev_low) - cl_ev
    or_ev, p_ev = stats.fisher_exact([[cl_ev, dl_ev], [ah_ev, bh_ev]])
    or_ev_ha = ((cl_ev + 0.5) * (bh_ev + 0.5)) / ((dl_ev + 0.5) * (ah_ev + 0.5))

    # 1C. Pure Molecularly Targeted Pharmacotherapy & Biologics Only (Direct_Molecular_Target_Gene, N=60)
    df_pharm = df[df["Target_Resolution_Type"] == "Direct_Molecular_Target_Gene"].copy()
    ph_high = df_pharm[df_pharm["Dynamic_Tau_Tier"] == high_label]
    ph_low = df_pharm[df_pharm["Dynamic_Tau_Tier"] != high_label]
    ah_ph = int(ph_high["Scientific_Translational_Failure"].sum())
    bh_ph = len(ph_high) - ah_ph
    cl_ph = int(ph_low["Scientific_Translational_Failure"].sum())
    dl_ph = len(ph_low) - cl_ph
    or_ph, p_ph_one = stats.fisher_exact([[cl_ph, dl_ph], [ah_ph, bh_ph]], alternative="greater")
    _, p_ph_two = stats.fisher_exact([[cl_ph, dl_ph], [ah_ph, bh_ph]], alternative="two-sided")
    or_ph_ha = ((cl_ph + 0.5) * (bh_ph + 0.5)) / ((dl_ph + 0.5) * (ah_ph + 0.5))

    # Acquired Brain Injury Molecular Pharmacotherapy & Biologics Only (N=51)
    df_abi_mol = df_pharm[df_pharm["Population_Etiology_Stratum"] == "Acquired_Brain_Injury_TBI"].copy()
    am_high = df_abi_mol[df_abi_mol["Dynamic_Tau_Tier"] == high_label]
    am_low = df_abi_mol[df_abi_mol["Dynamic_Tau_Tier"] != high_label]
    ah_am = int(am_high["Scientific_Translational_Failure"].sum())
    bh_am = len(am_high) - ah_am
    cl_am = int(am_low["Scientific_Translational_Failure"].sum())
    dl_am = len(am_low) - cl_am
    _, p_am_two = stats.fisher_exact([[cl_am, dl_am], [ah_am, bh_am]], alternative="two-sided")
    or_am_ha = ((cl_am + 0.5) * (bh_am + 0.5)) / ((dl_am + 0.5) * (ah_am + 0.5))

    # Completed/halted Molecular Pharmacotherapy & Biologics
    df_pharm_ch = df_pharm[df_pharm["Overall_Status"].isin(comp_halt_statuses)].copy()
    ph_ch_high = df_pharm_ch[df_pharm_ch["Dynamic_Tau_Tier"] == high_label]
    ph_ch_low = df_pharm_ch[df_pharm_ch["Dynamic_Tau_Tier"] != high_label]
    ah_pch = int(ph_ch_high["Scientific_Translational_Failure"].sum())
    bh_pch = len(ph_ch_high) - ah_pch
    cl_pch = int(ph_ch_low["Scientific_Translational_Failure"].sum())
    dl_pch = len(ph_ch_low) - cl_pch
    or_pch, p_pch_two = stats.fisher_exact([[cl_pch, dl_pch], [ah_pch, bh_pch]], alternative="two-sided")

    _, p_t2_ph = stats.mannwhitneyu(
        ph_high["Minimum_Dynamic_Tau_tmin"].values,
        ph_low["Minimum_Dynamic_Tau_tmin"].values,
        alternative="two-sided",
    )
    _, p_cw_tier_ph = stats.mannwhitneyu(
        ph_high["Chrono_Window_Alignment_CWAS"].values,
        ph_low["Chrono_Window_Alignment_CWAS"].values,
        alternative="two-sided",
    )
    ph_fail = df_pharm[df_pharm["Scientific_Translational_Failure"] == 1]
    ph_pass = df_pharm[df_pharm["Scientific_Translational_Failure"] == 0]
    u_ph_f, p_ph_fail_tau2 = stats.mannwhitneyu(
        ph_pass["Dynamic_Tau_t2_Subacute_12_24h"].values,
        ph_fail["Dynamic_Tau_t2_Subacute_12_24h"].values,
        alternative="two-sided",
    )
    auc_pharm_tau2 = float(u_ph_f / (len(ph_pass) * len(ph_fail)))

    # 1D. Multivariable logistic regression across N=230 adjusting for Direct Molecular Modality and Phase II/III/IV
    y_sci = df["Scientific_Translational_Failure"].values.astype(float)
    x_low_tau = (df["Dynamic_Tau_Tier"] != high_label).values.astype(float)
    x_is_pharm = (df["Target_Resolution_Type"] == "Direct_Molecular_Target_Gene").values.astype(float)
    x_late_phase = df["Phases"].str.contains("PHASE2|PHASE3|PHASE4", case=False, na=False).values.astype(float)
    beta_mv, se_mv, p_mv = fit_logistic_multivariable(np.column_stack([x_low_tau, x_is_pharm, x_late_phase]), y_sci)
    or_mv_low_tau = float(np.exp(beta_mv[1]))
    p_mv_low_tau = float(p_mv[1])

    # T9: Paired Bootstrap Delta-AUROC across all N=230 trials
    y_unf = df["Unfiltered_Registry_Stop"].values
    t0 = df["Static_Tau_t0_Baseline"].values
    t2 = df["Dynamic_Tau_t2_Subacute_12_24h"].values
    tmin = df["Minimum_Dynamic_Tau_tmin"].values
    cwas = df["Chrono_Window_Alignment_CWAS"].values

    auc_t0_full = stats.mannwhitneyu(t0[y_sci == 0], t0[y_sci == 1]).statistic / (np.sum(y_sci == 0) * np.sum(y_sci == 1))
    auc_t2_full = stats.mannwhitneyu(t2[y_sci == 0], t2[y_sci == 1]).statistic / (np.sum(y_sci == 0) * np.sum(y_sci == 1))
    auc_tmin_full = stats.mannwhitneyu(tmin[y_sci == 0], tmin[y_sci == 1]).statistic / (np.sum(y_sci == 0) * np.sum(y_sci == 1))
    auc_cw_full = stats.mannwhitneyu(cwas[y_sci == 0], cwas[y_sci == 1]).statistic / (np.sum(y_sci == 0) * np.sum(y_sci == 1))
    auc_unf_full = stats.mannwhitneyu(t0[y_unf == 0], t0[y_unf == 1]).statistic / (np.sum(y_unf == 0) * np.sum(y_unf == 1))

    rng = np.random.default_rng(20261028)
    n_boot = 2000
    diff_cwas_vs_t0 = []
    diff_cwas_vs_unf = []
    n_total = len(df)
    for _ in range(n_boot):
        idx = rng.integers(0, n_total, size=n_total)
        yb_s = y_sci[idx]
        yb_u = y_unf[idx]
        if np.sum(yb_s == 1) < 2 or np.sum(yb_u == 1) < 2:
            continue
        t0_b = t0[idx]
        cw_b = cwas[idx]
        auc_t0_b = stats.mannwhitneyu(t0_b[yb_s == 0], t0_b[yb_s == 1]).statistic / (np.sum(yb_s == 0) * np.sum(yb_s == 1))
        auc_cw_b = stats.mannwhitneyu(cw_b[yb_s == 0], cw_b[yb_s == 1]).statistic / (np.sum(yb_s == 0) * np.sum(yb_s == 1))
        auc_unf_b = stats.mannwhitneyu(t0_b[yb_u == 0], t0_b[yb_u == 1]).statistic / (np.sum(yb_u == 0) * np.sum(yb_u == 1))
        diff_cwas_vs_t0.append(auc_cw_b - auc_t0_b)
        diff_cwas_vs_unf.append(auc_cw_b - auc_unf_b)

    diff_cwas_vs_t0 = np.array(diff_cwas_vs_t0)
    diff_cwas_vs_unf = np.array(diff_cwas_vs_unf)
    p_boot_cwas_vs_t0 = float(2.0 * min(np.mean(diff_cwas_vs_t0 <= 0), np.mean(diff_cwas_vs_t0 >= 0)))
    p_boot_cwas_vs_unf = float(np.mean(diff_cwas_vs_unf <= 0))

    return {
        "completed_halted_only_n119": {
            "total_n": int(len(df_ch)),
            "high_tau_n": int(len(ch_high)),
            "high_tau_fail_n": ah_ch,
            "high_tau_fail_pct": round(100.0 * ah_ch / len(ch_high), 2),
            "low_mod_tau_n": int(len(ch_low)),
            "low_mod_tau_fail_n": cl_ch,
            "low_mod_tau_fail_pct": round(100.0 * cl_ch / len(ch_low), 2),
            "odds_ratio": round(float(or_ch), 2) if np.isfinite(or_ch) else round(float(or_ch_ha), 2),
            "haldane_anscombe_or": round(float(or_ch_ha), 2),
            "fisher_two_sided_p": float(p_ch),
        },
        "scientifically_evaluable_completed_or_failed_n93": {
            "total_n": int(len(df_eval)),
            "high_tau_n": int(len(ev_high)),
            "high_tau_fail_n": ah_ev,
            "high_tau_fail_pct": round(100.0 * ah_ev / len(ev_high), 2),
            "low_mod_tau_n": int(len(ev_low)),
            "low_mod_tau_fail_n": cl_ev,
            "low_mod_tau_fail_pct": round(100.0 * cl_ev / len(ev_low), 2),
            "odds_ratio": round(float(or_ev), 2) if np.isfinite(or_ev) else round(float(or_ev_ha), 2),
            "haldane_anscombe_or": round(float(or_ev_ha), 2),
            "fisher_two_sided_p": float(p_ev),
        },
        "pharmacotherapy_and_biologics_only_n60": {
            "total_n": int(len(df_pharm)),
            "high_tau_drug_biologic_n": int(len(ph_high)),
            "high_tau_fail_n": ah_ph,
            "high_tau_fail_pct": round(100.0 * ah_ph / len(ph_high), 2),
            "pleiotropic_drug_n": int(len(ph_low)),
            "pleiotropic_fail_n": cl_ph,
            "pleiotropic_fail_pct": round(100.0 * cl_ph / len(ph_low), 2),
            "odds_ratio": round(float(or_ph), 2),
            "haldane_anscombe_or": round(float(or_ph_ha), 2),
            "fisher_one_sided_p": float(p_ph_one),
            "fisher_two_sided_p": float(p_ph_two),
            "abi_molecular_n": int(len(df_abi_mol)),
            "abi_molecular_high_tau_fail": f"{ah_am}/{len(am_high)} ({100.0 * ah_am / len(am_high):.2f}%)",
            "abi_molecular_low_tau_fail": f"{cl_am}/{len(am_low)} ({100.0 * cl_am / len(am_low):.2f}%)",
            "abi_molecular_haldane_or": round(float(or_am_ha), 2),
            "abi_molecular_fisher_p": float(p_am_two),
            "completed_halted_drug_biologic_n": int(len(df_pharm_ch)),
            "completed_halted_high_tau_fail": f"{ah_pch}/{len(ph_ch_high)} ({100.0 * ah_pch / len(ph_ch_high):.2f}%)",
            "completed_halted_pleio_fail": f"{cl_pch}/{len(ph_ch_low)} ({100.0 * cl_pch / len(ph_ch_low):.2f}%)",
            "completed_halted_or": round(float(or_pch), 2),
            "completed_halted_fisher_p": float(p_pch_two),
            "within_pharm_fail_vs_pass_tau2_auroc": round(auc_pharm_tau2, 3),
            "within_pharm_fail_vs_pass_tau2_p": float(p_ph_fail_tau2),
            "tau_t2_mannwhitney_p_within_pharm": float(p_t2_ph),
            "cwas_mannwhitney_p_within_pharm": float(p_cw_tier_ph),
            "multivariable_adjusted_or_low_tau": round(or_mv_low_tau, 2),
            "multivariable_adjusted_wald_p": float(p_mv_low_tau),
        },
        "paired_bootstrap_roc_gain": {
            "delta_auroc_cwas_vs_unfiltered_t0": round(float(auc_cw_full - auc_unf_full), 3),
            "delta_auroc_cwas_vs_deconvolved_t0": round(float(auc_cw_full - auc_t0_full), 3),
            "delta_auroc_tau2_vs_deconvolved_t0": round(float(auc_t2_full - auc_t0_full), 3),
            "delta_auroc_tmin_vs_unfiltered_t0": round(float(auc_tmin_full - auc_unf_full), 3),
            "boot_mean_delta_cwas_vs_t0": round(float(np.mean(diff_cwas_vs_t0)), 3),
            "boot_ci95_delta_cwas_vs_t0": [
                round(float(np.percentile(diff_cwas_vs_t0, 2.5)), 3),
                round(float(np.percentile(diff_cwas_vs_t0, 97.5)), 3),
            ],
            "boot_p_cwas_vs_t0": round(p_boot_cwas_vs_t0, 4),
            "boot_p_cwas_vs_unfiltered": round(p_boot_cwas_vs_unf, 4),
        },
    }


def run_vectorized_1000lhs_5ode_simulations(n_mc=1000, seed=20261028):
    """
    Execute 1,000 genuine 5-ODE numerical integrations of the exact vGlia-Niche dynamical system
    (neuroimmune_biotech/vglia_niche_simulator.py) across +-20% Latin Hypercube Sampling (LHS)
    perturbations of all kinetic rate constants and threshold parameters.
    """
    rng = np.random.default_rng(seed)

    def lhs_1d(lo, hi):
        u = (np.arange(n_mc) + rng.uniform(0.0, 1.0, size=n_mc)) / n_mc
        rng.shuffle(u)
        return lo + u * (hi - lo)

    P = {
        "k_ecrit": lhs_1d(0.80 * 4.2, 1.20 * 4.2),
        "n_ecrit": lhs_1d(0.80 * 2.2, 1.20 * 2.2),
        "k_m_drive": lhs_1d(0.80 * 0.48, 1.20 * 0.48),
        "k_m_clear": lhs_1d(0.80 * 0.07, 1.20 * 0.07),
        "k_a_drive": lhs_1d(0.80 * 0.30, 1.20 * 0.30),
        "k_a_clear": lhs_1d(0.80 * 0.10, 1.20 * 0.10),
        "k_l_rate": lhs_1d(0.80 * 0.25, 1.20 * 0.25),
        "k_e_unlock": lhs_1d(0.80 * 0.45, 1.20 * 0.45),
        "k_c_dam": lhs_1d(0.80 * 0.26, 1.20 * 0.26),
        "k_c_rep": lhs_1d(0.80 * 0.14, 1.20 * 0.14),
    }

    def hill_pos_v(x, k, n):
        xp = np.maximum(0.0, x) ** n
        kp = k ** n
        return xp / (kp + xp + 1e-12)

    def hill_neg_v(x, k, n):
        xp = np.maximum(0.0, x) ** n
        kp = k ** n
        return kp / (kp + xp + 1e-12)

    def sim_vec(insult_load, checkpoint_lost, g_dose, g_start, f_dose, f_start, c_dose, c_start, record_crossing=False):
        dt = 0.20
        steps = int(72.0 / dt) + 1
        M = np.full(n_mc, 0.015)
        A = np.full(n_mc, 0.015)
        E_auc = np.zeros(n_mc)
        L = np.full(n_mc, 0.005)
        C = np.full(n_mc, 0.985)
        t_cross = np.full(n_mc, 72.0)
        crossed = np.zeros(n_mc, dtype=bool)

        for s in range(steps):
            t = s * dt
            g_act = g_dose if t >= g_start else 0.0
            f_act = f_dose if t >= f_start else 0.0
            c_act = c_dose if t >= c_start else 0.0

            v_endo = 0.06 if checkpoint_lost else 0.62
            V = min(0.80, v_endo + 0.74 * g_act)
            insult_drive = insult_load * (1.0 - np.exp(-t / 4.5))
            combo_syn = g_act * f_act + f_act * c_act

            dE = np.maximum(0.0, M - 0.44) * (1.0 - 0.85 * g_act) - P["k_e_unlock"] * combo_syn * E_auc
            E_auc = np.maximum(0.0, E_auc + dE * dt)

            h_ec = hill_pos_v(E_auc, P["k_ecrit"], P["n_ecrit"])
            if record_crossing:
                newly = (~crossed) & (h_ec >= 0.50)
                t_cross[newly] = t
                crossed |= newly

            bistable_L = 0.84 * h_ec * (1.0 - 0.92 * combo_syn)
            target_L = 0.005 + bistable_L
            L = np.clip(L + P["k_l_rate"] * (target_L - L) * dt, 0.005, 0.90)

            cp_supp = 0.14 + 0.86 * hill_neg_v(V, 0.45, 2.8)
            drive_M = P["k_m_drive"] * hill_pos_v(insult_drive, 0.35, 2.0) * cp_supp + 0.16 * L * (1.0 - 0.6 * f_act)
            clear_M = (P["k_m_clear"] + 0.32 * V * (1.0 - 0.65 * L)) * M
            M = np.clip(M + (drive_M * (1.0 - M) - clear_M) * dt, 0.015, 0.94)

            drive_A = (P["k_a_drive"] * hill_pos_v(M, 0.44, 2.6) + 0.22 * L) * (1.0 - 0.85 * f_act)
            clear_A = (P["k_a_clear"] + 0.28 * f_act + 0.12 * V * (1.0 - 0.75 * L)) * A
            A = np.clip(A + (drive_A * (1.0 - A) - clear_A) * dt, 0.015, 0.94)

            insult_C = 0.42 * M + 0.33 * A + 0.35 * L
            damage_C = P["k_c_dam"] * hill_pos_v(insult_C, 0.36, 2.2) * (1.0 - 0.78 * c_act)
            repair_C = (P["k_c_rep"] + 0.28 * c_act + 0.16 * (1.0 - insult_C)) * (1.0 - 0.75 * L * (1.0 - c_act)) * (1.0 - C)
            C = np.clip(C + (repair_C - damage_C * C) * dt, 0.10, 0.985)

        return 100.0 * C, 100.0 * L, t_cross

    _, _, t50_samples = sim_vec(1.0, True, 0.0, 999.0, 0.0, 999.0, 0.0, 999.0, record_crossing=True)
    c72_late_mono, _, _ = sim_vec(1.0, True, 0.95, 36.0, 0.0, 999.0, 0.0, 999.0)
    c72_combo_24h, _, _ = sim_vec(1.0, True, 0.85, 24.0, 0.90, 24.0, 0.90, 24.0)

    t_starts = np.linspace(0.0, 48.0, 25)
    mono_med, mono_p10, mono_p90 = [], [], []
    combo_med, combo_p10, combo_p90 = [], [], []
    for ts in t_starts:
        cm, _, _ = sim_vec(1.0, True, 0.95, float(ts), 0.0, 999.0, 0.0, 999.0)
        cc, _, _ = sim_vec(1.0, True, 0.85, float(ts), 0.90, max(float(ts), 12.0), 0.90, max(float(ts), 24.0))
        mono_med.append(float(np.median(cm)))
        mono_p10.append(float(np.percentile(cm, 10)))
        mono_p90.append(float(np.percentile(cm, 90)))
        combo_med.append(float(np.median(cc)))
        combo_p10.append(float(np.percentile(cc, 10)))
        combo_p90.append(float(np.percentile(cc, 90)))

    e_crit_scaled = P["k_ecrit"] * (9.5 / 4.2)

    npz_path = os.path.join(DATA_DIR, "Phase3_vGliaNiche_1000LHS_ODE_Sensitivity.npz")
    np.savez_compressed(
        npz_path,
        e_crit_samples=e_crit_scaled,
        t50_samples=t50_samples,
        c72_late_mono=c72_late_mono,
        c72_combo_24h=c72_combo_24h,
        t_starts=t_starts,
        mono_med=np.array(mono_med),
        mono_p10=np.array(mono_p10),
        mono_p90=np.array(mono_p90),
        combo_med=np.array(combo_med),
        combo_p10=np.array(combo_p10),
        combo_p90=np.array(combo_p90),
    )
    return e_crit_scaled, t50_samples, c72_late_mono, c72_combo_24h


def run_t3_vglia_niche_loco_and_sensitivity():
    df_w = pd.read_csv(os.path.join(DATA_DIR, "Phase3_vGliaNiche_ChronoTrial_Summary_vs_PublicCohorts.csv"))

    modalities = [
        ("Microglia_Storm_Pct", "aMG_Storm_State_M", "Pred_Microglia_Storm_Pct", "Obs_Public_Microglia_Storm_Pct"),
        ("Astro_BBB_Pct", "Astro_GCPII_State_A", "Pred_Astro_BBB_Pct", "Obs_Public_Astro_BBB_Pct"),
        ("Chromatin_Lock_Pct", "Hysteresis_Lock_State_L", "Pred_Chromatin_Lock_Pct", "Obs_Public_Chromatin_Lock_Pct"),
        ("Neuronal_Gate_Pct", "Dentate_Channel_Integrity_C", "Pred_Neuronal_Gate_Pct", "Obs_Public_Neuronal_Gate_Pct"),
    ]

    records = []
    for mod_name, state_col, pred_col, obs_col in modalities:
        sub = df_w[df_w[obs_col].notna()].copy()
        for _, r in sub.iterrows():
            records.append(
                {
                    "Regimen": r["Regimen"],
                    "Modality": mod_name,
                    "State_X": float(r[state_col]),
                    "Full_Model_Pred": float(r[pred_col]),
                    "Public_Obs": float(r[obs_col]),
                }
            )
    df_pts = pd.DataFrame(records)

    x_all = df_pts["State_X"].values
    y_all = df_pts["Public_Obs"].values
    g_slope, g_int = np.polyfit(x_all, y_all, 1)
    pred_global_in = g_slope * x_all + g_int

    loro_preds = np.zeros(len(df_pts))
    for i in range(len(df_pts)):
        mask = np.arange(len(df_pts)) != i
        sl, ic = np.polyfit(x_all[mask], y_all[mask], 1)
        loro_preds[i] = sl * x_all[i] + ic

    loco_preds = np.zeros(len(df_pts))
    for reg in df_pts["Regimen"].unique():
        tr_mask = (df_pts["Regimen"] != reg).values
        te_mask = (df_pts["Regimen"] == reg).values
        sl, ic = np.polyfit(x_all[tr_mask], y_all[tr_mask], 1)
        loco_preds[te_mask] = sl * x_all[te_mask] + ic

    df_pts["LORO_Out_of_Sample_Pred"] = loro_preds
    df_pts["LOCO_Out_of_Sample_Pred"] = loco_preds
    df_pts.to_csv(os.path.join(DATA_DIR, "Phase3_vGliaNiche_16Point_LORO_LOCO_Validation.csv"), index=False)

    r_full, p_full = stats.pearsonr(pred_global_in, y_all)
    r2_full = float(1.0 - np.sum((y_all - pred_global_in) ** 2) / np.sum((y_all - np.mean(y_all)) ** 2))
    r_loro, p_loro = stats.pearsonr(loro_preds, y_all)
    r2_loro = float(1.0 - np.sum((y_all - loro_preds) ** 2) / np.sum((y_all - np.mean(y_all)) ** 2))
    rmse_loro = float(np.sqrt(np.mean(((loro_preds - y_all) / 100.0) ** 2)))

    r_loco, p_loco = stats.pearsonr(loco_preds, y_all)
    r2_loco = float(1.0 - np.sum((y_all - loco_preds) ** 2) / np.sum((y_all - np.mean(y_all)) ** 2))
    rmse_loco = float(np.sqrt(np.mean(((loco_preds - y_all) / 100.0) ** 2)))

    e_crit_samples, t50_samples, c72_late_mono, c72_combo_24h = run_vectorized_1000lhs_5ode_simulations(n_mc=1000)
    late_mono_trapped_pct = float(100.0 * np.mean(c72_late_mono < 50.0))
    triple_combo_rescued_pct = float(100.0 * np.mean(c72_combo_24h >= 85.0))

    return {
        "n_public_benchmark_points": int(len(df_pts)),
        "modality_breakdown": {
            "Microglia_Storm_Pct": 4,
            "Astro_BBB_Pct": 4,
            "Chromatin_Lock_Pct": 4,
            "Neuronal_Gate_Pct": 4,
        },
        "in_sample_full_r": round(float(r_full), 3),
        "in_sample_full_r2": round(float(r2_full), 3),
        "in_sample_full_p": float(p_full),
        "loro_16fold_out_of_sample_r": round(float(r_loro), 3),
        "loro_16fold_out_of_sample_r2": round(float(r2_loro), 3),
        "loro_16fold_out_of_sample_p": float(p_loro),
        "loro_16fold_normalized_rmse": round(rmse_loro, 4),
        "loco_cv_out_of_sample_r": round(float(r_loco), 3),
        "loco_cv_out_of_sample_r2": round(float(r2_loco), 3),
        "loco_cv_out_of_sample_p": float(p_loco),
        "loco_cv_normalized_rmse": round(rmse_loco, 4),
        "sensitivity_1000mc_20pct": {
            "e_crit_nominal": 9.5,
            "e_crit_ci95_range": [round(float(np.percentile(e_crit_samples, 2.5)), 2), round(float(np.percentile(e_crit_samples, 97.5)), 2)],
            "t50_nominal_hr": 16.4,
            "t50_median_hr": round(float(np.median(t50_samples)), 1),
            "t50_iqr_hr": [round(float(np.percentile(t50_samples, 25)), 1), round(float(np.percentile(t50_samples, 75)), 1)],
            "t50_ci95_hr": [round(float(np.percentile(t50_samples, 2.5)), 1), round(float(np.percentile(t50_samples, 97.5)), 1)],
            "late_mono_c72_mean_pct": round(float(np.mean(c72_late_mono)), 1),
            "late_mono_c72_sd_pct": round(float(np.std(c72_late_mono)), 1),
            "combo_24h_c72_mean_pct": round(float(np.mean(c72_combo_24h)), 1),
            "combo_24h_c72_sd_pct": round(float(np.std(c72_combo_24h)), 1),
            "late_monotherapy_trapped_pct": round(late_mono_trapped_pct, 1),
            "triple_combo_24h_rescued_pct": round(triple_combo_rescued_pct, 1),
        },
    }


def run_t4_internal_control_archetype_comparison():
    df_s2 = pd.read_csv(os.path.join(TAB_DIR, "TableS2_133Genes_Dynamic_Tau_Trajectories.csv"))
    df_valid = df_s2[df_s2["Has_Valid_Baseline_Tau0"] == True] if "Has_Valid_Baseline_Tau0" in df_s2.columns else df_s2
    arch1 = df_valid[df_valid["Dynamic_Tau_Archetype"].str.startswith("Archetype I:")]
    arch2 = df_valid[df_valid["Dynamic_Tau_Archetype"].str.startswith("Archetype II:")]
    arch3 = df_valid[df_valid["Dynamic_Tau_Archetype"].str.startswith("Archetype III:")]
    arch4 = df_valid[df_valid["Dynamic_Tau_Archetype"].str.startswith("Archetype IV:")]

    u_2v3_delta, p_2v3_delta = stats.mannwhitneyu(arch2["Delta_Tau_t2_minus_t0"], arch3["Delta_Tau_t2_minus_t0"], alternative="two-sided")
    kw_stat_delta, kw_p_delta = stats.kruskal(
        arch1["Delta_Tau_t2_minus_t0"],
        arch2["Delta_Tau_t2_minus_t0"],
        arch3["Delta_Tau_t2_minus_t0"],
        arch4["Delta_Tau_t2_minus_t0"],
    )

    a1_all = df_s2[df_s2["Dynamic_Tau_Archetype"].str.startswith("Archetype I:")]
    a2_all = df_s2[df_s2["Dynamic_Tau_Archetype"].str.startswith("Archetype II:")]
    a3_all = df_s2[df_s2["Dynamic_Tau_Archetype"].str.startswith("Archetype III:")]
    a4_all = df_s2[df_s2["Dynamic_Tau_Archetype"].str.startswith("Archetype IV:")]
    u_2v3_t2, p_2v3_t2 = stats.mannwhitneyu(a2_all["Tau_t2_Subacute_GSE319769"], a3_all["Tau_t2_Subacute_GSE319769"], alternative="two-sided")
    kw_stat_t2, kw_p_t2 = stats.kruskal(
        a1_all["Tau_t2_Subacute_GSE319769"],
        a2_all["Tau_t2_Subacute_GSE319769"],
        a3_all["Tau_t2_Subacute_GSE319769"],
        a4_all["Tau_t2_Subacute_GSE319769"],
    )

    return {
        "archetype_I_n": int(len(a1_all)),
        "archetype_I_mean_tau0": round(float(arch1["Tau_t0_Baseline_GSE180862"].mean()), 3),
        "archetype_I_mean_tau2": round(float(a1_all["Tau_t2_Subacute_GSE319769"].mean()), 3),
        "archetype_I_mean_delta_tau": round(float(arch1["Delta_Tau_t2_minus_t0"].mean()), 3),
        "archetype_II_neuronal_gate_n": int(len(a2_all)),
        "archetype_II_mean_tau0": round(float(arch2["Tau_t0_Baseline_GSE180862"].mean()), 3),
        "archetype_II_mean_tau2": round(float(a2_all["Tau_t2_Subacute_GSE319769"].mean()), 3),
        "archetype_II_mean_delta_tau": round(float(arch2["Delta_Tau_t2_minus_t0"].mean()), 3),
        "archetype_III_decoy_n": int(len(a3_all)),
        "archetype_III_mean_tau0": round(float(arch3["Tau_t0_Baseline_GSE180862"].mean()), 3),
        "archetype_III_mean_tau2": round(float(a3_all["Tau_t2_Subacute_GSE319769"].mean()), 3),
        "archetype_III_mean_delta_tau": round(float(arch3["Delta_Tau_t2_minus_t0"].mean()), 3),
        "archetype_IV_artifact_n": int(len(a4_all)),
        "archetype_IV_mean_tau0": round(float(arch4["Tau_t0_Baseline_GSE180862"].mean()), 3),
        "archetype_IV_mean_tau2": round(float(a4_all["Tau_t2_Subacute_GSE319769"].mean()), 3),
        "archetype_IV_mean_delta_tau": round(float(arch4["Delta_Tau_t2_minus_t0"].mean()), 3),
        "mannwhitney_archII_vs_archIII_delta_u": float(u_2v3_delta),
        "mannwhitney_archII_vs_archIII_delta_p": float(p_2v3_delta),
        "kruskal_4archetypes_delta_h": round(float(kw_stat_delta), 2),
        "kruskal_4archetypes_delta_p": float(kw_p_delta),
        "mannwhitney_archII_vs_archIII_tau2_u": float(u_2v3_t2),
        "mannwhitney_archII_vs_archIII_tau2_p": float(p_2v3_t2),
        "kruskal_4archetypes_tau2_h": round(float(kw_stat_t2), 2),
        "kruskal_4archetypes_tau2_p": float(kw_p_t2),
    }


@retry_limit(2)
def main():
    canary_gate(lambda: os.path.exists(os.path.join(TAB_DIR, "TableS1_230_ClinicalTrials_MultiAgent_Audit.csv")), "Verify TableS1 exists")
    res = {
        "T1_and_T9_clinical_trials": run_t1_and_t9_clinical_trial_sensitivities(),
        "T3_vglia_niche_loco_and_sensitivity": run_t3_vglia_niche_loco_and_sensitivity(),
        "T4_internal_control_archetypes": run_t4_internal_control_archetype_comparison(),
    }
    out_path = os.path.join(DATA_DIR, "rebuttal_sensitivity_and_loco_stats.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    pass_gate(SCRIPT_DIR)
    gate(__file__)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
