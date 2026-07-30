"""
Configuração de logging e alerta de falha. A automação roda sem
ninguém olhando, então uma falha não pode morrer em silêncio: fica
registrada em arquivo (ver LOG_FILE_PATH em config.py).

Alerta por e-mail fica pendente da permissão de aplicação Mail.Send
no App Registration (ver README) — quando ela estiver concedida e
propagada, é só voltar a chamar graph_client.send_mail() aqui dentro.

Nunca passar o corpo do e-mail nem o VagaFechada inteiro para
notify_failure — só o id da mensagem/nome da etapa, para não logar
dado de candidato (CPF etc.), como o CLAUDE.md pede.
"""
import logging
import logging.handlers

from config import LOG_FILE_PATH


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.handlers.RotatingFileHandler(
                LOG_FILE_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            ),
            logging.StreamHandler(),
        ],
    )


def notify_failure(context: str, error: Exception) -> None:
    logger = logging.getLogger(__name__)
    logger.error("Falha na automação Fechamento Vaga -> Tiflux. Contexto: %s. Erro: %s", context, error)
