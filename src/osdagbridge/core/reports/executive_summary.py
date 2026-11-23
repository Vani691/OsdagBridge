# =============================================================================
# Executive Summary — One-Page Design Summary Dashboard + Geometry Overview
# =============================================================================

from osdagbridge.core.reports.charts import (
    extract_material_quantities,
    extract_primary_element_urs,
)
from osdagbridge.core.reports.report_utils import (
    _fig_or_placeholder,
    _render_value,
    _tex,
    get_girder_entries,
)
from osdagbridge.core.reports.styles import (
    TABLE_LAYOUT,
    format_status,
    format_ur_cell,
)
from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_SD_SECTION_DESIGNATION,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS,
)


def executive_summary(input_dict, output_dict, fig_paths) -> str:
    plan_fig = _fig_or_placeholder(
        fig_paths.get("girder_top"), "Figure 1 -- Overall Bridge Plan"
    )
    cs_fig = _fig_or_placeholder(
        fig_paths.get("cross_section"),
        "Figure 2 -- Typical Cross-Section (with girder, deck, barriers, footpath)",
    )
    geom_fig = _fig_or_placeholder(
        fig_paths.get("final_geometry"),
        "Figure 3 -- 3D View of Bridge Superstructure",
    )

    sec = _render_value(output_dict, KEY_SD_SECTION_DESIGNATION)

    design_results = (output_dict or {}).get("design_results", {}) or {}
    per_girder = design_results.get("per_girder", {}) or {}

    # Girder governing check name & failing checks
    failing = []
    gov_name, gov_dcr = "", None
    for g, gd in per_girder.items():
        if str(g).startswith("EB"):
            continue
        for chk in (gd.get("checks") or []):
            try:
                _val = chk.get("dcr")
                dcr = float(_val) if _val is not None else None
            except (TypeError, ValueError):
                dcr = None
            name = str(chk.get("name", "")).strip()
            is_fail = ("FAIL" in str(chk.get("status", "")).upper()) or (
                dcr is not None and dcr > 1.0
            )
            if is_fail and name and name not in failing:
                failing.append(name)
            if dcr is not None and (gov_dcr is None or dcr > gov_dcr):
                gov_dcr, gov_name = dcr, name

    # Primary component URs (reused identically for Section 5.5 UR chart)
    elem_urs = extract_primary_element_urs(input_dict, output_dict)
    valid_elem_urs = [(lbl.replace("\n", " "), v) for lbl, v in elem_urs if v is not None]

    if valid_elem_urs:
        gov_elem_label, max_ur_val = max(valid_elem_urs, key=lambda t: t[1])
        any_fail = bool(failing) or any(v > 1.0 for _, v in valid_elem_urs)
        verdict_label = "FAIL" if any_fail else "PASS"
        if failing:
            escaped_fails = ", ".join(_tex(f) for f in failing)
            verdict_badge = format_status(f"FAIL ({escaped_fails})")
        else:
            verdict_badge = format_status("FAIL" if any_fail else "ALL CHECKS PASS")
        max_ur_cell = format_ur_cell(max_ur_val, decimals=2)
        gov_elem_tex = _tex(gov_elem_label)
        ur_plain = f"{max_ur_val:.2f} ({gov_elem_label})"
    else:
        verdict_label = "---"
        verdict_badge = "---"
        max_ur_cell = "---"
        gov_elem_tex = "---"
        ur_plain = ""

    gov = _tex(gov_name) if gov_name not in (None, "", "None") else "---"
    ur = _tex(ur_plain) if ur_plain else "---"

    # Total quantities (reused identically for Chapter 7 charts)
    qty = extract_material_quantities(input_dict)
    steel_str = f"{qty['total_steel_mt']:.2f} MT" if qty["total_steel_mt"] > 0 else "---"
    conc_str = f"{qty['concrete_m3']:.2f} m\\textsuperscript{{3}}" if qty["concrete_m3"] > 0 else "---"
    rebar_str = f"{qty['rebar_mt']:.2f} MT" if qty["rebar_mt"] > 0 else "---"

    # Dynamic component status table rows (replaces previous hardcoded "pass" lines)
    comp_rows = []
    for raw_lbl, val in elem_urs:
        clean_lbl = _tex(raw_lbl.replace("\n", " "))
        if val is None:
            comp_rows.append(rf"{clean_lbl} & --- & --- \\ \hline")
        else:
            st = format_status("PASS" if val <= 1.0 else "FAIL")
            comp_rows.append(
                rf"{clean_lbl} & {format_ur_cell(val, decimals=2)} & {st} \\ \hline"
            )
    comp_status_rows = "\n".join(comp_rows)

    # Dynamic Table 1: Final Bridge Geometry
    labels = get_girder_entries(input_dict)
    if not labels:
        labels = [("", "")]
    n_cols = len(labels)
    label_col_cm = 3.2
    avail_cm = TABLE_LAYOUT.content_width_cm - 0.8
    girder_col_cm = round(max(1.6, (avail_cm - label_col_cm) / n_cols), 1)
    col_spec = (
        f"|L{{{label_col_cm}cm}}|"
        + "|".join([f"C{{{girder_col_cm}cm}}"] * n_cols)
        + "|"
    )

    hdr_cells = " & ".join(
        [rf"\textcolor{{tableHeaderText}}{{\textbf{{{_tex(lbl)}}}}}" for lbl, _ in labels]
    )
    header_row = rf"\rowcolor{{tableHeaderBg}} \textcolor{{tableHeaderText}}{{\textbf{{Parameter}}}} & {hdr_cells} \\" + "\n"
    mid_cells = " & ".join([_tex(mid) for _, mid in labels])
    member_id_row = f"Member ID & {mid_cells} \\\\\n"
    sec_cells = " & ".join([sec] * n_cols)
    sections = f"Section Designation & {sec_cells} \\\\"
    gov_cells = " & ".join([gov] * n_cols)
    gov_checks = f"Governing Check & {gov_cells} \\\\"
    ur_display = format_ur_cell(max_ur_val, decimals=2) if valid_elem_urs else "---"
    ur_cells = " & ".join([ur_display] * n_cols)
    urs = f"Utilization Ratio & {ur_cells} \\\\"

    table1 = (
        r"\noindent\textbf{Table 1 -- Final Bridge Geometry (after optimization)}" + "\n\n"
        r"\vspace{0.4em}" + "\n"
        r"\noindent" + "\n"
        r"\begin{tabular}{" + col_spec + "}\n"
        r"\hline" + "\n"
        + header_row
        + r"\hline" + "\n"
        + member_id_row
        + r"\hline" + "\n"
        + sections + "\n"
        r"\hline" + "\n"
        + gov_checks + "\n"
        r"\hline" + "\n"
        + urs + "\n"
        r"\hline" + "\n"
        r"\end{tabular}"
    )

    return (
        r"""
\newpage
{\centering\Large\bfseries Executive Summary\par}
\addcontentsline{toc}{chapter}{Executive Summary}
\vspace{0.6em}

This one-page design summary highlights the overall structural verdict, governing element, key bridge geometry, and estimated material quantities.

\vspace{0.5em}
\noindent
\begin{tabular}{|L{4.4cm}|L{4.0cm}|L{4.4cm}|L{3.4cm}|}
\hline
\rowcolor{tableHeaderBg}
\multicolumn{4}{|l|}{\textcolor{tableHeaderText}{\textbf{At-a-Glance Design Dashboard}}} \\
\hline
\textbf{Overall Design Verdict} & """ + verdict_badge + r""" & \textbf{Max Utilization Ratio} & """ + max_ur_cell + r""" \\
\hline
\textbf{Governing Element} & """ + gov_elem_tex + r""" & \textbf{Governing Girder Check} & """ + gov + r""" \\
\hline
\textbf{Total Structural Steel} & """ + steel_str + r""" & \textbf{Concrete / Rebar} & """ + conc_str + r""" / """ + rebar_str + r""" \\
\hline
\end{tabular}

\vspace{0.6em}
\section*{Project Overview}
\addcontentsline{toc}{section}{Project Overview}
\label{sec:project-overview}

\begin{tabular}{|L{5.8cm}|L{10.4cm}|}
\hline
\rowcolor{tableHeaderBg}
\textcolor{tableHeaderText}{\textbf{Parameter}} & \textcolor{tableHeaderText}{\textbf{Design Value}} \\
\hline
\textbf{Bridge Type} & """ + _render_value(input_dict, KEY_STRUCTURE_TYPE) + r""" \\
\hline
\textbf{Design Standards} & IRC 5, IRC 6, IRC 22, IRC 24, IRC 112, IS 800 \\
\hline
\textbf{Span} & """ + _render_value(input_dict, KEY_SPAN, " m") + r""" \\
\hline
\textbf{Carriageway Width} & """ + _render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, " m") + r""" \\
\hline
\textbf{No. of Girders / Spacing} & """ + _render_value(input_dict, KEY_TS_NO_OF_GIRDERS) + r""" girders @ """ + _render_value(input_dict, KEY_TS_GIRDER_SPACING, " m") + r""" \\
\hline
\textbf{Deck Thickness} & """ + _render_value(input_dict, KEY_TS_DECK_THICKNESS, " mm") + r""" \\
\hline
\textbf{Overall Utilization Ratio (max)} & """ + ur + r""" \\
\hline
\end{tabular}

\vspace{0.6em}
\section*{Component Design Status Summary}
\addcontentsline{toc}{section}{Component Design Status Summary}
\label{sec:key-outcomes}

\begin{tabular}{|L{7.2cm}|C{4.5cm}|C{4.5cm}|}
\hline
\rowcolor{tableHeaderBg}
\textcolor{tableHeaderText}{\textbf{Primary Structural Element}} & \textcolor{tableHeaderText}{\textbf{Governing UR}} & \textcolor{tableHeaderText}{\textbf{Status}} \\
\hline
""" + comp_status_rows + r"""
\end{tabular}

\newpage
"""
        + plan_fig + "\n\n"
        + cs_fig + "\n\n"
        + geom_fig + "\n\n"
        + table1
        + r"""

\vspace{0.4em}
\noindent\textit{\small Note: Utilization ratio (UR) = Demand / Capacity. Values $\leq 1.00$ indicate passing checks.}

\vspace{0.8em}
\section*{Design Assumptions and Limitations}
\addcontentsline{toc}{section}{Design Assumptions and Limitations}
\label{sec:assumptions}

\begin{itemize}
\item Additional inputs not provided by the user were assumed by software per IRC/IS code defaults or practical considerations.
\item Grillage analysis was performed using OSPGrillage assuming simply supported I-girders.
\item Substructure and foundation design are not included in this report.
\item Splice connections and bearings are not designed in this version.
\end{itemize}

% Restore numbered chapter format
\titleformat{\chapter}[block]{\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{-20pt}{10pt}
"""
    )
