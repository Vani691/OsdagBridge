# =============================================================================
# OsdagBridge — Programmatic Report Visualizations (UR & Material Quantities)
# =============================================================================
"""
Generates publication-ready matplotlib bar charts for:
  1. Section 5.5 — Overall Utilization Ratio (UR = Demand / Capacity) across
     primary structural elements (Steel Plate Girders, Concrete Deck Slab,
     Cross Bracing, End Diaphragms) with a red dashed UR = 1.0 threshold line,
     bar value annotations, and governing-element highlight.
  2. Chapter 7  — Material Take-off & Quantity Summary:
     (a) Structural Steel Tonnage (Girders, Cross Bracing, End Diaphragms)
     (b) Concrete Volume (m3) vs. Reinforcement Steel Weight (MT)

Uses matplotlib's OOP ``Figure`` + ``FigureCanvasAgg`` API so chart rendering
is 100% thread-safe inside PyQt background workers (never touches GUI threads).
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional, Tuple

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from .styles import ReportTheme, get_theme

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Numeric Extraction Helpers
# ---------------------------------------------------------------------------

def _to_float(val) -> Optional[float]:
    """Safely parse a float from numbers or strings like '12.34 MT', '45.2 m3'."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ("N.A.", "N/A", "NONE", "---", "-"):
        return None
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s.replace(",", ""))
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None


def _max_member_efficiency(pair_designs: dict) -> Optional[float]:
    """Extract max utilization ratio ('efficiency') from cross-bracing / ED dicts."""
    if not isinstance(pair_designs, dict):
        return None
    try:
        from osdagbridge.core.bridge_types.plate_girder.results_data import (
            _extract_osdag_summary,
        )
    except Exception:
        def _extract_osdag_summary(raw):
            return raw if isinstance(raw, dict) else {}

    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                if not isinstance(raw, dict):
                    continue
                val = _extract_osdag_summary(raw).get("efficiency")
                if val is None:
                    val = raw.get("efficiency") or raw.get("ur") or raw.get("dcr")
                f = _to_float(val)
                if f is not None and (best is None or f > best):
                    best = f
    return best


def extract_primary_element_urs(
    input_dict: dict,
    output_dict: dict,
) -> List[Tuple[str, Optional[float]]]:
    """
    Extract governing Utilization Ratios (Demand / Capacity) for the four
    primary structural elements:
      - Steel Plate Girders
      - Concrete Deck Slab
      - Cross Bracing
      - End Diaphragms
    """
    od = output_dict or {}
    design_results = od.get("design_results", {}) or {}
    per_girder = design_results.get("per_girder", {}) or {}
    deck_results = od.get("deck_design_results", {}) or {}
    deck_rpt = od.get("deck_report_values", {}) or {}
    cb_results = od.get("crossbracing_design_results", {}) or {}
    ed_results = od.get("end_diaphragm_design_results", {}) or {}

    # 1. Steel Plate Girders — max DCR across all non-EB girders
    girder_ur: Optional[float] = None
    for g, gd in per_girder.items():
        if str(g).startswith("EB"):
            continue
        for chk in (gd.get("checks") or []):
            d = _to_float(chk.get("dcr"))
            if d is not None and (girder_ur is None or d > girder_ur):
                girder_ur = d

    # 2. Concrete Deck Slab — max of ur_* in deck_design_results, or compute from deck_rpt
    deck_urs: List[float] = []
    for k, v in deck_results.items():
        if str(k).startswith("ur_"):
            f = _to_float(v)
            if f is not None:
                deck_urs.append(f)
    if not deck_urs and deck_rpt:
        # Fallback: compute URs directly from demand / capacity pairs if present
        pairs = [
            ("deck_design.m_uls_sag", "deck_design.mu_bot"),
            ("deck_design.m_uls_hog", "deck_design.mu_top"),
            ("deck_design.punch_ved", "deck_design.vrd_c_mpa"),
            ("deck_design.shear_ved", "deck_design.shear_vrdc"),
        ]
        for dk, ck in pairs:
            dv = _to_float(deck_rpt.get(dk))
            cv = _to_float(deck_rpt.get(ck))
            if dv is not None and cv and cv > 0:
                deck_urs.append(dv / cv)
    deck_ur = max(deck_urs) if deck_urs else None

    # 3. Cross Bracing
    cb_ur = _max_member_efficiency(cb_results)

    # 4. End Diaphragms (use end_diaphragm_design_results; if configured as cross-bracing
    #    and ED dict is empty, fall back to cross-bracing UR just like Table 5.22)
    ed_ur = _max_member_efficiency(ed_results)
    if ed_ur is None:
        for k, v in (input_dict or {}).items():
            if "end_diaphragm" in str(k).lower() and "type" in str(k).lower():
                if v and "brac" in str(v).lower() and cb_ur is not None:
                    ed_ur = cb_ur
                    break

    return [
        ("Steel Plate\nGirders", girder_ur),
        ("Concrete\nDeck Slab", deck_ur),
        ("Cross\nBracing", cb_ur),
        ("End\nDiaphragms", ed_ur),
    ]


def extract_material_quantities(input_dict: dict) -> Dict[str, float]:
    """Extract numeric material quantities populated by calculate_material_quantities()."""
    d = input_dict or {}
    girders_mt = _to_float(d.get("steel_girders_wt_total")) or 0.0
    cb_top = _to_float(d.get("bracing_top_wt_total")) or 0.0
    cb_bot = _to_float(d.get("bracing_bot_wt_total")) or 0.0
    cb_diag = _to_float(d.get("bracing_diag_wt_total")) or 0.0
    cross_bracing_mt = cb_top + cb_bot + cb_diag

    # End diaphragm steel tonnage if populated by BOQ module
    ed_mt = (
        (_to_float(d.get("end_diaphragm_wt_total")) or 0.0)
        + (_to_float(d.get("ed_top_wt_total")) or 0.0)
        + (_to_float(d.get("ed_bot_wt_total")) or 0.0)
        + (_to_float(d.get("ed_diag_wt_total")) or 0.0)
    )

    concrete_m3 = _to_float(d.get("concrete_deck_vol_total")) or 0.0
    rebar_mt = _to_float(d.get("rebar_deck_wt_total")) or 0.0

    return {
        "steel_girders_mt": girders_mt,
        "cross_bracing_mt": cross_bracing_mt,
        "end_diaphragms_mt": ed_mt,
        "total_steel_mt": girders_mt + cross_bracing_mt + ed_mt,
        "concrete_m3": concrete_m3,
        "rebar_mt": rebar_mt,
    }


# ---------------------------------------------------------------------------
# Chart 1: Utilization Ratio (Demand / Capacity) Bar Chart (Section 5.5)
# ---------------------------------------------------------------------------

def generate_ur_summary_chart(
    input_dict: dict,
    output_dict: dict,
    out_path: str,
    theme: Optional[ReportTheme] = None,
) -> Optional[str]:
    """
    Generate and save the Overall Utilization Ratio (UR) bar chart for Section 5.5.
    Includes red dashed UR = 1.0 threshold line, numeric annotations above each
    bar, and a highlight callout on the governing element.
    """
    t = theme or get_theme()
    items = extract_primary_element_urs(input_dict, output_dict)

    labels = [lbl for lbl, _ in items]
    values = [v if v is not None else 0.0 for _, v in items]
    is_missing = [v is None for _, v in items]

    # Determine governing element among available (non-missing) URs
    valid_indices = [i for i, miss in enumerate(is_missing) if not miss]
    gov_idx = max(valid_indices, key=lambda i: values[i]) if valid_indices else None

    fig = Figure(figsize=(7.6, 4.1), dpi=220)
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bar_colors = []
    edge_colors = []
    edge_widths = []
    for i, (val, miss) in enumerate(zip(values, is_missing)):
        if miss:
            bar_colors.append("#D0D0D0")
            edge_colors.append("#888888")
            edge_widths.append(0.8)
        elif val > 1.0:
            bar_colors.append(t.chart_fail)
            edge_colors.append("#7F1D1D" if i == gov_idx else t.chart_fail)
            edge_widths.append(2.0 if i == gov_idx else 0.8)
        elif i == gov_idx:
            bar_colors.append(t.chart_governing)
            edge_colors.append("#111111")
            edge_widths.append(1.8)
        else:
            bar_colors.append(t.chart_pass)
            edge_colors.append(t.chart_pass)
            edge_widths.append(0.8)

    x = list(range(len(labels)))
    bars = ax.bar(
        x, values, width=0.52,
        color=bar_colors, edgecolor=edge_colors, linewidth=edge_widths, zorder=3
    )

    # Red dashed threshold line at UR = 1.0
    ax.axhline(
        1.0, color=t.chart_threshold, linestyle="--", linewidth=1.6, zorder=4,
        label="Limit (UR = 1.00)"
    )

    y_max = max(max(values, default=0.0), 1.0)
    ax.set_ylim(0, max(1.28, y_max * 1.24))

    # Annotate each bar with value (+ governing tag on highest UR)
    for i, (bar, val, miss) in enumerate(zip(bars, values, is_missing)):
        bx = bar.get_x() + bar.get_width() / 2.0
        if miss:
            ax.text(
                bx, 0.04, "N/A", ha="center", va="bottom",
                fontsize=8.5, color="#666666", style="italic", zorder=5
            )
            continue
        status_tag = "FAIL" if val > 1.0 else "PASS"
        label_txt = f"{val:.2f}"
        if i == gov_idx:
            label_txt += f"\n(Governing - {status_tag})"
        ax.text(
            bx, val + (y_max * 0.03), label_txt,
            ha="center", va="bottom",
            fontsize=8.5 if i == gov_idx else 9.0,
            fontweight="bold",
            color=t.chart_fail if val > 1.0 else t.chart_text,
            zorder=5,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5, color=t.chart_text)
    ax.set_ylabel("Utilization Ratio (UR = Demand / Capacity)", fontsize=9.5, fontweight="bold", color=t.chart_text)
    ax.set_title("Overall Structural Utilization Ratio Summary", fontsize=11, fontweight="bold", color=t.chart_text, pad=12)
    ax.yaxis.grid(True, linestyle=":", color=t.chart_grid, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend_handles = [
        Patch(facecolor=t.chart_pass, label="Passing (UR <= 1.0)"),
        Patch(facecolor=t.chart_governing, edgecolor="#111111", linewidth=1.2, label="Governing Element"),
        Patch(facecolor=t.chart_fail, label="Failing (UR > 1.0)"),
        ax.lines[0],
    ]
    ax.legend(handles=legend_handles, loc="upper right", frameon=True, fontsize=7.8, framealpha=0.92)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    return out_path


# ---------------------------------------------------------------------------
# Chart 2 & 3: Material Quantity Bar Charts (Chapter 7)
# ---------------------------------------------------------------------------

def generate_steel_quantity_chart(
    input_dict: dict,
    out_path: str,
    theme: Optional[ReportTheme] = None,
) -> Optional[str]:
    """Generate Structural Steel Tonnage (MT) bar chart for Chapter 7."""
    t = theme or get_theme()
    q = extract_material_quantities(input_dict)

    labels = ["Plate Girders", "Cross Bracing", "End Diaphragms"]
    values = [q["steel_girders_mt"], q["cross_bracing_mt"], q["end_diaphragms_mt"]]
    total = q["total_steel_mt"]

    fig = Figure(figsize=(7.2, 3.8), dpi=220)
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    colors = list(t.chart_steel_palette[:3])
    x = list(range(len(labels)))
    bars = ax.bar(x, values, width=0.50, color=colors, edgecolor="#333333", linewidth=0.7, zorder=3)

    y_max = max(values) if max(values) > 0 else 1.0
    ax.set_ylim(0, y_max * 1.24)

    for bar, val in zip(bars, values):
        bx = bar.get_x() + bar.get_width() / 2.0
        pct = (val / total * 100.0) if total > 0 else 0.0
        txt = f"{val:.2f} MT\n({pct:.1f}%)" if val > 0 else "0.00 MT\n(N/A)"
        ax.text(
            bx, val + y_max * 0.025, txt,
            ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=t.chart_text
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5, color=t.chart_text)
    ax.set_ylabel("Structural Steel Weight (MT)", fontsize=9.5, fontweight="bold", color=t.chart_text)
    ax.set_title(
        f"Structural Steel Tonnage Breakdown (Total: {total:.2f} MT)",
        fontsize=10.5, fontweight="bold", color=t.chart_text, pad=10,
    )
    ax.yaxis.grid(True, linestyle=":", color=t.chart_grid, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    return out_path


def generate_concrete_rebar_chart(
    input_dict: dict,
    out_path: str,
    theme: Optional[ReportTheme] = None,
) -> Optional[str]:
    """
    Generate side-by-side Concrete Volume (m3) vs. Reinforcement Steel Weight (MT)
    bar chart for Chapter 7 (two clean panels so each unit has an exact scale).
    """
    t = theme or get_theme()
    q = extract_material_quantities(input_dict)
    conc = q["concrete_m3"]
    rebar = q["rebar_mt"]

    fig = Figure(figsize=(7.2, 3.6), dpi=220)
    FigureCanvasAgg(fig)
    ax1, ax2 = fig.subplots(1, 2)
    fig.patch.set_facecolor("white")

    # Left panel: Concrete Volume (m3)
    ax1.set_facecolor("white")
    b1 = ax1.bar(["Deck Slab\nConcrete"], [conc], width=0.45, color=t.chart_concrete, edgecolor="#222222", linewidth=0.7, zorder=3)
    ymax1 = max(conc, 1.0) * 1.25
    ax1.set_ylim(0, ymax1)
    ax1.set_xlim(-0.65, 0.65)
    ax1.text(b1[0].get_x() + b1[0].get_width() / 2.0, conc + ymax1 * 0.03, f"{conc:.2f} m³", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=t.chart_text)
    ax1.set_ylabel("Volume (m³)", fontsize=9.5, fontweight="bold", color=t.chart_text)
    ax1.set_title("Concrete Volume (m³)", fontsize=10, fontweight="bold", color=t.chart_text)
    ax1.yaxis.grid(True, linestyle=":", color=t.chart_grid, zorder=0)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Right panel: Reinforcement Steel Weight (MT)
    ax2.set_facecolor("white")
    b2 = ax2.bar(["Reinforcement\nSteel (Fe 500)"], [rebar], width=0.45, color=t.chart_rebar, edgecolor="#222222", linewidth=0.7, zorder=3)
    ymax2 = max(rebar, 1.0) * 1.25
    ax2.set_ylim(0, ymax2)
    ax2.set_xlim(-0.65, 0.65)
    ax2.text(b2[0].get_x() + b2[0].get_width() / 2.0, rebar + ymax2 * 0.03, f"{rebar:.2f} MT", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=t.chart_text)
    ax2.set_ylabel("Weight (MT)", fontsize=9.5, fontweight="bold", color=t.chart_text)
    ax2.set_title("Reinforcement Steel (MT)", fontsize=10, fontweight="bold", color=t.chart_text)
    ax2.yaxis.grid(True, linestyle=":", color=t.chart_grid, zorder=0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.suptitle("Concrete Volume vs. Reinforcement Steel Quantity", fontsize=11, fontweight="bold", color=t.chart_text, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    return out_path


def generate_all_report_charts(
    input_dict: dict,
    output_dict: dict,
    images_dir: str,
    theme: Optional[ReportTheme] = None,
) -> Dict[str, str]:
    """
    Generate all programmatic charts into ``images_dir`` and return a dict of
    ``{fig_key: normalized_path}`` ready to merge into ``fig_paths``.
    """
    generated: Dict[str, str] = {}
    t = theme or get_theme()

    chart_jobs = [
        ("ur_summary", "ur_summary.png", lambda p: generate_ur_summary_chart(input_dict, output_dict, p, theme=t)),
        ("material_steel", "material_steel.png", lambda p: generate_steel_quantity_chart(input_dict, p, theme=t)),
        ("material_concrete_rebar", "material_concrete_rebar.png", lambda p: generate_concrete_rebar_chart(input_dict, p, theme=t)),
    ]

    for key, filename, fn in chart_jobs:
        target = os.path.join(images_dir, filename)
        try:
            res = fn(target)
            if res and os.path.exists(res):
                generated[key] = res.replace("\\", "/")
        except Exception as exc:
            logger.warning("Failed to generate chart '%s': %s", key, exc)

    return generated
