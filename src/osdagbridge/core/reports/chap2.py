# =============================================================================
# Chapter 2: Input Parameters — Refactored to use centralized styles.py
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_CB_TYPE,
    KEY_CROSS_BRACING,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DO_GAMMA_C_BASIC,
    KEY_DO_GAMMA_FLT,
    KEY_DO_GAMMA_M0,
    KEY_DO_GAMMA_M1,
    KEY_DO_GAMMA_MF,
    KEY_DO_GAMMA_S,
    KEY_DO_GAMMA_V,
    KEY_END_DIAPHRAGM,
    KEY_FOOTPATH,
    KEY_GIRDER,
    KEY_INCLUDE_MEDIAN,
    KEY_MD_TYPE,
    KEY_MP_CB_BRACING_SECTION_DESIGNATION,
    KEY_MP_CB_MEMBER_ID,
    KEY_MP_CB_SELECT_GIRDERS,
    KEY_MP_CB_SPACING,
    KEY_MP_CB_TYPE,
    KEY_MP_ED_BRACING_SECTION_DESIGNATION,
    KEY_MP_ED_MEMBER_ID,
    KEY_MP_ED_SELECT_GIRDERS,
    KEY_MP_ED_TYPE,
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS,
    KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH,
    KEY_MP_GIRDER_DEPTH,
    KEY_MP_GIRDER_SYMMETRY,
    KEY_MP_GIRDER_TOP_FLANGE_THICKNESS,
    KEY_MP_GIRDER_TOP_FLANGE_WIDTH,
    KEY_MP_GIRDER_TORSIONAL_RESTRAINT,
    KEY_MP_GIRDER_TYPE,
    KEY_MP_GIRDER_WARPING_RESTRAINT,
    KEY_MP_GIRDER_WEB_THICKNESS,
    KEY_MP_GIRDER_WEB_TYPE,
    KEY_MP_STIFFENER_BEARING_THICKNESS,
    KEY_MP_STIFFENER_INTERMEDIATE,
    KEY_MP_STIFFENER_INTERMEDIATE_SPACING,
    KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS,
    KEY_MP_STIFFENER_LONGITUDINAL,
    KEY_MP_STIFFENER_NO_BEARING_STIFFENERS,
    KEY_MP_STIFFENER_SPACING,
    KEY_RL_LOAD_VALUE,
    KEY_RL_TYPE,
    KEY_SD_SHEAR_DIAMETER,
    KEY_SD_SHEAR_HEIGHT,
    KEY_SD_SHEAR_STUDS_PER_SECTION,
    KEY_SD_SHEAR_ULTIMATE_STRENGTH,
    KEY_SD_SHEAR_YIELD_STRENGTH,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_OVERALL_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
)

from osdagbridge.core.reports.report_utils import _render_value, _tex, get_girder_entries
from osdagbridge.core.reports.styles import build_longtable


def ch2_input_parameters(m, input_dict, output_dict=None):
    girder_entries = get_girder_entries(input_dict)
    n_girders = len(girder_entries)

    median_row = ""
    if str(input_dict.get(KEY_INCLUDE_MEDIAN, "")).strip().lower() in ("yes", "true", "1"):
        median_row = (
            r"\textnormal{Median Type} & "
            + _render_value(input_dict, KEY_MD_TYPE)
            + r" \\ \hline" + "\n"
        )

    t_loc = build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Project Location",
        headers=["Parameter", "Value"],
        label="subsec:project-location",
        body="\n".join([
            rf"\textnormal{{Project Location}} & {_tex(m.project_location)} \\ \hline",
            rf"\textnormal{{Latitude / Longitude}} & {_render_value(input_dict, 'latitude')}, {_render_value(input_dict, 'longitude')} \\ \hline",
            rf"\textnormal{{Seismic Zone (IRC 6)}} & {_render_value(input_dict, 'seismic_zone')} \\ \hline",
            rf"\textnormal{{Basic Wind Speed (IRC 6)}} & {_render_value(input_dict, 'wind_speed', ' m/s')} \\ \hline",
            rf"\textnormal{{Shade Temp. Max / Min (IRC 6)}} & {_render_value(input_dict, 'shade_temp_max')} $^\circ$C / {_render_value(input_dict, 'shade_temp_min')} $^\circ$C \\ \hline",
        ]),
    )

    t_geom = build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Bridge Geometry",
        headers=["Parameter", "Value"],
        label="subsec:bridge-geometry",
        body="\n".join([
            rf"\textnormal{{Type of Structure}} & {_render_value(input_dict, KEY_STRUCTURE_TYPE)} \\ \hline",
            rf"\textnormal{{Span (m)}} & {_render_value(input_dict, KEY_SPAN, ' m')} \\ \hline",
            rf"\textnormal{{Carriageway Width (m)}} & {_render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, ' m')} \\ \hline",
            rf"\textnormal{{Include Median}} & {_render_value(input_dict, KEY_INCLUDE_MEDIAN)} \\ \hline",
            rf"\textnormal{{Footpath}} & {_render_value(input_dict, KEY_FOOTPATH)} \\ \hline",
            rf"\textnormal{{Skew Angle (degrees)}} & {_render_value(input_dict, KEY_SKEW_ANGLE)} $^\circ$ (IRC 24 Cl. 504.8 limit: $\pm 15^\circ$) \\ \hline",
        ]),
    )

    t_mat = build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Material Selection",
        headers=["Parameter", "Value"],
        label="subsec:material",
        body="\n".join([
            rf"\textnormal{{Girder Steel Grade (IS 2062)}} & {_render_value(input_dict, KEY_GIRDER)} \\ \hline",
            rf"\textnormal{{Cross Bracing Steel Grade}} & {_render_value(input_dict, KEY_CROSS_BRACING)} \\ \hline",
            rf"\textnormal{{End Diaphragm Steel Grade}} & {_render_value(input_dict, KEY_END_DIAPHRAGM)} \\ \hline",
            rf"\textnormal{{Concrete Deck Grade (IRC 22)}} & {_render_value(input_dict, KEY_DECK_CONCRETE_GRADE_BASIC)} \\ \hline",
        ]),
    )

    t_typical = build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Typical Section Details",
        headers=["Parameter", "Value"],
        body="\n".join([
            rf"\textnormal{{Overall Bridge Width (m)}} & {_render_value(input_dict, KEY_TS_OVERALL_WIDTH)} \\ \hline",
            rf"\textnormal{{No. of Girders}} & {_render_value(input_dict, KEY_TS_NO_OF_GIRDERS)} \\ \hline",
            rf"\textnormal{{Girder Spacing (m)}} & {_render_value(input_dict, KEY_TS_GIRDER_SPACING, ' m')} \\ \hline",
            rf"\textnormal{{Deck Overhang Width (m)}} & {_render_value(input_dict, KEY_TS_DECK_OVERHANG, ' m')} \\ \hline",
            rf"\textnormal{{Deck Thickness (mm)}} & {_render_value(input_dict, KEY_TS_DECK_THICKNESS, ' mm')} \\ \hline",
            rf"\textnormal{{Footpath Width (m)}} & {_render_value(input_dict, KEY_TS_FOOTPATH_WIDTH, ' m')} (IRC 5 Cl. 104.3.6 min: 1.5 m) \\ \hline",
            rf"\textnormal{{No. of Traffic Lanes}} & {_render_value(input_dict, KEY_WC_LD_LANE_TABLE_COUNT)} (per IRC 5 Cl. 104.3.1) \\ \hline",
        ]),
    )

    t_comp = build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Components Details",
        headers=["Parameter", "Value"],
        body=(
            rf"\textnormal{{Crash Barrier Type}} & {_render_value(input_dict, KEY_CB_TYPE)} \\ \hline" + "\n"
            rf"\textnormal{{Crash Barrier Load (kN/m)}} & {_render_value(input_dict, KEY_CB_LOAD)} \\ \hline" + "\n"
            + median_row
            + rf"\textnormal{{Railing Type}} & {_render_value(input_dict, KEY_RL_TYPE)} \\ \hline" + "\n"
            + rf"\textnormal{{Railing Load (kN/m)}} & {_render_value(input_dict, KEY_RL_LOAD_VALUE)} \\ \hline" + "\n"
            + rf"\textnormal{{Wearing Course Material}} & {_render_value(input_dict, KEY_WC_MATERIAL)} \\ \hline" + "\n"
            + rf"\textnormal{{Wearing Course Thickness (mm)}} & {_render_value(input_dict, KEY_WC_THICKNESS, ' mm')} \\ \hline"
        ),
    )

    return (
        r"""
\chapter{Input Parameters}

This section documents all inputs provided to OsdagBridge. User-provided inputs are clearly distinguished from software-assumed defaults. Where the user did not supply a value, the software has applied the IRC/IS code default or an empirical guideline; these are annotated with an asterisk (\sdstar{}).

\section{Basic Inputs (User-Defined)}
\label{sec:basic-inputs}

\noindent\textit{Note: These inputs are mandatory and were provided by the user.}
"""
        + t_loc
        + t_geom
        + t_mat
        + r"""
\newpage
\section{Additional Inputs}
\label{sec:additional-inputs}

Where the user has modified additional inputs, those values are reported here. Where no modification was made, the software default is shown.
"""
        + t_typical
        + t_comp
        + _girder_tables(input_dict, n_girders)
        + _bracing_tables(input_dict, n_girders)
        + _shear_connector_table(input_dict, output_dict)
        + _safety_factors_table(input_dict)
    )


def _girder_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 1 else 1
    girder_entries = get_girder_entries(input_dict)
    if not girder_entries:
        girder_entries = [(f"Girder {i}", "M1") for i in range(1, n + 1)]

    entries_for_table = [
        (lbl, mid, i) for i, (lbl, mid) in enumerate(girder_entries, start=1)
    ]

    def _gen_row(g_lbl, m_id, i):
        return (
            f"{_tex(g_lbl)} & {_tex(m_id)} & "
            + _render_value(input_dict, KEY_DESIGN_MODE) + " & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_TYPE}.G{i}.M1") + " & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_SYMMETRY}.G{i}.M1")
            + r" \\ \hline" + "\n"
        )

    def _dim_row(g_lbl, i):
        return (
            f"{_tex(g_lbl)} & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_DEPTH}.G{i}.M1", " mm") + " & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_WEB_THICKNESS}.G{i}.M1", " mm") + " & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_TOP_FLANGE_WIDTH}.G{i}.M1", " mm")
            + ", "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_TOP_FLANGE_THICKNESS}.G{i}.M1", " mm") + " & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH}.G{i}.M1", " mm")
            + ", "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS}.G{i}.M1", " mm")
            + r" \\ \hline" + "\n"
        )

    def _rst_row(g_lbl, i):
        return (
            f"{_tex(g_lbl)} & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_TORSIONAL_RESTRAINT}.G{i}.M1")
            + ", "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_WARPING_RESTRAINT}.G{i}.M1") + " & "
            + _render_value(input_dict, f"{KEY_MP_GIRDER_WEB_TYPE}.G{i}.M1") + " & "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE}.G{i}.M1")
            + "; Spacing: "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G{i}.M1", " mm")
            + "; Thickness: "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS}.G{i}.M1", " mm") + " & "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_LONGITUDINAL}.G{i}.M1") + " & No.: "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_NO_BEARING_STIFFENERS}.G{i}.M1")
            + "; Spacing: "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_SPACING}.G{i}.M1", " mm")
            + "; Thickness: "
            + _render_value(input_dict, f"{KEY_MP_STIFFENER_BEARING_THICKNESS}.G{i}.M1", " mm")
            + r" \\ \hline" + "\n"
        )

    gen_rows = "".join(_gen_row(g_lbl, m_id, i) for g_lbl, m_id, i in entries_for_table)
    dim_rows = "".join(_dim_row(g_lbl, i) for g_lbl, _, i in entries_for_table)
    rst_rows = "".join(_rst_row(g_lbl, i) for g_lbl, _, i in entries_for_table)

    t_gen = build_longtable(
        col_spec="|C{1.8cm}|C{2.0cm}|L{3.6cm}|L{3.8cm}|L{3.8cm}|",
        caption="Girder General Information",
        headers=["Girder", "Member ID", "Design Mode", "Girder Type", "Girder Symmetry"],
        body=gen_rows,
        font_size=r"\small",
    )

    t_dim = build_longtable(
        col_spec="|C{1.6cm}|C{2.5cm}|C{2.1cm}|C{4.4cm}|C{4.4cm}|",
        caption="Girder Section Dimensions",
        headers=[
            "Girder",
            "Total Depth, D (mm)",
            r"Web, $t_w$ (mm)",
            r"Top Flange ($b_{tf}, t_{tf}$) mm",
            r"Bottom Flange ($b_{bf}, t_{bf}$) mm",
        ],
        body=dim_rows,
        font_size=r"\small",
    )

    t_rst = build_longtable(
        col_spec="|C{1.3cm}|L{2.7cm}|L{2.3cm}|L{3.5cm}|L{2.3cm}|L{3.1cm}|",
        caption="Girder Restraint and Stiffener Details",
        headers=[
            "Girder",
            "Torsional / Warping Restraint",
            "Web Philosophy",
            "Intermediate Stiffeners",
            "Longitudinal Stiffeners",
            "Bearing Stiffener",
        ],
        body=rst_rows,
        font_size=r"\footnotesize",
        tabcolsep="3.5pt",
    )

    return "\n\\newpage\n" + t_gen + t_dim + t_rst


def _bracing_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 2 else 2
    panels = [
        (
            _render_value(input_dict, f"{KEY_MP_CB_SELECT_GIRDERS}.G{i}G{i+1}.B{i}M1"),
            _render_value(input_dict, f"{KEY_MP_CB_MEMBER_ID}.G{i}G{i+1}.B{i}M1"),
            _render_value(input_dict, f"{KEY_MP_ED_SELECT_GIRDERS}.G{i}G{i+1}.E{i}M1"),
            _render_value(input_dict, f"{KEY_MP_ED_MEMBER_ID}.G{i}G{i+1}.E{i}M1"),
            i,
        )
        for i in range(1, n)
    ]

    cb_rows = "".join(
        f"{cb_loc} & {cb_ids} & "
        + _render_value(input_dict, f"{KEY_MP_CB_TYPE}.G{i}G{i+1}.B{i}M1") + " & "
        + _render_value(input_dict, f"{KEY_MP_CB_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.B{i}M1") + " & "
        + _render_value(input_dict, f"{KEY_MP_CB_SPACING}.G{i}G{i+1}.B{i}M1", " m")
        + r" \\ \hline" + "\n"
        for cb_loc, cb_ids, _, _, i in panels
    )

    ed_rows = "".join(
        f"{ed_loc} & {ed_ids} & "
        + _render_value(input_dict, f"{KEY_MP_ED_TYPE}.G{i}G{i+1}.E{i}M1") + " & "
        + _render_value(input_dict, f"{KEY_MP_ED_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.E{i}M1")
        + r" \\ \hline" + "\n"
        for _, _, ed_loc, ed_ids, i in panels
    )

    t_cb = build_longtable(
        col_spec="|C{2.4cm}|C{2.4cm}|L{3.8cm}|L{4.0cm}|C{2.4cm}|",
        caption="Member Properties: Cross Bracing Details",
        headers=["Location", "Member IDs", "Type of Bracing", "Bracing Section", "Spacing (m)"],
        body=cb_rows,
        font_size=r"\small",
        tabcolsep="4pt",
    )

    t_ed = build_longtable(
        col_spec="|C{2.8cm}|C{2.8cm}|L{4.6cm}|L{4.8cm}|",
        caption="Member Properties: End Diaphragm Details",
        headers=["Location", "Member IDs", "Type of Bracing", "Bracing Section"],
        body=ed_rows,
        font_size=r"\small",
        tabcolsep="4pt",
    )

    return "\n\\newpage\n" + t_cb + t_ed


def _shear_connector_table(input_dict, output_dict=None):
    od = output_dict or {}
    return build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Shear Connector Details",
        headers=["Parameter", "Value"],
        label="subsec:shear-connectors",
        body="\n".join([
            rf"\textnormal{{Stud Diameter (mm)}} & {_render_value(od, KEY_SD_SHEAR_DIAMETER, ' mm')} \\ \hline",
            rf"\textnormal{{Stud Height (mm)}} & {_render_value(od, KEY_SD_SHEAR_HEIGHT, ' mm')} \\ \hline",
            rf"\textnormal{{Stud $f_y$ (MPa)}} & {_render_value(od, KEY_SD_SHEAR_YIELD_STRENGTH, ' MPa')} \\ \hline",
            rf"\textnormal{{Stud $f_u$ (MPa)}} & {_render_value(od, KEY_SD_SHEAR_ULTIMATE_STRENGTH, ' MPa')} \\ \hline",
            rf"\textnormal{{No. of Studs per Section}} & {_render_value(od, KEY_SD_SHEAR_STUDS_PER_SECTION)} \\ \hline",
        ]),
    )


def _safety_factors_table(input_dict):
    return build_longtable(
        col_spec="|L{6.0cm}|L{9.8cm}|",
        caption="Partial Safety Factors",
        headers=["Parameter", "Value"],
        label="subsec:safety-factors",
        note="All values are per IRC 22 Table 1 unless user-modified.",
        body="\n".join([
            rf"\textnormal{{$\gamma_{{M0}}$ (Yielding / Buckling)}} & {_render_value(input_dict, KEY_DO_GAMMA_M0)} \\ \hline",
            rf"\textnormal{{$\gamma_{{M1}}$ (Ultimate Stress)}} & {_render_value(input_dict, KEY_DO_GAMMA_M1)} \\ \hline",
            rf"\textnormal{{$\gamma_C$ (Concrete, Basic)}} & {_render_value(input_dict, KEY_DO_GAMMA_C_BASIC)} \\ \hline",
            rf"\textnormal{{$\gamma_s$ (Reinforcement)}} & {_render_value(input_dict, KEY_DO_GAMMA_S)} \\ \hline",
            rf"\textnormal{{$\gamma_v$ (Shear Connectors)}} & {_render_value(input_dict, KEY_DO_GAMMA_V)} \\ \hline",
            rf"\textnormal{{$\gamma_{{fft}}$ (Fatigue Load)}} & {_render_value(input_dict, KEY_DO_GAMMA_FLT)} \\ \hline",
            rf"\textnormal{{$\gamma_{{Mft}}$ (Fatigue Strength)}} & {_render_value(input_dict, KEY_DO_GAMMA_MF)} \\ \hline",
        ]),
    )
