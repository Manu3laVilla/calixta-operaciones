"""Pantalla de contabilidad interna (capital, inversiones y gastos)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from config import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    MOVEMENT_TYPE_EXPENSE,
    MOVEMENT_TYPE_INCOME,
    MOVEMENT_TYPES,
)
from services.accounting_service import (
    create_movement,
    filter_movements,
    get_movement,
    movement_label,
    summary_by_category,
    summary_totals,
    update_movement,
)
from ui.cached_data import load_movements
from ui.charts import (
    PLOTLY_CONFIG,
    accounting_by_category_chart,
    accounting_comparison_chart,
)
from ui.components import page_header, page_section, panel_card, stat_chips
from ui.styles import format_cop


def _refresh_and_rerun() -> None:
    from ui.cached_data import clear_data_cache

    clear_data_cache()
    st.rerun()


def _date_range_defaults(movements: pd.DataFrame) -> tuple[date, date]:
    today = date.today()
    if movements.empty or "fecha" not in movements.columns:
        return today.replace(day=1), today

    dates = pd.to_datetime(movements["fecha"], errors="coerce").dropna()
    if dates.empty:
        return today.replace(day=1), today
    return dates.min().date(), dates.max().date()


def _render_summary_filters(
    movements: pd.DataFrame,
) -> tuple[bool, date | None, date | None]:
    default_desde, default_hasta = _date_range_defaults(movements)
    with panel_card("Filtros", accent="sage"):
        apply_filters = st.checkbox("Aplicar filtros", value=False, key="acc_summary_apply_filters")
        c1, c2 = st.columns(2)
        fecha_desde = c1.date_input(
            "Desde",
            value=default_desde,
            disabled=not apply_filters,
            key="acc_summary_desde",
        )
        fecha_hasta = c2.date_input(
            "Hasta",
            value=default_hasta,
            disabled=not apply_filters,
            key="acc_summary_hasta",
        )
    if not apply_filters:
        return False, None, None
    return True, fecha_desde, fecha_hasta


def _tab_resumen() -> None:
    movements_all = load_movements()
    _, fecha_desde, fecha_hasta = _render_summary_filters(movements_all)

    movements = filter_movements(
        movements_all,
        fecha_desde=str(fecha_desde) if fecha_desde else None,
        fecha_hasta=str(fecha_hasta) if fecha_hasta else None,
    )

    total_ingresos, total_gastos, balance = summary_totals(movements)
    stat_chips([
        ("Total ingresos", format_cop(total_ingresos), "capital e inversiones", "terra"),
        ("Total gastos", format_cop(total_gastos), "sobre esos ingresos", "pink"),
        ("Balance contable", format_cop(balance), "ingresos − gastos", "olive"),
    ])

    with panel_card("Por categoría", accent="cream"):
        summary = summary_by_category(movements)
        if summary.empty:
            st.info("Aún no hay movimientos registrados.")
        else:
            display = summary.copy()
            display["monto"] = display["monto"].apply(format_cop)
            display.columns = ["Tipo", "Categoría", "Monto"]
            st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown('<p class="dashboard-section-title">Resumen visual</p>', unsafe_allow_html=True)

    row_top, row_bottom = st.columns([1.35, 1], gap="medium")

    with row_top:
        with panel_card("Ingresos vs gastos", accent="terra"):
            if movements.empty:
                st.markdown(
                    '<p class="chart-empty-msg">Aún no hay movimientos registrados.</p>',
                    unsafe_allow_html=True,
                )
            else:
                fig = accounting_comparison_chart(total_ingresos, total_gastos)
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with row_bottom:
        col_income, col_expense = st.columns(2, gap="small")
        with col_income:
            with panel_card("Ingresos por categoría", accent="olive"):
                income = movements[movements["tipo"] == MOVEMENT_TYPE_INCOME] if not movements.empty else movements
                if income.empty:
                    st.markdown(
                        '<p class="chart-empty-msg">Sin ingresos registrados.</p>',
                        unsafe_allow_html=True,
                    )
                else:
                    by_cat = income.groupby("categoria", as_index=False)["monto"].sum()
                    fig = accounting_by_category_chart(by_cat, "categoria", "monto")
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

        with col_expense:
            with panel_card("Gastos por categoría", accent="pink"):
                expense = movements[movements["tipo"] == MOVEMENT_TYPE_EXPENSE] if not movements.empty else movements
                if expense.empty:
                    st.markdown(
                        '<p class="chart-empty-msg">Sin gastos registrados.</p>',
                        unsafe_allow_html=True,
                    )
                else:
                    by_cat = expense.groupby("categoria", as_index=False)["monto"].sum()
                    fig = accounting_by_category_chart(by_cat, "categoria", "monto")
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


def _movement_form(
    *,
    form_key: str,
    submit_label: str,
    movement_tipo: str,
    category_label: str,
) -> None:
    categories = INCOME_CATEGORIES if movement_tipo == MOVEMENT_TYPE_INCOME else EXPENSE_CATEGORIES
    with st.form(form_key, clear_on_submit=True):
        c1, c2 = st.columns(2)
        fecha = c1.date_input("Fecha del movimiento *", value=date.today())
        categoria = c2.selectbox(f"{category_label} *", categories)

        concepto = st.text_input(
            "Concepto *",
            placeholder="Ej: Aporte de socios, compra de insumos, equipo nuevo...",
        )
        monto = st.number_input("Monto (COP) *", min_value=0.0, step=1000.0, format="%.0f")
        notas = st.text_area("Notas", placeholder="Detalles adicionales (opcional)")

        submitted = st.form_submit_button(submit_label, type="primary")
        if submitted:
            if not concepto.strip():
                st.error("El concepto es obligatorio.")
                return
            try:
                create_movement(
                    tipo=movement_tipo,
                    categoria=categoria,
                    concepto=concepto,
                    monto=float(monto),
                    fecha=str(fecha),
                    notas=notas,
                )
                st.success("Movimiento registrado correctamente.")
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_nuevo_ingreso() -> None:
    _movement_form(
        form_key="new_income_form",
        submit_label="Registrar ingreso",
        movement_tipo=MOVEMENT_TYPE_INCOME,
        category_label="Tipo de ingreso",
    )


def _tab_nuevo_gasto() -> None:
    _movement_form(
        form_key="new_expense_form",
        submit_label="Registrar gasto",
        movement_tipo=MOVEMENT_TYPE_EXPENSE,
        category_label="Tipo de gasto",
    )


def _tab_editar_movimiento() -> None:
    movements = load_movements()
    if movements.empty:
        st.info("No hay movimientos para editar.")
        return

    options = {movement_label(row.to_dict()): row["id"] for _, row in movements.iterrows()}
    selected = st.selectbox("Selecciona movimiento", list(options.keys()), key="acc_edit_select")
    movement_id = options[selected]
    current = get_movement(movement_id)
    if current is None:
        st.error("No se encontró el movimiento seleccionado.")
        return

    with st.form("edit_movement_form"):
        c1, c2 = st.columns(2)
        tipo = c1.selectbox(
            "Tipo de movimiento *",
            MOVEMENT_TYPES,
            index=MOVEMENT_TYPES.index(str(current.get("tipo", MOVEMENT_TYPE_INCOME))),
        )
        cat_options = INCOME_CATEGORIES if tipo == MOVEMENT_TYPE_INCOME else EXPENSE_CATEGORIES
        current_cat = str(current.get("categoria", cat_options[0]))
        categoria = c2.selectbox(
            "Categoría *",
            cat_options,
            index=cat_options.index(current_cat) if current_cat in cat_options else 0,
        )

        c3, c4 = st.columns(2)
        fecha_raw = str(current.get("fecha", date.today()))
        try:
            fecha_default = date.fromisoformat(fecha_raw[:10])
        except ValueError:
            fecha_default = date.today()
        fecha = c3.date_input("Fecha del movimiento *", value=fecha_default)
        monto = c4.number_input(
            "Monto (COP) *",
            min_value=0.0,
            step=1000.0,
            format="%.0f",
            value=float(current.get("monto", 0) or 0),
        )

        concepto = st.text_input("Concepto *", value=str(current.get("concepto", "")))
        notas = st.text_area("Notas", value=str(current.get("notas", "")))

        if st.form_submit_button("Actualizar movimiento", type="primary"):
            if not concepto.strip():
                st.error("El concepto es obligatorio.")
                return
            try:
                update_movement(
                    movement_id,
                    {
                        "tipo": tipo,
                        "categoria": categoria,
                        "fecha": str(fecha),
                        "concepto": concepto,
                        "monto": float(monto),
                        "notas": notas,
                    },
                )
                st.success("Movimiento actualizado.")
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_movimientos() -> None:
    movements_all = load_movements()
    default_desde, default_hasta = _date_range_defaults(movements_all)

    with panel_card("Filtros", accent="sage"):
        c1, c2, c3 = st.columns(3)
        tipo_filter = c1.selectbox("Tipo de movimiento", ["Todos"] + MOVEMENT_TYPES, key="acc_list_tipo")
        fecha_desde = c2.date_input("Desde", value=default_desde, key="acc_list_desde")
        fecha_hasta = c3.date_input("Hasta", value=default_hasta, key="acc_list_hasta")

    movements = filter_movements(
        movements_all,
        tipo=None if tipo_filter == "Todos" else tipo_filter,
        fecha_desde=str(fecha_desde),
        fecha_hasta=str(fecha_hasta),
    )

    with panel_card("Historial de movimientos", accent="cream"):
        if movements.empty:
            st.info("No hay movimientos en el período seleccionado.")
            return

        display = movements.copy()
        display["monto"] = display["monto"].apply(format_cop)
        columns = ["id", "fecha", "tipo", "categoria", "concepto", "monto", "notas"]
        display = display[[c for c in columns if c in display.columns]]
        display.columns = ["ID", "Fecha", "Tipo", "Categoría", "Concepto", "Monto", "Notas"]
        st.dataframe(display, use_container_width=True, hide_index=True)


def page_contabilidad() -> None:
    page_header(
        "Contabilidad",
        "Capital, inversiones y gastos del negocio (aparte de las ventas).",
    )

    with page_section():
        (
            tab_resumen,
            tab_ingreso,
            tab_gasto,
            tab_editar,
            tab_movimientos,
        ) = st.tabs([
            "Resumen",
            "Nuevo ingreso",
            "Nuevo gasto",
            "Editar movimiento",
            "Movimientos",
        ])

        with tab_resumen:
            _tab_resumen()
        with tab_ingreso:
            _tab_nuevo_ingreso()
        with tab_gasto:
            _tab_nuevo_gasto()
        with tab_editar:
            _tab_editar_movimiento()
        with tab_movimientos:
            _tab_movimientos()
