from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from ui.theme import (
    CREAM,
    OLIVE,
    OLIVE_DARK,
    OLIVE_DEEP,
    PINK,
    SAGE,
    TERRACOTTA,
    TEXT_MUTED,
    WHITE,
)

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}

CHART_PLOT_BG = "rgba(255, 255, 255, 0.55)"
TRACK_COLOR = "rgba(198, 186, 128, 0.28)"
CORNER_RADIUS = 22
CHART_HEIGHT_BAR = 340
CHART_HEIGHT_DONUT = 380

# Paleta principal Calixta (crema, oliva, rosa) + extensiones para más categorías
PALETTE = [OLIVE, PINK, CREAM, TERRACOTTA, SAGE, OLIVE_DARK]

_ORDER_STATE_COLORS = {
    "Recibido": SAGE,
    "Pago Confirmado": TERRACOTTA,
    "Envío Agendado": PINK,
    "Entregado": OLIVE,
}

_CATEGORY_COLORS = {
    "Ropa": OLIVE,
    "Accesorio": PINK,
}


def _palette_color(index: int) -> str:
    return PALETTE[index % len(PALETTE)]


def _state_color(estado: str) -> str:
    return _ORDER_STATE_COLORS.get(estado, _palette_color(0))


def _category_color(categoria: str, index: int) -> str:
    return _CATEGORY_COLORS.get(categoria, _palette_color(index))


def _bar_width(n_bars: int) -> float:
    if n_bars <= 1:
        return 0.24
    if n_bars <= 3:
        return 0.4
    if n_bars <= 6:
        return 0.5
    return 0.58


def _bar_gap(n_bars: int) -> float:
    if n_bars <= 1:
        return 0.78
    if n_bars <= 3:
        return 0.55
    return 0.4


def style_chart(
    fig: go.Figure,
    *,
    height: int = 340,
    chart_type: str = "default",
    margin: dict | None = None,
) -> go.Figure:
    layout: dict = dict(
        plot_bgcolor=CHART_PLOT_BG,
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Plus Jakarta Sans",
        font_color=OLIVE_DEEP,
        height=height,
        autosize=True,
        hoverlabel=dict(
            bgcolor=WHITE,
            bordercolor="rgba(130,143,89,0.25)",
            font=dict(family="Plus Jakarta Sans", size=12, color=OLIVE_DEEP),
        ),
    )
    if margin is not None:
        layout["margin"] = margin
    elif chart_type != "donut":
        layout["margin"] = dict(l=20, r=24, t=28, b=20)

    fig.update_layout(**layout)

    if chart_type == "hbar":
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(198,186,128,0.28)",
            showline=False,
            zeroline=False,
            tickfont=dict(size=11, color=TEXT_MUTED),
        )
        fig.update_yaxes(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickfont=dict(size=12, color=OLIVE_DEEP),
            automargin=True,
        )
    elif chart_type == "category":
        fig.update_xaxes(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickfont=dict(size=12, color=OLIVE_DEEP),
            automargin=True,
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(198,186,128,0.28)",
            showline=False,
            zeroline=False,
            tickfont=dict(size=11, color=TEXT_MUTED),
            tickformat=",.0f",
            automargin=True,
        )
    elif chart_type == "donut":
        pass  # márgenes definidos en _donut_chart

    return fig


def _bar_marker(colors: list[str]) -> dict:
    if len(colors) == 1:
        color = colors[0]
        line_color = OLIVE_DARK if color.upper() == CREAM.upper() else WHITE
        line_width = 1.5 if color.upper() == CREAM.upper() else 0
        return dict(color=color, line=dict(color=line_color, width=line_width), cornerradius=CORNER_RADIUS)
    return dict(color=colors, line=dict(width=0), cornerradius=CORNER_RADIUS)


def _vertical_pill_bars(
    labels: list[str],
    values: list[float],
    *,
    colors: list[str],
    hover_template: str,
    text_template: str,
) -> go.Figure:
    n = len(labels)
    width = _bar_width(n)
    max_val = max(values) * 1.2 if values and max(values) > 0 else 1.0

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=[max_val] * n,
            marker=dict(color=TRACK_COLOR, line=dict(width=0), cornerradius=CORNER_RADIUS),
            hoverinfo="skip",
            showlegend=False,
            width=width,
        )
    )
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            text=values,
            texttemplate=text_template,
            textposition="outside",
            textfont=dict(size=11, color=OLIVE_DEEP),
            marker=_bar_marker(colors),
            hovertemplate=hover_template,
            showlegend=False,
            width=width,
        )
    )

    fig.update_layout(
        barmode="overlay",
        bargap=_bar_gap(n),
        showlegend=False,
        xaxis=dict(type="category"),
    )
    style_chart(fig, height=CHART_HEIGHT_BAR, chart_type="category")
    return fig


def _horizontal_pill_bars(
    labels: list[str],
    values: list[float],
    *,
    colors: list[str],
    hover_template: str,
    text_template: str,
) -> go.Figure:
    n = len(labels)
    width = _bar_width(n)
    max_val = max(values) * 1.22 if values and max(values) > 0 else 1.0

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=labels,
            x=[max_val] * n,
            orientation="h",
            marker=dict(color=TRACK_COLOR, line=dict(width=0), cornerradius=CORNER_RADIUS),
            hoverinfo="skip",
            showlegend=False,
            width=width,
        )
    )
    fig.add_trace(
        go.Bar(
            y=labels,
            x=values,
            orientation="h",
            text=values,
            texttemplate=text_template,
            textposition="outside",
            textfont=dict(size=11, color=OLIVE_DEEP),
            marker=_bar_marker(colors),
            hovertemplate=hover_template,
            showlegend=False,
            width=width,
        )
    )
    fig.update_layout(
        barmode="overlay",
        bargap=_bar_gap(n),
        showlegend=False,
        yaxis=dict(categoryorder="total ascending", automargin=True),
        margin=dict(l=10, r=50, t=28, b=20),
    )
    style_chart(fig, height=CHART_HEIGHT_BAR, chart_type="hbar")
    return fig


def _single_ring_chart(
    value: float,
    name: str,
    subtitle: str,
    color: str,
    *,
    value_format: str = ",.0f",
) -> go.Figure:
    """Anillo limpio para un solo dato — sin leyenda ni etiquetas externas."""
    fig = go.Figure(
        go.Pie(
            values=[1],
            labels=[name],
            hole=0.72,
            marker=dict(colors=[color], line=dict(color=WHITE, width=2)),
            textinfo="none",
            hoverinfo="skip",
            showlegend=False,
            sort=False,
        )
    )
    fig.add_annotation(
        text=(
            f"<span style='font-size:24px;font-weight:700;color:{OLIVE_DEEP}'>"
            f"{value:{value_format}}</span>"
            f"<br><span style='font-size:11px;color:{TEXT_MUTED}'>{subtitle}</span>"
            f"<br><span style='font-size:13px;font-weight:600;color:{color}'>{name}</span>"
        ),
        showarrow=False,
        x=0.5,
        y=0.5,
        font=dict(family="Plus Jakarta Sans"),
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(domain=dict(x=[0.15, 0.85], y=[0.08, 0.92]))
    style_chart(
        fig,
        height=300,
        chart_type="donut",
        margin=dict(t=10, b=10, l=10, r=10),
    )
    return fig


def _donut_chart(
    labels: list[str],
    values: list[float],
    *,
    colors: list[str],
    hover_suffix: str,
    center_label: str,
    value_format: str = ",.0f",
) -> go.Figure:
    n = len(labels)
    total = sum(values)

    if n == 1:
        return _single_ring_chart(
            values[0],
            labels[0],
            center_label,
            colors[0],
            value_format=value_format,
        )

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color=WHITE, width=2)),
            textinfo="percent",
            textposition="inside",
            textfont=dict(size=11, color=WHITE),
            insidetextfont=dict(size=11, color=WHITE),
            pull=[0.02] * n,
            sort=False,
            showlegend=True,
            hovertemplate=(
                f"<b>%{{label}}</b><br>%{{value:{value_format}}}{hover_suffix}"
                "<br>%{{percent}}<extra></extra>"
            ),
        )
    )
    fig.add_annotation(
        text=(
            f"<span style='font-size:18px;font-weight:700;color:{OLIVE_DEEP}'>"
            f"{total:{value_format}}</span>"
            f"<br><span style='font-size:10px;color:{TEXT_MUTED}'>{center_label}</span>"
        ),
        showarrow=False,
        x=0.5,
        y=0.5,
        font=dict(family="Plus Jakarta Sans"),
    )
    fig.update_traces(domain=dict(x=[0.0, 0.72], y=[0.05, 0.95]))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0.78,
            font=dict(size=11, color=OLIVE_DEEP),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
    )
    style_chart(
        fig,
        height=CHART_HEIGHT_DONUT,
        chart_type="donut",
        margin=dict(t=16, b=16, l=8, r=8),
    )
    return fig


def revenue_monthly_chart(monthly: pd.DataFrame) -> go.Figure:
    labels = monthly["mes_label"].tolist()
    values = monthly["subtotal"].tolist()
    colors = [_palette_color(i) for i in range(len(labels))]
    return _vertical_pill_bars(
        labels,
        values,
        colors=colors,
        hover_template="<b>%{x}</b><br>%{y:,.0f} COP<extra></extra>",
        text_template="%{y:,.0f}",
    )


def top_products_chart(top: pd.DataFrame) -> go.Figure:
    labels = top["producto_nombre"].astype(str).tolist()
    values = top["cantidad"].tolist()
    colors = [_palette_color(i) for i in range(len(labels))]
    return _horizontal_pill_bars(
        labels,
        values,
        colors=colors,
        hover_template="<b>%{y}</b><br>%{x} unidades<extra></extra>",
        text_template="%{x}",
    )


def orders_donut_chart(status_counts: pd.DataFrame) -> go.Figure:
    labels = status_counts["estado"].astype(str).tolist()
    values = status_counts["cantidad"].tolist()
    colors = [_state_color(label) for label in labels]
    return _donut_chart(
        labels,
        values,
        colors=colors,
        hover_suffix=" pedidos",
        center_label="pedidos",
    )


def sales_by_category_donut(by_category: pd.DataFrame) -> go.Figure:
    labels = by_category["categoria"].astype(str).tolist()
    values = by_category["subtotal"].tolist()
    colors = [_category_color(label, i) for i, label in enumerate(labels)]
    return _donut_chart(
        labels,
        values,
        colors=colors,
        hover_suffix=" COP",
        center_label="COP",
    )


def accounting_comparison_chart(total_ingresos: float, total_gastos: float) -> go.Figure:
    labels = ["Ingresos", "Gastos"]
    values = [total_ingresos, total_gastos]
    colors = [OLIVE, PINK]
    return _vertical_pill_bars(
        labels,
        values,
        colors=colors,
        hover_template="%{x}: $%{y:,.0f}<extra></extra>",
        text_template="$%{y:,.0f}",
    )


def accounting_by_category_chart(
    by_category: pd.DataFrame,
    label_col: str,
    value_col: str,
) -> go.Figure:
    labels = by_category[label_col].astype(str).tolist()
    values = by_category[value_col].tolist()
    colors = [_palette_color(i) for i in range(len(labels))]
    return _horizontal_pill_bars(
        labels,
        values,
        colors=colors,
        hover_template="%{y}: $%{x:,.0f}<extra></extra>",
        text_template="$%{x:,.0f}",
    )


# Compatibilidad
orders_status_chart = orders_donut_chart
sales_by_category_chart = sales_by_category_donut


__all__ = [
    "PLOTLY_CONFIG",
    "accounting_by_category_chart",
    "accounting_comparison_chart",
    "orders_donut_chart",
    "orders_status_chart",
    "revenue_monthly_chart",
    "sales_by_category_chart",
    "sales_by_category_donut",
    "style_chart",
    "top_products_chart",
]
