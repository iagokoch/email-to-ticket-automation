"""
Transforma um VagaFechada em título/descrição de texto para o
chamado. Não faz HTTP, não conhece Graph nem Tiflux — só formata.
Existe para o main.py continuar sem lógica de negócio própria.
"""
from email_parser import VagaFechada


def build_ticket_title(vaga: VagaFechada) -> str:
    return f"Fechamento de vaga - {vaga.cargo} - {vaga.candidato}"


def build_ticket_description(vaga: VagaFechada) -> str:
    linhas = [
        f"Cargo: {vaga.cargo}",
        f"Candidato: {vaga.candidato}",
        f"Data de início: {vaga.data_inicio}",
    ]
    campos_opcionais = [
        ("Setor", vaga.setor),
        ("Líder responsável", vaga.lider_responsavel),
        ("Madrinha", vaga.madrinha),
        ("CRECI", vaga.creci),
        ("CPF", vaga.cpf),
        ("Telefone", vaga.telefone),
    ]
    for rotulo, valor in campos_opcionais:
        if valor:
            linhas.append(f"{rotulo}: {valor}")
    return "\n".join(linhas)
