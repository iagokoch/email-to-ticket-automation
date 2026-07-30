"""
Guarda o que já foi processado, para a automação não abrir chamado
duplicado se rodar de novo sobre o mesmo e-mail (reinício do script,
sobreposição entre execuções agendadas, etc.).

Não existe cursor de "última execução" persistido: load_last_run_iso()
sempre devolve "agora - LOOKBACK_HOURS". Isso evita o bug clássico de
o cursor avançar mesmo quando uma execução falha (e um e-mail nunca
mais ser buscado) — o dedupe de verdade é via processed_ids. O
"receivedDateTime" de cada id processado é guardado só para podar
entradas mais velhas que a janela de lookback a cada execução, senão
state.json cresceria pra sempre.

Limitação aceita: se a automação ficar mais de LOOKBACK_HOURS sem
rodar com sucesso, um e-mail poderia ser perdido. Dado o agendamento
2x/dia, isso exigiria falha total por mais de 2 dias.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import STATE_FILE_PATH, LOOKBACK_HOURS


def _load_raw() -> dict:
    path = Path(STATE_FILE_PATH)
    if not path.exists():
        return {"processed": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"processed": {}}  # state.json corrompido: reseta em vez de derrubar a execução


def load_processed_ids() -> set[str]:
    return set(_load_raw().get("processed", {}).keys())


def load_last_run_iso() -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    return cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_processed(message_id: str, received_iso: str) -> None:
    data = _load_raw()
    data.setdefault("processed", {})[message_id] = received_iso
    _prune_old_entries(data)
    _save_atomic(data)


def _prune_old_entries(data: dict) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    kept = {}
    for message_id, received in data.get("processed", {}).items():
        try:
            received_dt = datetime.fromisoformat(received.replace("Z", "+00:00"))
        except ValueError:
            continue  # entrada corrompida, descarta na poda
        if received_dt >= cutoff:
            kept[message_id] = received
    data["processed"] = kept


def _save_atomic(data: dict) -> None:
    path = Path(STATE_FILE_PATH)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, path)  # atômico e sobrescreve em Windows (Path.rename falharia se já existir)
