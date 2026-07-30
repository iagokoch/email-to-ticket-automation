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
    Busca e-mails na caixa MAILBOX_USER recebidos após `since_iso`
    (ISO 8601 UTC, ex.: "2026-07-28T00:00:00Z") cujo assunto contenha
    `subject_filter`.

    O $filter da Graph API só cobre a data: contains() não tem suporte
    garantido em $filter sobre subject (só startswith é documentado
    como confiável), então o filtro por assunto é feito aqui mesmo,
    em Python, depois de buscar.

    Pede o corpo em texto puro (Prefer: outlook.body-content-type=text)
    para o parsing em email_parser.py não precisar lidar com HTML.
    """
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Prefer": 'outlook.body-content-type="text"',
    }
    url = f"https://graph.microsoft.com/v1.0/users/{MAILBOX_USER}/messages"
    params = {
        "$filter": f"receivedDateTime ge {since_iso}",
        "$select": "id,subject,receivedDateTime,body",
        "$orderby": "receivedDateTime asc",
        "$top": 50,
    }

    results = []
    while url:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = None  # @odata.nextLink já vem com todos os query params embutidos

    return [msg for msg in results if subject_filter.lower() in msg.get("subject", "").lower()]


def send_mail(to_address: str, subject: str, body_text: str) -> None:
    """
    Envia um e-mail a partir da caixa MAILBOX_USER. Usado só para o
    alerta de falha (ver alerting.py) — precisa da permissão de
    aplicação Mail.Send no App Registration (além de Mail.Read).
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/users/{MAILBOX_USER}/sendMail"
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body_text},
            "toRecipients": [{"emailAddress": {"address": to_address}}],
        }
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
