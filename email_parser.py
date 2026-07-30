"""
Extrai os dados do e-mail de Fechamento de Vaga.
Responsabilidade única: transformar o corpo do e-mail (string) em um
dado estruturado. Não sabe nada sobre Graph nem sobre Tiflux.

O template varia por tipo de vaga: vagas de Corretor trazem Setor,
Líder responsável, CRECI, CPF e Telefone; outras vagas (ex.: CLT) só
trazem Cargo/Candidato/Data de início e um campo "Madrinha" no lugar
de "Líder responsável" — sem CPF/Telefone/Setor. Por isso só
Cargo, Candidato e Data de início são obrigatórios sempre; Setor,
Líder responsável, CPF e Telefone só são obrigatórios quando o cargo
é de Corretor. Os demais campos são sempre opcionais (entram na
descrição do chamado se existirem, são omitidos se não existirem).

Extração por rótulo (ex.: "Setor", "CPF"), não por emoji — emoji pode
variar de encoding entre o texto puro devolvido pelo Graph e é frágil
como âncora de regex. Cada rótulo aceita o valor tanto na mesma linha
quanto na linha seguinte, que é o formato do template real.
"""
import re
from dataclasses import dataclass
from datetime import date


class EmailParseError(Exception):
    pass


@dataclass
class VagaFechada:
    cargo: str
    candidato: str
    data_inicio: str
    setor: str | None = None
    lider_responsavel: str | None = None
    madrinha: str | None = None
    creci: str | None = None
    cpf: str | None = None
    telefone: str | None = None


_CARGO_CANDIDATO_RE = re.compile(
    r"Fechamos a posi[cç][aã]o de\s+(?P<cargo>.+?)\s+com\s+"
    r"(?:(?:a\s+candidata|o\s+candidato)\s+)?(?P<candidato>.+?)[.\n]",
    re.IGNORECASE,
)

_OPTIONAL_LABELS = {
    "setor": "Setor",
    "lider_responsavel": "Líder responsável",
    "madrinha": "Madrinha",
    "creci": "CRECI",
    "cpf": "CPF",
    "telefone": "Telefone",
}

# Só vagas de Corretor exigem esses dados no e-mail (registro/contato
# formal do candidato para abertura de CRECI etc.). Outros cargos
# (CLT etc.) não têm necessariamente essas informações no template.
_CORRETOR_REQUIRED_FIELDS = ["setor", "lider_responsavel", "cpf", "telefone"]


def _is_corretor(cargo: str) -> bool:
    return "corretor" in cargo.lower()


def _extract_labeled_value(body: str, label: str) -> str | None:
    pattern = re.compile(rf"{re.escape(label)}\s*:?\s*\n?\s*(?P<value>.+)", re.IGNORECASE)
    match = pattern.search(body)
    if not match:
        return None
    value = match.group("value").strip()
    return value or None


def _validate_date(raw: str) -> str:
    try:
        date.fromisoformat(raw)
    except ValueError:
        raise EmailParseError(f"Data de início em formato inesperado: {raw!r}") from None
    return raw


def parse_vaga_email(body_text: str) -> VagaFechada:
    body = body_text.replace("\r\n", "\n").replace("\xa0", " ")

    match = _CARGO_CANDIDATO_RE.search(body)
    if not match:
        raise EmailParseError(
            "Não foi possível localizar a frase 'Fechamos a posição de ... com ...' no e-mail"
        )
    cargo = match.group("cargo").strip()
    candidato = match.group("candidato").strip()

    data_inicio_raw = _extract_labeled_value(body, "Data de início")
    if not data_inicio_raw:
        raise EmailParseError("Campo obrigatório ausente no e-mail: data_inicio")

    optional_values = {
        field: _extract_labeled_value(body, label) for field, label in _OPTIONAL_LABELS.items()
    }

    if _is_corretor(cargo):
        missing = [field for field in _CORRETOR_REQUIRED_FIELDS if not optional_values[field]]
        if missing:
            raise EmailParseError(
                f"Campos obrigatórios ausentes no e-mail (vaga de Corretor): {', '.join(missing)}"
            )

    return VagaFechada(
        cargo=cargo,
        candidato=candidato,
        data_inicio=_validate_date(data_inicio_raw),
        **optional_values,
    )
