from osdagbridge.core.reports.styles import build_figure_block


def ch6_drawings(fig_paths):
    """Chapter 6 -- Drawings and Visualizations (uses centralized figure helpers)."""

    def _sec_fig(path, title, label=None):
        return build_figure_block(
            path, title, width=r"0.84\textwidth", label=label, numbered=True
        )

    sup3d = _sec_fig(fig_paths.get("final_geometry"), "Overall 3D Bridge Superstructure", "fig:bridge-3d")
    cs = _sec_fig(fig_paths.get("cross_section"), "Typical Cross Section", "fig:cross-section")
    gtop = _sec_fig(fig_paths.get("girder_top"), "Top View", "fig:top-view")
    g3d = _sec_fig(fig_paths.get("girder_3d"), "3D View of Plate Girders", "fig:girder-3d")
    gxsec = _sec_fig(fig_paths.get("section_preview"), "Cross Section of Plate Girder", "fig:girder-xsec")
    gside = _sec_fig(fig_paths.get("stiffener_preview"), "Side View of Girder", "fig:girder-side")
    cbdia = _sec_fig(fig_paths.get("cb_diagram"), "Cross Bracing Layout", "fig:cb-layout")

    def _sec_cell(path, title, label=None):
        label_tex = rf"\label{{{label}}}" if label else ""
        if path:
            p = path.replace("\\", "/")
            body = rf"\includegraphics[width=\linewidth]{{{p}}}"
        else:
            body = rf"\fbox{{\parbox{{0.95\linewidth}}{{\centering\textit{{[ {title} ]}}}}}}"
        return (
            r"\begin{minipage}[t]{0.31\textwidth}" + "\n"
            r"\centering" + "\n"
            + body + "\n"
            rf"\captionof{{figure}}{{{title}}}" + "\n"
            + label_tex + "\n"
            r"\end{minipage}"
        )

    cb_sections_row = (
        r"\noindent" + "\n"
        + _sec_cell(fig_paths.get("cb_bracing"), "Cross Bracing -- Bracing Section", "fig:cb-bracing-sec") + "\n"
        + r"\hfill" + "\n"
        + _sec_cell(fig_paths.get("cb_top_chord"), "Cross Bracing -- Top Chord Section", "fig:cb-top-chord") + "\n"
        + r"\hfill" + "\n"
        + _sec_cell(fig_paths.get("cb_bottom_chord"), "Cross Bracing -- Bottom Chord Section", "fig:cb-bottom-chord")
    )

    eddia = _sec_fig(fig_paths.get("ed_diagram"), "End Diaphragm Layout", "fig:ed-layout")

    ed_sections_row = (
        r"\noindent" + "\n"
        + _sec_cell(fig_paths.get("ed_bracing"), "End Diaphragm -- Bracing Section", "fig:ed-bracing-sec") + "\n"
        + r"\hfill" + "\n"
        + _sec_cell(fig_paths.get("ed_top_chord"), "End Diaphragm -- Top Chord Section", "fig:ed-top-chord") + "\n"
        + r"\hfill" + "\n"
        + _sec_cell(fig_paths.get("ed_bottom_chord"), "End Diaphragm -- Bottom Chord Section", "fig:ed-bottom-chord")
    )

    return (
        r"""
\chapter{Drawings and Visualizations}
\label{ch:drawings}

This section presents CAD-generated views of the designed bridge and its components. All views are generated automatically by OsdagBridge using pythonOCC.

\section{Bridge Configuration and Layout}
\label{sec:bridge-layout}

"""
        + sup3d + "\n\n"
        + cs + "\n\n"
        + gtop
        + r"""

\section{Plate Girder --- Detailed Views}
\label{sec:girder-views}

"""
        + g3d + "\n\n"
        + gxsec + "\n\n"
        + gside
        + r"""

\section{Cross Bracing Detail}
\label{sec:bracing-detail}

"""
        + cbdia + "\n\n"
        + cb_sections_row
        + r"""

\section{End Diaphragm Detail}
\label{sec:diaphragm-detail}

"""
        + eddia + "\n\n"
        + ed_sections_row + "\n"
    )
