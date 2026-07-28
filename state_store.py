"""
Guarda o que já foi processado, para a automação não abrir chamado
duplicado se rodar de novo sobre o mesmo e-mail (reinício do script,
sobreposição entre execuções agendadas, etc.).

Um arquivo JSON local é suficiente para o volume esperado desse
processo. Se um dia isso rodar em mais de uma máquina ao mesmo tempo,
precisaria virar algo compartilhado (banco, storage) — não é o caso
agora, então não vale a complexidade de antecipar isso.
"""
import json
from pathlib import Path

from config import STATE_FILE_PATH


def load_processed_ids() -> set[str]:
    path = Path(STATE_FILE_PATH)
    if not path.exists():
        return set()
    return set(json.loads(path.read_text()).get("processed_ids", []))


def load_last_run_iso() -> str | None:
    """TODO: ler o timestamp da última execução bem-sucedida, salvo pela
    mesma lógica de mark_processed. Usado por main.py como `since_iso`
    na busca de novos e-mails."""
    raise NotImplementedError


def mark_processed(message_id: str) -> None:
    """
    TODO: implementar a escrita de forma que não corrompa o arquivo se
    o processo for interrompido no meio (ex.: escrever em um arquivo
    temporário e só então renomear por cima do original — não escrever
    direto em cima do state.json existente).
    """
    raise NotImplementedError
