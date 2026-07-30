"""
Client fino para a API v1 do Tiflux. Responsabilidade única: criar um
chamado a partir de um payload já pronto. Não sabe nada sobre e-mail
nem sobre Graph — se amanhã a fonte dos dados mudar (outro sistema
além de e-mail), este arquivo não deveria precisar mudar.

A API v1 usa Basic Auth (email:senha de um "Usuário API" cadastrado
em Tiflux > Configurações > Integrações > Dados), não Bearer.
"""
import requests

from config import (
    TIFLUX_TOKEN,
    TIFLUX_API_EMAIL,
    TIFLUX_BASE_URL,
    TIFLUX_DESK_ID,
    TIFLUX_CLIENT_ID,
    TIFLUX_PRIORITY_ID,
    TIFLUX_REQUESTOR_NAME,
    TIFLUX_REQUESTOR_EMAIL,
    TIFLUX_REQUESTOR_PHONE_RAW,
)


class TifluxApiError(Exception):
    pass


def _normalize_phone_e164(raw: str, default_ddi: str = "55") -> str:
    raw = raw.strip()
    if raw.startswith("+"):
        return raw
    digits = "".join(ch for ch in raw if ch.isdigit())
    return f"+{default_ddi}{digits}"


def create_ticket(titulo: str, descricao: str) -> dict:
    payload = {
        "client_id": TIFLUX_CLIENT_ID,
        "desk_id": TIFLUX_DESK_ID,
        "priority_id": TIFLUX_PRIORITY_ID,
        "title": titulo,
        "description": descricao,
        "requestor": {
            "name": TIFLUX_REQUESTOR_NAME,
            "email": TIFLUX_REQUESTOR_EMAIL,
            "telephone": {"number": _normalize_phone_e164(TIFLUX_REQUESTOR_PHONE_RAW)},
        },
    }
    response = requests.post(
        f"{TIFLUX_BASE_URL}/tickets",
        auth=(TIFLUX_API_EMAIL, TIFLUX_TOKEN),
        json=payload,
        timeout=30,
    )
    if not response.ok:
        raise TifluxApiError(f"Tiflux retornou {response.status_code} ao criar chamado: {response.text}")
    return response.json()
