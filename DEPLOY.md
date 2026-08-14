# Despliegue en Streamlit Community Cloud

Guía paso a paso para publicar **Calixta Centro de Operaciones** gratis.

## Requisitos previos

- Repositorio en GitHub: https://github.com/Manu3laVilla/calixta-operaciones
- Google Sheets configurado con Service Account
- Cuenta en [share.streamlit.io](https://share.streamlit.io)

---

## Paso 1: Preparar el JSON del Service Account

1. Abre el archivo `credentials/service_account.json` en tu PC (no lo subas a GitHub).
2. Copia **todo** el contenido del JSON.
3. Lo usarás en el Paso 4 para rellenar la sección `[gcp_service_account]`.

---

## Paso 2: Crear la app en Streamlit Cloud

1. Entra a **[share.streamlit.io](https://share.streamlit.io)** e inicia sesión con **GitHub**.
2. Clic en **Create app**.
3. Configura:
   - **Repository:** `Manu3laVilla/calixta-operaciones`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Clic en **Advanced settings** (opcional):
   - Python version: **3.12** (recomendado)
5. **Aún no despliegues** — primero configura los Secrets.

---

## Paso 3: Obtener tu SPREADSHEET_ID

En la URL de tu hoja de Google Sheets:

```
https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
```

Copia ese ID.

---

## Paso 4: Configurar Secrets

1. En Streamlit Cloud, ve a tu app → **Settings** → **Secrets**.
2. Pega el contenido adaptado (usa `.streamlit/secrets.toml.example` como guía):

```toml
SPREADSHEET_ID = "pega_tu_id_de_la_hoja"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "calixtaa.co@gmail.com"
SMTP_PASSWORD = "tu_contraseña_de_aplicacion_de_16_caracteres"
ALERT_EMAIL_TO = "calixtaa.co@gmail.com"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

### Importante sobre `private_key`

- Debe estar en **una sola línea** con `\n` donde hay saltos de línea.
- Ejemplo: `"-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n"`
- Copia los valores exactos desde tu `service_account.json`.

3. Clic en **Save**.

---

## Paso 5: Desplegar

1. Ve a **Deploy** o haz clic en **Reboot app** si ya estaba creada.
2. Espera 2–5 minutos mientras instala dependencias.
3. Cuando termine, verás una URL como:

```
https://calixta-operaciones.streamlit.app
```

¡Esa es la URL para compartir con tu equipo (2–3 personas)!

---

## Paso 6: Verificar

- [ ] La app carga sin error de Google Sheets
- [ ] Ves el Dashboard con datos (o vacío si es hoja nueva)
- [ ] Puedes crear un producto de prueba
- [ ] El producto aparece en Google Sheets

---

## Notas

| Tema | Detalle |
|------|---------|
| **Datos** | Siguen en Google Sheets; local y cloud usan la misma hoja |
| **Costo** | Gratis en Streamlit Community Cloud |
| **Inactividad** | La app duerme tras ~15 min; el primer acceso tarda unos segundos |
| **Privacidad** | La URL es pública; no la compartas fuera de tu equipo |
| **Secrets** | Nunca subas `.env` ni `service_account.json` a GitHub |

---

## Si algo falla

| Error | Solución |
|-------|----------|
| `SPREADSHEET_ID` faltante | Revisa Secrets en Streamlit Cloud |
| Credenciales inválidas | Verifica `[gcp_service_account]` y los `\n` en `private_key` |
| Hoja no encontrada | Comparte la hoja con el `client_email` del service account |
| Error SMTP | Revisa contraseña de aplicación de Gmail |

---

## Actualizar la app

Cada vez que hagas `git push` a `main`, Streamlit Cloud redespliega automáticamente.

---

## Alertas automáticas por correo (GitHub Actions)

Los envíos programados (1–3 veces al día) los ejecuta un workflow de GitHub Actions, no Streamlit Cloud.

### Paso A: Migración en Supabase

Ejecuta en el SQL Editor de Supabase el archivo:

`supabase/migrations/20260814_alertas_email_config.sql`

### Paso B: Configurar en la app

1. **Administración → Alertas por correo**
2. Agrega destinatarios activos
3. Activa **Envío automático** y define horarios (zona `America/Bogota`)

SMTP sigue en `.env` local y en Streamlit Secrets (igual que el envío manual).

### Paso C: Secrets en GitHub

En el repositorio → **Settings → Secrets and variables → Actions**, crea:

| Secret | Uso |
|--------|-----|
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role (misma que local) |
| `SMTP_HOST` | p. ej. `smtp.gmail.com` |
| `SMTP_PORT` | p. ej. `587` |
| `SMTP_USER` | Cuenta Gmail |
| `SMTP_PASSWORD` | Contraseña de aplicación |
| `ALERT_EMAIL_TO` | Respaldo si no hay destinatarios en BD |

### Paso D: Workflow

El archivo `.github/workflows/scheduled-stock-alerts.yml` corre **cada 5 minutos** (UTC). El script solo envía si:

- El envío automático está activo en Administración
- La hora actual cae en la ventana ±25 min de un horario configurado
- Ese slot no se procesó ya hoy en esa misma ventana horaria

Prueba manual desde GitHub: **Actions → Scheduled stock alerts → Run workflow**.

Prueba local:

```bash
python scripts/send_scheduled_alerts.py --json
python scripts/send_scheduled_alerts.py --force --json
```
