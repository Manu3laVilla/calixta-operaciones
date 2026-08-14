"""Generación de reportes PDF con identidad Calixta."""

from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ui.styles import format_cop
from ui.theme import CREAM, LOGO_PATH, OLIVE, TEXT, TEXT_MUTED
from utils.settings import BASE_DIR

LOGO_RATIO = 176 / 246
WATERMARK_WIDTH = 4.2 * inch
WATERMARK_ALPHA = 0.17
_LOGO_FILE = BASE_DIR / LOGO_PATH


def _hex(hex_color: str) -> colors.Color:
    return colors.HexColor(hex_color)


def _escape(text: Any) -> str:
    value = str(text if text is not None else "")
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


_DDMMYYYY = re.compile(r"^\d{2}/\d{2}/\d{4}$")
_DDMMYYYY_TIME = re.compile(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$")


def _format_date(value: Any, *, with_time: bool = True) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if with_time and _DDMMYYYY_TIME.match(text):
        return text
    if not with_time and _DDMMYYYY.match(text):
        return text
    parsed = pd.to_datetime(value, errors="coerce", utc=True, dayfirst=True)
    if pd.isna(parsed):
        return text[:16]
    if getattr(parsed, "tzinfo", None) is not None:
        try:
            parsed = parsed.tz_convert("America/Bogota")
        except Exception:
            pass
    if with_time:
        return parsed.strftime("%d/%m/%Y %H:%M")
    return parsed.strftime("%d/%m/%Y")


def _apply_pdf_formats(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in out.columns:
        name = str(col).lower()
        if name == "fecha":
            out[col] = out[col].apply(lambda v: _format_date(v, with_time=False))
        elif "fecha" in name or name == "enviado_en":
            out[col] = out[col].apply(lambda v: _format_date(v, with_time=True))
    return out


def _dataframe_table(df: pd.DataFrame, *, headers: list[str] | None = None) -> tuple[list[str], list[list[str]]]:
    if df.empty:
        return headers or [], []
    display = _apply_pdf_formats(df.copy())
    table_headers = headers or [str(col) for col in display.columns]
    columns = list(display.columns)
    rows = [
        [_escape(row.get(col, "")) for col in columns]
        for _, row in display.iterrows()
    ]
    return table_headers, rows


def _watermark_image() -> ImageReader | None:
    if not _LOGO_FILE.exists():
        return None
    try:
        from PIL import Image as PILImage

        image = PILImage.open(_LOGO_FILE).convert("RGBA")
        red, green, blue, alpha = image.split()
        alpha = alpha.point(lambda px: int(px * WATERMARK_ALPHA))
        faded = PILImage.merge("RGBA", (red, green, blue, alpha))
        buffer = BytesIO()
        faded.save(buffer, format="PNG")
        buffer.seek(0)
        return ImageReader(buffer)
    except Exception:
        return ImageReader(str(_LOGO_FILE))


def _draw_logo_watermark(canvas, doc) -> None:
    """Marca de agua centrada detrás del contenido en cada página."""
    watermark = _watermark_image()
    if watermark is None:
        return

    page_width, page_height = letter
    logo_width = WATERMARK_WIDTH
    logo_height = logo_width * LOGO_RATIO
    x = (page_width - logo_width) / 2
    y = (page_height - logo_height) / 2

    canvas.saveState()
    canvas.drawImage(
        watermark,
        x,
        y,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask="auto",
    )
    canvas.restoreState()


class _CalixtaDocTemplate(SimpleDocTemplate):
    def beforePage(self) -> None:
        _draw_logo_watermark(self.canv, self)


def build_pdf(
    *,
    title: str,
    subtitle: str = "",
    filters: list[str] | None = None,
    sections: list[dict[str, Any]],
) -> bytes:
    buffer = BytesIO()
    doc = _CalixtaDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CalixtaTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=_hex(OLIVE),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "CalixtaSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=_hex(TEXT),
        spaceAfter=2,
    )
    meta_style = ParagraphStyle(
        "CalixtaMeta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=_hex(TEXT_MUTED),
        spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "CalixtaSection",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=_hex(OLIVE),
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "CalixtaBody",
        parent=styles["Normal"],
        fontSize=9,
        textColor=_hex(TEXT),
        alignment=TA_LEFT,
    )

    story: list[Any] = []

    story.append(Paragraph(_escape(title), title_style))
    if subtitle:
        story.append(Paragraph(_escape(subtitle), subtitle_style))
    story.append(
        Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            meta_style,
        )
    )

    if filters:
        filter_lines = "<br/>".join(f"• {_escape(line)}" for line in filters if line)
        story.append(Paragraph(f"<b>Filtros aplicados</b><br/>{filter_lines}", body_style))
        story.append(Spacer(1, 0.08 * inch))

    for section in sections:
        kind = section.get("type")
        if kind == "heading":
            story.append(Paragraph(_escape(section.get("text", "")), section_style))
        elif kind == "text":
            story.append(Paragraph(_escape(section.get("text", "")), body_style))
            story.append(Spacer(1, 0.05 * inch))
        elif kind == "stats":
            items = section.get("items", [])
            if items:
                table_data = [[Paragraph(f"<b>{_escape(label)}</b>", body_style), _escape(value)] for label, value in items]
                table = Table(table_data, colWidths=[2.4 * inch, 4.0 * inch])
                table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), _hex(CREAM)),
                        ("BOX", (0, 0), (-1, -1), 0.5, _hex(OLIVE)),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, _hex(OLIVE)),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ])
                )
                story.append(table)
                story.append(Spacer(1, 0.1 * inch))
        elif kind == "table":
            headers = section.get("headers", [])
            rows = section.get("rows", [])
            if not rows:
                story.append(Paragraph("Sin datos para mostrar.", body_style))
                story.append(Spacer(1, 0.08 * inch))
                continue
            wrap_cols = set(section.get("wrap_cols", []))
            table_rows: list[list[Any]] = [headers]
            for row in rows:
                formatted_row: list[Any] = []
                for idx, cell in enumerate(row):
                    if idx in wrap_cols and cell:
                        formatted_row.append(Paragraph(str(cell), body_style))
                    else:
                        formatted_row.append(cell)
                table_rows.append(formatted_row)
            table_data = table_rows
            col_count = len(headers)
            width = 7.0 * inch
            custom_widths = section.get("col_widths")
            if custom_widths:
                col_widths = [float(w) * inch for w in custom_widths]
            else:
                col_widths = [width / max(col_count, 1)] * col_count
            table = Table(
                table_data,
                colWidths=col_widths,
                repeatRows=1,
            )
            table.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), _hex(OLIVE)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _hex(CREAM)]),
                    ("BOX", (0, 0), (-1, -1), 0.5, _hex(OLIVE)),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, _hex(OLIVE)),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ])
            )
            story.append(table)
            story.append(Spacer(1, 0.12 * inch))

    story.append(Spacer(1, 0.15 * inch))
    story.append(
        Paragraph(
            "Calixta Centro de Operaciones",
            ParagraphStyle(
                "CalixtaFooter",
                parent=styles["Normal"],
                fontSize=8,
                textColor=_hex(TEXT_MUTED),
            ),
        )
    )
    doc.build(story)
    return buffer.getvalue()


def report_alerts_stock(alerts: pd.DataFrame) -> bytes:
    display = alerts.copy()
    if not display.empty:
        for col in ("precio",):
            if col in display.columns:
                display[col] = display[col].apply(lambda v: format_cop(float(v)) if pd.notna(v) else "")
    headers, rows = _dataframe_table(
        display[
            [c for c in ["referencia", "nombre", "talla", "color", "stock", "stock_minimo", "faltante", "precio"] if c in display.columns]
        ],
        headers=["Referencia", "Nombre", "Talla", "Color", "Stock", "Mínimo", "Faltante", "Precio"],
    )
    return build_pdf(
        title="Reporte de alertas de stock",
        subtitle="Productos con stock en o por debajo del mínimo.",
        sections=[
            {
                "type": "stats",
                "items": [("Productos en alerta", str(len(alerts)))],
            },
            {"type": "heading", "text": "Detalle de inventario crítico"},
            {"type": "table", "headers": headers, "rows": rows},
        ],
    )


def report_inventory(products: pd.DataFrame) -> bytes:
    display = products.copy()
    if not display.empty and "precio" in display.columns:
        display["precio"] = display["precio"].apply(lambda v: format_cop(float(v)) if pd.notna(v) else "")
    columns = [
        c
        for c in ["referencia", "nombre", "categoria", "talla", "color", "stock", "stock_minimo", "precio", "activo"]
        if c in display.columns
    ]
    headers, rows = _dataframe_table(
        display[columns],
        headers=["Referencia", "Nombre", "Categoría", "Talla", "Color", "Stock", "Mínimo", "Precio", "Activo"],
    )
    return build_pdf(
        title="Reporte de inventario",
        subtitle="Snapshot del inventario visible en pantalla.",
        sections=[
            {"type": "stats", "items": [("Total productos", str(len(products)))]},
            {"type": "heading", "text": "Listado de productos"},
            {"type": "table", "headers": headers, "rows": rows},
        ],
    )


def report_orders(orders: pd.DataFrame) -> bytes:
    display = orders.drop(columns=["items_json"], errors="ignore").copy()
    if not display.empty:
        if "total" in display.columns:
            display["total"] = display["total"].apply(
                lambda v: format_cop(float(v)) if pd.notna(v) else ""
            )
        if "fecha_creacion" in display.columns:
            display["fecha_creacion"] = display["fecha_creacion"].apply(
                lambda v: _format_date(v, with_time=True)
            )
    columns = [
        c
        for c in ["id", "cliente_nombre", "estado", "total", "fecha_creacion", "direccion_entrega"]
        if c in display.columns
    ]
    headers, rows = _dataframe_table(
        display[columns],
        headers=["Pedido", "Cliente", "Estado", "Total", "Fecha", "Dirección"],
    )
    return build_pdf(
        title="Reporte de pedidos",
        subtitle="Estado actual de los pedidos registrados.",
        sections=[
            {"type": "stats", "items": [("Total pedidos", str(len(orders)))]},
            {"type": "heading", "text": "Listado de pedidos"},
            {
                "type": "table",
                "headers": headers,
                "rows": rows,
                "col_widths": [0.9, 0.95, 0.75, 0.75, 1.05, 2.6],
                "wrap_cols": [5],
            },
        ],
    )


def report_sales(filtered: pd.DataFrame, *, filters: list[str], total: float) -> bytes:
    display = filtered.copy()
    if not display.empty:
        if "precio_unitario" in display.columns:
            display["precio_unitario"] = display["precio_unitario"].apply(
                lambda v: format_cop(float(v)) if pd.notna(v) else ""
            )
        if "subtotal" in display.columns:
            display["subtotal"] = display["subtotal"].apply(
                lambda v: format_cop(float(v)) if pd.notna(v) else ""
            )
    columns = [
        c
        for c in ["fecha_entrega", "pedido_id", "cliente_nombre", "producto_nombre", "cantidad", "precio_unitario", "subtotal"]
        if c in display.columns
    ]
    headers, rows = _dataframe_table(
        display[columns],
        headers=["Fecha", "Pedido", "Cliente", "Producto", "Cant.", "Precio unit.", "Subtotal"],
    )
    return build_pdf(
        title="Reporte de ventas",
        subtitle="Ventas generadas al entregar pedidos.",
        filters=filters,
        sections=[
            {
                "type": "stats",
                "items": [
                    ("Registros", str(len(filtered))),
                    ("Total filtrado", format_cop(total)),
                ],
            },
            {"type": "heading", "text": "Detalle de ventas"},
            {"type": "table", "headers": headers, "rows": rows},
        ],
    )


def report_accounting_summary(
    movements: pd.DataFrame,
    *,
    filters: list[str],
    total_ingresos: float,
    total_gastos: float,
    balance: float,
    category_summary: pd.DataFrame,
) -> bytes:
    summary_display = category_summary.copy()
    if not summary_display.empty and "monto" in summary_display.columns:
        summary_display["monto"] = summary_display["monto"].apply(
            lambda v: format_cop(float(v)) if pd.notna(v) else ""
        )
    headers, rows = _dataframe_table(
        summary_display,
        headers=["Tipo", "Categoría", "Monto"],
    )
    return build_pdf(
        title="Reporte contable — Resumen",
        subtitle="Capital, inversiones y gastos del negocio.",
        filters=filters,
        sections=[
            {
                "type": "stats",
                "items": [
                    ("Total ingresos", format_cop(total_ingresos)),
                    ("Total gastos", format_cop(total_gastos)),
                    ("Balance", format_cop(balance)),
                ],
            },
            {"type": "heading", "text": "Totales por categoría"},
            {"type": "table", "headers": headers, "rows": rows},
        ],
    )


def report_accounting_movements(movements: pd.DataFrame, *, filters: list[str]) -> bytes:
    display = movements.copy()
    if not display.empty and "monto" in display.columns:
        display["monto"] = display["monto"].apply(lambda v: format_cop(float(v)) if pd.notna(v) else "")
    columns = [c for c in ["fecha", "tipo", "categoria", "concepto", "monto", "notas"] if c in display.columns]
    headers, rows = _dataframe_table(
        display[columns],
        headers=["Fecha", "Tipo", "Categoría", "Concepto", "Monto", "Notas"],
    )
    return build_pdf(
        title="Reporte contable — Movimientos",
        subtitle="Historial de ingresos y gastos.",
        filters=filters,
        sections=[
            {"type": "stats", "items": [("Movimientos", str(len(movements)))]},
            {"type": "heading", "text": "Detalle de movimientos"},
            {"type": "table", "headers": headers, "rows": rows},
        ],
    )


def report_dashboard(
    *,
    filters: list[str],
    total_revenue: float,
    units_sold: int,
    orders_count: int,
    pending_orders: int,
    delivered: int,
    alerts_count: int,
    recent_orders: pd.DataFrame,
    alerts: pd.DataFrame,
) -> bytes:
    recent = recent_orders.copy()
    if not recent.empty and "total" in recent.columns:
        recent["total"] = recent["total"].apply(lambda v: format_cop(float(v)) if pd.notna(v) else "")
    order_headers, order_rows = _dataframe_table(
        recent[[c for c in ["id", "cliente_nombre", "estado", "total"] if c in recent.columns]],
        headers=["Pedido", "Cliente", "Estado", "Total"],
    )

    alert_display = alerts.copy()
    if not alert_display.empty and "precio" in alert_display.columns:
        alert_display["precio"] = alert_display["precio"].apply(
            lambda v: format_cop(float(v)) if pd.notna(v) else ""
        )
    alert_headers, alert_rows = _dataframe_table(
        alert_display[
            [c for c in ["referencia", "nombre", "stock", "stock_minimo"] if c in alert_display.columns]
        ],
        headers=["Referencia", "Nombre", "Stock", "Mínimo"],
    )

    sections: list[dict[str, Any]] = [
        {
            "type": "stats",
            "items": [
                ("Ingresos del período", format_cop(total_revenue)),
                ("Unidades vendidas", str(units_sold)),
                ("Pedidos", f"{orders_count} ({pending_orders} activos · {delivered} entregados)"),
                ("Alertas de stock", str(alerts_count)),
            ],
        },
        {"type": "heading", "text": "Últimos pedidos del período"},
        {"type": "table", "headers": order_headers, "rows": order_rows},
    ]
    if alerts_count:
        sections.extend([
            {"type": "heading", "text": "Productos con stock bajo"},
            {"type": "table", "headers": alert_headers, "rows": alert_rows},
        ])

    return build_pdf(
        title="Reporte operativo",
        subtitle="Resumen del dashboard con los filtros actuales.",
        filters=filters,
        sections=sections,
    )
