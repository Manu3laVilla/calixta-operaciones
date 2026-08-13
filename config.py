import os
from pathlib import Path

from utils.settings import BASE_DIR, get_env

CREDENTIALS_PATH = get_env(
    "GOOGLE_CREDENTIALS_PATH",
    str(BASE_DIR / "credentials" / "service_account.json"),
)
SPREADSHEET_ID = get_env("SPREADSHEET_ID", "")

SMTP_HOST = get_env("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(get_env("SMTP_PORT", "587"))
SMTP_USER = get_env("SMTP_USER", "")
SMTP_PASSWORD = get_env("SMTP_PASSWORD", "")
ALERT_EMAIL_TO = get_env("ALERT_EMAIL_TO", "calixtaa.co@gmail.com")

SHEET_PRODUCTOS = "Productos"
SHEET_CLIENTES = "Clientes"
SHEET_VENTAS = "Ventas"
SHEET_PEDIDOS = "Pedidos"
SHEET_CONTABILIDAD = "Contabilidad"

MOVEMENT_TYPE_INCOME = "Ingreso"
MOVEMENT_TYPE_EXPENSE = "Gasto"
MOVEMENT_TYPES = [MOVEMENT_TYPE_INCOME, MOVEMENT_TYPE_EXPENSE]

INCOME_CATEGORIES = ["Capital", "Inversión", "Otros ingresos"]
EXPENSE_CATEGORIES = ["Insumos", "Equipos", "Otros gastos"]

SIZES = ["XS", "S", "M", "L", "XL", "Talla Única"]
CATEGORIES = ["Ropa", "Accesorio"]

ORDER_STATES = [
    "Recibido",
    "Pago Confirmado",
    "Envío Agendado",
    "Entregado",
]

DELIVERED_STATE = "Entregado"

SHEET_SCHEMAS = {
    SHEET_PRODUCTOS: [
        "id",
        "referencia",
        "nombre",
        "color",
        "talla",
        "categoria",
        "descripcion",
        "stock",
        "stock_minimo",
        "precio",
        "activo",
        "fecha_registro",
    ],
    SHEET_CLIENTES: [
        "id",
        "nombre",
        "email",
        "telefono",
        "direccion",
        "notas",
        "fecha_registro",
    ],
    SHEET_VENTAS: [
        "id",
        "fecha_entrega",
        "pedido_id",
        "cliente_id",
        "cliente_nombre",
        "producto_id",
        "referencia",
        "producto_nombre",
        "color",
        "talla",
        "cantidad",
        "precio_unitario",
        "subtotal",
    ],
    SHEET_PEDIDOS: [
        "id",
        "cliente_id",
        "cliente_nombre",
        "items_json",
        "total",
        "estado",
        "direccion_entrega",
        "fecha_entrega",
        "fecha_creacion",
        "fecha_actualizacion",
        "notas",
    ],
    SHEET_CONTABILIDAD: [
        "id",
        "fecha",
        "tipo",
        "categoria",
        "concepto",
        "monto",
        "notas",
        "fecha_registro",
        "fecha_actualizacion",
    ],
}
