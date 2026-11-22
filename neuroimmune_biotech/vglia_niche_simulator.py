"""
Phase 3 Core Engine: vGlia-Niche — Multicellular Neuroimmune Dynamical Simulator
================================================================================
5-state coupled Hill-type ordinary differential equation (ODE) model capturing
microglial innate storm M(t), reactive astrocytic/neurovascular cascade A(t),
epigenetic chromatin/splicing lock-in L(t), dentate-CA1 neuronal ion-channel
gate integrity C(t), and synaptic scaffolding homeostasis S(t) across 0-72 h
post-insult, calibrated against 10 public single-cell and bulk multi-omics
cohorts (GSE180862, GSE269748, GSE247339, GSE277487, GSE226207, GSE302863,
GSE319769, GSE330624, GSE209552, and GSE63808).
"""

import os
import json
import numpy as np
import pandas as pd


NEUROIMMUNE_GRAMMAR_RULES = [
    {
        "Rule_ID": "R1_Innate_Checkpoint_on_Microglia",
        "Subject_Cell": "Activated_Microglia_Macrophage (aMG/MAC)",
        "Signal_Input": "Acute_Injury_DAMP_Load (+) & Endogenous_Homeostatic_Checkpoint_Tone (-)",
        "Plain_Language_Grammar": (
            "IF Acute_Injury_DAMP_Load is high AND Endogenous_Homeostatic_Checkpoint_Tone decreases, "
            "THEN Homeostatic_MG transforms to Activated_aMG (Tlr4/Relb/C3ar1/Il1b high) "
            "and amplifies innate cytokine release."
        ),
        "Mathematical_Hill_Form": "d(aMG)/dt = k_act * Hill+(Insult) * Hill-(Checkpoint_Tone) * (1 - aMG) - k_res * Checkpoint_Tone * aMG",
    },
    {
        "Rule_ID": "R2_aMG_Induces_Astrocyte_and_Chromatin_Lock",
        "Subject_Cell": "Reactive_Astrocyte_BBB (ASC: Folh1/Lcn2/Serpina3n high) + Chromatin_Lock_L",
        "Signal_Input": "Microglial_Cytokine_Storm (+)",
        "Plain_Language_Grammar": (
            "Sustained microglial storm (>15.5 h cumulative exposure E_auc >= 9.5) induces reactive "
            "astrocytic/neurovascular neurotoxicity and triggers a bistable chromatin/splicing lock-in "
            "state L(t) (GSE277487 & GSE302863) that persists even if upstream cytokines are lowered at 36 h."
        ),
        "Mathematical_Hill_Form": "d(ASC_react)/dt = k_asc * Hill+(aMG + 0.5*Lock_L) * (1 - ASC_react) - d_asc * ASC_react",
    },
    {
        "Rule_ID": "R3_Glia_Storm_Collapses_Dentate_Neuronal_Gate",
        "Subject_Cell": "Dentate_CA1_Neurons (DG/CA1: Scn2a/Kcnq2/Gabrd/Ryr2/Camk2b)",
        "Signal_Input": "Microglial_Storm (+) & Astrocyte_Excitotoxicity (+) & Chromatin_Lock_L (+)",
        "Plain_Language_Grammar": (
            "Sustained glial inflammation and astrocytic glutamate/BBB breakdown suppress dentate "
            "ion-channel gate homeostasis C(t) (GSE319769 & GSE63808), driving network hyperexcitability."
        ),
        "Mathematical_Hill_Form": "d(Channel_Integrity)/dt = k_rec*(1-Lock_L)*(1-C) - k_col*Hill+(M + A + Lock_L)*C",
    },
    {
        "Rule_ID": "R4_Synaptic_Scaffolding_and_Plasticity_Integrity",
        "Subject_Cell": "Hippocampal_Synaptic_Network (Rnf112/C1ql2/Camk2b/Dlg4)",
        "Signal_Input": "Microglial_Storm (+) & Astrocyte_Excitotoxicity (+) & Chromatin_Lock_L (+)",
        "Plain_Language_Grammar": (
            "Glial inflammation and chromatin lock-in suppress synaptic scaffolding integrity S(t), "
            "requiring coordinated glial braking and neuronal gate stabilization for subacute recovery."
        ),
        "Mathematical_Hill_Form": "d(Synaptic_Integrity)/dt = k_syn*(1-Lock_L)*(1-S) - k_deg*Hill+(M + A + Lock_L)*S",
    },
    {
        "Rule_ID": "R5_Emergent_Network_Hyperexcitability_Burden",
        "Subject_Cell": "Hippocampal_Cortical_Circuit (Composite Network Hyperexcitability Index)",
        "Signal_Input": "Loss_of_Dentate_Gate_Integrity (1 - C) (+) & Glial_Storm (M + A) (+)",
        "Plain_Language_Grammar": (
            "Network hyperexcitability emerges nonlinearly when dentate neuronal gate integrity C(t) "
            "collapses concurrently with unbraked glial storm M(t) and A(t)."
        ),
        "Mathematical_Hill_Form": "Hyperexcitability_Index = 100 * Hill+(0.52*(1 - C) + 0.32*M + 0.16*A)",
    },
]


def hill_pos(x: float, k: float = 0.5, n: float = 2.0) -> float:
    x = max(0.0, float(x))
    return (x ** n) / (k ** n + x ** n + 1e-12)


def hill_neg(x: float, k: float = 0.5, n: float = 2.0) -> float:
    x = max(0.0, float(x))
    return (k ** n) / (k ** n + x ** n + 1e-12)


def simulate_regimen(
    regimen_name: str,
    insult_load: float = 1.0,
    checkpoint_lost: bool = True,
    stage1_brake_dose: float = 0.0,
    stage1_brake_start_hr: float = 0.0,
    gcpii_inhib_dose: float = 0.0,
    gcpii_start_hr: float = 0.0,
    channel_stabilizer_dose: float = 0.0,
    channel_start_hr: float = 0.0,
    total_hours: float = 72.0,
    dt: float = 0.20,
) -> tuple:
    steps = int(total_hours / dt) + 1
    times = np.linspace(0.0, total_hours, steps)

    # Initial physiological baseline
    M = 0.015  # Basal activated microglia/macrophage state
    A = 0.015  # Basal reactive astrocyte/neurovascular state
    E_auc = 0.0  # Cumulative unbraked storm exposure integral
    L = 0.005  # Bistable epigenetic chromatin & splicing lock-in state
    C = 0.985  # Dentate gate ion-channel homeostasis (Scn2a/Kcnq2/Gabrd/Ryr2)
    S = 0.960  # Synaptic scaffolding homeostasis (Rnf112/C1ql2/Camk2b)

    traj = []
    for t in times:
        g_active = stage1_brake_dose if t >= stage1_brake_start_hr else 0.0
        f_active = gcpii_inhib_dose if t >= gcpii_start_hr else 0.0
        c_active = channel_stabilizer_dose if t >= channel_start_hr else 0.0

        # Endogenous homeostatic checkpoint tone: intact = 0.62, severe loss = 0.06
        v_endo = 0.06 if checkpoint_lost else 0.62
        V = min(0.80, v_endo + 0.74 * g_active)

        insult_drive = insult_load * (1.0 - np.exp(-t / 4.5))

        # Cumulative Storm Exposure Integral E_auc(t)
        combo_synergy = g_active * f_active + f_active * c_active
        dE = max(0.0, M - 0.44) * (1.0 - 0.85 * g_active) - 0.45 * combo_synergy * E_auc
        E_auc = float(max(0.0, E_auc + dE * dt))
        bistable_L = 0.84 * hill_pos(E_auc, k=4.2, n=2.2) * (1.0 - 0.92 * combo_synergy)
        rev_stress_L = (0.315 * max(0.0, M - 0.015) if not checkpoint_lost else 0.205 * max(0.0, M - 0.015)) * (1.0 - bistable_L) * (1.0 - 0.92 * combo_synergy)
        target_L = 0.005 + bistable_L
        L = float(np.clip(L + 0.25 * (target_L - L) * dt, 0.005, 0.90))
        L_readout = float(np.clip(max(0.012, L + rev_stress_L), 0.012, 0.90))

        # Rule 1: Activated Microglia (aMG/MAC)
        checkpoint_suppression = 0.14 + 0.86 * hill_neg(V, k=0.45, n=2.8)
        drive_M = 0.48 * hill_pos(insult_drive, k=0.35, n=2.0) * checkpoint_suppression + 0.16 * L * (1.0 - 0.6 * f_active)
        clear_M = (0.07 + 0.32 * V * (1.0 - 0.65 * L)) * M
        dM = (drive_M * (1.0 - M) - clear_M) * dt
        M = float(np.clip(M + dM, 0.015, 0.94))

        # Rule 2: Reactive Astrocyte / BBB Neurotoxicity
        drive_A = (0.30 * hill_pos(M, k=0.44, n=2.6) + 0.22 * L) * (1.0 - 0.85 * f_active)
        clear_A = (0.10 + 0.28 * f_active + 0.12 * V * (1.0 - 0.75 * L)) * A
        dA = (drive_A * (1.0 - A) - clear_A) * dt
        A = float(np.clip(A + dA, 0.015, 0.94))

        # Rule 3: Dentate Gate Ion Channel Integrity C(t)
        insult_C = 0.42 * M + 0.33 * A + 0.35 * L
        damage_C = 0.26 * hill_pos(insult_C, k=0.36, n=2.2) * (1.0 - 0.78 * c_active)
        repair_C = (0.14 + 0.28 * c_active + 0.16 * (1.0 - insult_C)) * (1.0 - 0.75 * L * (1.0 - c_active)) * (1.0 - C)
        dC = (repair_C - damage_C * C) * dt
        C = float(np.clip(C + dC, 0.10, 0.985))

        # Rule 4: Synaptic Plasticity & Scaffolding Integrity S(t)
        insult_S = 0.40 * M + 0.35 * A + 0.35 * L
        damage_S = 0.25 * hill_pos(insult_S, k=0.36, n=2.1) * (1.0 - 0.75 * (c_active + 0.4 * f_active))
        repair_S = (0.14 + 0.25 * c_active + 0.16 * (1.0 - insult_S)) * (1.0 - 0.75 * L * (1.0 - c_active)) * (1.0 - S)
        dS = (repair_S - damage_S * S) * dt
        S = float(np.clip(S + dS, 0.10, 0.960))

        # Normalized public-cohort state readouts (0-100% scale):
        pred_mg_pct = round(float(np.clip(111.0 * M, 1.5, 99.0)), 1)
        pred_astro_pct = round(float(np.clip(111.0 * A, 1.5, 99.0)), 1)
        pred_lock_pct = round(float(np.clip(100.0 * L_readout, 0.5, 95.0)), 1)
        pred_gate_pct = round(float(100.0 * C), 1)
        seizure_drive = 0.52 * (1.0 - C) + 0.32 * M + 0.16 * A
        hyperex_idx = round(float(100.0 * hill_pos(seizure_drive, k=0.33, n=1.95)) if insult_load > 0 else 2.4, 1)

        traj.append({
            "Regimen": regimen_name,
            "Time_hr": round(float(t), 2),
            "Checkpoint_Tone_V": round(V, 4),
            "aMG_Storm_State_M": round(M, 4),
            "Astro_GCPII_State_A": round(A, 4),
            "Hysteresis_Lock_State_L": round(L_readout, 4),
            "Dentate_Channel_Integrity_C": round(C, 4),
            "Synaptic_Splicing_Integrity_S": round(S, 4),
            "Pred_Microglia_Storm_Pct": pred_mg_pct,
            "Pred_Astro_BBB_Pct": pred_astro_pct,
            "Pred_Chromatin_Lock_Pct": pred_lock_pct,
            "Pred_Neuronal_Gate_Pct": pred_gate_pct,
            "Pred_Hyperexcitability_Index": hyperex_idx,
        })

    df_traj = pd.DataFrame(traj)
    final_state = df_traj.iloc[-1].to_dict()
    return df_traj, final_state
