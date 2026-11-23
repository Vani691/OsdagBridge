# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# Refactored to use centralized build_longtable (fixing the unclosed \begingroup)
# and embed programmatic Material Quantity bar charts.
# =============================================================================

from osdagbridge.core.reports.styles import build_figure_block, build_longtable


def ch7_quantities(input_dict, fig_paths=None):
    fp = fig_paths or {}

    def _v(key):
        val = input_dict.get(key, "N.A.")
        return "N.A." if val in (None, "") else str(val)

    rows = [
        ("1",    "Structural Steel (IS 2062) for Girders", "steel_girders"),
        ("2(a)", "Cross Bracing --- Top Chord",            "bracing_top"),
        ("2(b)", "Cross Bracing --- Bottom Chord",         "bracing_bot"),
        ("2(c)", "Cross Bracing --- Diagonal Chord",       "bracing_diag"),
        ("3",    "Concrete (M40) for Deck Slab",           "concrete_deck"),
        ("4",    "Reinforcement Steel (Fe 500)",           "rebar_deck"),
        ("5",    "Shear Stud Connectors",                  "shear_studs"),
        ("6",    "Crash Barrier",                          "crash_barrier"),
    ]

    body_lines = []
    for sn, desc, pfx in rows:
        body_lines.append(
            f"{sn} & {desc} & {_v(pfx + '_vol_formula')} & {_v(pfx + '_qty')} "
            f"& {_v(pfx + '_vol_total')} & {_v(pfx + '_wt_single')} & {_v(pfx + '_wt_total')} "
            r"\\ \hline"
        )

    table_boq = build_longtable(
        col_spec="|C{1.0cm}|L{4.0cm}|C{2.7cm}|C{1.6cm}|C{2.0cm}|C{2.0cm}|C{2.1cm}|",
        caption="Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        headers=[
            "S.N.",
            "Item Description",
            "Volume",
            "Qty",
            "Total Vol.",
            "Unit Wt. (MT)",
            "Total Wt. (MT)",
        ],
        body="\n".join(body_lines),
        label="tab:boq",
        font_size=r"\small",
        tabcolsep="3.5pt",
    )

    charts_tex = ""
    if fp.get("material_steel") or fp.get("material_concrete_rebar"):
        charts_tex += "\n\\section{Material Quantity Visualizations}\n\\label{sec:material-charts}\n\n"
        if fp.get("material_steel"):
            charts_tex += build_figure_block(
                fp["material_steel"],
                "Structural Steel Tonnage Breakdown (Girders, Cross Bracing, End Diaphragms)",
                width=r"0.86\textwidth",
                label="fig:material-steel",
                numbered=True,
            ) + "\n\n"
        if fp.get("material_concrete_rebar"):
            charts_tex += build_figure_block(
                fp["material_concrete_rebar"],
                "Deck Concrete Volume (m\\textsuperscript{3}) vs. Reinforcement Steel Weight (MT)",
                width=r"0.86\textwidth",
                label="fig:material-concrete-rebar",
                numbered=True,
            ) + "\n"

    return (
        r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter summarizes the estimated bill of materials for structural steelwork, deck concrete, reinforcement steel, and bridge appurtenances.
"""
        + table_boq
        + charts_tex
    )
