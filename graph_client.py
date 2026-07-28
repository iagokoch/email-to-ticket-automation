"""
Client fino para Microsoft Graph. Responsabilidade única: autenticar e
buscar e-mails novos. Não sabe nada sobre Tiflux nem sobre o formato
do e-mail de Fechamento de Vaga — se um desses mudar, este arquivo
não deveria precisar mudar.
"""
import msal
import requests

from config import GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, MAILBOX_USER

GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]


def get_access_token() -> str:
    app = msal.ConfidentialClientApplication(
        client_id=GRAPH_CLIENT_ID,
        client_credential=GRAPH_CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}",
    )
    result = app.acquire_token_for_client(scopes=GRAPH_SCOPE)
    if "access_token" not in result:
        raise RuntimeError(
            f"Falha ao autenticar no Graph: {result.get('error_description')}"
        )
    return result["access_token"]


def fetch_new_emails(subject_filter: str, since_iso: str) -> list[dict]:
    """
    Busca e-mails na caixa MAILBOX_USER com o assunto contendo `subject_filter`,
    recebidos após `since_iso` (ISO 8601 UTC, ex.: "2026-07-28T00:00:00Z").

    TODO: montar o $filter da Graph API. Começando pelo caminho mais simples:

        $filter=receivedDateTime gt {since_iso} and contains(subject,'{subject_filter}')

    Isso é suficiente para o volume esperado. Só migre para delta query
    (/messages/delta com token salvo entre execuções) se perceber e-mail
    sendo perdido entre execuções — não implemente isso agora, é
    complexidade que talvez nunca seja necessária.

    Atenção: se o volume por execução puder passar de ~10 e-mails,
    trate paginação (campo "@odata.nextLink" na resposta).
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/users/{MAILBOX_USER}/messages"
    params = {
        "$filter": "...",  # TODO
        "$select": "id,subject,receivedDateTime,body",
        "$orderby": "receivedDateTime asc",
    }
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("value", [])
