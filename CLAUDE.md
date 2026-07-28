# Projeto

Automação em Python: ao chegar e-mail com assunto contendo "Fechamento
Vaga" na caixa monitorada, extrai os dados do template e abre um
chamado no Tiflux.

# Comandos

- Rodar: `python main.py`
- TODO: ainda não há lint nem testes configurados neste projeto —
  definir isso antes de crescer o código (ex.: ruff pra lint, pytest
  pros testes do email_parser).

# Arquitetura

- `graph_client.py`: só busca e-mail via Microsoft Graph (client
  credentials). Não conhece Tiflux.
- `email_parser.py`: só transforma o corpo do e-mail em dados
  estruturados (`VagaFechada`). Não conhece Graph nem Tiflux.
- `tiflux_client.py`: só cria chamado no Tiflux a partir de um payload
  pronto. Não conhece e-mail.
- `state_store.py`: controla dedupe (ids já processados) e o último
  timestamp processado, em `state.json` local.
- `main.py`: só orquestra a ordem das chamadas — não deve conter
  lógica de negócio própria.
- Regra geral: mudar um desses módulos não deveria exigir mudar os
  outros. Se isso acontecer, é sinal de que a responsabilidade vazou
  pro lugar errado.

# Segurança

- Nunca commitar `.env` nem `state.json` se ele vier a guardar dado
  sensível
- Nunca logar o corpo completo do e-mail (pode conter dado de
  candidato) — logar só o id da mensagem e o necessário pra debug
- Credenciais (client secret do Graph, token do Tiflux) só via
  variável de ambiente, nunca hardcoded

# Workflow

- Antes de implementar ou alterar qualquer TODO (parsing, payload do
  Tiflux, state store), apresentar o plano antes de codar
- Depois de qualquer mudança, rodar o script manualmente e conferir no
  Tiflux que o chamado abriu certo antes de considerar terminado
