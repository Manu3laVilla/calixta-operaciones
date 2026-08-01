# Calixta | Centro de Operaciones

Sistema de inventario y ventas con **Google Sheets** como base de datos.

## Funcionalidades

- Registro y edición de **productos**
- Registro de **clientes**
- Registro de **ventas** con descuento automático de stock
- Gestión de **pedidos** con estados
- **Alertas** por stock bajo (con notificación por correo)
- **Dashboard** con métricas y resumen

## Requisitos

- Python 3.10+
- Cuenta de Google
- Proyecto en Google Cloud con Sheets API habilitada

## 1. Configurar Google Sheets API

### Paso A: Crear proyecto en Google Cloud

1. Entra a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo (ej: `calixta-operaciones`)
3. Ve a **APIs y servicios > Biblioteca**
4. Busca y habilita:
   - **Google Sheets API**
   - **Google Drive API**

### Paso B: Crear Service Account

1. Ve a **APIs y servicios > Credenciales**
2. Clic en **Crear credenciales > Cuenta de servicio**
3. Asigna un nombre (ej: `calixta-sheets`)
4. En la cuenta creada, ve a la pestaña **Claves**
5. **Agregar clave > Crear clave nueva > JSON**
6. Guarda el archivo descargado como:

```
credentials/service_account.json
```

### Paso C: Crear la hoja de cálculo

1. Crea una hoja nueva en [Google Sheets](https://sheets.google.com)
2. Copia el **ID** de la URL:

```
https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
```

3. **Comparte la hoja** con el email del Service Account  
   (aparece en el JSON como `client_email`) con permiso de **Editor**

## 2. Instalar y ejecutar

```bash
cd calixta-centro-operaciones
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edita `.env`:

```env
GOOGLE_CREDENTIALS_PATH=credentials/service_account.json
SPREADSHEET_ID=tu_id_de_la_hoja
```

Ejecuta la app:

```bash
streamlit run app.py
```

La app creará automáticamente las pestañas:

| Pestaña   | Contenido                          |
|-----------|------------------------------------|
| Productos | Inventario                         |
| Clientes  | Cartera de clientes                |
| Ventas    | Historial de ventas                |
| Pedidos   | Pedidos y estados                  |

## 3. Configurar alertas por correo (Gmail)

1. Activa la verificación en 2 pasos en la cuenta `calixtaa.co@gmail.com`
2. Crea una **Contraseña de aplicación** en [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Agrega estas variables a tu `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=calixtaa.co@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
ALERT_EMAIL_TO=calixtaa.co@gmail.com
```

4. En la app, ve a **Alertas de stock** y haz clic en **Enviar alerta por correo**

## 4. Estados de pedidos

- Recibido
- Pago Confirmado
- Envío Agendado
- Entregado

Al marcar un pedido como **Entregado**, se descuenta el stock y se generan las ventas automáticamente.

## 5. Despliegue (opcional)

Puedes desplegar gratis en [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Sube el repo a GitHub (sin subir `credentials/` ni `.env`)
2. En Streamlit Cloud, agrega los secrets con el contenido del JSON y el `SPREADSHEET_ID`

## Estructura del proyecto

```
calixta-centro-operaciones/
├── app.py                  # Interfaz principal
├── config.py               # Configuración y esquemas
├── services/
│   ├── sheets_db.py        # Conexión a Google Sheets
│   ├── product_service.py
│   ├── customer_service.py
│   ├── sale_service.py
│   ├── order_service.py
│   ├── alert_service.py
│   └── email_service.py
├── credentials/            # Credenciales (no subir a git)
└── requirements.txt
```

## Notas

- Las ventas descuentan stock automáticamente.
- Las alertas se activan cuando `stock <= stock_minimo`.
- Puedes ver y editar los datos directamente en Google Sheets.
