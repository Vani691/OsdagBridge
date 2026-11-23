# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored to separate Vehicle Live Loads and Footpath Live Loads into
# distinct, structured tables with explicit Unit columns and repeating headers.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE,
)

from osdagbridge.core.reports.report_utils import _render_value, _tex
from osdagbridge.core.reports.styles import build_longtable


def _val_or_dash(val, fmt: str = None) -> str:
    if val in (None, ""):
        return "---"
    if fmt:
        try:
            return fmt.format(float(val))
        except (TypeError, ValueError):
            pass
    return _tex(val)


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span_raw = input_dict.get(KEY_SPAN)
    try:
        span_m = float(span_raw) if span_raw not in (None, "") else None
    except (TypeError, ValueError):
        span_m = None

    # ── 1. Selected Live Load Vehicles (driven strictly by UI Loading tab) ────
    selected_vehicles = []  # list of (vehicle_name, category_for_impact, irc_ref)
    vehicle_flags = [
        (KEY_LL_IRC_CLASS_A,       "IRC Class A",           "class_a",  "IRC 6 Cl. 204.1 / Cl. 208.2"),
        (KEY_LL_IRC_70R_WHEELED,   "IRC Class 70R (Wheeled)", "heavy",  "IRC 6 Cl. 204.1 / Cl. 208.3"),
        (KEY_LL_IRC_70R_TRACKED,   "IRC Class 70R (Tracked)", "heavy",  "IRC 6 Cl. 204.1 / Cl. 208.3"),
        (KEY_LL_IRC_70R_BOGIE,     "IRC Class 70R (Bogie)",   "heavy",  "IRC 6 Cl. 204.1 / Cl. 208.3"),
        (KEY_LL_IRC_AA_WHEELED,    "IRC Class AA (Wheeled)",  "heavy",  "IRC 6 Cl. 204.1 / Cl. 208.3"),
        (KEY_LL_IRC_AA_TRACKED,    "IRC Class AA (Tracked)",  "heavy",  "IRC 6 Cl. 204.1 / Cl. 208.3"),
        (KEY_LL_IRC_CLASS_SV,      "IRC Special Vehicle (SV)", "sv",    "IRC 6 Cl. 204.5"),
        (KEY_LL_IRC_CLASS_FATIGUE, "IRC Fatigue Vehicle",     "fatigue","IRC 6 Cl. 204.6"),
    ]
    for key, label, cat, ref in vehicle_flags:
        if input_dict.get(key):
            selected_vehicles.append((label, cat, ref))

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            if isinstance(c, dict) and c.get("name"):
                selected_vehicles.append((str(c["name"]), "custom", "User-defined"))
            elif isinstance(c, str) and c.strip():
                selected_vehicles.append((c.strip(), "custom", "User-defined"))

    # Compute IRC 6 Impact Factor per selected vehicle class
    im_class_a = None
    im_heavy = None
    if span_m is not None:
        try:
            im_class_a = 1.0 + float(IRC6_2017.cl_208_2_impact_factor(span_m))
        except Exception:
            im_class_a = None
        try:
            im_heavy = 1.0 + float(IRC6_2017.cl_208_3_impact_factor(span_m))
        except Exception:
            im_heavy = None

    # Braking force (IRC 6 Cl. 211.2)
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_kn_str = "N/A"
    braking_t_str = "N/A"
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            bf_t = float(IRC6_2017.cl_211_2_braking_force(lanes_int))
            bf_kn = bf_t * 9.81
            braking_kn_str = f"{bf_kn:.2f}"
            braking_t_str = f"{bf_t:.2f}"
        except Exception:
            pass

    # Build Vehicle Live Load rows (Table 3.3) with explicit Unit column
    veh_rows = []
    if selected_vehicles:
        for vname, cat, ref in selected_vehicles:
            if cat == "class_a" and im_class_a is not None:
                if_val = f"{im_class_a:.3f}"
            elif cat == "heavy" and im_heavy is not None:
                if_val = f"{im_heavy:.3f}"
            elif cat == "sv":
                if_val = "1.000 (No impact)"
            else:
                if_val = "As specified"
            veh_rows.append(
                rf"\textnormal{{{_tex(vname)}}} & Impact Factor (1 + IF): {if_val} & --- & {_tex(ref)} \\ \hline"
            )
    else:
        veh_rows.append(
            r"\textnormal{Selected Vehicles} & None selected & --- & UI Loading Tab \\ \hline"
        )

    veh_rows.append(
        rf"\textnormal{{Design Traffic Lanes}} & {_val_or_dash(lanes)} & Nos. & IRC 5 Cl. 104.3.1 \\ \hline"
    )
    veh_rows.append(
        rf"\textnormal{{Longitudinal Braking Force}} & {braking_kn_str} ({braking_t_str} t) & kN & IRC 6 Cl. 211.2 \\ \hline"
    )
    veh_rows.append(
        r"\textnormal{Centrifugal Force} & 0.00 (Straight alignment) & kN & IRC 6 Cl. 212 \\ \hline"
    )
    vehicle_ll_body = "\n".join(veh_rows)

    # ── 2. Separate Footpath (Footway) Live Load Table (Table 3.4) ────────────
    footpath_cfg = str(input_dict.get(KEY_FOOTPATH, "None") or "None").strip()
    has_footpath = footpath_cfg.lower() not in ("", "none", "no")
    fp_width = _render_value(input_dict, KEY_TS_FOOTPATH_WIDTH) or ("---" if not has_footpath else "1.50")
    fp_mode = str(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "") or "").strip()
    fp_val_raw = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE)

    fp_intensity_str = "N/A"
    fp_ref = "IRC 6 Cl. 206.1"
    if has_footpath:
        if fp_mode.lower() in ("as per irc 6", "as per irc6", "automatic", ""):
            try:
                fp_intensity_str = f"{float(IRC6_2017.cl_206_1_footway_load()):.3f}"
                fp_mode = fp_mode or "As per IRC 6"
            except Exception:
                fp_intensity_str = _val_or_dash(fp_val_raw)
        elif fp_val_raw not in (None, ""):
            fp_intensity_str = _val_or_dash(fp_val_raw, "{:.3f}")
            fp_ref = "User-defined"
    else:
        fp_mode = "Not Applicable"
        fp_intensity_str = "0.000 (No footpath)"

    footpath_ll_body = "\n".join([
        rf"\textnormal{{Footpath Configuration}} & {_tex(footpath_cfg)} & --- & Basic Inputs \\ \hline",
        rf"\textnormal{{Footpath Width (each side)}} & {fp_width if has_footpath else 'N/A'} & m & IRC 5 Cl. 104.3.6 \\ \hline",
        rf"\textnormal{{Footpath Loading Mode}} & {_tex(fp_mode)} & --- & UI Loading Tab \\ \hline",
        rf"\textnormal{{Design Footpath Live Load Intensity}} & {fp_intensity_str} & kN/m\textsuperscript{{2}} & {_tex(fp_ref)} \\ \hline",
    ])

    # ── 3. Wind Load (Vz / Pz fallback to IRC 6 Table 12) ─────────────────────
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get("wind_speed")
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass

    # ── 4. Seismic Load (fallback to IRC 6 Cl. 218.5.1) ───────────────────────
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get("seismic_zone")
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z, _z)
            _smap = {
                "Type I – Rocky or Hard": 1,
                "Type II – Medium Soil": 2,
                "Type III – Soft Soil": 3,
            }
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res = IRC6_2017.cl_218_5_1(
                zone=f"Zone {_z}",
                soil_type=_st,
                dead_load_kN=_dead,
                live_load_kN=_live,
                period_T=float(_tp) if _tp else None,
                damping_percent=float(_damp),
            )
            sl_zone_factor = sl_zone_factor or _res.get("Z")
            sl_spectral = sl_spectral or _res.get("Sa_g_adjusted")
            sl_ah = sl_ah or _res.get("Ah")
            sl_av = sl_av or round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    # ── 5. Temperature Load (prefer stored keys, fallback to IRC 6 Cl. 215.2) ─
    tl_temp_min = input_dict.get(KEY_TL_BRIDGE_TEMP_MIN)
    tl_temp_max = input_dict.get(KEY_TL_BRIDGE_TEMP_MAX)
    tl_rise = input_dict.get(KEY_TL_TEMP_RISE)
    tl_fall = input_dict.get(KEY_TL_TEMP_FALL)
    if not tl_temp_min or not tl_temp_max:
        try:
            _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get("shade_temp_max")
            _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP) or input_dict.get("shade_temp_min")
            if _tmax and _tmin:
                _res = IRC6_2017.cl_215_2_effective_bridge_temperature(
                    float(_tmax), float(_tmin), "metallic", False
                )
                _bt_min = _res.get("T_min", 0)
                _bt_max = _res.get("T_max", 0)
                _mean = (_bt_max + _bt_min) / 2.0
                tl_temp_min = f"{_bt_min:.2f}"
                tl_temp_max = f"{_bt_max:.2f}"
                tl_rise = f"{_bt_max - _mean:.2f}"
                tl_fall = f"{_mean - _bt_min:.2f}"
        except Exception:
            pass

    # ── 6. Load Combinations (IRC 6 ULS + SLS) ────────────────────────────────
    _LOAD_LABEL_MAP = {
        "dead_load": "DL",
        "surfacing": "SIDL",
        "live_load": "LL",
        "wind_load": "WL",
        "thermal_load": "TL",
        "vehicle_collision": "VC",
        "barge_impact": "BI",
        "floating_bodies": "FB",
        "seismic": "EQ",
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get("adding")
                rel = val.get("relieving")
                add_s = f"{add:.2f}" if add is not None else "--"
                rel_s = f"{rel:.2f}" if rel is not None else "--"
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return " + ".join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        lc_rows.append(rf"ULS-{i:02d} & {_fmt_factors(combo['factors'])} \\ \hline")
    for i, combo in enumerate(sls_combos, start=1):
        lc_rows.append(rf"SLS-{i:02d} & {_fmt_factors(combo['factors'])} \\ \hline")
    lc_rows_str = "\n".join(lc_rows)

    # ── Assemble Tables via Centralized build_longtable() ─────────────────────
    t_dl = build_longtable(
        col_spec="|L{6.5cm}|C{5.5cm}|C{3.5cm}|",
        caption="Dead Load -- Self Weight (DL)",
        headers=["Parameter", "Value", "Unit"],
        body="\n".join([
            rf"\textnormal{{Steel Self-Weight Density}} & {_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY) or '---'} & kN/m\textsuperscript{{3}} \\ \hline",
            rf"\textnormal{{Concrete Deck Density}} & {_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY) or '---'} & kN/m\textsuperscript{{3}} \\ \hline",
            rf"\textnormal{{Self-Weight Factor}} & {_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR) or '---'} & --- \\ \hline",
        ]),
    )

    t_dw = build_longtable(
        col_spec="|L{6.5cm}|C{5.5cm}|C{3.5cm}|",
        caption="Dead Load for Surfacing and Appurtenances (DW / SIDL)",
        headers=["Parameter", "Value", "Unit"],
        body="\n".join([
            rf"\textnormal{{Wearing Course Material \& Thickness}} & {_render_value(input_dict, KEY_WC_MATERIAL)} $\times$ {_render_value(input_dict, KEY_WC_THICKNESS)} & mm \\ \hline",
            rf"\textnormal{{Additional SIDL (Crash Barrier)}} & {_render_value(input_dict, KEY_CB_LOAD) or '---'} & kN/m per barrier \\ \hline",
            rf"\textnormal{{Railing Load}} & {_render_value(input_dict, KEY_RL_LOAD_VALUE) or '---'}\sdstar{{}} & kN/m \\ \hline",
        ]),
    )

    t_vehicle_ll = build_longtable(
        col_spec="|L{4.8cm}|L{4.8cm}|C{2.0cm}|L{4.0cm}|",
        caption="Vehicle Live Loads (LL) --- per IRC 6",
        headers=["Vehicle Class / Parameter", "Design Value", "Unit", "IRC 6 Reference"],
        body=vehicle_ll_body,
        note="Vehicles reflect the active selections in Additional Inputs (Loading tab).",
    )

    t_footpath_ll = build_longtable(
        col_spec="|L{5.5cm}|C{4.2cm}|C{2.2cm}|L{3.7cm}|",
        caption="Footpath (Footway) Live Loads --- per IRC 6 Cl. 206.1",
        headers=["Parameter", "Value", "Unit", "Reference"],
        body=footpath_ll_body,
    )

    t_wl = build_longtable(
        col_spec="|L{6.5cm}|C{5.5cm}|C{3.5cm}|",
        caption="Wind Load (WL) --- per IRC 6",
        headers=["Parameter", "Value", "Unit"],
        body="\n".join([
            rf"\textnormal{{Basic Wind Speed, $V_b$ [from Project Location]}} & {_render_value(input_dict, 'wind_speed') or '---'} & m/s \\ \hline",
            rf"\textnormal{{Terrain Type}} & {_render_value(input_dict, KEY_WL_TERRAIN_TYPE) or '---'} & --- \\ \hline",
            rf"\textnormal{{Average Exposed Height, $H$}} & {_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT) or '---'} & m \\ \hline",
            rf"\textnormal{{Hourly Mean Wind Speed, $V_z$}} & {_val_or_dash(vz_val, '{:.2f}')} & m/s \\ \hline",
            rf"\textnormal{{Hourly Wind Pressure, $P_z$}} & {_val_or_dash(pz_val, '{:.2f}')} & N/m\textsuperscript{{2}} \\ \hline",
            rf"\textnormal{{Transverse Wind Force}} & {_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE) or '---'} & kN \\ \hline",
            rf"\textnormal{{Longitudinal Wind Force}} & {_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE) or '---'} & kN \\ \hline",
            rf"\textnormal{{Vertical Wind Force}} & {_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE) or '---'} & kN \\ \hline",
        ]),
    )

    t_el = build_longtable(
        col_spec="|L{6.5cm}|C{5.5cm}|C{3.5cm}|",
        caption="Earthquake Load (EL) --- per IRC 6",
        headers=["Parameter", "Value", "Unit"],
        body="\n".join([
            rf"\textnormal{{Seismic Zone [from Project Location]}} & {_render_value(input_dict, 'seismic_zone') or '---'} & --- \\ \hline",
            rf"\textnormal{{Zone Factor, $Z$}} & {_val_or_dash(sl_zone_factor, '{:.4f}')} & --- \\ \hline",
            rf"\textnormal{{Importance Factor, $I$}} & {_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR) or '---'} & --- \\ \hline",
            rf"\textnormal{{Type of Soil}} & {_render_value(input_dict, KEY_SL_SOIL_TYPE) or '---'} & --- \\ \hline",
            rf"\textnormal{{Spectral Acceleration Coefficient, $S_a/g$}} & {_val_or_dash(sl_spectral, '{:.4f}')} & --- \\ \hline",
            rf"\textnormal{{Horizontal Seismic Coefficient, $A_h$}} & {_val_or_dash(sl_ah, '{:.4f}')} & --- \\ \hline",
            rf"\textnormal{{Vertical Seismic Coefficient, $A_v$}} & {_val_or_dash(sl_av, '{:.4f}')} & --- \\ \hline",
        ]),
    )

    t_tl = build_longtable(
        col_spec="|L{6.5cm}|C{5.5cm}|C{3.5cm}|",
        caption="Temperature Load (TL) --- per IRC 6",
        headers=["Parameter", "Value", "Unit"],
        body="\n".join([
            rf"\textnormal{{Maximum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_max') or '---'} & $^\circ$C \\ \hline",
            rf"\textnormal{{Minimum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_min') or '---'} & $^\circ$C \\ \hline",
            rf"\textnormal{{Effective Bridge Temperature Range}} & {_val_or_dash(tl_temp_min)} to {_val_or_dash(tl_temp_max)} & $^\circ$C \\ \hline",
            rf"\textnormal{{Design Temperature Rise / Fall}} & +{_val_or_dash(tl_rise)} / -{_val_or_dash(tl_fall)} & $^\circ$C \\ \hline",
        ]),
    )

    t_lc = build_longtable(
        col_spec="|C{3.2cm}|L{12.6cm}|",
        caption="Load Combinations (IRC 6 ULS and SLS)",
        headers=["Combination ID", "Load Cases and Partial Safety Factors"],
        body=lc_rows_str,
        font_size=r"\small",
        note="All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.",
    )

    return (
        r"""
\chapter{Loads and Load Combinations}

This chapter summarizes all permanent, live, wind, seismic, and thermal loads applied to the bridge along with the IRC~6 load combinations considered for analysis and design.

\section{Permanent Loads}
"""
        + t_dl
        + t_dw
        + r"""
\section{Live Loads}
"""
        + t_vehicle_ll
        + t_footpath_ll
        + r"""
\section{Environmental Loads}
"""
        + t_wl
        + t_el
        + t_tl
        + r"""
\section{Load Combinations}
"""
        + t_lc
    )
