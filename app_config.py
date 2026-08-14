from utils.settings import get_env

SMTP_HOST = get_env("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(get_env("SMTP_PORT", "587"))
SMTP_USER = get_env("SMTP_USER", "").strip()
SMTP_PASSWORD = get_env("SMTP_PASSWORD", "").strip().replace(" ", "")
ALERT_EMAIL_TO = get_env("ALERT_EMAIL_TO", "calixtaa.co@gmail.com").strip()

TABLE_PRODUCTOS = "productos"
TABLE_CLIENTES = "clientes"
TABLE_VENTAS = "ventas"
TABLE_PEDIDOS = "pedidos"
TABLE_PEDIDO_ITEMS = "pedido_items"
TABLE_CONTABILIDAD = "contabilidad"
TABLE_TIPOS_PRODUCTO = "tipos_producto"
TABLE_TIPOS_INGRESO = "tipos_ingreso"
TABLE_TIPOS_GASTO = "tipos_gasto"
TABLE_ESTADOS_PEDIDO = "estados_pedido"
TABLE_CONFIG_ALERTAS_EMAIL = "config_alertas_email"
TABLE_ALERTAS_DESTINATARIOS = "alertas_destinatarios"
TABLE_ALERTAS_ENVIOS_LOG = "alertas_envios_log"

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
