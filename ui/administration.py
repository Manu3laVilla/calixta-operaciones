"""Módulo Administración: catálogos configurables."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app_config import CATEGORIES
from services.catalog_service import (
    create_expense_type,
    create_income_type,
    create_order_state,
    create_product_type,
    delete_expense_type,
    delete_income_type,
    delete_order_state,
    delete_product_type,
    update_expense_type,
    update_income_type,
    update_order_state,
    update_product_type,
)
from ui.cached_data import (
    clear_data_cache,
    load_expense_types,
    load_income_types,
    load_order_states,
    load_product_types,
)
from ui.components import calixta_table, clear_search_select, page_header, page_section, search_select


def _refresh_and_rerun() -> None:
    clear_data_cache()
    st.rerun()


def _bool_select(label: str, value: bool, *, key: str) -> bool:
    options = ["Si", "No"]
    index = 0 if value else 1
    return st.selectbox(label, options, index=index, key=key) == "Si"


def _as_bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "si", "sí")


def _catalog_display(df: pd.DataFrame) -> pd.DataFrame:
    display = df.copy()
    display = display.drop(columns=["orden", "fecha_registro"], errors="ignore")
    if "activo" in display.columns:
        display["activo"] = display["activo"].map(lambda v: "Si" if _as_bool(v) else "No")
    return display


def _tab_tipos_producto() -> None:
    st.markdown(
        "Tipos dentro de cada categoría (ej. Camiseta, Pantalón para Ropa; "
        "Totebag, Pañoleta para Accesorios)."
    )

    tab_list, tab_new, tab_edit = st.tabs(["Listado", "Nuevo tipo", "Editar / eliminar"])

    with tab_list:
        types_df = load_product_types()
        if types_df.empty:
            st.info("No hay tipos registrados.")
        else:
            calixta_table(_catalog_display(types_df), key="admin_product_types_list")

    with tab_new:
        with st.form("admin_new_product_type"):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre *")
            categoria = c2.selectbox("Categoría *", CATEGORIES)

            if st.form_submit_button("Guardar tipo", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    try:
                        created = create_product_type(nombre, categoria)
                        st.success(f"Tipo creado: {created['nombre']} ({created['id']})")
                        _refresh_and_rerun()
                    except Exception as exc:
                        st.error(str(exc))

    with tab_edit:
        types_df = load_product_types()
        if types_df.empty:
            st.info("Primero registra tipos de producto.")
            return

        options = {
            f"{row['nombre']} | {row['categoria']} ({row['id']})": row["id"]
            for _, row in types_df.iterrows()
        }
        type_id = search_select(
            "Buscar tipo",
            options,
            key="admin_edit_product_type_sel",
            placeholder="Buscar por nombre, categoría o ID…",
        )
        if type_id is None:
            return

        current = types_df[types_df["id"] == type_id].iloc[0]

        with st.form("admin_edit_product_type"):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre", value=str(current.get("nombre", "")))
            categoria = c2.selectbox(
                "Categoría",
                CATEGORIES,
                index=CATEGORIES.index(current["categoria"])
                if current.get("categoria") in CATEGORIES else 0,
            )
            activo = _bool_select(
                "Activo",
                _as_bool(current.get("activo", True)),
                key="admin_edit_product_type_active",
            )

            c_save, c_delete = st.columns(2)
            save = c_save.form_submit_button("Actualizar", type="primary")
            delete = c_delete.form_submit_button("Eliminar")

        if save:
            try:
                update_product_type(
                    type_id,
                    {"nombre": nombre, "categoria": categoria, "activo": activo},
                )
                st.success("Tipo actualizado.")
                clear_search_select("admin_edit_product_type_sel")
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))

        if delete:
            try:
                delete_product_type(type_id)
                st.success("Tipo eliminado.")
                clear_search_select("admin_edit_product_type_sel")
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_simple_types(
    *,
    title: str,
    load_fn,
    create_fn,
    update_fn,
    delete_fn,
    list_key: str,
    new_form_key: str,
    edit_form_key: str,
    edit_sel_key: str,
) -> None:
    st.markdown(title)

    tab_list, tab_new, tab_edit = st.tabs(["Listado", "Nuevo tipo", "Editar / eliminar"])

    with tab_list:
        types_df = load_fn()
        if types_df.empty:
            st.info("No hay tipos registrados.")
        else:
            calixta_table(_catalog_display(types_df), key=list_key)

    with tab_new:
        with st.form(new_form_key):
            nombre = st.text_input("Nombre *")

            if st.form_submit_button("Guardar tipo", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    try:
                        created = create_fn(nombre)
                        st.success(f"Tipo creado: {created['nombre']} ({created['id']})")
                        _refresh_and_rerun()
                    except Exception as exc:
                        st.error(str(exc))

    with tab_edit:
        types_df = load_fn()
        if types_df.empty:
            st.info("Primero registra tipos.")
            return

        options = {
            f"{row['nombre']} ({row['id']})": row["id"] for _, row in types_df.iterrows()
        }
        type_id = search_select(
            "Buscar tipo",
            options,
            key=edit_sel_key,
            placeholder="Buscar por nombre o ID…",
        )
        if type_id is None:
            return

        current = types_df[types_df["id"] == type_id].iloc[0]

        with st.form(edit_form_key):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre", value=str(current.get("nombre", "")))
            activo = c2.selectbox(
                "Activo",
                ["Si", "No"],
                index=0 if _as_bool(current.get("activo", True)) else 1,
            )

            c_save, c_delete = st.columns(2)
            save = c_save.form_submit_button("Actualizar", type="primary")
            delete = c_delete.form_submit_button("Eliminar")

        if save:
            try:
                update_fn(type_id, {"nombre": nombre, "activo": activo == "Si"})
                st.success("Tipo actualizado.")
                clear_search_select(edit_sel_key)
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))

        if delete:
            try:
                delete_fn(type_id)
                st.success("Tipo eliminado.")
                clear_search_select(edit_sel_key)
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_estados_pedido() -> None:
    st.markdown(
        "Configura el flujo de pedidos. Al crear un pedido se reserva stock. "
        "Marca **Genera venta** en los estados que registran la venta en dinero "
        "(sin descontar stock otra vez). Marca **Revierte venta** en los estados "
        "que anulan una venta ya registrada y devuelven el stock; si no hubo venta, "
        "liberan la reserva."
    )

    tab_list, tab_new, tab_edit = st.tabs(["Listado", "Nuevo estado", "Editar / eliminar"])

    with tab_list:
        states_df = load_order_states()
        if states_df.empty:
            st.info("No hay estados registrados.")
        else:
            display = _catalog_display(states_df)
            for col in ("genera_venta", "revierte_venta", "es_inicial", "bloquea_edicion"):
                if col in display.columns:
                    display[col] = display[col].map(lambda v: "Si" if _as_bool(v) else "No")
            calixta_table(display, key="admin_order_states_list")

    with tab_new:
        with st.form("admin_new_order_state"):
            nombre = st.text_input("Nombre *")

            c1, c2, c3, c4 = st.columns(4)
            genera_venta = c1.checkbox("Genera venta")
            revierte_venta = c2.checkbox("Revierte venta")
            es_inicial = c3.checkbox("Estado inicial")
            bloquea_edicion = c4.checkbox("Bloquea edición")

            if st.form_submit_button("Guardar estado", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    try:
                        created = create_order_state(
                            nombre,
                            genera_venta=genera_venta,
                            revierte_venta=revierte_venta,
                            es_inicial=es_inicial,
                            bloquea_edicion=bloquea_edicion,
                        )
                        st.success(f"Estado creado: {created['nombre']} ({created['id']})")
                        _refresh_and_rerun()
                    except Exception as exc:
                        st.error(str(exc))

    with tab_edit:
        states_df = load_order_states()
        if states_df.empty:
            st.info("Primero registra estados de pedido.")
            return

        options = {
            f"{row['nombre']} ({row['id']})": row["id"] for _, row in states_df.iterrows()
        }
        state_id = search_select(
            "Buscar estado",
            options,
            key="admin_edit_order_state_sel",
            placeholder="Buscar por nombre o ID…",
        )
        if state_id is None:
            return

        current = states_df[states_df["id"] == state_id].iloc[0]

        with st.form("admin_edit_order_state"):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre", value=str(current.get("nombre", "")))
            activo = c2.selectbox(
                "Activo",
                ["Si", "No"],
                index=0 if _as_bool(current.get("activo", True)) else 1,
            )

            c3, c4, c5, c6 = st.columns(4)
            genera_venta = c3.checkbox("Genera venta", value=_as_bool(current.get("genera_venta")))
            revierte_venta = c4.checkbox("Revierte venta", value=_as_bool(current.get("revierte_venta")))
            es_inicial = c5.checkbox("Estado inicial", value=_as_bool(current.get("es_inicial")))
            bloquea_edicion = c6.checkbox(
                "Bloquea edición",
                value=_as_bool(current.get("bloquea_edicion")),
            )

            c_save, c_delete = st.columns(2)
            save = c_save.form_submit_button("Actualizar", type="primary")
            delete = c_delete.form_submit_button("Eliminar")

        if save:
            try:
                update_order_state(
                    state_id,
                    {
                        "nombre": nombre,
                        "genera_venta": genera_venta,
                        "revierte_venta": revierte_venta,
                        "es_inicial": es_inicial,
                        "bloquea_edicion": bloquea_edicion,
                        "activo": activo == "Si",
                    },
                )
                st.success("Estado actualizado.")
                clear_search_select("admin_edit_order_state_sel")
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))

        if delete:
            try:
                delete_order_state(state_id)
                st.success("Estado eliminado.")
                clear_search_select("admin_edit_order_state_sel")
                _refresh_and_rerun()
            except Exception as exc:
                st.error(str(exc))


def page_administracion() -> None:
    page_header("Administración", "Catálogos y configuración del flujo operativo")

    with page_section():
        tab_productos, tab_ingresos, tab_gastos, tab_estados = st.tabs(
            ["Tipos de producto", "Tipos de ingreso", "Tipos de gasto", "Estados de pedido"]
        )

        with tab_productos:
            _tab_tipos_producto()
        with tab_ingresos:
            _tab_simple_types(
                title="Tipos de ingreso usados en contabilidad (Capital, Inversión, etc.).",
                load_fn=load_income_types,
                create_fn=create_income_type,
                update_fn=update_income_type,
                delete_fn=delete_income_type,
                list_key="admin_income_types_list",
                new_form_key="admin_new_income_type",
                edit_form_key="admin_edit_income_type",
                edit_sel_key="admin_edit_income_type_sel",
            )
        with tab_gastos:
            _tab_simple_types(
                title="Tipos de gasto usados en contabilidad (Insumos, Equipos, etc.).",
                load_fn=load_expense_types,
                create_fn=create_expense_type,
                update_fn=update_expense_type,
                delete_fn=delete_expense_type,
                list_key="admin_expense_types_list",
                new_form_key="admin_new_expense_type",
                edit_form_key="admin_edit_expense_type",
                edit_sel_key="admin_edit_expense_type_sel",
            )
        with tab_estados:
            _tab_estados_pedido()
