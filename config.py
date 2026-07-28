"""
Carrega configuração da aplicação a partir de variáveis de ambiente.
Nunca commitar valores reais — use um .env local (fora do git, veja
.env.example) ou variáveis de ambiente do agendador de tarefas.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Pasta do projeto — usada como base para os defaults de arquivo
# abaixo, para não depender do diretório de onde o processo é
# iniciado (o Task Scheduler pode iniciar em outra pasta).
_BASE_DIR = Path(__file__).resolve().parent

# --- Microsoft Graph (app-only / client credentials) ---
GRAPH_TENANT_ID = os.environ["GRAPH_TENANT_ID"]
GRAPH_CLIENT_ID = os.environ["GRAPH_CLIENT_ID"]
GRAPH_CLIENT_SECRET = os.environ["GRAPH_CLIENT_SECRET"]

# Caixa de entrada monitorada (ex.: rh@suaempresa.com.br)
MAILBOX_USER = os.environ["MAILBOX_USER"]

# --- Tiflux (API v1 — a v2 não está disponível para esta conta) ---
TIFLUX_TOKEN = os.environ["TIFLUX_TOKEN"]
TIFLUX_API_EMAIL = os.environ["TIFLUX_API_EMAIL"]
TIFLUX_BASE_URL = os.environ.get("TIFLUX_BASE_URL", "https://api.tiflux.com/api/v1")
TIFLUX_DESK_ID = int(os.environ["TIFLUX_DESK_ID"])
TIFLUX_CLIENT_ID = int(os.environ["TIFLUX_CLIENT_ID"])
TIFLUX_PRIORITY_ID = int(os.environ["TIFLUX_PRIORITY_ID"])

# Solicitante fixo usado em todo ticket criado por esta automação
TIFLUX_REQUESTOR_NAME = os.environ["TIFLUX_REQUESTOR_NAME"]
TIFLUX_REQUESTOR_EMAIL = os.environ["TIFLUX_REQUESTOR_EMAIL"]
TIFLUX_REQUESTOR_PHONE_RAW = os.environ["TIFLUX_REQUESTOR_PHONE_RAW"]

# Janela de busca de e-mails: sempre "agora - LOOKBACK_HOURS" (ver state_store.py)
LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", "48"))

# Onde a automação loga falhas (ver alerting.py). Alerta por e-mail
# está pendente da permissão Mail.Send — ver README.
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", str(_BASE_DIR / "automacao.log"))

# Onde fica o "estado" da automação entre execuções (ver state_store.py)
STATE_FILE_PATH = os.environ.get("STATE_FILE_PATH", str(_BASE_DIR / "state.json"))
