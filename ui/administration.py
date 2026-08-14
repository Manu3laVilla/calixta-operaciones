"""Módulo Administración: catálogos configurables."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app_config import CATEGORIES
from services.alert_config_service import (
    create_alert_recipient,
    delete_alert_recipient,
    format_config_summary,
    list_alert_send_logs,
    save_alert_email_config,
    time_input_defaults,
    update_alert_recipient,
)
from services.alert_scheduler import run_scheduled_alert_job
from services.alert_service import get_low_stock_alerts, notify_low_stock_by_email
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
from services.email_service import alert_recipient, is_email_configured
from ui.cached_data import (
    clear_data_cache,
    load_alert_email_config,
    load_alert_recipients,
    load_alert_send_logs,
    load_expense_types,
    load_income_types,
    load_order_states,
    load_product_types,
)
from ui.components import calixta_table, clear_search_select, page_header, page_section, search_select


def _refresh_and_rerun() -> None:
    clear_data_cache()
    st.rerun()


def _show_flash(flash_key: str) -> None:
    if flash := st.session_state.pop(flash_key, None):
        st.success(flash)


def _apply_pending_reset(reset_flag_key: str, **fields: object) -> None:
    if st.session_state.pop(reset_flag_key, False):
        for key, value in fields.items():
            st.session_state[key] = value


def _schedule_reset(reset_flag_key: str) -> None:
    st.session_state[reset_flag_key] = True


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
        flash_key = "admin_new_product_type_flash"
        reset_key = "admin_new_product_type_reset"
        nombre_key = "admin_new_product_type_nombre"
        categoria_key = "admin_new_product_type_categoria"
        _apply_pending_reset(reset_key, **{nombre_key: "", categoria_key: CATEGORIES[0]})
        _show_flash(flash_key)

        with st.form("admin_new_product_type", enter_to_submit=False):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre *", key=nombre_key)
            categoria = c2.selectbox("Categoría *", CATEGORIES, key=categoria_key)

            if st.form_submit_button("Guardar tipo", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    try:
                        created = create_product_type(nombre, categoria)
                        st.session_state[flash_key] = (
                            f"Tipo creado: {created['nombre']} ({created['id']})"
                        )
                        _schedule_reset(reset_key)
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
        flash_key = f"{new_form_key}_flash"
        reset_key = f"{new_form_key}_reset"
        nombre_key = f"{new_form_key}_nombre"
        _apply_pending_reset(reset_key, **{nombre_key: ""})
        _show_flash(flash_key)

        with st.form(new_form_key, enter_to_submit=False):
            nombre = st.text_input("Nombre *", key=nombre_key)

            if st.form_submit_button("Guardar tipo", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    try:
                        created = create_fn(nombre)
                        st.session_state[flash_key] = (
                            f"Tipo creado: {created['nombre']} ({created['id']})"
                        )
                        _schedule_reset(reset_key)
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
        flash_key = "admin_new_order_state_flash"
        reset_key = "admin_new_order_state_reset"
        nombre_key = "admin_new_order_state_nombre"
        genera_key = "admin_new_order_state_genera"
        revierte_key = "admin_new_order_state_revierte"
        inicial_key = "admin_new_order_state_inicial"
        bloquea_key = "admin_new_order_state_bloquea"
        _apply_pending_reset(
            reset_key,
            **{
                nombre_key: "",
                genera_key: False,
                revierte_key: False,
                inicial_key: False,
                bloquea_key: False,
            },
        )
        _show_flash(flash_key)

        with st.form("admin_new_order_state", enter_to_submit=False):
            nombre = st.text_input("Nombre *", key=nombre_key)

            c1, c2, c3, c4 = st.columns(4)
            genera_venta = c1.checkbox("Genera venta", key=genera_key)
            revierte_venta = c2.checkbox("Revierte venta", key=revierte_key)
            es_inicial = c3.checkbox("Estado inicial", key=inicial_key)
            bloquea_edicion = c4.checkbox("Bloquea edición", key=bloquea_key)

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
                        st.session_state[flash_key] = (
                            f"Estado creado: {created['nombre']} ({created['id']})"
                        )
                        _schedule_reset(reset_key)
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


def _tab_alertas_email() -> None:
    st.markdown(
        "Configura destinatarios, horarios y envío automático de alertas de stock. "
        "El servidor SMTP (Gmail) sigue configurándose en `.env` / Streamlit Secrets."
    )
    st.info(
        "La app **guarda** la programación, pero **no envía sola** a la hora indicada. "
        "Los envíos automáticos los ejecuta **GitHub Actions** (en producción) o el script "
        "`scripts/send_scheduled_alerts.py` en una tarea programada de Windows. "
        "Usa el botón de abajo para probar el envío programado sin esperar."
    )

    config = load_alert_email_config()
    st.caption(format_config_summary(config))

    tab_config, tab_dest, tab_log = st.tabs(["Programación", "Destinatarios", "Historial"])

    with tab_config:
        h1, h2, h3 = time_input_defaults(config)
        with st.form("admin_alert_email_config", enter_to_submit=False):
            activo = _bool_select("Envío automático activo", _as_bool(config.get("activo")), key="admin_alert_auto")
            envios = st.selectbox(
                "Envíos por día",
                [1, 2, 3],
                index=max(0, int(config.get("envios_por_dia", 1)) - 1),
                key="admin_alert_envios",
            )
            c1, c2, c3 = st.columns(3)
            hora_1 = c1.text_input("Horario 1 (HH:MM)", value=h1, key="admin_alert_h1")
            hora_2 = c2.text_input("Horario 2 (HH:MM)", value=h2, key="admin_alert_h2")
            hora_3 = c3.text_input("Horario 3 (HH:MM)", value=h3, key="admin_alert_h3")
            solo_con_alertas = _bool_select(
                "Enviar solo si hay productos en alerta",
                _as_bool(config.get("solo_si_hay_alertas", True)),
                key="admin_alert_solo",
            )
            zona = st.text_input(
                "Zona horaria",
                value=str(config.get("zona_horaria") or "America/Bogota"),
                key="admin_alert_tz",
            )

            if st.form_submit_button("Guardar programación", type="primary"):
                try:
                    save_alert_email_config(
                        activo=activo,
                        envios_por_dia=int(envios),
                        horario_1=hora_1,
                        horario_2=hora_2,
                        horario_3=hora_3,
                        solo_si_hay_alertas=solo_con_alertas,
                        zona_horaria=zona,
                    )
                    st.success("Programación de alertas guardada.")
                    _refresh_and_rerun()
                except Exception as exc:
                    st.error(str(exc))

        st.divider()
        st.markdown("**Envío programado (prueba)**")
        st.caption(
            "Solo envía si la hora actual está dentro de ±25 min de un horario configurado "
            "y ese slot no se procesó ya hoy en esa ventana."
        )
        if st.button("Ejecutar envío programado ahora", key="admin_alert_run_scheduled"):
            try:
                result = run_scheduled_alert_job()
                if result.get("skipped"):
                    st.warning(result.get("reason", "No correspondía enviar ahora."))
                elif result.get("ok"):
                    slots = result.get("slots") or [result.get("slot")]
                    st.success(
                        f"Enviado en slot(s) {slots} a {', '.join(result.get('recipients', []))} "
                        f"({result.get('products', 0)} producto(s))."
                    )
                    _refresh_and_rerun()
                else:
                    st.error(result.get("reason", "No se pudo enviar."))
            except Exception as exc:
                st.error(str(exc))

        st.divider()
        st.markdown("**Prueba manual**")
        if not is_email_configured():
            st.warning("SMTP no configurado en `.env` / Secrets.")
        else:
            st.caption(f"Destinatarios actuales: **{alert_recipient() or 'ninguno'}**")
            alerts = get_low_stock_alerts()
            st.caption(f"Productos en alerta ahora: **{len(alerts)}**")
            if st.button("Enviar alerta ahora (manual)", key="admin_alert_send_now"):
                try:
                    count = notify_low_stock_by_email()
                    st.success(
                        f"Correo enviado a {alert_recipient()} con {count} producto(s). "
                        "Revisa Spam si no lo ves."
                    )
                except Exception as exc:
                    st.error(str(exc))

    with tab_dest:
        tab_list, tab_new, tab_edit = st.tabs(["Listado", "Nuevo correo", "Editar / eliminar"])

        with tab_list:
            recipients = load_alert_recipients()
            if recipients.empty:
                st.info("No hay destinatarios. Agrega al menos uno para el envío automático.")
            else:
                display = recipients.copy()
                if "activo" in display.columns:
                    display["activo"] = display["activo"].map(lambda v: "Si" if _as_bool(v) else "No")
                calixta_table(display.drop(columns=["fecha_registro"], errors="ignore"), key="admin_alert_recipients_list")

        with tab_new:
            with st.form("admin_new_alert_recipient", enter_to_submit=False):
                email = st.text_input("Correo *")
                nombre = st.text_input("Nombre (opcional)")
                if st.form_submit_button("Guardar destinatario", type="primary"):
                    if not email.strip():
                        st.error("El correo es obligatorio.")
                    else:
                        try:
                            created = create_alert_recipient(email, nombre)
                            st.success(f"Destinatario creado: {created['email']}")
                            _refresh_and_rerun()
                        except Exception as exc:
                            st.error(str(exc))

        with tab_edit:
            recipients = load_alert_recipients()
            if recipients.empty:
                st.info("No hay destinatarios registrados.")
            else:
                options = {
                    f"{row['email']} ({row['id']})": row["id"]
                    for _, row in recipients.iterrows()
                }
                recipient_id = search_select(
                    "Buscar destinatario",
                    options,
                    key="admin_edit_alert_recipient_sel",
                    placeholder="Buscar por correo…",
                )
                if recipient_id is not None:
                    current = recipients[recipients["id"] == recipient_id].iloc[0]
                    with st.form("admin_edit_alert_recipient", enter_to_submit=False):
                        email = st.text_input("Correo *", value=str(current.get("email", "")))
                        nombre = st.text_input("Nombre", value=str(current.get("nombre", "")))
                        activo = _bool_select("Activo", _as_bool(current.get("activo")), key="admin_edit_alert_recipient_activo")

                        c1, c2 = st.columns(2)
                        save = c1.form_submit_button("Actualizar", type="primary")
                        delete = c2.form_submit_button("Eliminar", type="secondary")

                    if save:
                        try:
                            update_alert_recipient(
                                recipient_id,
                                {"email": email, "nombre": nombre, "activo": activo},
                            )
                            st.success("Destinatario actualizado.")
                            clear_search_select("admin_edit_alert_recipient_sel")
                            _refresh_and_rerun()
                        except Exception as exc:
                            st.error(str(exc))
                    if delete:
                        try:
                            delete_alert_recipient(recipient_id)
                            st.success("Destinatario eliminado.")
                            clear_search_select("admin_edit_alert_recipient_sel")
                            _refresh_and_rerun()
                        except Exception as exc:
                            st.error(str(exc))

    with tab_log:
        if st.button("Actualizar historial", key="admin_alert_refresh_logs"):
            load_alert_send_logs.clear()
        logs = list_alert_send_logs()
        if logs.empty:
            st.info("Aún no hay envíos registrados.")
        else:
            display = logs.copy()
            if "enviado_en" in display.columns:
                display["enviado_en"] = pd.to_datetime(display["enviado_en"]).dt.strftime("%Y-%m-%d %H:%M")
            if "exito" in display.columns:
                display["exito"] = display["exito"].map(lambda v: "Si" if _as_bool(v) else "No")
            calixta_table(
                display[["fecha", "slot", "enviado_en", "destinatarios", "productos_count", "exito", "mensaje"]],
                key="admin_alert_send_logs",
                paginate=False,
            )


def page_administracion() -> None:
    page_header("Administración", "Catálogos y configuración del flujo operativo")

    with page_section():
        tab_productos, tab_ingresos, tab_gastos, tab_estados, tab_alertas = st.tabs(
            ["Tipos de producto", "Tipos de ingreso", "Tipos de gasto", "Estados de pedido", "Alertas por correo"]
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
        with tab_alertas:
            _tab_alertas_email()
