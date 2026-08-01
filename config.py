import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS_PATH",
    str(BASE_DIR / "credentials" / "service_account.json"),
)
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "calixtaa.co@gmail.com")

SHEET_PRODUCTOS = "Productos"
SHEET_CLIENTES = "Clientes"
SHEET_VENTAS = "Ventas"
SHEET_PEDIDOS = "Pedidos"

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
}
