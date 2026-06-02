# =========================================================
# GRÁFICAS INTERACTIVAS DEL DASHBOARD
# Archivo: charts.py
# =========================================================

import re

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import config


# ---------------------------------------------------------
# HELPERS GENERALES
# ---------------------------------------------------------
def safe_float(value, default: float = 0.0) -> float:
    """
    Convierte valores a float sin romper la app cuando hay nulos,
    textos, comas, símbolos de moneda o paréntesis de negativos.
    """
    if value is None:
        return default

    try:
        numeric_value = float(value)
        if pd.isna(numeric_value):
            return default
        return numeric_value
    except (TypeError, ValueError):
        pass

    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "nat", "-"}:
        return default

    is_negative = text.startswith("(") and text.endswith(")")
    text = text.replace("$", "")
    text = text.replace(",", "")
    text = text.replace(" ", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace("%", "")

    # Conserva solamente dígitos, signo y punto decimal.
    text = re.sub(r"[^0-9.\-]", "", text)

    try:
        numeric_value = float(text)
        if pd.isna(numeric_value):
            return default
        return -abs(numeric_value) if is_negative else numeric_value
    except (TypeError, ValueError):
        return default


def get_safe_exchange_rate(exchange_rate: float | int | str | None) -> float:
    try:
        numeric_rate = float(exchange_rate)
    except (TypeError, ValueError):
        numeric_rate = float(config.DEFAULT_EXCHANGE_RATE)

    if numeric_rate <= 0:
        numeric_rate = float(config.DEFAULT_EXCHANGE_RATE)

    return numeric_rate


def normalize_currency_mode(currency_mode: str | None) -> str:
    return "USD" if str(currency_mode or "").strip().upper() == "USD" else config.DEFAULT_CURRENCY


def convert_value_by_currency(value, currency_mode: str, exchange_rate: float) -> float:
    numeric_value = safe_float(value)
    normalized_currency = normalize_currency_mode(currency_mode)

    if normalized_currency == "USD":
        return numeric_value / get_safe_exchange_rate(exchange_rate)

    return numeric_value


def apply_corporate_layout(fig, title: str, height: int = 430):
    fig.update_layout(
        title={
            "text": title,
            "x": 0.02,
            "xanchor": "left",
            "font": {
                "size": 20,
                "family": "Segoe UI, Arial, sans-serif",
                "color": config.COLOR_SECONDARY,
            },
        },
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=45, t=80, b=35),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Segoe UI, Arial, sans-serif",
            color=config.COLOR_TEXT,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Segoe UI, Arial, sans-serif",
            align="left",
        ),
        transition=dict(duration=500, easing="cubic-in-out"),
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EEF1F5",
        zeroline=False,
        linecolor="#D9DEE5",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEF1F5",
        zeroline=False,
        linecolor="#D9DEE5",
    )

    return fig


# ---------------------------------------------------------
# HELPERS PREMIUM PARA GRÁFICAS EJECUTIVAS
# ---------------------------------------------------------
def _clean_business_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina totales y subtotales técnicos para que las gráficas muestren
    únicamente filas de negocio. Las tablas conservan sus totales.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    chart_df = df.copy().reset_index(drop=True)

    for flag_col in [
        "__is_total__",
        "__is_grand_total__",
        "__is_highlight__",
        "__is_group_summary__",
    ]:
        if flag_col in chart_df.columns:
            chart_df = chart_df[~chart_df[flag_col].fillna(False).astype(bool)].copy()

    return chart_df.reset_index(drop=True)


def _format_currency_hover(value, currency_label: str) -> str:
    return f"{safe_float(value) / 1000:,.0f} K {currency_label}"


def _dynamic_axis_range(values: list[float]) -> tuple[float, float]:
    clean_values = [safe_float(value) for value in values if pd.notna(value)]
    if not clean_values:
        return (-1.0, 1.0)

    min_value = min(clean_values)
    max_value = max(clean_values)

    if min_value == max_value:
        buffer = abs(max_value) * 0.20 if max_value != 0 else 1.0
        return (min_value - buffer, max_value + buffer)

    buffer = (max_value - min_value) * 0.18
    return (min_value - buffer, max_value + buffer)


def _comparison_config(comparison_type: str) -> dict:
    comparison = str(comparison_type or "plan").strip().lower()

    if comparison == "py":
        return {
            "base_col": "PY",
            "var_col": "Var VS PY",
            "pct_col": "%Var VS PY",
            "label": "PY",
        }

    return {
        "base_col": "Plan",
        "var_col": "Var VS Plan",
        "pct_col": "%Var VS Plan",
        "label": "Plan",
    }


def _display_channel_label(value) -> str:
    text = str(value or "").strip()
    return "BARRILITO" if text.upper() == "GOBA" else text


# ---------------------------------------------------------
# GRÁFICA PREMIUM: Heatmap Segment x Region
# ---------------------------------------------------------
def build_segment_region_heatmap_chart(
    df_segment_region: pd.DataFrame,
    title: str,
    comparison_type: str = "plan",
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    """Heatmaps deshabilitados."""
    return None


# ---------------------------------------------------------
# GRÁFICA PREMIUM: Donut contribution Channel
# ---------------------------------------------------------
def build_channel_mix_donut_chart(
    df_channel: pd.DataFrame,
    title: str,
    value_column: str = "Actual",
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    if df_channel is None or df_channel.empty:
        return None

    if "Channel" not in df_channel.columns or value_column not in df_channel.columns:
        return None

    df = _clean_business_rows(df_channel)
    if df.empty:
        return None

    df["__channel_label__"] = df["Channel"].apply(_display_channel_label)
    df["__value__"] = df[value_column].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    )
    df = df[df["__value__"].apply(lambda value: safe_float(value) != 0)].copy()

    if df.empty:
        return None

    currency_label = normalize_currency_mode(currency_mode)
    labels = df["__channel_label__"].astype(str).tolist()
    values = [safe_float(value) / 1000 for value in df["__value__"].tolist()]
    total = sum(values)

    palette = [
        config.COLOR_PRIMARY,
        config.COLOR_SECONDARY,
        "#0B5A7A",
        "#D4A017",
        "#1E9E63",
        "#7C3AED",
        "#64748B",
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.64,
                sort=False,
                direction="clockwise",
                marker=dict(
                    colors=[palette[i % len(palette)] for i in range(len(labels))],
                    line=dict(color="white", width=3),
                ),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    f"{value_column}: %{{value:,.0f}} K {currency_label}<br>"
                    "Participación: %{percent}"
                    "<extra></extra>"
                ),
                pull=[0.035 if i == 0 else 0 for i in range(len(labels))],
            )
        ]
    )

    fig = apply_corporate_layout(fig, title=title, height=510)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.10,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
        ),
        annotations=[
            dict(
                text=f"<b>{total:,.0f}</b><br><span style='font-size:12px'>K {currency_label}</span>",
                x=0.5,
                y=0.5,
                font=dict(size=22, color=config.COLOR_SECONDARY),
                showarrow=False,
            )
        ],
        margin=dict(l=20, r=20, t=82, b=85),
    )

    return fig


# ---------------------------------------------------------
# GRÁFICA PREMIUM: Pareto Ranking Clientes con comparación
# ---------------------------------------------------------
def build_report_4_pareto_chart(
    df_report_4: pd.DataFrame,
    title: str,
    comparison_type: str = "plan",
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    if df_report_4 is None or df_report_4.empty:
        return None

    cfg = _comparison_config(comparison_type)
    required_cols = ["Client Name", "Actual", cfg["base_col"], cfg["var_col"], cfg["pct_col"]]
    if any(col not in df_report_4.columns for col in required_cols):
        return None

    df = _clean_business_rows(df_report_4)
    if df.empty:
        return None

    labels_to_exclude = {"total top 15", "total mexico", "total méxico", "total general"}
    df["__client_name__"] = df["Client Name"].astype(str).str.strip()
    df = df[~df["__client_name__"].str.lower().isin(labels_to_exclude)].copy()

    if df.empty:
        return None

    currency_label = normalize_currency_mode(currency_mode)

    for col in ["Actual", cfg["base_col"], cfg["var_col"], cfg["pct_col"]]:
        df[col] = df[col].apply(safe_float)

    df["__actual_k__"] = df["Actual"].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    ) / 1000
    df["__base_k__"] = df[cfg["base_col"]].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    ) / 1000
    df["__var_k__"] = df[cfg["var_col"]].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    ) / 1000

    # Pareto real: se ordena por Actual para mostrar concentración.
    df = df.sort_values("__actual_k__", ascending=False).reset_index(drop=True)
    total_actual = df["__actual_k__"].sum()
    if total_actual == 0:
        df["__cum_pct__"] = 0.0
    else:
        df["__cum_pct__"] = df["__actual_k__"].cumsum() / total_actual * 100

    x_labels = df["__client_name__"].tolist()
    actual_values = [safe_float(value) for value in df["__actual_k__"].tolist()]
    base_values = [safe_float(value) for value in df["__base_k__"].tolist()]
    cumulative_values = [safe_float(value) for value in df["__cum_pct__"].tolist()]

    customdata = list(
        zip(
            [f"{value:,.0f}" for value in actual_values],
            [f"{value:,.0f}" for value in base_values],
            [f"{value:,.0f}" for value in df["__var_k__"].tolist()],
            [safe_float(value) * 100 for value in df[cfg["pct_col"]].tolist()],
            [f"{value:,.1f}%" for value in cumulative_values],
        )
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=x_labels,
            y=actual_values,
            name="Actual",
            marker=dict(
                color=config.COLOR_PRIMARY,
                line=dict(color="rgba(230, 0, 35, 0.25)", width=1),
            ),
            opacity=0.92,
            customdata=customdata,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Actual: %{customdata[0]} K " + currency_label + "<br>"
                f"{cfg['label']}: %{{customdata[1]}} K {currency_label}<br>"
                f"Var vs {cfg['label']}: %{{customdata[2]}} K {currency_label}<br>"
                f"% Var vs {cfg['label']}: %{{customdata[3]:,.2f}}%<br>"
                "Acumulado Pareto: %{customdata[4]}"
                "<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=base_values,
            name=cfg["label"],
            mode="markers",
            marker=dict(
                size=10,
                color=config.COLOR_SECONDARY if cfg["label"] == "Plan" else "#0B5A7A",
                symbol="diamond",
                line=dict(color="white", width=1.5),
            ),
            hovertemplate=(
                f"<b>%{{x}}</b><br>{cfg['label']}: %{{y:,.0f}} K {currency_label}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=x_labels,
            y=cumulative_values,
            name="Acumulado %",
            mode="lines+markers",
            line=dict(color="#111827", width=3, shape="spline", smoothing=0.7),
            marker=dict(size=7, color="#111827", line=dict(color="white", width=1)),
            hovertemplate="<b>%{x}</b><br>Acumulado: %{y:,.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    fig = apply_corporate_layout(fig, title=title, height=610)
    fig.update_layout(
        barmode="group",
        bargap=0.28,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=40, r=60, t=92, b=120),
    )
    fig.update_xaxes(
        tickangle=-35,
        tickfont=dict(size=10),
        rangeslider=dict(visible=False),
    )
    fig.update_yaxes(
        title_text=f"GSNR · K {currency_label}",
        secondary_y=False,
        rangemode="tozero",
    )
    fig.update_yaxes(
        title_text="Acumulado %",
        secondary_y=True,
        range=[0, 105],
        ticksuffix="%",
        showgrid=False,
    )

    return fig



# ---------------------------------------------------------
# GRÁFICA PREMIUM: Donut interactivo tipo Power BI
# ---------------------------------------------------------
def _prepare_channel_mix_series(
    df_channel: pd.DataFrame,
    value_column: str,
    currency_mode: str,
    exchange_rate: float,
) -> tuple[list[str], list[float], list[str], float]:
    """
    Prepara labels/values/customdata para una dona de participación por channel.
    Devuelve valores en K de la moneda activa.
    """
    if df_channel is None or df_channel.empty:
        return [], [], [], 0.0

    if "Channel" not in df_channel.columns or value_column not in df_channel.columns:
        return [], [], [], 0.0

    df = _clean_business_rows(df_channel)
    if df.empty:
        return [], [], [], 0.0

    df["__channel_label__"] = df["Channel"].apply(_display_channel_label)
    df["__value__"] = df[value_column].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    ) / 1000
    df = df[df["__value__"].apply(lambda value: safe_float(value) != 0)].copy()

    if df.empty:
        return [], [], [], 0.0

    labels = df["__channel_label__"].astype(str).tolist()
    values = [safe_float(value) for value in df["__value__"].tolist()]
    total = sum(values)

    customdata = [f"{value:,.0f}" for value in values]
    return labels, values, customdata, total


def build_channel_mix_donut_interactive_chart(
    df_mtd_channel: pd.DataFrame,
    df_ytd_channel: pd.DataFrame,
    title: str,
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    """
    Dona multinivel con solo 2 botones internos: MTD y YTD.

    Cada vista muestra 3 anillos concéntricos:
    - Anillo interno: Actual
    - Anillo medio: Plan
    - Anillo externo: PY

    Los colores se mantienen por Channel y el hover aclara periodo, métrica,
    canal, valor y participación para evitar confusión visual.
    """
    currency_label = normalize_currency_mode(currency_mode)

    period_sources = {
        "MTD": df_mtd_channel,
        "YTD": df_ytd_channel,
    }

    metric_specs = [
        {
            "metric": "Actual",
            "ring_label": "Anillo interno",
            "hole": 0.44,
            "line_width": 4,
            "opacity": 0.98,
            "show_text": False,
        },
        {
            "metric": "Plan",
            "ring_label": "Anillo medio",
            "hole": 0.62,
            "line_width": 4,
            "opacity": 0.88,
            "show_text": False,
        },
        {
            "metric": "PY",
            "ring_label": "Anillo externo",
            "hole": 0.78,
            "line_width": 4,
            "opacity": 0.78,
            "show_text": True,
        },
    ]

    prepared: dict[str, dict] = {}
    all_labels: list[str] = []

    for period_label, df_source in period_sources.items():
        prepared[period_label] = {"period": period_label, "metrics": {}, "actual_total": 0.0}

        for metric_spec in metric_specs:
            metric_name = metric_spec["metric"]
            labels, values, customdata, total = _prepare_channel_mix_series(
                df_source,
                metric_name,
                currency_mode,
                exchange_rate,
            )

            prepared[period_label]["metrics"][metric_name] = {
                "labels": labels,
                "values": values,
                "customdata": customdata,
                "total": total,
            }

            if metric_name == "Actual":
                prepared[period_label]["actual_total"] = total

            all_labels.extend(labels)

    if not any(
        prepared[period]["metrics"][metric_spec["metric"]]["labels"]
        for period in prepared
        for metric_spec in metric_specs
    ):
        return None

    unique_labels: list[str] = []
    for channel in all_labels:
        if channel not in unique_labels:
            unique_labels.append(channel)

    palette = [
        config.COLOR_PRIMARY,
        config.COLOR_SECONDARY,
        "#0B5A7A",
        "#D4A017",
        "#1E9E63",
        "#7C3AED",
        "#64748B",
    ]
    color_map = {
        label: palette[index % len(palette)]
        for index, label in enumerate(unique_labels)
    }

    first_period = "MTD" if any(
        prepared["MTD"]["metrics"][metric_spec["metric"]]["labels"]
        for metric_spec in metric_specs
    ) else "YTD"

    def _empty_trace(metric_spec: dict, period_label: str):
        # Trace mínimo para conservar los 3 anillos aunque algún periodo/métrica no tenga datos.
        return go.Pie(
            labels=["Sin datos"],
            values=[1],
            hole=metric_spec["hole"],
            sort=False,
            direction="clockwise",
            domain=dict(x=[0.26, 0.96], y=[0.08, 0.92]),
            marker=dict(colors=["#E5E7EB"], line=dict(color="white", width=metric_spec["line_width"])),
            opacity=0.28,
            textinfo="none",
            hovertemplate=(
                f"<b>{period_label} · {metric_spec['metric']}</b><br>"
                "Sin información disponible"
                "<extra></extra>"
            ),
            showlegend=False,
        )

    def _ring_trace(period_label: str, metric_spec: dict, showlegend: bool = False):
        metric_name = metric_spec["metric"]
        metric_data = prepared[period_label]["metrics"][metric_name]

        if not metric_data["labels"]:
            return _empty_trace(metric_spec, period_label)

        labels = metric_data["labels"]
        values = metric_data["values"]
        totals_by_metric = metric_data["total"]
        hovertext = []

        for label, value in zip(labels, values):
            numeric_value = safe_float(value)
            share = 0.0 if totals_by_metric == 0 else (numeric_value / totals_by_metric) * 100
            hovertext.append(
                "<b>" + str(label) + "</b><br>"
                + "Vista seleccionada: <b>" + period_label + "</b><br>"
                + "Anillo: <b>" + metric_spec["ring_label"] + "</b><br>"
                + "Dato del anillo: <b>" + metric_name + "</b><br>"
                + "Valor: <b>" + f"{numeric_value:,.0f}" + " K " + currency_label + "</b><br>"
                + "Participación dentro de " + metric_name + ": <b>" + f"{share:,.2f}%" + "</b>"
            )

        return go.Pie(
            labels=labels,
            values=values,
            hovertext=hovertext,
            hole=metric_spec["hole"],
            sort=False,
            direction="clockwise",
            domain=dict(x=[0.26, 0.96], y=[0.08, 0.92]),
            marker=dict(
                colors=[color_map[label] for label in labels],
                line=dict(color="white", width=metric_spec["line_width"]),
            ),
            opacity=metric_spec["opacity"],
            textinfo="label+percent" if metric_spec["show_text"] else "none",
            textposition="outside" if metric_spec["show_text"] else "none",
            hovertemplate="%{hovertext}<extra></extra>",
            pull=[0.018 if i == 0 else 0 for i in range(len(labels))],
            showlegend=showlegend,
            legendgroup=metric_name,
            name=metric_name,
        )

    def _period_traces(period_label: str):
        # Orden importante:
        # 1) Actual se dibuja primero y deja visible el centro.
        # 2) Plan se encima y deja visible el anillo interno.
        # 3) PY se encima y deja visible los anillos interno y medio.
        return [
            _ring_trace(period_label, metric_specs[0], showlegend=True),
            _ring_trace(period_label, metric_specs[1], showlegend=False),
            _ring_trace(period_label, metric_specs[2], showlegend=False),
        ]

    def _period_annotations(period_label: str):
        actual_total = prepared[period_label]["metrics"]["Actual"]["total"]
        plan_total = prepared[period_label]["metrics"]["Plan"]["total"]
        py_total = prepared[period_label]["metrics"]["PY"]["total"]

        return [
            dict(
                text=(
                    f"<b>{period_label}</b><br>"
                    f"<span style='font-size:12px;color:#667085'>Actual total</span><br>"
                    f"<b>{actual_total:,.0f}</b><br>"
                    f"<span style='font-size:12px'>K {currency_label}</span>"
                ),
                x=0.61,
                y=0.50,
                xref="paper",
                yref="paper",
                font=dict(size=20, color=config.COLOR_SECONDARY),
                align="center",
                showarrow=False,
            ),
            dict(
                text=(
                    "<b>Lectura del anillo</b><br>"
                    "Interno · Actual<br>"
                    "Medio · Plan<br>"
                    "Externo · PY"
                ),
                x=0.03,
                y=0.68,
                xref="paper",
                yref="paper",
                font=dict(size=12, color=config.COLOR_SECONDARY),
                align="left",
                showarrow=False,
                bordercolor="#E7EAF0",
                borderwidth=1,
                borderpad=10,
                bgcolor="#FFFFFF",
            ),
            dict(
                text=(
                    f"Actual: <b>{actual_total:,.0f}</b> K {currency_label}<br>"
                    f"Plan: <b>{plan_total:,.0f}</b> K {currency_label}<br>"
                    f"PY: <b>{py_total:,.0f}</b> K {currency_label}"
                ),
                x=0.03,
                y=0.38,
                xref="paper",
                yref="paper",
                font=dict(size=12, color="#667085"),
                align="left",
                showarrow=False,
            ),
        ]

    fig = go.Figure(data=_period_traces(first_period))

    frames = []
    buttons = []

    for period_label in ["MTD", "YTD"]:
        if not any(
            prepared[period_label]["metrics"][metric_spec["metric"]]["labels"]
            for metric_spec in metric_specs
        ):
            continue

        frames.append(
            go.Frame(
                name=period_label,
                data=_period_traces(period_label),
                layout=go.Layout(annotations=_period_annotations(period_label)),
            )
        )

        buttons.append(
            dict(
                label=period_label,
                method="animate",
                args=[
                    [period_label],
                    {
                        "mode": "immediate",
                        "frame": {"duration": 520, "redraw": True},
                        "transition": {"duration": 420, "easing": "cubic-in-out"},
                    },
                ],
            )
        )

    fig.frames = frames

    fig = apply_corporate_layout(fig, title=title, height=560)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.11,
            xanchor="center",
            x=0.61,
            font=dict(size=12),
            title=dict(text="Channel"),
        ),
        annotations=_period_annotations(first_period),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.03,
                y=0.88,
                xanchor="left",
                yanchor="top",
                showactive=True,
                active=0 if first_period == "MTD" else 1,
                bgcolor="white",
                bordercolor="#E7EAF0",
                borderwidth=1,
                font=dict(size=13, color=config.COLOR_SECONDARY),
                buttons=buttons,
                pad=dict(r=8, t=4, b=4, l=4),
            )
        ],
        margin=dict(l=25, r=30, t=90, b=90),
    )

    return fig


# ---------------------------------------------------------
# GRÁFICA PREMIUM: Heatmap doble Segment x Region
# ---------------------------------------------------------
def _build_segment_region_heatmap_trace(
    df_segment_region: pd.DataFrame,
    comparison_type: str,
    currency_mode: str,
    exchange_rate: float,
):
    cfg = _comparison_config(comparison_type)
    required_cols = ["Segmento", "Región", "Actual", cfg["base_col"], cfg["var_col"], cfg["pct_col"]]
    if df_segment_region is None or df_segment_region.empty:
        return None
    if any(col not in df_segment_region.columns for col in required_cols):
        return None

    df = _clean_business_rows(df_segment_region)
    if df.empty:
        return None

    df["Segmento"] = df["Segmento"].astype(str).str.strip()
    df["Región"] = df["Región"].astype(str).str.strip()
    df = df[(df["Segmento"] != "") & (df["Región"] != "")].copy()
    if df.empty:
        return None

    currency_label = normalize_currency_mode(currency_mode)
    for col in ["Actual", cfg["base_col"], cfg["var_col"], cfg["pct_col"]]:
        df[col] = df[col].apply(safe_float)

    for col in ["Actual", cfg["base_col"], cfg["var_col"]]:
        df[f"__{col}_display__"] = df[col].apply(
            lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
        )

    pivot_pct = df.pivot_table(index="Segmento", columns="Región", values=cfg["pct_col"], aggfunc="sum", fill_value=0)
    if pivot_pct.empty:
        return None

    segment_order = [seg for seg in getattr(config, "REPORT_2_SEGMENT_ORDER", []) if seg in pivot_pct.index]
    segment_extra = [seg for seg in pivot_pct.index.tolist() if seg not in segment_order]
    region_order = [reg for reg in getattr(config, "REPORT_2_REGION_ORDER", []) if reg in pivot_pct.columns]
    region_extra = [reg for reg in pivot_pct.columns.tolist() if reg not in region_order]
    pivot_pct = pivot_pct.loc[segment_order + segment_extra, region_order + region_extra]

    pivot_actual = df.pivot_table(index="Segmento", columns="Región", values="__Actual_display__", aggfunc="sum", fill_value=0).reindex_like(pivot_pct)
    pivot_base = df.pivot_table(index="Segmento", columns="Región", values=f"__{cfg['base_col']}_display__", aggfunc="sum", fill_value=0).reindex_like(pivot_pct)
    pivot_var = df.pivot_table(index="Segmento", columns="Región", values=f"__{cfg['var_col']}_display__", aggfunc="sum", fill_value=0).reindex_like(pivot_pct)

    customdata = []
    for segment in pivot_pct.index:
        row_data = []
        for region in pivot_pct.columns:
            row_data.append([
                f"{pivot_actual.loc[segment, region] / 1000:,.0f}",
                f"{pivot_base.loc[segment, region] / 1000:,.0f}",
                f"{pivot_var.loc[segment, region] / 1000:,.0f}",
                cfg["label"],
                currency_label,
            ])
        customdata.append(row_data)

    z_values = pivot_pct.values.astype(float) * 100
    return {
        "z": z_values,
        "x": pivot_pct.columns.tolist(),
        "y": pivot_pct.index.tolist(),
        "customdata": customdata,
        "label": cfg["label"],
    }


def build_segment_region_heatmap_pair_chart(
    df_segment_region: pd.DataFrame,
    title: str,
    period_label: str,
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    """
    Construye dos mapas lado a lado: vs Plan y vs PY para el mismo periodo.
    """
    left_data = _build_segment_region_heatmap_trace(df_segment_region, "plan", currency_mode, exchange_rate)
    right_data = _build_segment_region_heatmap_trace(df_segment_region, "py", currency_mode, exchange_rate)

    if left_data is None and right_data is None:
        return None

    z_pool = []
    for item in [left_data, right_data]:
        if item is not None:
            z_pool.extend(pd.DataFrame(item["z"]).values.flatten().tolist())
    max_abs = min(100.0, max(25.0, abs(min(z_pool)), abs(max(z_pool)))) if z_pool else 25.0

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(f"{period_label} vs Plan", f"{period_label} vs PY"),
        horizontal_spacing=0.10,
    )

    colorscale = [
        [0.00, "#9F1D1D"],
        [0.35, "#F0A9A1"],
        [0.50, "#F8FAFC"],
        [0.65, "#A9DAB9"],
        [1.00, "#0F8B5F"],
    ]

    for col, item in enumerate([left_data, right_data], start=1):
        if item is None:
            continue
        fig.add_trace(
            go.Heatmap(
                z=pd.DataFrame(item["z"]).clip(lower=-max_abs, upper=max_abs).values,
                x=item["x"],
                y=item["y"],
                customdata=item["customdata"],
                zmid=0,
                zmin=-max_abs,
                zmax=max_abs,
                colorscale=colorscale,
                showscale=(col == 2),
                colorbar=dict(
                    title="% Var",
                    ticksuffix="%",
                    thickness=12,
                    len=0.72,
                    outlinewidth=0,
                ),
                hovertemplate=(
                    "<b>%{y} · %{x}</b><br>"
                    "Actual: %{customdata[0]} K %{customdata[4]}<br>"
                    "%{customdata[3]}: %{customdata[1]} K %{customdata[4]}<br>"
                    "Var: %{customdata[2]} K %{customdata[4]}<br>"
                    "% Var: %{z:.2f}%"
                    "<extra></extra>"
                ),
                xgap=3,
                ygap=3,
            ),
            row=1,
            col=col,
        )

    fig = apply_corporate_layout(fig, title=title, height=445)
    fig.update_layout(
        margin=dict(l=40, r=60, t=90, b=30),
        hovermode="closest",
    )
    fig.update_xaxes(side="top", tickfont=dict(size=11), showgrid=False)
    fig.update_yaxes(tickfont=dict(size=11), showgrid=False, autorange="reversed")

    return fig

# ---------------------------------------------------------
# GRÁFICA 1: Tendencia mensual GSNR
# ---------------------------------------------------------
def build_monthly_gsnr_trend_chart(
    df_processed_sales: pd.DataFrame,
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    if df_processed_sales is None or df_processed_sales.empty:
        return None

    required_cols = [config.COL_YEAR, config.COL_MONTH, config.COL_GSNR]
    if any(col not in df_processed_sales.columns for col in required_cols):
        return None

    df = df_processed_sales.copy()
    df = df.dropna(subset=[config.COL_YEAR, config.COL_MONTH])

    if df.empty:
        return None

    df[config.COL_YEAR] = pd.to_numeric(df[config.COL_YEAR], errors="coerce")
    df[config.COL_MONTH] = pd.to_numeric(df[config.COL_MONTH], errors="coerce")
    df[config.COL_GSNR] = df[config.COL_GSNR].apply(safe_float)

    df = df.dropna(subset=[config.COL_YEAR, config.COL_MONTH])
    df[config.COL_YEAR] = df[config.COL_YEAR].astype(int)
    df[config.COL_MONTH] = df[config.COL_MONTH].astype(int)

    trend_df = (
        df.groupby([config.COL_YEAR, config.COL_MONTH], as_index=False)[config.COL_GSNR]
        .sum()
        .sort_values([config.COL_YEAR, config.COL_MONTH])
    )

    trend_df["Periodo"] = (
        trend_df[config.COL_YEAR].astype(str)
        + "-"
        + trend_df[config.COL_MONTH].astype(str).str.zfill(2)
    )

    trend_df["GSNR K"] = trend_df[config.COL_GSNR].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    ) / 1000

    currency_label = normalize_currency_mode(currency_mode)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_df["Periodo"].tolist(),
            y=trend_df["GSNR K"].astype(float).tolist(),
            mode="lines+markers",
            line=dict(
                color=config.COLOR_PRIMARY,
                width=3,
                shape="spline",
                smoothing=0.8,
            ),
            marker=dict(
                size=8,
                color=config.COLOR_PRIMARY,
                line=dict(color="white", width=2),
            ),
            fill="tozeroy",
            fillcolor="rgba(230, 0, 35, 0.08)",
            name="GSNR",
            hovertemplate=(
                "<b>Periodo:</b> %{x}<br>"
                f"<b>GSNR:</b> %{{y:,.0f}} K {currency_label}"
                "<extra></extra>"
            ),
        )
    )

    fig = apply_corporate_layout(
        fig,
        title=f"Tendencia Mensual de GSNR · K {currency_label}",
        height=430,
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Periodo",
        yaxis_title=f"GSNR · K {currency_label}",
    )

    return fig


# ---------------------------------------------------------
# GRÁFICA 2: Ranking Clientes Top 15 + bloques
# ---------------------------------------------------------
def build_report_4_ranking_chart(
    df_report_4: pd.DataFrame,
    title: str,
    currency_mode: str = "MXN",
    exchange_rate: float = 20.0,
):
    """
    Construye una gráfica de barras horizontales para Reporte 4.

    Corrección importante:
    - Se elimina el uso de px.bar.
    - Se limpian comas/símbolos y se fuerza float real antes del trace.
    - El hover usa exactamente el mismo valor que la longitud de la barra.
    """
    if df_report_4 is None or df_report_4.empty:
        return None

    required_cols = ["Client Name", "Cliente", "Actual"]
    if any(col not in df_report_4.columns for col in required_cols):
        return None

    df = df_report_4.copy().reset_index(drop=True)

    if "__is_grand_total__" in df.columns:
        df = df[~df["__is_grand_total__"].fillna(False).astype(bool)].copy()

    labels_to_exclude = {
        "total top 15",
        "total mexico",
        "total méxico",
        "total general",
    }

    df["__client_name_clean__"] = df["Client Name"].astype(str).str.strip()
    df = df[
        ~df["__client_name_clean__"].str.lower().isin(labels_to_exclude)
    ].copy()

    if df.empty:
        return None

    # Fuerza numérico limpio desde el valor fuente de la tabla.
    df["__actual_numeric__"] = df["Actual"].apply(safe_float).astype(float)
    df["__actual_visual__"] = df["__actual_numeric__"].apply(
        lambda value: convert_value_by_currency(value, currency_mode, exchange_rate)
    ).astype(float)
    df["__actual_k__"] = (df["__actual_visual__"] / 1000).astype(float)

    # Importante: NO eliminamos clientes con valor 0.
    # En MTD puede haber clientes del Top 15 sin venta en el mes,
    # pero deben seguir apareciendo para respetar el ranking fijo de negocio.
    if df.empty:
        return None

    # Conserva el orden ejecutivo original de la tabla.
    chart_df = df[["__client_name_clean__", "Cliente", "__actual_k__"]].copy()
    chart_df["__actual_k__"] = chart_df["__actual_k__"].apply(safe_float).astype(float)

    currency_label = normalize_currency_mode(currency_mode)
    max_value = float(chart_df["__actual_k__"].max())
    axis_max = max_value * 1.18 if max_value > 0 else 1.0

    summary_labels = {"clients 16 to 50", "clients 51 to 100", "other clients"}
    colors = [
        config.COLOR_SECONDARY
        if str(label).strip().lower() in summary_labels
        else config.COLOR_PRIMARY
        for label in chart_df["__client_name_clean__"].tolist()
    ]

    y_values = chart_df["__client_name_clean__"].astype(str).tolist()
    x_values = [float(value) for value in chart_df["__actual_k__"].tolist()]
    codes = chart_df["Cliente"].astype(str).tolist()
    text_values = [f"{value:,.0f}" for value in x_values]

    fig = go.Figure(
        data=[
            go.Bar(
                x=x_values,
                y=y_values,
                orientation="h",
                marker=dict(
                    color=colors,
                    line=dict(color="rgba(31, 42, 68, 0.22)", width=1),
                ),
                width=0.72,
                opacity=0.96,
                text=text_values,
                textposition="outside",
                customdata=list(zip(codes, text_values)),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Código: %{customdata[0]}<br>"
                    f"Actual: %{{customdata[1]}} K {currency_label}"
                    "<extra></extra>"
                ),
            )
        ]
    )

    fig = apply_corporate_layout(fig, title=title, height=720)

    fig.update_layout(
        xaxis_title=f"Ventas netas / GSNR · K {currency_label}",
        yaxis_title="Cliente / bloque",
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, axis_max]),
        bargap=0.26,
        showlegend=False,
        uniformtext_minsize=9,
        uniformtext_mode="show",
    )

    return fig