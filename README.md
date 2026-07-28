# Automação Fechamento de Vaga → Tiflux

Ao chegar um e-mail com assunto contendo "Fechamento Vaga" na caixa
monitorada, abre um chamado no Tiflux com os dados do e-mail.

## Por que os arquivos estão separados assim

Cada módulo tem uma responsabilidade e não conhece os outros:

- `graph_client.py` só sabe buscar e-mail. Não sabe o que é Tiflux.
- `email_parser.py` só sabe transformar texto em dados estruturados.
  Não sabe de onde o texto veio nem para onde os dados vão.
- `tiflux_client.py` só sabe criar chamado a partir de um payload pronto.
- `state_store.py` só sabe o que já foi processado.
- `main.py` só orquestra a ordem — sem lógica de negócio própria.

Isso significa que se o template do e-mail mudar, você mexe só em
`email_parser.py`. Se a API do Tiflux mudar, só em `tiflux_client.py`.
Isso é o que evita retrabalho de verdade: mudança isolada não quebra
o resto.

## Pré-requisito de infraestrutura (fora do código)

1. App Registration no Azure AD com permissão de **aplicação**
   `Mail.Read` (não delegada — client credentials flow, sem usuário
   logado).
2. Recomendado: uma **Application Access Policy** no Exchange Online
   restringindo esse app a enxergar só a caixa monitorada, não o
   tenant inteiro (princípio do menor privilégio).
3. Client ID, client secret e tenant ID desse app registration vão no
   `.env` (a partir do `.env.example`).

## O que ainda está em TODO e por quê

- **`email_parser.py`**: preciso de um exemplo real (pode anonimizar)
  do e-mail de Fechamento de Vaga para desenhar a extração certa.
- **`tiflux_client.py`**: preciso saber os campos obrigatórios reais do
  endpoint de criação de chamado (categoria? prioridade? cliente?).
- **`state_store.py`**: a lógica de dedupe é simples de propósito
  (arquivo JSON local) — só evolua pra algo mais robusto se isso um
  dia rodar em mais de uma máquina.
- **Alertas de falha** em `main.py`: hoje só imprime no console. Como
  isso vai rodar sem ninguém olhando, decida como quer ser avisado
  quando falhar (e-mail, Slack, log monitorado?).

## Como rodar

```bash
pip install -r requirements.txt
# configurar .env com os valores reais (não commitar)
python main.py
```

Ainda falta decidir como isso vai ser agendado (Task Scheduler do
Windows rodando a cada N minutos é o caminho mais simples, dado que
vocês já usam ambiente Windows/M365).
