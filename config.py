import os
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/prueba")
API_KEY = os.getenv("API_KEY", "")
TIMEOUT = float(os.getenv("TIMEOUT", "500.0"))
REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")
SESSION_PREFIX = os.getenv("SESSION_PREFIX", "session_")
