from typing import TYPE_CHECKING
from osdagbridge.core.utils.common import (
    KEY_SPAN,
    KEY_TS_NO_OF_GIRDERS,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
)
from osdagbridge.core.reports.report_utils import _tex, _fig_embed
from osdagbridge.core.reports.styles import build_longtable, format_status

if TYPE_CHECKING:
    from .report_generator import ReportDataBridge


def ch4_analysis(asum, fig_paths, bridge: "ReportDataBridge", span_m: float):
    lc_summary = (asum or {}).get("load_cases", {})
    rxn_summary = (asum or {}).get("reactions", {})

    def _is_moving(lc_name: str) -> bool:
        n = lc_name.lower()
        return "moving" in n or " pos_" in n

    lc_summary = {k: v for k, v in lc_summary.items() if not _is_moving(k)}
    rxn_summary = {k: v for k, v in rxn_summary.items() if not _is_moving(k)}

    def _fmt(val, nd=3):
        try:
            return f"{float(val):.{nd}f}"
        except (TypeError, ValueError):
            return r"---"

    def _merged_row(lc, bm_d, rxn_d):
        bm_d = bm_d or {}
        rxn_d = rxn_d or {}
        return (
            _tex(lc) + r" & "
            + _fmt(bm_d.get("max_bm")) + r" & "
            + _tex(bm_d.get("bm_girder", "---")) + r" & "
            + _fmt(bm_d.get("bm_location")) + r" & "
            + _fmt(bm_d.get("max_sf")) + r" & "
            + _tex(bm_d.get("sf_girder", "---")) + r" & "
            + _fmt(bm_d.get("sf_location")) + r" & "
            + _fmt(rxn_d.get("left_kN")) + r" & "
            + _fmt(rxn_d.get("right_kN")) + r" \\ \hline"
        )

    all_lcs = list(lc_summary.keys()) + [k for k in rxn_summary if k not in lc_summary]

    merged_body = (
        "\n".join(
            _merged_row(lc, lc_summary.get(lc), rxn_summary.get(lc))
            for lc in all_lcs
        )
        if all_lcs
        else r"--- & --- & --- & --- & --- & --- & --- & --- & --- \\ \hline"
    )

    _span_m = float(bridge.input_dict.get(KEY_SPAN, 0) or 0)
    _allow_live_mm = _span_m * 1000.0 / 800.0
    _allow_total_mm = _span_m * 1000.0 / 600.0

    try:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1) or 1)
    except (TypeError, ValueError):
        n = 1

    _live_mm = None
    _total_mm = None
    for _gi in range(1, n + 1):
        _l = bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G{_gi}")
        _t = bridge.output_dict.get(f"{KEY_SD_DEFL_TOTAL}.G{_gi}")
        if _l is not None:
            _live_mm = max(_live_mm, float(_l)) if _live_mm is not None else float(_l)
        if _t is not None:
            _total_mm = max(_total_mm, float(_t)) if _total_mm is not None else float(_t)

    _live_str = f"{_live_mm:.3f} mm" if _live_mm is not None else "---"
    _total_str = f"{_total_mm:.3f} mm" if _total_mm is not None else "---"
    _allow_live_str = f"L/800 = {_allow_live_mm:.1f} mm"
    _allow_total_str = f"L/600 = {_allow_total_mm:.1f} mm"
    _live_status = (
        format_status("PASS" if _live_mm <= _allow_live_mm else "FAIL")
        if _live_mm is not None
        else "---"
    )
    _total_status = (
        format_status("PASS" if _total_mm <= _allow_total_mm else "FAIL")
        if _total_mm is not None
        else "---"
    )

    # Reactions table populated from rxn_summary (instead of blank placeholder rows)
    rxn_rows = []
    for lc in all_lcs:
        r_d = rxn_summary.get(lc) or {}
        if r_d.get("left_kN") is not None or r_d.get("right_kN") is not None:
            rxn_rows.append(
                rf"{_tex(lc)} & {_fmt(r_d.get('left_kN'))} & {_fmt(r_d.get('right_kN'))} \\ \hline"
            )
    rxn_body = "\n".join(rxn_rows) if rxn_rows else r"--- & --- & --- \\ \hline"

    t_rxn = build_longtable(
        col_spec="|L{7.2cm}|C{4.2cm}|C{4.2cm}|",
        caption="Reactions at Supports",
        headers=["Load Case / Combination", "Left Support (kN)", "Right Support (kN)"],
        body=rxn_body,
        font_size=r"\small",
    )

    t_defl = build_longtable(
        col_spec="|L{7.5cm}|L{8.2cm}|",
        caption="Deflection Summary (Live Load \\& Total Load)",
        headers=["Parameter", "Value / Status"],
        body="\n".join([
            rf"\textnormal{{Deflection due to Live Load, $\delta_{{LL}}$}} & {_live_str} \\ \hline",
            rf"\textnormal{{Allowable Live Load Deflection ($\Delta_{{allow}}$)}} & {_allow_live_str} \\ \hline",
            rf"\textnormal{{Live Load Deflection Check Status}} & {_live_status} \\ \hline",
            rf"\textnormal{{Deflection due to Total Load, $\delta_{{total}}$}} & {_total_str} \\ \hline",
            rf"\textnormal{{Allowable Total Deflection ($\Delta_{{allow}}$)}} & {_allow_total_str} \\ \hline",
            rf"\textnormal{{Total Load Deflection Check Status}} & {_total_status} \\ \hline",
        ]),
    )

    return (
        r"""
\chapter{Analysis Results}

A grillage model was used for structural analysis. The deck is idealized as a grid of elastic beam elements --- longitudinal members represent the composite steel girders with effective slab, and transverse members represent the slab or cross frames. This section summarizes the critical output from that analysis.

\vspace{0.6em}
\begingroup
\footnotesize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.2}

\begin{longtable}{|
>{\centering\arraybackslash}p{3.3cm}|
>{\centering\arraybackslash}p{1.7cm}|
>{\centering\arraybackslash}p{1.2cm}|
>{\centering\arraybackslash}p{1.3cm}|
>{\centering\arraybackslash}p{1.7cm}|
>{\centering\arraybackslash}p{1.2cm}|
>{\centering\arraybackslash}p{1.3cm}|
>{\centering\arraybackslash}p{1.7cm}|
>{\centering\arraybackslash}p{1.7cm}|}

\caption{\textbf{Summary of Maximum Demands}}\\
\hline
\rowcolor{tableHeaderBg}
\textcolor{tableHeaderText}{\textbf{Load Case /}}
& \multicolumn{3}{c|}{\textcolor{tableHeaderText}{\textbf{Bending Moment}}}
& \multicolumn{3}{c|}{\textcolor{tableHeaderText}{\textbf{Shear Force}}}
& \multicolumn{2}{c|}{\textcolor{tableHeaderText}{\textbf{Support Reaction}}}\\
\cline{2-9}
\rowcolor{tableHeaderBg}
\textcolor{tableHeaderText}{\textbf{Combination}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Max}}\\\textcolor{tableHeaderText}{\textbf{(kNm)}}}
& \textcolor{tableHeaderText}{\textbf{Girder}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Loc.}}\\\textcolor{tableHeaderText}{\textbf{(m)}}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Max}}\\\textcolor{tableHeaderText}{\textbf{(kN)}}}
& \textcolor{tableHeaderText}{\textbf{Girder}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Loc.}}\\\textcolor{tableHeaderText}{\textbf{(m)}}}
& \textcolor{tableHeaderText}{\textbf{Left}}
& \textcolor{tableHeaderText}{\textbf{Right}}\\
\hline
\endfirsthead

\multicolumn{9}{l}{\footnotesize\textit{\tablename\ \thetable\ --- Summary of Maximum Demands (continued)}}\\
\hline
\rowcolor{tableHeaderBg}
\textcolor{tableHeaderText}{\textbf{Load Case /}}
& \multicolumn{3}{c|}{\textcolor{tableHeaderText}{\textbf{Bending Moment}}}
& \multicolumn{3}{c|}{\textcolor{tableHeaderText}{\textbf{Shear Force}}}
& \multicolumn{2}{c|}{\textcolor{tableHeaderText}{\textbf{Support Reaction}}}\\
\cline{2-9}
\rowcolor{tableHeaderBg}
\textcolor{tableHeaderText}{\textbf{Combination}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Max}}\\\textcolor{tableHeaderText}{\textbf{(kNm)}}}
& \textcolor{tableHeaderText}{\textbf{Girder}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Loc.}}\\\textcolor{tableHeaderText}{\textbf{(m)}}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Max}}\\\textcolor{tableHeaderText}{\textbf{(kN)}}}
& \textcolor{tableHeaderText}{\textbf{Girder}}
& \makecell{\textcolor{tableHeaderText}{\textbf{Loc.}}\\\textcolor{tableHeaderText}{\textbf{(m)}}}
& \textcolor{tableHeaderText}{\textbf{Left}}
& \textcolor{tableHeaderText}{\textbf{Right}}\\
\hline
\endhead
\hline
\endfoot
\hline
\endlastfoot

"""
        + merged_body
        + r"""
\end{longtable}
\endgroup
"""
        + t_rxn
        + t_defl
        + r"""
\vspace{0.6em}
\noindent
"""
        + _fig_embed(
            fig_paths.get("bm_envelope"),
            "Bending Moment Envelope (Envelope ULS): Max/min BM along span. X-axis: distance from left support (m). Y-axis: Bending Moment (kN-m).",
            width=r"0.78\textwidth",
        )
        + "\n"
        + _fig_embed(
            fig_paths.get("sf_envelope"),
            "Shear Force Envelope (Envelope ULS): Max/min SF along span. X-axis: distance from left support (m). Y-axis: Shear Force (kN).",
            width=r"0.78\textwidth",
        )
        + "\n"
        + _fig_embed(
            fig_paths.get("defl_ll"),
            "Vertical Deflection D$_y$ (1.0 LL): Maximum deflection along span. Load Case: 1.0 LL, Combination: $D_y$. Nodes shown. Isometric view.",
            width=r"0.78\textwidth",
        )
        + "\n"
    )
