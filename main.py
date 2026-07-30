"""
Orquestra o fluxo. De propósito, não deveria ter lógica de negócio —
só decide a ordem das chamadas e trata erro de alto nível. Se você
sentir vontade de colocar parsing ou regra do Tiflux aqui, é sinal de
que esse código deveria estar em email_parser.py ou tiflux_client.py.
"""
import logging

from alerting import notify_failure, setup_logging
from email_parser import parse_vaga_email
from graph_client import fetch_new_emails
from state_store import load_last_run_iso, load_processed_ids, mark_processed
from ticket_builder import build_ticket_description, build_ticket_title
from tiflux_client import create_ticket

SUBJECT_FILTER = "Fechamento Vaga"
logger = logging.getLogger(__name__)


def run() -> None:
    setup_logging()
    processed = load_processed_ids()
    since_iso = load_last_run_iso()

    try:
        emails = fetch_new_emails(SUBJECT_FILTER, since_iso)
    except Exception as exc:
        logger.exception("Falha ao buscar e-mails no Graph")
        notify_failure("busca de e-mails no Graph", exc)
        return

    for email in emails:
        if email["id"] in processed:
            continue  # já processado, não duplica chamado

        try:
            dados = parse_vaga_email(email["body"]["content"])
            ticket = create_ticket(
                titulo=build_ticket_title(dados),
                descricao=build_ticket_description(dados),
            )
            logger.info("Chamado %s criado para e-mail %s", ticket.get("ticket_number"), email["id"])
            mark_processed(email["id"], email["receivedDateTime"])
        except Exception as exc:
            logger.exception("Falha ao processar e-mail %s", email["id"])
            notify_failure(f"processamento do e-mail {email['id']}", exc)


if __name__ == "__main__":
    run()
