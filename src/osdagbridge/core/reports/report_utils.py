from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS,
)
from osdagbridge.core.reports.styles import build_figure_block


def _tex(value):
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ''
    if not s:
        return r''
    # Normalise ASCII-safe glyphs first
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x'), ('–', '--'), ('—', '---'), ('\x0b', ' ')]:
        s = s.replace(uni, ascii_)
    # Escape LaTeX specials
    s = s.replace('\\', r'\textbackslash{}')
    for ch, esc in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                    ('{', r'\{'), ('}', r'\}'),
                    ('_', r'\_\allowbreak{}'),
                    ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(ch, esc)
    # Replace math Unicode glyphs AFTER escaping so LaTeX math stays intact
    for uni, tex_math in [
        ('≤', r'$\leq$'),
        ('≥', r'$\geq$'),
        ('±', r'$\pm$'),
        ('°', r'$^\circ$'),
        ('²', r'$^2$'),
        ('³', r'$^3$'),
    ]:
        s = s.replace(uni, tex_math)
    s = s.replace(':', r':\allowbreak{}')
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """Retrieve all girder labels and member IDs from backend keys."""
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))
    entries = []
    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", ""),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", ""),
            )
        )
    return entries


def _fig_or_placeholder(path, caption, width=r'0.88\textwidth'):
    """Embed figure via centralized styles.build_figure_block (unnumbered caption)."""
    return build_figure_block(path, caption, width=width, numbered=False)


def _fig_embed(path, caption, width=r'0.88\textwidth', height=None):
    """Embed figure via centralized styles.build_figure_block with optional height."""
    return build_figure_block(path, caption, width=width, numbered=False, height=height)
