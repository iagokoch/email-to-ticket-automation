"""
Extrai os dados do e-mail de Fechamento de Vaga.
Responsabilidade única: transformar o corpo do e-mail (string) em um
dado estruturado. Não sabe nada sobre Graph nem sobre Tiflux.

Como o formato é sempre o mesmo template, isso deveria ser regex/parsing
simples — mas é o ponto mais frágil do sistema inteiro: se alguém mudar
o template do e-mail sem avisar, o parser pode não achar um campo e
devolver algo vazio SEM dar erro nenhum. Aí o chamado abre no Tiflux
com dado faltando e ninguém percebe até reclamarem.

Antes de implementar: pegue um exemplo real do e-mail (pode anonimizar
nome/dados sensíveis) e escreva pelo menos um teste com ele. Se o
template mudar depois, o teste quebra e você sabe na hora — em vez de
descobrir porque um chamado abriu incompleto.
"""
from dataclasses import dataclass


@dataclass
class VagaFechada:
    cargo: str
    departamento: str
    # TODO: completar com os campos reais do template do e-mail
    # (ex.: nome do candidato, gestor responsável, data de admissão?)


def parse_vaga_email(body_text: str) -> VagaFechada:
    """
    TODO: implementar a extração real, baseada no template do e-mail.

    Sugestão: regex nomeada por campo (ex.: r"Cargo:\\s*(.+)") em vez de
    split por posição/linha — quebra menos se um campo opcional estiver
    ausente ou a ordem dos campos mudar levemente.

    Se algum campo obrigatório não for encontrado, levante uma exceção
    clara (ex.: ValueError com o nome do campo que faltou) em vez de
    devolver None silenciosamente — isso é o que permite o main.py
    decidir alertar em vez de abrir chamado incompleto.
    """
    raise NotImplementedError
