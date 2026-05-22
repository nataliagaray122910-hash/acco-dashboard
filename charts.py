# =========================================================
# GRÁFICAS INTERACTIVAS DEL DASHBOARD
# Archivo: charts.py
# =========================================================

import re

import pandas as pd
import plotly.graph_objects as go

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

