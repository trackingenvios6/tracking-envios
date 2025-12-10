"""
Módulo de configuración de variables globales para la integración con n8n.

Este archivo centraliza parámetros leídos desde variables de entorno y valores
por defecto utilizados por el sistema. Su propósito es evitar valores
dispersos en el código y facilitar su modificación en entornos de desarrollo,
testing o producción.

Variables:
N8N_WEBHOOK_URL (str): URL del webhook de n8n. Puede configurarse con la
variable de entorno 'N8N_WEBHOOK_URL'. Si no se define, se usa una URL
local por defecto.

```
API_KEY (str): Clave opcional para autenticación en n8n. Proviene de la
    variable de entorno 'API_KEY'.

TIMEOUT (float): Tiempo máximo permitido para esperar una respuesta HTTP.
    Se obtiene desde la variable de entorno 'TIMEOUT'; si no existe, se
    usa 500.0 segundos como valor de seguridad.

REPORTS_DIR (str): Directorio donde se guardarán reportes generados.
    Configurable mediante 'REPORTS_DIR'. El valor por defecto es './reports'.

SESSION_PREFIX (str): Prefijo estándar usado para la generación de IDs de
    sesión en las conversaciones. Configurable por variable de entorno.
```

"""

import os

# URL del webhook de n8n (entorno → fallback local)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/piki")

# API Key opcional para autenticación (string vacío si no está definida)
API_KEY = os.getenv("API_KEY", "")

# Timeout para solicitudes HTTP (convertido explícitamente a float)

TIMEOUT = float(os.getenv("TIMEOUT", "120.0"))

# Carpeta donde se almacenarán reportes generados

REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")

# Prefijo usado para generar IDs únicos de sesión

SESSION_PREFIX = os.getenv("SESSION_PREFIX", "session_")
