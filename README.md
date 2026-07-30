# Automação Fechamento de Vaga → Tiflux

Ao chegar um e-mail com assunto contendo "Fechamento Vaga" na caixa
monitorada, abre um chamado no Tiflux com os dados do e-mail.

## Por que os arquivos estão separados assim

Cada módulo tem uma responsabilidade e não conhece os outros:

- `graph_client.py` só sabe buscar e-mail e enviar e-mail. Não sabe o que é Tiflux.
- `email_parser.py` só sabe transformar texto em dados estruturados.
  Não sabe de onde o texto veio nem para onde os dados vão.
- `ticket_builder.py` só sabe transformar dados estruturados em texto
  de título/descrição. Não faz HTTP, não conhece Graph nem Tiflux.
- `tiflux_client.py` só sabe criar chamado a partir de um payload pronto.
- `state_store.py` só sabe o que já foi processado.
- `alerting.py` só sabe configurar logging e decidir como alertar uma
  falha (hoje só log em arquivo — ver seção "Log e alertas" abaixo).
- `main.py` só orquestra a ordem — sem lógica de negócio própria.

Isso significa que se o template do e-mail mudar, você mexe só em
`email_parser.py`. Se a API do Tiflux mudar, só em `tiflux_client.py`.
Isso é o que evita retrabalho de verdade: mudança isolada não quebra
o resto.

## Pré-requisito de infraestrutura (fora do código)

1. App Registration no Azure AD com permissão de **aplicação**
   `Mail.Read` (não delegada — client credentials flow, sem usuário
   logado). `Mail.Send` não é necessária hoje (alerta de falha é só
   log em arquivo, ver "Log e alertas" abaixo) — só seria preciso se
   um dia reativarmos o alerta por e-mail.
2. Recomendado: uma **Application Access Policy** no Exchange Online
   restringindo esse app a enxergar só a caixa monitorada, não o
   tenant inteiro (princípio do menor privilégio).
3. Client ID, client secret e tenant ID desse app registration, mais
   as credenciais do "Usuário API" do Tiflux (Configurações >
   Integrações > Dados), vão no `.env` (a partir do `.env.example`).

## Tiflux: API v1

A automação usa a **API v1** do Tiflux (a v2 não está disponível para
esta conta). Diferenças importantes em relação à v2:
- Autenticação é **Basic Auth** (e-mail + senha do "Usuário API"), não
  Bearer token.
- O corpo da requisição de criação de ticket é `application/json`.
- `client_id`, `desk_id` e `priority_id` são fixos por configuração
  (`.env`) — não vêm do e-mail.

## Como rodar

```bash
pip install -r requirements.txt
# configurar .env com os valores reais (não commitar), a partir do .env.example
python main.py
```

Rodar os testes (cobre principalmente `email_parser.py`, que é o
ponto mais frágil do sistema):

```bash
pytest
```

Rodar o lint:

```bash
ruff check .
```

## Dependências e segurança

As versões mínimas em `requirements.txt` (`requests>=2.33.0`,
`idna>=3.15`, `urllib3>=2.7.0`) não são arbitrárias — foram fixadas
para corrigir CVEs conhecidas, identificadas rodando o Snyk.

Checar vulnerabilidades nas dependências instaladas:

```bash
snyk test
```

Também foi rodado `snyk monitor`, que manda um snapshot do projeto
pro dashboard do Snyk (snyk.io) e avisa por e-mail se uma CVE nova for
descoberta pra alguma dependência já usada aqui — mesmo sem rodar
`snyk test` de novo:

```bash
snyk monitor
```

Nenhum dos dois roda sozinho no CI (ver seção "CI/CD" abaixo, que usa
só recursos nativos do GitHub, sem Snyk): `snyk test` precisa ser
rodado manualmente antes de atualizar `requirements.txt`, e `snyk
monitor` precisa ser re-rodado sempre que `requirements.txt` mudar,
senão o snapshot monitorado no dashboard fica desatualizado.

## CI/CD (GitHub Actions)

Tudo em `.github/`, usando só recursos nativos do GitHub (sem serviço
externo, sem secret novo):

- `workflows/ci.yml`: a cada push e pull request na `main`, roda
  `ruff check .` e `pytest` em `ubuntu-latest` com Python 3.14 (CI não
  precisa espelhar o Windows de produção — só valida que o código
  funciona).
- `workflows/codeql.yml`: CodeQL (code scanning) para Python, a cada
  push e pull request na `main`.
- `dependabot.yml`: monitora dependências `pip` (`requirements.txt`) e
  GitHub Actions, checando semanalmente e abrindo PR automático quando
  há nova versão ou CVE conhecida.

## Log e alertas

Toda execução loga em `LOG_FILE_PATH` (por padrão, `automacao.log`
dentro da própria pasta do projeto — caminho absoluto, não depende de
onde o processo foi iniciado). É o primeiro lugar a olhar se um
chamado não abriu: linhas de erro trazem o id do e-mail e a exceção
(nunca o corpo do e-mail nem dado de candidato).

O alerta por e-mail em caso de falha está desativado por enquanto —
`Mail.Send` no Azure AD ainda não tomou efeito (permissão concedida,
mas `sendMail` retornou 403; provavelmente falta consentimento de
admin realmente aplicado, ou é permissão do tipo errado). Enquanto
isso não for resolvido, `notify_failure()` em `alerting.py` só loga
localmente. Pra reativar o e-mail: confirmar `Mail.Send` como
"Application" com "Granted for [tenant]" nas API permissions do App
Registration, e então voltar a chamar `graph_client.send_mail()`
dentro de `notify_failure()`.

## Agendamento

Já configurado nesta máquina via Task Scheduler do Windows, rodando
`python main.py` 2x ao dia (10:00 e 17:00), com "Não iniciar uma nova
instância" (evita sobreposição se uma execução atrasar):

```
FechamentoVaga_Tiflux_10h  -> 10:00 diário
FechamentoVaga_Tiflux_17h  -> 17:00 diário
```

Pra recriar em outra máquina:

```bash
schtasks /create /tn "FechamentoVaga_Tiflux_10h" /tr "\"<caminho_do_python>\" \"<caminho_do_main.py>\"" /sc DAILY /st 10:00 /rl LIMITED
schtasks /create /tn "FechamentoVaga_Tiflux_17h" /tr "\"<caminho_do_python>\" \"<caminho_do_main.py>\"" /sc DAILY /st 17:00 /rl LIMITED
```

Depois de criadas, nas Propriedades de cada tarefa, marcar "Não
iniciar uma nova instância" para evitar sobreposição se uma execução
atrasar.

## Riscos aceitos (conhecidos, não resolvidos)

- Se o POST ao Tiflux for aceito mas a resposta não chegar (timeout),
  o e-mail não é marcado como processado e pode gerar chamado
  duplicado na próxima execução — a API v1 não expõe idempotency key.
- Se a automação ficar mais de `LOOKBACK_HOURS` (padrão 48h) sem
  rodar com sucesso, um e-mail poderia ser perdido — mitigado pelo
  agendamento 2x/dia, mas é uma janela finita.
