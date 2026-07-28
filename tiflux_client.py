"""
Client fino para a API do Tiflux. Responsabilidade única: criar um
chamado a partir de um payload já pronto. Não sabe nada sobre e-mail
nem sobre Graph — se amanhã a fonte dos dados mudar (outro sistema
além de e-mail), este arquivo não deveria precisar mudar.
"""
import requests

from config import TIFLUX_TOKEN, TIFLUX_BASE_URL, TIFLUX_DESK_ID


def create_ticket(titulo: str, descricao: str) -> dict:
    """
    TODO: conferir na documentação da API do Tiflux quais campos são
    obrigatórios além de título/descrição (categoria, cliente,
    prioridade, responsável, tipo de chamado?). Ajuste o payload abaixo
    de acordo — hoje ele só tem o mínimo que eu sei que provavelmente
    existe.
    """
    headers = {"Authorization": f"Bearer {TIFLUX_TOKEN}"}
    payload = {
        "desk_id": TIFLUX_DESK_ID,
        "title": titulo,
        "description": descricao,
        # TODO: demais campos obrigatórios da API do Tiflux
    }
    response = requests.post(
        f"{TIFLUX_BASE_URL}/tickets", headers=headers, json=payload, timeout=30
    )
    response.raise_for_status()
    return response.json()
