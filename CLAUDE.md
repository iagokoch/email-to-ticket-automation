# Projeto

Automação em Python: ao chegar e-mail com assunto contendo "Fechamento
Vaga" na caixa monitorada, extrai os dados do template e abre um
chamado no Tiflux.

# Comandos

- Rodar: `python main.py`
- Testes: `pytest` (cobre principalmente `email_parser.py`, o ponto
  mais frágil do sistema). Ainda não há lint configurado.

# Arquitetura

- `graph_client.py`: busca e-mail e envia e-mail (alerta) via
  Microsoft Graph (client credentials). Não conhece Tiflux.
- `email_parser.py`: só transforma o corpo do e-mail em dados
  estruturados (`VagaFechada`). Não conhece Graph nem Tiflux.
- `ticket_builder.py`: só transforma um `VagaFechada` em título/
  descrição de texto. Não faz HTTP, não conhece Graph nem Tiflux.
- `tiflux_client.py`: só cria chamado no Tiflux (API v1, Basic Auth) a
  partir de um payload pronto. Não conhece e-mail.
- `state_store.py`: controla dedupe (ids já processados). Não existe
  cursor de "última execução" persistido — `load_last_run_iso()`
  sempre devolve `agora - LOOKBACK_HOURS`; dedupe real é via
  `processed_ids` em `state.json` local.
- `alerting.py`: configura logging e decide como alertar uma falha
  (log + e-mail via `graph_client.send_mail`).
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
