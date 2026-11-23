from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.styles import build_longtable


def ch1_project_info(m):
    info_body = "\n".join([
        rf"\textbf{{Project Name}} & {_tex(m.project_name)} \\ \hline",
        rf"\textbf{{Project Location}} & {_tex(m.project_location)} \\ \hline",
        rf"\textbf{{Designer}} & {_tex(m.designer)} \\ \hline",
        rf"\textbf{{Reviewer}} & {_tex(m.reviewer)} \\ \hline",
        rf"\textbf{{Organization}} & {_tex(m.company)} \\ \hline",
        rf"\textbf{{Client}} & {_tex(m.client)} \\ \hline",
        r"\textbf{Software Version} & OsdagBridge \\ \hline",
    ])
    info_table = build_longtable(
        col_spec="|L{5.5cm}|L{10.5cm}|",
        caption="Project and Design Team Details",
        headers=["Field", "Details"],
        body=info_body,
        label="tab:project-details",
    )
    return (
        r"""
\chapter{Project Information}

This section records all project metadata as entered by the designer.

\section{Project and Design Team Details}
\label{sec:project-details}
"""
        + info_table
        + r"""
\section{Applicable Codes and Standards}
\label{sec:codes}

\begin{itemize}
\item Indian Roads Congress (IRC) 5: General Features of Design
\item Indian Roads Congress (IRC) 6: Loads and Load Combinations
\item Indian Roads Congress (IRC) 22: Composite Construction (Limit State Design)
\item Indian Roads Congress (IRC) 24: Steel Road Bridges (Limit State Method)
\item Indian Roads Congress (IRC) 112: Concrete Road Bridges (deck design)
\item Indian Roads Congress Special Publication (IRC SP) 114: Seismic Design of Road Bridges
\item Indian Standard (IS) 800: General Construction in Steel
\item Indian Standard (IS) 2062: Hot Rolled Structural Steel Specification
\item Indian Standard (IS) 6006: Steel Bearings
\end{itemize}
"""
    )
