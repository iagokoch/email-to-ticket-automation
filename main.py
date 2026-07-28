"""
Orquestra o fluxo. De propósito, não deveria ter lógica de negócio —
só decide a ordem das chamadas e trata erro de alto nível. Se você
sentir vontade de colocar parsing ou regra do Tiflux aqui, é sinal de
que esse código deveria estar em email_parser.py ou tiflux_client.py.
"""
from graph_client import fetch_new_emails
from email_parser import parse_vaga_email
from tiflux_client import create_ticket
from state_store import load_processed_ids, load_last_run_iso, mark_processed

SUBJECT_FILTER = "Fechamento Vaga"


def run() -> None:
    processed = load_processed_ids()
    since_iso = load_last_run_iso()

    emails = fetch_new_emails(SUBJECT_FILTER, since_iso)

    for email in emails:
        if email["id"] in processed:
            continue  # já processado, não duplica chamado

        try:
            dados = parse_vaga_email(email["body"]["content"])
            create_ticket(
                titulo=f"Fechamento de vaga: {dados.cargo}",
                descricao="...",  # TODO: montar descrição a partir de `dados`
            )
            mark_processed(email["id"])
        except Exception as exc:
            # TODO: decidir o que fazer aqui. Isso é uma automação sem
            # ninguém olhando — não deixe uma falha morrer em silêncio.
            # Sugestão: logar em arquivo e, se possível, mandar um
            # alerta (e-mail ou mensagem) quando falhar, pra você saber
            # que precisa abrir o chamado manualmente dessa vez.
            print(f"Falha ao processar e-mail {email['id']}: {exc}")


if __name__ == "__main__":
    run()
