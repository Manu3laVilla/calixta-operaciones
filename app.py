from __future__ import annotations

import utils.ssl_fix  # noqa: F401 — debe cargarse antes que Google APIs

from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from config import ALERT_EMAIL_TO, CATEGORIES, DELIVERED_STATE, ORDER_STATES, SIZES
from services.alert_service import (
    count_low_stock,
    get_low_stock_alerts,
    notify_low_stock_by_email,
)
from services.email_service import is_email_configured
from services.customer_service import create_customer, list_customers, update_customer
from services.order_service import (
    create_order,
    delete_order,
    get_order_items,
    list_orders,
    update_order,
    update_order_status,
)
from services.product_service import (
    create_product,
    list_products,
    product_label,
    update_product,
)
from services.sale_service import list_sales
from services.sheets_db import get_db
from ui.styles import CALIXTA_CSS, format_cop

st.set_page_config(
    page_title="Calixta | Centro de Operaciones",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CALIXTA_CSS, unsafe_allow_html=True)

CHART_COLORS = ["#2C2C2C", "#6B6560", "#A89F94", "#D4C9BC", "#E8E2D9"]


def init_connection() -> bool:
    try:
        get_db().connect()
        return True
    except Exception as exc:
        st.error("No se pudo conectar con Google Sheets")
        st.info(
            "Configura tu archivo `.env` y las credenciales siguiendo el README. "
            f"Detalle: {exc}"
        )
        return False


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<p class="main-header">{title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{subtitle}</p>', unsafe_allow_html=True)


def sidebar() -> str:
    st.sidebar.markdown('<p class="brand-sidebar">Calixta</p>', unsafe_allow_html=True)
    st.sidebar.caption("Centro de Operaciones")

    alerts = 0
    try:
        alerts = count_low_stock()
    except Exception:
        pass

    menu = {
        "Dashboard": "dashboard",
        "Productos": "productos",
        "Clientes": "clientes",
        "Pedidos": "pedidos",
        "Ventas": "ventas",
        f"Alertas de stock ({alerts})": "alertas",
    }

    choice = st.sidebar.radio("Menú", list(menu.keys()), label_visibility="collapsed")
    st.sidebar.divider()
    st.sidebar.caption("Base de datos: Google Sheets")
    return menu[choice]


def _init_cart(key: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = []


def _render_cart_editor(key: str, products: pd.DataFrame) -> list[dict]:
    _init_cart(key)
    cart: list[dict] = st.session_state[key]

    if products.empty:
        st.warning("No hay productos disponibles.")
        return []

    options = {product_label(row.to_dict()): row["id"] for _, row in products.iterrows()}
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        selected = c1.selectbox("Producto", list(options.keys()), key=f"{key}_product")
    with c2:
        qty = c2.number_input("Cantidad", min_value=1, step=1, key=f"{key}_qty")
    with c3:
        if c3.button("Agregar", key=f"{key}_add"):
            cart.append({"producto_id": options[selected], "cantidad": int(qty)})
            st.session_state[key] = cart
            st.rerun()

    if cart:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Producto": next(
                            (k for k, v in options.items() if v == item["producto_id"]),
                            item["producto_id"],
                        ),
                        "Cantidad": item["cantidad"],
                    }
                    for item in cart
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
        if st.button("Vaciar lista", key=f"{key}_clear"):
            st.session_state[key] = []
            st.rerun()

    return cart


def page_dashboard() -> None:
    page_header("Dashboard", "Resumen del negocio Calixta")

    products = list_products()
    customers = list_customers()
    sales = list_sales()
    orders = list_orders()
    alerts = get_low_stock_alerts()

    total_revenue = float(sales["subtotal"].sum()) if not sales.empty else 0.0
    pending_orders = (
        len(orders[orders["estado"] != DELIVERED_STATE]) if not orders.empty else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Productos", len(products))
    c2.metric("Clientes", len(customers))
    c3.metric("Ingresos (COP)", format_cop(total_revenue))
    c4.metric("Pedidos activos", pending_orders)
    c5.metric("Alertas stock", len(alerts))

    left, right = st.columns(2)

    with left:
        st.subheader("Ingresos por mes")
        if sales.empty:
            st.info("Sin ventas registradas aún.")
        else:
            chart_df = sales.copy()
            chart_df["mes"] = pd.to_datetime(
                chart_df["fecha_entrega"], errors="coerce"
            ).dt.to_period("M").astype(str)
            monthly = chart_df.groupby("mes", as_index=False)["subtotal"].sum()
            fig = px.bar(
                monthly,
                x="mes",
                y="subtotal",
                labels={"mes": "Mes", "subtotal": "Ingresos (COP)"},
                color_discrete_sequence=[CHART_COLORS[0]],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Montserrat",
            )
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Pedidos por estado")
        if orders.empty:
            st.info("Sin pedidos registrados.")
        else:
            status_counts = orders["estado"].value_counts().reset_index()
            status_counts.columns = ["estado", "cantidad"]
            fig = px.pie(
                status_counts,
                names="estado",
                values="cantidad",
                color_discrete_sequence=CHART_COLORS,
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Montserrat",
            )
            st.plotly_chart(fig, use_container_width=True)

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:
        st.subheader("Productos más vendidos")
        if sales.empty:
            st.info("Sin datos de ventas.")
        else:
            top = (
                sales.groupby("producto_nombre", as_index=False)["cantidad"]
                .sum()
                .sort_values("cantidad", ascending=False)
                .head(8)
            )
            fig = px.bar(
                top,
                x="cantidad",
                y="producto_nombre",
                orientation="h",
                labels={"producto_nombre": "Producto", "cantidad": "Unidades"},
                color_discrete_sequence=[CHART_COLORS[1]],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Montserrat",
                yaxis={"categoryorder": "total ascending"},
            )
            st.plotly_chart(fig, use_container_width=True)

    with bottom_right:
        st.subheader("Ventas por categoría")
        if sales.empty or products.empty:
            st.info("Sin datos suficientes.")
        else:
            merged = sales.merge(
                products[["id", "categoria"]],
                left_on="producto_id",
                right_on="id",
                how="left",
            )
            cat = merged.groupby("categoria", as_index=False)["subtotal"].sum()
            fig = px.bar(
                cat,
                x="categoria",
                y="subtotal",
                labels={"categoria": "Categoría", "subtotal": "Ingresos (COP)"},
                color_discrete_sequence=[CHART_COLORS[2]],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Montserrat",
            )
            st.plotly_chart(fig, use_container_width=True)

    if not alerts.empty:
        st.warning(f"{len(alerts)} producto(s) requieren reposición.")
        st.dataframe(
            alerts[
                ["referencia", "nombre", "talla", "color", "stock", "stock_minimo", "precio"]
            ],
            use_container_width=True,
            hide_index=True,
        )
        _render_email_alert_button(alerts)


def page_products() -> None:
    page_header("Productos", "Inventario de ropa y accesorios")

    tab_list, tab_new, tab_edit = st.tabs(["Inventario", "Nuevo producto", "Editar producto"])

    with tab_list:
        products = list_products()
        if products.empty:
            st.info("No hay productos registrados.")
        else:
            display = products.copy()
            if "precio" in display.columns:
                display["precio"] = display["precio"].apply(format_cop)
            st.dataframe(display, use_container_width=True, hide_index=True)

    with tab_new:
        with st.form("new_product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            referencia = c1.text_input("Referencia *")
            nombre = c2.text_input("Nombre *")
            c3, c4, c5 = st.columns(3)
            color = c3.text_input("Color *")
            talla = c4.selectbox("Talla *", SIZES)
            categoria = c5.selectbox("Categoría *", CATEGORIES)
            descripcion = st.text_area("Descripción")
            c6, c7, c8 = st.columns(3)
            stock = c6.number_input("Stock inicial", min_value=0, step=1)
            stock_minimo = c7.number_input("Stock mínimo alerta", min_value=0, step=1)
            precio = c8.number_input("Precio (COP)", min_value=0, step=1000, format="%d")

            if st.form_submit_button("Guardar producto", type="primary"):
                if not referencia.strip() or not nombre.strip() or not color.strip():
                    st.error("Referencia, nombre y color son obligatorios.")
                else:
                    product = create_product(
                        referencia, nombre, color, talla, categoria,
                        descripcion, stock, stock_minimo, precio,
                    )
                    st.success(f"Producto creado: {product['nombre']} ({product['id']})")
                    st.rerun()

    with tab_edit:
        products = list_products()
        if products.empty:
            st.info("Primero registra productos.")
        else:
            options = {
                f"{row['referencia']} | {row['nombre']} ({row['id']})": row["id"]
                for _, row in products.iterrows()
            }
            selected = st.selectbox("Selecciona producto", list(options.keys()))
            product_id = options[selected]
            current = products[products["id"] == product_id].iloc[0]

            with st.form("edit_product_form"):
                c1, c2 = st.columns(2)
                referencia = c1.text_input("Referencia", value=str(current.get("referencia", "")))
                nombre = c2.text_input("Nombre", value=str(current["nombre"]))
                c3, c4, c5 = st.columns(3)
                color = c3.text_input("Color", value=str(current.get("color", "")))
                talla = c4.selectbox(
                    "Talla", SIZES,
                    index=SIZES.index(current["talla"]) if current.get("talla") in SIZES else 0,
                )
                categoria = c5.selectbox(
                    "Categoría", CATEGORIES,
                    index=CATEGORIES.index(current["categoria"])
                    if current.get("categoria") in CATEGORIES else 0,
                )
                descripcion = st.text_area(
                    "Descripción", value=str(current.get("descripcion", ""))
                )
                c6, c7, c8, c9 = st.columns(4)
                stock = c6.number_input("Stock", value=int(current.get("stock", 0)))
                stock_minimo = c7.number_input(
                    "Stock mínimo", value=int(current.get("stock_minimo", 0))
                )
                precio = c8.number_input(
                    "Precio (COP)", value=int(current.get("precio", 0)), step=1000, format="%d"
                )
                activo = c9.selectbox("Activo", ["Si", "No"])

                if st.form_submit_button("Actualizar", type="primary"):
                    update_product(
                        product_id,
                        {
                            "referencia": referencia,
                            "nombre": nombre,
                            "color": color,
                            "talla": talla,
                            "categoria": categoria,
                            "descripcion": descripcion,
                            "stock": stock,
                            "stock_minimo": stock_minimo,
                            "precio": precio,
                            "activo": activo,
                        },
                    )
                    st.success("Producto actualizado.")
                    st.rerun()


def page_customers() -> None:
    page_header("Clientes", "Cartera de clientes Calixta")

    tab_list, tab_new, tab_edit = st.tabs(["Listado", "Nuevo cliente", "Editar cliente"])

    with tab_list:
        customers = list_customers()
        if customers.empty:
            st.info("No hay clientes registrados.")
        else:
            st.dataframe(customers, use_container_width=True, hide_index=True)

    with tab_new:
        with st.form("new_customer_form", clear_on_submit=True):
            nombre = st.text_input("Nombre *")
            c1, c2 = st.columns(2)
            email = c1.text_input("Email")
            telefono = c2.text_input("Teléfono")
            direccion = st.text_input("Dirección")
            notas = st.text_area("Notas")

            if st.form_submit_button("Guardar cliente", type="primary"):
                if not nombre.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    customer = create_customer(nombre, email, telefono, direccion, notas)
                    st.success(f"Cliente creado: {customer['nombre']} ({customer['id']})")
                    st.rerun()

    with tab_edit:
        customers = list_customers()
        if customers.empty:
            st.info("Primero registra clientes.")
        else:
            options = {
                f"{row['nombre']} ({row['id']})": row["id"] for _, row in customers.iterrows()
            }
            selected = st.selectbox("Selecciona cliente", list(options.keys()))
            customer_id = options[selected]
            current = customers[customers["id"] == customer_id].iloc[0]

            with st.form("edit_customer_form"):
                nombre = st.text_input("Nombre", value=str(current["nombre"]))
                c1, c2 = st.columns(2)
                email = c1.text_input("Email", value=str(current.get("email", "")))
                telefono = c2.text_input("Teléfono", value=str(current.get("telefono", "")))
                direccion = st.text_input("Dirección", value=str(current.get("direccion", "")))
                notas = st.text_area("Notas", value=str(current.get("notas", "")))

                if st.form_submit_button("Actualizar", type="primary"):
                    update_customer(
                        customer_id,
                        {
                            "nombre": nombre,
                            "email": email,
                            "telefono": telefono,
                            "direccion": direccion,
                            "notas": notas,
                        },
                    )
                    st.success("Cliente actualizado.")
                    st.rerun()


def page_orders() -> None:
    page_header("Pedidos", "Gestión del ciclo de pedidos")

    tab_list, tab_new, tab_edit, tab_status, tab_delete = st.tabs(
        ["Listado", "Nuevo pedido", "Editar pedido", "Actualizar estado", "Eliminar pedido"]
    )

    with tab_list:
        orders = list_orders()
        if orders.empty:
            st.info("No hay pedidos registrados.")
        else:
            display = orders.drop(columns=["items_json"], errors="ignore").copy()
            if "total" in display.columns:
                display["total"] = display["total"].apply(format_cop)
            st.dataframe(display, use_container_width=True, hide_index=True)

    with tab_new:
        customers = list_customers()
        products = list_products(active_only=True)

        if customers.empty:
            st.warning("Registra al menos un cliente.")
        else:
            customer_options = {
                f"{row['nombre']} ({row['id']})": (row["id"], row["nombre"])
                for _, row in customers.iterrows()
            }
            customer_label = st.selectbox("Cliente", list(customer_options.keys()), key="new_order_client")
            direccion = st.text_input("Dirección de entrega *", key="new_order_address")
            notas = st.text_area("Notas", key="new_order_notes")
            st.markdown("**Productos del pedido**")
            cart = _render_cart_editor("new_order_cart", products)

            if st.button("Crear pedido", type="primary", key="create_order_btn"):
                if not direccion.strip():
                    st.error("La dirección de entrega es obligatoria.")
                elif not cart:
                    st.error("Agrega al menos un producto.")
                else:
                    cliente_id, cliente_nombre = customer_options[customer_label]
                    try:
                        order = create_order(
                            cliente_id, cliente_nombre, cart, direccion, notas
                        )
                        st.session_state["new_order_cart"] = []
                        st.success(
                            f"Pedido {order['id']} creado — Total {format_cop(order['total'])}"
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

    with tab_edit:
        orders = list_orders()
        editable = orders[orders["estado"] != DELIVERED_STATE] if not orders.empty else orders
        products = list_products(active_only=True)
        customers = list_customers()

        if editable.empty:
            st.info("No hay pedidos editables (los entregados no se pueden modificar).")
        else:
            options = {
                f"{row['id']} | {row['cliente_nombre']} | {row['estado']}": row["id"]
                for _, row in editable.iterrows()
            }
            selected = st.selectbox("Selecciona pedido", list(options.keys()), key="edit_order_sel")
            order_id = options[selected]
            order = orders[orders["id"] == order_id].iloc[0]

            customer_options = {
                f"{row['nombre']} ({row['id']})": (row["id"], row["nombre"])
                for _, row in customers.iterrows()
            }
            default_customer = f"{order['cliente_nombre']} ({order['cliente_id']})"
            customer_labels = list(customer_options.keys())
            default_idx = customer_labels.index(default_customer) if default_customer in customer_labels else 0

            customer_label = st.selectbox("Cliente", customer_labels, index=default_idx, key="edit_order_client")
            direccion = st.text_input(
                "Dirección de entrega",
                value=str(order.get("direccion_entrega", "")),
                key="edit_order_address",
            )
            notas = st.text_area("Notas", value=str(order.get("notas", "")), key="edit_order_notes")

            if "edit_order_cart" not in st.session_state or st.session_state.get("edit_order_loaded") != order_id:
                st.session_state["edit_order_cart"] = [
                    {"producto_id": i["producto_id"], "cantidad": i["cantidad"]}
                    for i in get_order_items(order_id)
                ]
                st.session_state["edit_order_loaded"] = order_id

            st.markdown("**Productos del pedido**")
            cart = _render_cart_editor("edit_order_cart", products)

            if st.button("Guardar cambios", type="primary", key="save_order_btn"):
                cliente_id, cliente_nombre = customer_options[customer_label]
                try:
                    update_order(
                        order_id, cliente_id, cliente_nombre, cart, direccion, notas
                    )
                    st.success(f"Pedido {order_id} actualizado.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with tab_status:
        orders = list_orders()
        pending = orders[orders["estado"] != DELIVERED_STATE] if not orders.empty else orders

        if pending.empty:
            st.info("No hay pedidos pendientes de actualizar.")
        else:
            options = {
                f"{row['id']} | {row['cliente_nombre']} | {row['estado']}": row["id"]
                for _, row in pending.iterrows()
            }
            selected = st.selectbox("Selecciona pedido", list(options.keys()), key="status_order_sel")
            order_id = options[selected]
            items = get_order_items(order_id)

            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)

            current = orders[orders["id"] == order_id].iloc[0]
            st.caption(f"Dirección: {current.get('direccion_entrega', '')}")

            new_status = st.selectbox("Nuevo estado", ORDER_STATES, key="new_status_sel")
            fecha_entrega = None
            if new_status == DELIVERED_STATE:
                c1, c2 = st.columns(2)
                entrega_date = c1.date_input("Fecha de entrega", value=date.today())
                entrega_time = c2.time_input("Hora de entrega", value=datetime.now().time())
                fecha_entrega = f"{entrega_date} {entrega_time.strftime('%H:%M:%S')}"

            if st.button("Actualizar estado", type="primary", key="update_status_btn"):
                try:
                    update_order_status(order_id, new_status, fecha_entrega)
                    st.success(f"Pedido {order_id} → {new_status}")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with tab_delete:
        orders = list_orders()
        deletable = orders[orders["estado"] != DELIVERED_STATE] if not orders.empty else orders

        if deletable.empty:
            st.info("No hay pedidos que se puedan eliminar.")
        else:
            options = {
                f"{row['id']} | {row['cliente_nombre']} | {row['estado']}": row["id"]
                for _, row in deletable.iterrows()
            }
            selected = st.selectbox("Selecciona pedido", list(options.keys()), key="delete_order_sel")
            order_id = options[selected]
            st.warning("Esta acción no se puede deshacer.")

            if st.button("Eliminar pedido", type="primary", key="delete_order_btn"):
                try:
                    delete_order(order_id)
                    st.success(f"Pedido {order_id} eliminado.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))


def page_sales() -> None:
    page_header("Ventas", "Historial generado automáticamente al entregar pedidos")
    st.caption("Las ventas se crean al marcar un pedido como Entregado. No se pueden crear ni editar manualmente.")

    sales = list_sales()
    customers = list_customers()
    products = list_products()

    with st.expander("Filtros", expanded=True):
        c1, c2, c3 = st.columns(3)
        cliente_filter = c1.selectbox(
            "Cliente",
            ["Todos"] + [f"{r['nombre']} ({r['id']})" for _, r in customers.iterrows()],
        )
        producto_filter = c2.selectbox(
            "Producto",
            ["Todos"] + [f"{r['referencia']} | {r['nombre']}" for _, r in products.iterrows()],
        )
        pedido_filter = c3.text_input("ID de pedido")

        c4, c5 = st.columns(2)
        use_date_filter = st.checkbox("Filtrar por rango de fechas")
        fecha_desde_val = c4.date_input("Desde", value=date.today().replace(day=1), disabled=not use_date_filter)
        fecha_hasta_val = c5.date_input("Hasta", value=date.today(), disabled=not use_date_filter)

    cliente_id = None
    if cliente_filter != "Todos":
        cliente_id = cliente_filter.split("(")[-1].rstrip(")")

    producto_id = None
    if producto_filter != "Todos":
        ref = producto_filter.split(" | ")[0]
        match = products[products["referencia"] == ref]
        if not match.empty:
            producto_id = match.iloc[0]["id"]

    filtered = list_sales(
        cliente_id=cliente_id,
        producto_id=producto_id,
        pedido_id=pedido_filter or None,
        fecha_desde=str(fecha_desde_val) if use_date_filter else None,
        fecha_hasta=str(fecha_hasta_val) + " 23:59:59" if use_date_filter else None,
    )

    if filtered.empty:
        st.info("No hay ventas que coincidan con los filtros.")
    else:
        total = float(filtered["subtotal"].sum())
        st.metric("Total filtrado", format_cop(total))
        display = filtered.copy()
        display["precio_unitario"] = display["precio_unitario"].apply(format_cop)
        display["subtotal"] = display["subtotal"].apply(format_cop)
        st.dataframe(display, use_container_width=True, hide_index=True)


def _render_email_alert_button(alerts: pd.DataFrame) -> None:
    st.divider()
    st.subheader("Notificación por correo")

    if not is_email_configured():
        st.info(
            "Para enviar alertas por correo, configura `SMTP_USER` y `SMTP_PASSWORD` "
            "en tu archivo `.env`. Consulta `.env.example` para más detalles."
        )
        return

    st.caption(f"Los correos se enviarán a: **{ALERT_EMAIL_TO}**")

    if st.button("Enviar alerta por correo", type="primary", key="send_email_alert"):
        try:
            count = notify_low_stock_by_email()
            st.success(f"Correo enviado a {ALERT_EMAIL_TO} con {count} producto(s).")
        except Exception as exc:
            st.error(f"No se pudo enviar el correo: {exc}")


def page_alerts() -> None:
    page_header("Alertas de stock", "Productos que requieren reposición")

    alerts = get_low_stock_alerts()
    if alerts.empty:
        st.success("Todo en orden. No hay productos con stock bajo.")
    else:
        st.warning(f"{len(alerts)} producto(s) por debajo del stock mínimo.")
        display = alerts.copy()
        display["precio"] = display["precio"].apply(format_cop)
        st.dataframe(
            display[
                ["referencia", "nombre", "talla", "color", "categoria",
                 "stock", "stock_minimo", "faltante", "precio"]
            ],
            use_container_width=True,
            hide_index=True,
        )
        _render_email_alert_button(alerts)


def main() -> None:
    page = sidebar()

    if not init_connection():
        st.stop()

    pages = {
        "dashboard": page_dashboard,
        "productos": page_products,
        "clientes": page_customers,
        "pedidos": page_orders,
        "ventas": page_sales,
        "alertas": page_alerts,
    }
    pages[page]()


if __name__ == "__main__":
    main()
