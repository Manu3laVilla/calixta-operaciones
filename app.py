from __future__ import annotations

import utils.ssl_fix  # noqa: F401 — parche SSL para Windows

from datetime import date, datetime

import pandas as pd
import streamlit as st

from config import ALERT_EMAIL_TO, CATEGORIES, SIZES
from services.catalog_service import product_type_options
from services.alert_service import notify_low_stock_by_email
from services.customer_service import create_customer, update_customer
from services.email_service import is_email_configured
from services.order_service import (
    create_order,
    delete_order,
    get_allowed_next_states,
    list_editable_orders,
    state_requires_sale_date,
    update_order,
    update_order_status,
)
from services.product_service import create_product, product_label, update_product
from services.supabase_db import get_db
from ui.cached_data import (
    clear_data_cache,
    filter_sales,
    get_order_items_cached,
    load_customers,
    load_low_stock_alerts,
    load_order_states,
    load_orders,
    load_products,
    load_sales,
)
from ui.components import (
    calixta_table,
    clear_search_select,
    dashboard_welcome,
    page_header,
    page_section,
    panel_card,
    search_select,
    stat_chips,
)
from ui.accounting import page_contabilidad
from ui.administration import page_administracion
from ui.navigation import nav_layout
from ui.charts import (
    PLOTLY_CONFIG,
    orders_donut_chart,
    revenue_monthly_chart,
    sales_by_category_donut,
    top_products_chart,
)
from ui.styles import CALIXTA_CSS, CALIXTA_MODULE_TABS_CSS, CALIXTA_NAV_CSS, format_cop

_PAGE_ICON = "assets/calixta-icon.png"

st.set_page_config(
    page_title="Calixta | Centro de Operaciones",
    page_icon=_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(CALIXTA_CSS, unsafe_allow_html=True)
st.markdown(CALIXTA_NAV_CSS, unsafe_allow_html=True)
st.markdown(CALIXTA_MODULE_TABS_CSS, unsafe_allow_html=True)


def init_connection() -> bool:
    try:
        get_db().connect()
        return True
    except Exception as exc:
        st.error("No se pudo conectar con Supabase")
        st.info(
            "Configura SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en `.env` (local) "
            "o en Streamlit Secrets (cloud). "
            f"Detalle: {exc}"
        )
        return False


def _tipo_selectbox(
    categoria: str,
    key: str,
    *,
    default_type_id: str | None = None,
) -> str | None:
    options = product_type_options(categoria, active_only=True)
    if not options:
        st.warning(
            f"No hay tipos activos para «{categoria}». "
            "Créalos en Administración → Tipos de producto."
        )
        return None

    labels = [name for name, _ in options]
    type_ids = [type_id for _, type_id in options]
    default_index = 0
    if default_type_id and default_type_id in type_ids:
        default_index = type_ids.index(default_type_id)

    selected_index = st.selectbox(
        "Tipo *",
        range(len(labels)),
        format_func=lambda index: labels[index],
        index=default_index,
        key=key,
    )
    return type_ids[selected_index]


def _refresh_and_rerun() -> None:
    clear_data_cache()
    st.rerun()


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
    product_id = search_select(
        "Producto",
        options,
        key=f"{key}_product",
        placeholder="Buscar por referencia, nombre, color, talla o precio…",
    )
    if product_id is None:
        return cart
    qty_col, btn_col = st.columns([2, 1])
    with qty_col:
        qty = st.number_input("Cantidad", min_value=1, step=1, key=f"{key}_qty")
    with btn_col:
        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("Agregar", key=f"{key}_add", use_container_width=True):
            cart.append({"producto_id": product_id, "cantidad": int(qty)})
            st.session_state[key] = cart
            st.rerun()

    if cart:
        calixta_table(
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
            key=f"{key}_cart",
            paginate=len(cart) > 10,
        )
        if st.button("Vaciar lista", key=f"{key}_clear"):
            st.session_state[key] = []
            st.rerun()

    return cart


def _clear_new_order_form() -> None:
    clear_search_select("new_order_client", "new_order_cart_product")
    for state_key in (
        "new_order_address",
        "new_order_notes",
        "new_order_cart",
        "new_order_cart_qty",
    ):
        st.session_state.pop(state_key, None)


def _filter_orders_df(
    orders: pd.DataFrame,
    *,
    fecha_desde: date | None,
    fecha_hasta: date | None,
    estado: str,
) -> pd.DataFrame:
    if orders.empty:
        return orders
    df = orders.copy()
    if estado != "Todos":
        df = df[df["estado"] == estado]
    date_col = "fecha_creacion" if "fecha_creacion" in df.columns else "fecha_entrega"
    if date_col in df.columns:
        fechas = pd.to_datetime(df[date_col], errors="coerce", utc=True)
        df["_date"] = fechas.dt.date
        if fecha_desde:
            df = df[df["_date"] >= fecha_desde]
        if fecha_hasta:
            df = df[df["_date"] <= fecha_hasta]
        df = df.drop(columns=["_date"])
    return df


def _filter_sales_df(
    sales: pd.DataFrame,
    products: pd.DataFrame,
    *,
    fecha_desde: date | None,
    fecha_hasta: date | None,
    categoria: str,
) -> pd.DataFrame:
    if sales.empty:
        return sales
    df = filter_sales(
        sales,
        fecha_desde=fecha_desde.isoformat() if fecha_desde else None,
        fecha_hasta=fecha_hasta.isoformat() if fecha_hasta else None,
    )
    if categoria != "Todas" and not products.empty:
        merged = df.merge(
            products[["id", "categoria"]],
            left_on="producto_id",
            right_on="id",
            how="left",
        )
        df = merged[merged["categoria"] == categoria]
    return df


def _dashboard_filters(
    sales: pd.DataFrame,
    orders: pd.DataFrame,
) -> tuple[date | None, date | None, str, str]:
    min_date: date | None = None
    max_date: date | None = None
    for df, col in ((sales, "fecha_entrega"), (orders, "fecha_creacion")):
        if not df.empty and col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce").dropna()
            if not parsed.empty:
                dmin, dmax = parsed.min().date(), parsed.max().date()
                min_date = dmin if min_date is None else min(min_date, dmin)
                max_date = dmax if max_date is None else max(max_date, dmax)

    today = date.today()
    default_desde = min_date or today.replace(month=1, day=1)
    default_hasta = max_date or today
    range_min = min_date or date(2020, 1, 1)
    range_max = max_date or today

    with st.container(border=True):
        st.markdown('<p class="filter-bar-title">Filtros</p>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1:
            fecha_desde = st.date_input(
                "Desde",
                value=default_desde,
                min_value=range_min,
                max_value=range_max,
                key="dash_fecha_desde",
            )
        with c2:
            fecha_hasta = st.date_input(
                "Hasta",
                value=default_hasta,
                min_value=range_min,
                max_value=range_max,
                key="dash_fecha_hasta",
            )
        with c3:
            categoria = st.selectbox(
                "Categoría",
                ["Todas", *CATEGORIES],
                key="dash_categoria",
            )
        with c4:
            order_states = load_order_states(active_only=False)
            state_names = (
                [str(name) for name in order_states["nombre"].tolist()]
                if not order_states.empty
                else ["Recibido", "Pago Confirmado", "Envío Agendado", "Entregado"]
            )
            estado = st.selectbox(
                "Estado pedido",
                ["Todos", *state_names],
                key="dash_estado",
            )

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        st.warning("La fecha inicial no puede ser posterior a la final.")
        fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

    return fecha_desde, fecha_hasta, categoria, estado


def _sales_by_category(sales: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    if sales.empty or products.empty:
        return pd.DataFrame(columns=["categoria", "subtotal"])
    merged = sales.merge(
        products[["id", "categoria"]],
        left_on="producto_id",
        right_on="id",
        how="left",
    )
    merged["categoria"] = merged["categoria"].fillna("Sin categoría")
    return merged.groupby("categoria", as_index=False)["subtotal"].sum()


_MESES_ES = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]


def _prepare_monthly_revenue(sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty or "fecha_entrega" not in sales.columns:
        return pd.DataFrame(columns=["mes_label", "subtotal"])

    df = sales.copy()
    df["_fecha"] = pd.to_datetime(df["fecha_entrega"], errors="coerce")
    df = df.dropna(subset=["_fecha"])
    if df.empty:
        return pd.DataFrame(columns=["mes_label", "subtotal"])

    df["mes_key"] = df["_fecha"].dt.to_period("M")
    monthly = (
        df.groupby("mes_key", as_index=False)["subtotal"]
        .sum()
        .sort_values("mes_key")
    )
    monthly["mes_label"] = monthly["mes_key"].apply(
        lambda p: f"{_MESES_ES[p.month - 1]} {p.year}"
    )
    return monthly[["mes_label", "subtotal"]]


def page_dashboard() -> None:
    products = load_products()
    sales_all = load_sales()
    orders_all = load_orders()
    alerts = load_low_stock_alerts()

    dashboard_welcome()

    fecha_desde, fecha_hasta, categoria, estado = _dashboard_filters(sales_all, orders_all)

    sales = _filter_sales_df(
        sales_all, products,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, categoria=categoria,
    )
    orders = _filter_orders_df(
        orders_all,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, estado=estado,
    )

    total_revenue = float(sales["subtotal"].sum()) if not sales.empty else 0.0
    units_sold = int(sales["cantidad"].sum()) if not sales.empty else 0
    if not orders.empty and "venta_registrada" in orders.columns:
        sold_mask = orders["venta_registrada"].astype(str).str.lower().isin(
            ("true", "1", "si", "sí", "yes")
        )
        delivered = int(sold_mask.sum())
        pending_orders = int((~sold_mask).sum())
    else:
        delivered = 0
        pending_orders = len(orders) if not orders.empty else 0

    stat_chips([
        ("Ingresos", format_cop(total_revenue), "en el período", "terra"),
        ("Unidades vendidas", str(units_sold), "productos entregados", "olive"),
        ("Pedidos", str(len(orders)), f"{pending_orders} activos · {delivered} entregados", "sage"),
        ("Alertas stock", str(len(alerts)), "inventario actual", "pink"),
    ])

    st.markdown('<p class="dashboard-section-title">Resumen visual</p>', unsafe_allow_html=True)

    row1_left, row1_right = st.columns(2, gap="medium")
    row2_left, row2_right = st.columns(2, gap="medium")

    with row1_left:
        with panel_card("Ingresos por mes", accent="terra"):
            if sales.empty:
                st.markdown(
                    '<p class="chart-empty-msg">Aún no hay ventas registradas.</p>',
                    unsafe_allow_html=True,
                )
            else:
                monthly = _prepare_monthly_revenue(sales)
                if monthly.empty:
                    st.markdown(
                        '<p class="chart-empty-msg">Aún no hay ventas registradas.</p>',
                        unsafe_allow_html=True,
                    )
                else:
                    fig = revenue_monthly_chart(monthly)
                    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with row1_right:
        with panel_card("Pedidos por estado", accent="olive"):
            if orders.empty:
                st.markdown(
                    '<p class="chart-empty-msg">Aún no hay pedidos.</p>',
                    unsafe_allow_html=True,
                )
            else:
                status_counts = orders["estado"].value_counts().reset_index()
                status_counts.columns = ["estado", "cantidad"]
                fig = orders_donut_chart(status_counts)
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with row2_left:
        with panel_card("Productos más vendidos", accent="sage"):
            if sales.empty:
                st.markdown(
                    '<p class="chart-empty-msg">Sin datos de ventas.</p>',
                    unsafe_allow_html=True,
                )
            else:
                top = (
                    sales.groupby("producto_nombre", as_index=False)["cantidad"]
                    .sum()
                    .sort_values("cantidad", ascending=False)
                    .head(8)
                )
                fig = top_products_chart(top)
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with row2_right:
        with panel_card("Ventas por categoría", accent="pink"):
            by_category = _sales_by_category(sales, products)
            if by_category.empty:
                st.markdown(
                    '<p class="chart-empty-msg">Sin ventas por categoría.</p>',
                    unsafe_allow_html=True,
                )
            else:
                fig = sales_by_category_donut(by_category)
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with panel_card("Últimos pedidos", accent="cream"):
        if orders.empty:
            st.info("Sin pedidos en el período seleccionado.")
        else:
            sort_col = "fecha_creacion" if "fecha_creacion" in orders.columns else "id"
            recent = orders.sort_values(sort_col, ascending=False).head(5)
            display = recent[["id", "cliente_nombre", "estado", "total"]].copy()
            display["total"] = display["total"].apply(
                lambda v: format_cop(float(v)) if pd.notna(v) else ""
            )
            display.columns = ["Pedido", "Cliente", "Estado", "Total"]
            calixta_table(display, key="dash_recent_orders", paginate=False)

    if not alerts.empty:
        with panel_card("Productos con stock bajo", accent="cream"):
            st.warning(f"{len(alerts)} producto(s) requieren reposición.")
            alert_display = alerts.copy()
            alert_display["precio"] = alert_display["precio"].apply(format_cop)
            calixta_table(
                alert_display[
                    ["referencia", "nombre", "talla", "color", "stock", "stock_minimo", "precio"]
                ],
                key="dash_alerts_table",
            )
            _render_email_alert_button(alerts)


def page_products() -> None:
    page_header("Productos", "Inventario de ropa y accesorios")

    with page_section():
        tab_list, tab_new, tab_edit = st.tabs(["Inventario", "Nuevo producto", "Editar producto"])

        with tab_list:
            products = load_products()
            if products.empty:
                st.info("No hay productos registrados.")
            else:
                display = products.copy()
                if "precio" in display.columns:
                    display["precio"] = display["precio"].apply(format_cop)
                calixta_table(display, key="products_list")

        with tab_new:
            categoria = st.selectbox("Categoría *", CATEGORIES, key="new_product_cat")
            tipo_id = _tipo_selectbox(categoria, "new_product_tipo")
            talla = None
            if categoria == "Ropa":
                talla = st.selectbox("Talla *", SIZES, key="new_product_talla")

            with st.form("new_product_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                referencia = c1.text_input("Referencia *")
                nombre = c2.text_input("Nombre *")
                color = st.text_input("Color *")
                descripcion = st.text_area("Descripción")
                c6, c7, c8 = st.columns(3)
                stock = c6.number_input("Stock inicial", min_value=0, step=1)
                stock_minimo = c7.number_input("Stock mínimo alerta", min_value=0, step=1)
                precio = c8.number_input("Precio (COP)", min_value=0, step=1000, format="%d")

                if st.form_submit_button("Guardar producto", type="primary"):
                    if not referencia.strip() or not nombre.strip() or not color.strip():
                        st.error("Referencia, nombre y color son obligatorios.")
                    elif tipo_id is None:
                        st.error("Selecciona un tipo de producto válido.")
                    else:
                        product = create_product(
                            referencia,
                            nombre,
                            color,
                            talla,
                            categoria,
                            tipo_id,
                            descripcion,
                            stock,
                            stock_minimo,
                            precio,
                        )
                        st.success(f"Producto creado: {product['nombre']} ({product['id']})")
                        _refresh_and_rerun()

        with tab_edit:
            products = load_products()
            if products.empty:
                st.info("Primero registra productos.")
            else:
                options = {
                    f"{row['referencia']} | {row['nombre']} ({row['id']})": row["id"]
                    for _, row in products.iterrows()
                }
                product_id = search_select(
                    "Buscar producto",
                    options,
                    key="edit_product_sel",
                    placeholder="Buscar por referencia, nombre o ID…",
                )
                if product_id is not None:
                    current = products[products["id"] == product_id].iloc[0]
                    current_categoria = str(current.get("categoria", CATEGORIES[0]))
                    if st.session_state.get("edit_product_loaded") != product_id:
                        st.session_state["edit_product_cat"] = current_categoria
                        st.session_state["edit_product_loaded"] = product_id

                    categoria = st.selectbox(
                        "Categoría",
                        CATEGORIES,
                        index=CATEGORIES.index(current_categoria)
                        if current_categoria in CATEGORIES else 0,
                        key="edit_product_cat",
                    )
                    tipo_id = _tipo_selectbox(
                        categoria,
                        "edit_product_tipo",
                        default_type_id=str(current.get("tipo_id", "")) or None,
                    )
                    talla = None
                    if categoria == "Ropa":
                        current_talla = str(current.get("talla", ""))
                        talla = st.selectbox(
                            "Talla",
                            SIZES,
                            index=SIZES.index(current_talla) if current_talla in SIZES else 0,
                            key="edit_product_talla",
                        )

                    with st.form("edit_product_form"):
                        c1, c2 = st.columns(2)
                        referencia = c1.text_input(
                            "Referencia",
                            value=str(current.get("referencia", "")),
                        )
                        nombre = c2.text_input("Nombre", value=str(current["nombre"]))
                        color = st.text_input("Color", value=str(current.get("color", "")))
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
                            if tipo_id is None:
                                st.error("Selecciona un tipo de producto válido.")
                            else:
                                update_product(
                                    product_id,
                                    {
                                        "referencia": referencia,
                                        "nombre": nombre,
                                        "color": color,
                                        "talla": talla,
                                        "categoria": categoria,
                                        "tipo_id": tipo_id,
                                        "descripcion": descripcion,
                                        "stock": stock,
                                        "stock_minimo": stock_minimo,
                                        "precio": precio,
                                        "activo": activo,
                                    },
                                )
                                st.success("Producto actualizado.")
                                clear_search_select("edit_product_sel")
                                st.session_state.pop("edit_product_loaded", None)
                                _refresh_and_rerun()


def page_customers() -> None:
    page_header("Clientes", "Cartera de clientes Calixta")

    with page_section():
        tab_list, tab_new, tab_edit = st.tabs(["Listado", "Nuevo cliente", "Editar cliente"])

        with tab_list:
            customers = load_customers()
            if customers.empty:
                st.info("No hay clientes registrados.")
            else:
                calixta_table(customers, key="customers_list")

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
                        _refresh_and_rerun()

        with tab_edit:
            customers = load_customers()
            if customers.empty:
                st.info("Primero registra clientes.")
            else:
                options = {
                    f"{row['nombre']} ({row['id']})": row["id"] for _, row in customers.iterrows()
                }
                customer_id = search_select(
                    "Buscar cliente",
                    options,
                    key="edit_customer_sel",
                    placeholder="Buscar por nombre o ID…",
                )
                if customer_id is not None:
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
                            clear_search_select("edit_customer_sel")
                            _refresh_and_rerun()


def page_orders() -> None:
    page_header("Pedidos", "Gestión del ciclo de pedidos")

    with page_section():
        tab_list, tab_new, tab_edit, tab_status, tab_delete = st.tabs(
            ["Listado", "Nuevo pedido", "Editar pedido", "Actualizar estado", "Eliminar pedido"]
        )

        with tab_list:
            orders = load_orders()
            if orders.empty:
                st.info("No hay pedidos registrados.")
            else:
                display = orders.drop(columns=["items_json"], errors="ignore").copy()
                if "total" in display.columns:
                    display["total"] = display["total"].apply(format_cop)
                calixta_table(display, key="orders_list")

        with tab_new:
            if flash := st.session_state.pop("new_order_flash", None):
                st.success(flash)

            customers = load_customers()
            products = load_products(active_only=True)

            if customers.empty:
                st.warning("Registra al menos un cliente.")
            else:
                customer_options = {
                    f"{row['nombre']} ({row['id']})": (row["id"], row["nombre"])
                    for _, row in customers.iterrows()
                }
                customer_pick = search_select(
                    "Cliente",
                    customer_options,
                    key="new_order_client",
                    placeholder="Buscar por nombre o ID de cliente…",
                )
                if customer_pick is not None:
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
                            cliente_id, cliente_nombre = customer_pick
                            try:
                                order = create_order(
                                    cliente_id, cliente_nombre, cart, direccion, notas
                                )
                                st.session_state["new_order_flash"] = (
                                    f"Pedido {order['id']} creado — "
                                    f"Total {format_cop(order['total'])}"
                                )
                                _clear_new_order_form()
                                _refresh_and_rerun()
                            except Exception as exc:
                                st.error(str(exc))

        with tab_edit:
            editable = list_editable_orders()
            products = load_products(active_only=True)
            customers = load_customers()

            if editable.empty:
                st.info("No hay pedidos editables en su estado actual.")
            else:
                options = {
                    f"{row['id']} | {row['cliente_nombre']} | {row['estado']}": row["id"]
                    for _, row in editable.iterrows()
                }
                order_id = search_select(
                    "Buscar pedido",
                    options,
                    key="edit_order_sel",
                    placeholder="Buscar por ID de pedido, cliente o estado…",
                )
                if order_id is not None:
                    orders = load_orders()
                    order = orders[orders["id"] == order_id].iloc[0]

                    customer_options = {
                        f"{row['nombre']} ({row['id']})": (row["id"], row["nombre"])
                        for _, row in customers.iterrows()
                    }
                    default_customer = f"{order['cliente_nombre']} ({order['cliente_id']})"

                    customer_pick = search_select(
                        "Cliente",
                        customer_options,
                        key="edit_order_client",
                        placeholder="Buscar por nombre o ID de cliente…",
                        default_label=default_customer,
                    )
                    if customer_pick is not None:
                        direccion = st.text_input(
                            "Dirección de entrega",
                            value=str(order.get("direccion_entrega", "")),
                            key="edit_order_address",
                        )
                        notas = st.text_area("Notas", value=str(order.get("notas", "")), key="edit_order_notes")

                        if "edit_order_cart" not in st.session_state or st.session_state.get("edit_order_loaded") != order_id:
                            st.session_state["edit_order_cart"] = [
                                {"producto_id": i["producto_id"], "cantidad": i["cantidad"]}
                                for i in get_order_items_cached(order_id)
                            ]
                            st.session_state["edit_order_loaded"] = order_id

                        st.markdown("**Productos del pedido**")
                        cart = _render_cart_editor("edit_order_cart", products)

                        if st.button("Guardar cambios", type="primary", key="save_order_btn"):
                            cliente_id, cliente_nombre = customer_pick
                            try:
                                update_order(
                                    order_id, cliente_id, cliente_nombre, cart, direccion, notas
                                )
                                st.success(f"Pedido {order_id} actualizado.")
                                clear_search_select(
                                    "edit_order_sel",
                                    "edit_order_client",
                                    "edit_order_cart_product",
                                )
                                for state_key in (
                                    "edit_order_address",
                                    "edit_order_notes",
                                    "edit_order_loaded",
                                    "edit_order_cart",
                                ):
                                    st.session_state.pop(state_key, None)
                                _refresh_and_rerun()
                            except Exception as exc:
                                st.error(str(exc))

        with tab_status:
            orders = load_orders()

            if orders.empty:
                st.info("No hay pedidos registrados.")
            else:
                status_options = {}
                for _, row in orders.iterrows():
                    order_dict = row.to_dict()
                    allowed = get_allowed_next_states(order_dict)
                    if allowed:
                        status_options[
                            f"{row['id']} | {row['cliente_nombre']} | {row['estado']}"
                        ] = row["id"]

                if not status_options:
                    st.info("No hay pedidos con transiciones de estado disponibles.")
                else:
                    order_id = search_select(
                        "Buscar pedido",
                        status_options,
                        key="status_order_sel",
                        placeholder="Buscar por ID de pedido, cliente o estado…",
                    )
                    if order_id is not None:
                        items = get_order_items_cached(order_id)

                        if items:
                            calixta_table(
                                pd.DataFrame(items),
                                key=f"order_items_{order_id}",
                                paginate=len(items) > 10,
                            )

                        current = orders[orders["id"] == order_id].iloc[0]
                        st.caption(f"Dirección: {current.get('direccion_entrega', '')}")

                        order_dict = current.to_dict()
                        allowed_states = get_allowed_next_states(order_dict)
                        new_status = st.selectbox(
                            "Nuevo estado",
                            allowed_states,
                            key="new_status_sel",
                        )
                        fecha_entrega = None
                        if state_requires_sale_date(new_status):
                            c1, c2 = st.columns(2)
                            entrega_date = c1.date_input("Fecha de venta", value=date.today())
                            entrega_time = c2.time_input("Hora de venta", value=datetime.now().time())
                            fecha_entrega = f"{entrega_date} {entrega_time.strftime('%H:%M:%S')}"

                        if st.button("Actualizar estado", type="primary", key="update_status_btn"):
                            try:
                                update_order_status(order_id, new_status, fecha_entrega)
                                st.success(f"Pedido {order_id} → {new_status}")
                                clear_search_select("status_order_sel")
                                _refresh_and_rerun()
                            except Exception as exc:
                                st.error(str(exc))

        with tab_delete:
            deletable = list_editable_orders()

            if deletable.empty:
                st.info("No hay pedidos que se puedan eliminar.")
            else:
                options = {
                    f"{row['id']} | {row['cliente_nombre']} | {row['estado']}": row["id"]
                    for _, row in deletable.iterrows()
                }
                order_id = search_select(
                    "Buscar pedido",
                    options,
                    key="delete_order_sel",
                    placeholder="Buscar por ID de pedido, cliente o estado…",
                )
                if order_id is not None:
                    st.warning("Esta acción no se puede deshacer.")

                    if st.button("Eliminar pedido", type="primary", key="delete_order_btn"):
                        try:
                            delete_order(order_id)
                            st.success(f"Pedido {order_id} eliminado.")
                            clear_search_select("delete_order_sel")
                            _refresh_and_rerun()
                        except Exception as exc:
                            st.error(str(exc))


def page_sales() -> None:
    page_header("Ventas", "Historial generado automáticamente al entregar pedidos")

    with page_section():
        st.caption(
            "Las ventas se crean al marcar un pedido como Entregado. "
            "No se pueden crear ni editar manualmente."
        )

        sales = load_sales()
        customers = load_customers()
        products = load_products()

        with panel_card("Filtros", accent="sage"):
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
            fecha_desde_val = c4.date_input(
                "Desde", value=date.today().replace(day=1), disabled=not use_date_filter
            )
            fecha_hasta_val = c5.date_input(
                "Hasta", value=date.today(), disabled=not use_date_filter
            )

        cliente_id = None
        if cliente_filter != "Todos":
            cliente_id = cliente_filter.split("(")[-1].rstrip(")")

        producto_id = None
        if producto_filter != "Todos":
            ref = producto_filter.split(" | ")[0]
            match = products[products["referencia"] == ref]
            if not match.empty:
                producto_id = match.iloc[0]["id"]

        filtered = filter_sales(
            sales,
            cliente_id=cliente_id,
            producto_id=producto_id,
            pedido_id=pedido_filter or None,
            fecha_desde=str(fecha_desde_val) if use_date_filter else None,
            fecha_hasta=str(fecha_hasta_val) + " 23:59:59" if use_date_filter else None,
        )

        with panel_card("Historial de ventas", accent="olive"):
            if filtered.empty:
                st.info("No hay ventas que coincidan con los filtros.")
            else:
                total = float(filtered["subtotal"].sum())
                st.metric("Total filtrado", format_cop(total))
                display = filtered.copy()
                display["precio_unitario"] = display["precio_unitario"].apply(format_cop)
                display["subtotal"] = display["subtotal"].apply(format_cop)
                calixta_table(display, key="sales_list")


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

    with page_section():
        alerts = load_low_stock_alerts()
        with panel_card("Inventario crítico", accent="pink"):
            if alerts.empty:
                st.success("Todo en orden. No hay productos con stock bajo.")
            else:
                st.warning(f"{len(alerts)} producto(s) por debajo del stock mínimo.")
                display = alerts.copy()
                display["precio"] = display["precio"].apply(format_cop)
                calixta_table(
                    display[
                        ["referencia", "nombre", "talla", "color", "categoria",
                         "stock", "stock_minimo", "faltante", "precio"]
                    ],
                    key="alerts_list",
                )
                _render_email_alert_button(alerts)


def main() -> None:
    with nav_layout() as page:
        if not init_connection():
            st.stop()

        pages = {
            "dashboard": page_dashboard,
            "productos": page_products,
            "clientes": page_customers,
            "pedidos": page_orders,
            "ventas": page_sales,
            "contabilidad": page_contabilidad,
            "administracion": page_administracion,
            "alertas": page_alerts,
        }
        pages[page]()


if __name__ == "__main__":
    main()
