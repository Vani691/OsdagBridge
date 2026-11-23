# =============================================================================
# OsdagBridge — Centralized Report Formatting & Style System (Single Source of Truth)
# =============================================================================
"""
Centralized configuration for all visual, typographic, layout, and color rules
used across the OsdagBridge LaTeX report generator and embedded matplotlib charts.

Changing ``ACTIVE_THEME_NAME`` (or setting environment variable
``OSDAG_REPORT_THEME=bw`` / ``color``) restyles the entire PDF report and all
generated charts from a single location.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional, Sequence


# ---------------------------------------------------------------------------
# Theme & Layout Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PageGeometry:
    """Page margin and header/footer clearance settings (A4)."""
    paper: str = "a4paper"
    margin_top: str = "24mm"
    margin_bottom: str = "28mm"   # Extra bottom clearance to prevent footer overlap
    margin_left: str = "20mm"
    margin_right: str = "20mm"
    headheight: str = "16pt"
    headsep: str = "10pt"
    footskip: str = "13mm"


@dataclass(frozen=True)
class TableLayout:
    """Global table spacing, padding, and page-break guard parameters."""
    tabcolsep: str = "5pt"
    arraystretch: str = "1.18"
    arrayrulewidth: str = "0.5pt"
    extrarowheight: str = "1.0pt"
    lt_pre: str = "4pt"
    lt_post: str = "8pt"
    row_gap: str = "4pt"
    needspace_table: str = r"10\baselineskip"
    needspace_section: str = r"8\baselineskip"
    content_width_cm: float = 17.0  # A4 (21cm) - 2cm left - 2cm right


@dataclass(frozen=True)
class ReportTheme:
    """Complete visual theme consumed by LaTeX preamble, chapters, and charts."""
    name: str
    # Core brand & structural hex colors (without leading '#')
    accent_hex: str
    accent_dark_hex: str
    table_header_bg_hex: str
    table_header_text_hex: str
    zebra_bg_hex: str
    border_hex: str
    muted_text_hex: str
    # Semantic pass / warn / fail colors
    pass_text_hex: str
    pass_bg_hex: str
    warn_text_hex: str
    warn_bg_hex: str
    fail_text_hex: str
    fail_bg_hex: str
    # Executive summary KPI card background
    kpi_bg_hex: str
    # Chart palette (hex with leading '#')
    chart_pass: str
    chart_fail: str
    chart_governing: str
    chart_threshold: str
    chart_steel_palette: tuple
    chart_concrete: str
    chart_rebar: str
    chart_grid: str
    chart_text: str


# ---------------------------------------------------------------------------
# Built-in Theme Presets ("color" and print-friendly "bw")
# ---------------------------------------------------------------------------

THEMES: Dict[str, ReportTheme] = {
    "color": ReportTheme(
        name="color",
        accent_hex="91B014",            # Osdag Green
        accent_dark_hex="5A700A",
        table_header_bg_hex="EDF3D6",   # Soft Osdag green tint
        table_header_text_hex="1F2907",
        zebra_bg_hex="F9FAF5",
        border_hex="BFBFBF",
        muted_text_hex="555555",
        pass_text_hex="146C2E",         # Deep green text
        pass_bg_hex="E6F4EA",           # Soft green cell fill
        warn_text_hex="9A5B00",         # Amber text
        warn_bg_hex="FEF3C7",           # Soft amber fill
        fail_text_hex="B91C1C",         # Deep red text
        fail_bg_hex="FEE2E2",           # Soft red cell fill
        kpi_bg_hex="F4F7E8",
        chart_pass="#4F7942",
        chart_fail="#C0392B",
        chart_governing="#2C5E1A",
        chart_threshold="#D32F2F",
        chart_steel_palette=("#4A6B1C", "#7A9E2E", "#A6C44D", "#607D8B"),
        chart_concrete="#4B6A88",
        chart_rebar="#B85D19",
        chart_grid="#D8D8D8",
        chart_text="#222222",
    ),
    "bw": ReportTheme(
        name="bw",
        accent_hex="333333",            # Dark charcoal for B&W printing
        accent_dark_hex="111111",
        table_header_bg_hex="E8E8E8",   # Light neutral gray
        table_header_text_hex="000000",
        zebra_bg_hex="F7F7F7",
        border_hex="888888",
        muted_text_hex="444444",
        pass_text_hex="111111",
        pass_bg_hex="F0F0F0",
        warn_text_hex="222222",
        warn_bg_hex="E0E0E0",
        fail_text_hex="000000",
        fail_bg_hex="CCCCCC",
        kpi_bg_hex="F2F2F2",
        chart_pass="#666666",
        chart_fail="#1A1A1A",
        chart_governing="#333333",
        chart_threshold="#000000",
        chart_steel_palette=("#2B2B2B", "#595959", "#8C8C8C", "#B8B8B8"),
        chart_concrete="#4D4D4D",
        chart_rebar="#999999",
        chart_grid="#CCCCCC",
        chart_text="#111111",
    ),
}

# Single switch to restyle the entire report ("color" or "bw")
ACTIVE_THEME_NAME: str = "color"

PAGE_GEOMETRY = PageGeometry()
TABLE_LAYOUT = TableLayout()
FONT_SIZE_PT: int = 11
LINE_STRETCH: float = 1.15


def get_theme(theme_name: Optional[str] = None) -> ReportTheme:
    """Return the active ReportTheme (arg > OSDAG_REPORT_THEME env > default)."""
    name = (
        theme_name
        or os.environ.get("OSDAG_REPORT_THEME", "").strip().lower()
        or ACTIVE_THEME_NAME
    )
    return THEMES.get(name, THEMES["color"])


def set_active_theme(theme_name: str) -> ReportTheme:
    """Programmatically switch the active theme ('color' or 'bw')."""
    global ACTIVE_THEME_NAME
    key = theme_name.strip().lower()
    if key not in THEMES:
        raise ValueError(f"Unknown report theme '{theme_name}'. Choose from: {list(THEMES)}")
    ACTIVE_THEME_NAME = key
    return THEMES[key]


# ---------------------------------------------------------------------------
# Preamble Style Generation
# ---------------------------------------------------------------------------

def render_geometry_package(geom: PageGeometry = PAGE_GEOMETRY) -> str:
    """Return the LaTeX geometry package declaration with safe footer clearances."""
    return (
        rf"\usepackage[{geom.paper}, "
        rf"top={geom.margin_top}, bottom={geom.margin_bottom}, "
        rf"left={geom.margin_left}, right={geom.margin_right}, "
        rf"headheight={geom.headheight}, headsep={geom.headsep}, "
        rf"footskip={geom.footskip}]{{geometry}}"
    )


def render_color_definitions(theme: Optional[ReportTheme] = None) -> str:
    """Return all xcolor definitions for the active theme."""
    t = theme or get_theme()
    return "\n".join([
        rf"\definecolor{{osdagGreen}}{{HTML}}{{{t.accent_hex}}}",
        rf"\definecolor{{accentDark}}{{HTML}}{{{t.accent_dark_hex}}}",
        rf"\definecolor{{tableHeaderBg}}{{HTML}}{{{t.table_header_bg_hex}}}",
        rf"\definecolor{{tableHeaderText}}{{HTML}}{{{t.table_header_text_hex}}}",
        rf"\definecolor{{zebraBg}}{{HTML}}{{{t.zebra_bg_hex}}}",
        rf"\definecolor{{tableBorder}}{{HTML}}{{{t.border_hex}}}",
        rf"\definecolor{{mutedText}}{{HTML}}{{{t.muted_text_hex}}}",
        rf"\definecolor{{passText}}{{HTML}}{{{t.pass_text_hex}}}",
        rf"\definecolor{{passBg}}{{HTML}}{{{t.pass_bg_hex}}}",
        rf"\definecolor{{warnText}}{{HTML}}{{{t.warn_text_hex}}}",
        rf"\definecolor{{warnBg}}{{HTML}}{{{t.warn_bg_hex}}}",
        rf"\definecolor{{failText}}{{HTML}}{{{t.fail_text_hex}}}",
        rf"\definecolor{{failBg}}{{HTML}}{{{t.fail_bg_hex}}}",
        rf"\definecolor{{kpiBg}}{{HTML}}{{{t.kpi_bg_hex}}}",
    ])


def render_table_layout_rules(layout: TableLayout = TABLE_LAYOUT) -> str:
    """Return global LaTeX table spacing, padding, and page-break protection rules."""
    return "\n".join([
        r"% Centralized table padding, spacing, and page-bottom guards (styles.py)",
        rf"\setlength{{\tabcolsep}}{{{layout.tabcolsep}}}",
        rf"\renewcommand{{\arraystretch}}{{{layout.arraystretch}}}",
        rf"\setlength{{\LTpre}}{{{layout.lt_pre}}}",
        rf"\setlength{{\LTpost}}{{{layout.lt_post}}}",
        rf"\setlength{{\arrayrulewidth}}{{{layout.arrayrulewidth}}}",
        rf"\setlength{{\extrarowheight}}{{{layout.extrarowheight}}}",
        r"\setlength{\LTleft}{\fill}",
        r"\setlength{\LTright}{\fill}",
        r"\raggedbottom",
        rf"\BeforeBeginEnvironment{{table}}{{\needspace{{{layout.needspace_table}}}}}",
        r"\preto\section{\needspace{8\baselineskip}}",
        r"\preto\subsection{\needspace{6\baselineskip}}",
    ])


def render_header_footer_styles(pn: str, jn: str, rd: str, rv: str) -> str:
    """Return fancyhdr styles with non-overlapping footer spacing."""
    shared_footrule = r"""  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-10pt}%
      \hbox to \headwidth{\textcolor{mutedText}{\scriptsize\textit{* Software default value}}\hfil}%
      \vspace{2pt}%
    }{%
      \vspace{-4pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{4pt}%
  }"""

    return (
        r"""\fancypagestyle{main}{
  \fancyhf{}
  \fancyhead[L]{\small """ + pn + r""" $|$ """ + jn + r"""}
  \fancyhead[R]{\small """ + rd + r""" $|$ """ + rv + r"""}
  \fancyfoot[L]{\small Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{\small Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
""" + shared_footrule + r"""
}
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyhead[L]{\small """ + pn + r""" $|$ """ + jn + r"""}
  \fancyhead[R]{\small """ + rd + r""" $|$ """ + rv + r"""}
  \fancyfoot[L]{\small Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{\small Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}
""" + shared_footrule + r"""
}
\fancypagestyle{firstpage}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyfoot[L]{\small Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}
  \fancyfoot[R]{\small Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\footrule}{\vspace{-4pt}\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{4pt}}
}
\pagestyle{main}"""
    )


# ---------------------------------------------------------------------------
# Reusable Table, Status, UR, and Figure Builders
# ---------------------------------------------------------------------------

def _count_columns(col_spec: str) -> int:
    """Count top-level table columns from a LaTeX column specification."""
    depth = 0
    cleaned = []
    for ch in col_spec:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
        elif depth == 0:
            cleaned.append(ch)
    top = "".join(cleaned)
    # Count standard + custom column specifiers (l, c, r, p, m, b, X, L, C, R)
    # Exclude '>' and '<' prefixes
    return sum(1 for ch in top if ch in "lcrpmbXLCR")


def build_longtable(
    col_spec: str,
    caption: str,
    headers: Sequence[str],
    body: str,
    label: Optional[str] = None,
    font_size: Optional[str] = None,
    tabcolsep: Optional[str] = None,
    arraystretch: Optional[str] = None,
    note: Optional[str] = None,
    col_count: Optional[int] = None,
) -> str:
    """
    Build a standardized LaTeX ``longtable`` with automatic repeating headers
    (``\\endfirsthead`` and ``\\endhead``), tinted header rows, clean continuation
    markers, and properly scoped ``\\begingroup`` / ``\\endgroup`` overrides.
    """
    ncols = col_count or (len(headers) if headers else _count_columns(col_spec))
    label_tex = rf"\label{{{label}}}" if label else ""

    if headers:
        hdr_cells = " & ".join(
            rf"\textcolor{{tableHeaderText}}{{\textbf{{{h}}}}}" if h else ""
            for h in headers
        )
        hdr_row = rf"\rowcolor{{tableHeaderBg}} {hdr_cells} \\" + "\n" + r"\hline"
    else:
        hdr_row = ""

    parts = [r"\vspace{0.6em}"]
    needs_group = any([font_size, tabcolsep, arraystretch])
    if needs_group:
        parts.append(r"\begingroup")
        if font_size:
            parts.append(font_size)
        if tabcolsep:
            parts.append(rf"\setlength{{\tabcolsep}}{{{tabcolsep}}}")
        if arraystretch:
            parts.append(rf"\renewcommand{{\arraystretch}}{{{arraystretch}}}")

    parts.append(rf"\begin{{longtable}}{{{col_spec}}}")
    parts.append(rf"\caption{{\textbf{{{caption}}}}}{label_tex}\\")
    parts.append(r"\hline")
    if hdr_row:
        parts.append(hdr_row)
    parts.append(r"\endfirsthead")
    parts.append(
        rf"\multicolumn{{{ncols}}}{{l}}{{\footnotesize\textit{{\tablename\ \thetable\ --- {caption} (continued)}}}}\\"
    )
    parts.append(r"\hline")
    if hdr_row:
        parts.append(hdr_row)
    parts.append(r"\endhead")
    parts.append(r"\hline")
    parts.append(r"\endfoot")
    parts.append(r"\hline")
    parts.append(r"\endlastfoot")
    parts.append(body.strip())
    parts.append(r"\end{longtable}")

    if needs_group:
        parts.append(r"\endgroup")

    if note:
        parts.append(rf"\noindent\textit{{\small Note: {note}}}")

    return "\n".join(parts) + "\n"


def format_status(status: Optional[str], shade: bool = True) -> str:
    """Format PASS / WARN / FAIL status cells using theme colors."""
    if status is None:
        return "---"
    s = str(status).strip()
    if not s or s in ("---", "N/A"):
        return s or "---"
    upper = s.upper()
    if "FAIL" in upper:
        prefix = r"\cellcolor{failBg}" if shade else ""
        return rf"{prefix}\textcolor{{failText}}{{\textbf{{{s}}}}}"
    if "WARN" in upper:
        prefix = r"\cellcolor{warnBg}" if shade else ""
        return rf"{prefix}\textcolor{{warnText}}{{\textbf{{{s}}}}}"
    if "PASS" in upper:
        prefix = r"\cellcolor{passBg}" if shade else ""
        return rf"{prefix}\textcolor{{passText}}{{\textbf{{{s}}}}}"
    return s


def format_ur_cell(ur_value, decimals: int = 2, shade: bool = True) -> str:
    """
    Format a Utilization Ratio (UR) table cell with pass/fail color coding:
      - UR <= 1.0 : green text + soft green cell fill (passBg / passText)
      - UR >  1.0 : red text + soft red cell fill (failBg / failText)
    """
    try:
        val = float(ur_value)
    except (TypeError, ValueError):
        return "---"
    text = f"{val:.{decimals}f}"
    if val <= 1.0:
        prefix = r"\cellcolor{passBg}" if shade else ""
        return rf"{prefix}\textcolor{{passText}}{{\textbf{{{text}}}}}"
    prefix = r"\cellcolor{failBg}" if shade else ""
    return rf"{prefix}\textcolor{{failText}}{{\textbf{{{text}}}}}"


def build_figure_block(
    path: Optional[str],
    caption: str,
    width: str = r"0.88\textwidth",
    label: Optional[str] = None,
    numbered: bool = True,
    height: Optional[str] = None,
) -> str:
    """Consistent figure wrapper used across chapters and auto-generated charts."""
    label_tex = (rf"\label{{{label}}}" + "\n") if label else ""
    cap_cmd = rf"\caption{{{caption}}}" if numbered else rf"\caption*{{\small {caption}}}"
    if path:
        p = path.replace("\\", "/")
        opts = f"width={width}"
        if height:
            opts += f",height={height},keepaspectratio"
        return (
            r"\begin{figure}[H]" + "\n"
            r"\centering" + "\n"
            rf"\includegraphics[{opts}]{{{p}}}" + "\n"
            + cap_cmd + "\n"
            + label_tex
            + r"\end{figure}"
        )
    return (
        r"\begin{figure}[H]" + "\n"
        r"\centering" + "\n"
        r"\fbox{\parbox{0.94\textwidth}{\centering\textit{[ PLACEHOLDER: " + caption + r" ]}}}" + "\n"
        + cap_cmd + "\n"
        + label_tex
        + r"\end{figure}"
    )
