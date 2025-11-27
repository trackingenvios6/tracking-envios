# Sistema de Tracking de Envíos - Piki 📦

Sistema de consulta y reporte de envíos que se comunica con n8n para procesar 
solicitudes y generar reportes de manera inteligente.

## 📋 Tabla de Contenidos

- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Arquitectura](#-arquitectura)
- [Módulos](#-módulos)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Solución de Problemas](#-solución-de-problemas)

## ✨ Funcionalidades

- 🔍 **Consultar estado de envíos** - Busca información detallada de un envío por código
- 📊 **Reportes de envíos fallidos** - Genera reportes completos de envíos con problemas
- 🚚 **Reportes por repartidor/localidad** - Filtra envíos por criterios específicos
- 💬 **Consultas personalizadas** - Usa lenguaje natural para hacer preguntas sobre tus datos
- ☁️ **Compartir reportes** - Exporta y comparte vía Drive, Gmail o Sheets
- 💾 **Exportación local** - Descarga reportes en formato Excel (.xlsx) o CSV

## 🔧 Requisitos

### 1. Python
- **Python 3.10 o superior**
- Se recomienda utilizar un entorno virtual (venv)

### 2. Dependencias del proyecto

Las dependencias principales son:
- `pandas` - Procesamiento y análisis de datos
- `requests` - Comunicación con APIs y webhooks
- `openpyxl` - Generación de archivos Excel

**Instalación directa:**
```bash
pip install pandas requests openpyxl
```

**O usando requirements.txt:**
```bash
pip install -r requirements.txt
```

### 3. Conexión a Internet
- Requerida para comunicación con n8n y servicios externos
- APIs de compartir (Drive, Gmail, Sheets)

### 4. Permisos del sistema
- ✅ Lectura/escritura de archivos Excel/CSV
- ✅ Lectura/escritura de archivos JSON de configuración
- ✅ Ejecución desde consola/terminal

## 📥 Instalación

### Paso 1: Clonar o descargar el proyecto
```bash
git clone <url-del-repositorio>
cd tracking-envios
```

### Paso 2: Crear entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno
Crea un archivo `.env` o configura `config.py` con:
- URL del webhook de n8n
- Directorio de reportes (opcional)
- Otras configuraciones personalizadas

## ⚙️ Configuración

### Archivo `config.py`

```python
# URL del webhook de n8n
N8N_WEBHOOK_URL = "https://tu-instancia.n8n.cloud/webhook/..."

# Directorio para guardar reportes (opcional)
REPORTS_DIR = "C:\\Users\\TuUsuario\\Documents\\Reportes"
```

### Variables de entorno (opcional)
También puedes usar variables de entorno:
```bash
export N8N_WEBHOOK_URL="https://..."
export REPORTS_DIR="/ruta/a/reportes"
```

## 🚀 Uso

### Ejecución del programa
```bash
python main.py
```

### Menú Principal

Al iniciar el programa verás:

```
=== Bienvenido a Piki. Tu envío, sin estrés. ===
[1] Consultar estado de un envío
[2] Generar reporte para compartir
[3] Consulta personalizada
[4] Generar reporte local
[0] Salir
```

### Flujo de uso típico

1. **Consultar un envío:**
   - Selecciona opción `1`
   - Ingresa el código de envío (ej: `ABC123`)
   - Visualiza el estado y detalles

2. **Generar reporte local:**
   - Selecciona opción `4`
   - Elige tipo de reporte (fallidos, repartidores, personalizado)
   - Selecciona formato (Excel o CSV)
   - Elige carpeta de destino

3. **Compartir reporte:**
   - Selecciona opción `2`
   - Elige tipo de reporte
   - Selecciona plataforma (Drive/Gmail/Sheets)
   - Ingresa email de destino

4. **Consulta personalizada:**
   - Selecciona opción `3`
   - Escribe tu consulta en lenguaje natural
   - Ej: *"¿Cuántos envíos fallidos hay en Buenos Aires?"*

## 📁 Estructura del Proyecto

```
tracking-envios/
│
├── main.py                  # Punto de entrada principal
├── n8n_client.py           # Cliente para comunicación con n8n
├── data_models.py          # Modelos de datos (clases Pydantic)
├── report_generator.py     # Generación de reportes Excel/CSV
├── error_handler.py        # Manejo centralizado de errores
├── config.py               # Configuración del sistema
│
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Este archivo
│
└── reportes/              # Directorio de reportes (generado)
    ├── reporte_envios_fallidos_20231124_153045.xlsx
    └── reporte_localidad_repartidor_20231124_154210.csv
```

## 🏗️ Arquitectura

El sistema sigue una arquitectura modular:

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│           main.py                    │
│  (Interfaz de usuario + Menús)      │
└──────┬──────────────────────┬───────┘
       │                      │
       ▼                      ▼
┌──────────────┐      ┌──────────────────┐
│ n8n_client   │      │ report_generator │
│              │      │                  │
│ - Enviar     │      │ - Normalizar     │
│ - Recibir    │      │ - Generar Excel  │
│ - Validar    │      │ - Generar CSV    │
└──────┬───────┘      └──────────────────┘
       │
       ▼
┌──────────────┐
│  n8n Server  │
│  (Webhook)   │
└──────────────┘
```

### Flujo de datos

1. **Usuario** ingresa consulta en `main.py`
2. `main.py` crea una `SolicitudN8n` usando `data_models`
3. `n8n_client` envía la solicitud al webhook de n8n
4. **n8n** procesa la consulta (IA, base de datos, etc.)
5. `n8n_client` recibe y valida la respuesta
6. `error_handler` normaliza errores y mensajes
7. `report_generator` crea archivos Excel/CSV (si aplica)
8. **Usuario** recibe resultado formateado

## 📚 Módulos

### `main.py`
**Módulo principal** que contiene:
- Menús interactivos
- Lógica de navegación
- Funciones de consulta y reporte
- Validación de entrada de usuario

**Funciones clave:**
- `main()` - Punto de entrada
- `consultar_estado_envio()` - Consulta individual
- `generar_reporte_envios_fallidos()` - Reporte de fallidos
- `consulta_personalizada_directa()` - Consultas en lenguaje natural

### `n8n_client.py`
**Cliente HTTP** para comunicación con n8n:
- Genera IDs de sesión únicos
- Envía solicitudes POST al webhook
- Valida respuestas
- Manejo de timeouts y errores de red

**Funciones clave:**
- `nuevo_id_sesion()` - Genera UUID único
- `enviar_consulta()` - Envía solicitud a n8n

### `data_models.py`
**Modelos de datos** usando Pydantic:
- `SolicitudN8n` - Estructura de solicitudes
- `RespuestaN8n` - Estructura de respuestas
- Validación automática de tipos

### `report_generator.py`
**Generación de reportes**:
- Normalización de datos a DataFrame
- Exportación a Excel (.xlsx)
- Exportación a CSV
- Vista previa de datos
- Selección de carpeta con diálogo gráfico

**Funciones clave:**
- `generar_reporte()` - Función principal
- `solicitar_configuracion_salida()` - UI para configuración

### `error_handler.py`
**Manejo centralizado de errores**:
- Validación de respuestas de n8n
- Normalización de registros
- Mensajes de error personalizados
- Helpers para mostrar información al usuario

**Funciones clave:**
- `validar_respuesta_n8n()` - Valida y normaliza respuestas
- `normalizar_registros_respuesta()` - Extrae datos de respuestas
- `obtener_mensaje_desde_data()` - Extrae mensajes de IA

### `config.py`
**Configuración del sistema**:
- URL del webhook de n8n
- Directorio de reportes
- Timeout de conexión
- Variables de entorno

## 💡 Ejemplos de Uso

### Ejemplo 1: Consultar estado de envío
```
Seleccione una opción: 1
Ingrese el código de envío: ABC123

Estado: En tránsito
Destino: Buenos Aires, Argentina
Repartidor: Juan Pérez
Última actualización: 2023-11-24 15:30
```

### Ejemplo 2: Reporte de envíos fallidos
```
Seleccione una opción: 4
Seleccione una opción: 1

=== Vista previa del reporte ===
  codigo     destino        estado       fecha
  ABC123     Buenos Aires   Fallido      2023-11-24
  XYZ789     Córdoba        Fallido      2023-11-23
... (15 filas en total)

=== Seleccione el formato del reporte ===
[1] Excel (.xlsx)
[2] CSV (.csv)
Opción: 1

Archivo guardado en: C:\Users\...\reporte_envios_fallidos_20231124_153045.xlsx
```

### Ejemplo 3: Consulta personalizada
```
Seleccione una opción: 3
Ingrese su consulta en lenguaje natural: ¿Cuántos envíos hay en Buenos Aires?

Hay 342 envíos en Buenos Aires. De estos:
- 298 están en tránsito
- 38 fueron entregados
- 6 están fallidos
```

### Ejemplo 4: Compartir reporte en Gmail
```
Seleccione una opción: 2
Seleccione una opción: 1  (Reporte de envíos fallidos)

=== Seleccione la plataforma para compartir ===
[1] Drive
[2] Gmail
[3] Sheets
Opción: 2

Ingrese el correo electrónico para la notificación: gerencia@empresa.com

Reporte enviado exitosamente a gerencia@empresa.com
```

## 🔍 Solución de Problemas

### Error: "No se puede conectar con n8n"

**Causas posibles:**
- URL de webhook incorrecta en `config.py`
- n8n está desconectado o no accesible
- Problemas de red/firewall

**Solución:**
1. Verifica la URL en `config.py`
2. Prueba acceder al webhook desde el navegador
3. Verifica tu conexión a internet

### Error: "ModuleNotFoundError: No module named 'pandas'"

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "Permission denied" al guardar reportes

**Causa:** Sin permisos de escritura en el directorio

**Solución:**
1. Verifica permisos de la carpeta en `config.py`
2. Usa el diálogo de selección de carpeta
3. Cambia el directorio a uno con permisos

### Los reportes están vacíos

**Causas posibles:**
- No hay datos que coincidan con el filtro
- Error en la consulta a n8n
- Respuesta de n8n en formato inesperado

**Solución:**
1. Verifica que existan datos para tu consulta
2. Revisa los mensajes de n8n
3. Prueba con una consulta más amplia

### Tkinter no disponible (Linux)

**Causa:** tkinter no instalado en el sistema

**Solución:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, contacta al equipo de desarrollo.

---

**Desarrollado para Piki** - Tu envío, sin estrés 📦✨