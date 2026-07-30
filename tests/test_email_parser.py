from email_parser import EmailParseError, parse_vaga_email

EMAIL_CORRETOR = """🎉 Nova contratação confirmada
Olá,

Temos uma ótima notícia para compartilhar! ✨

Fechamos a posição de Corretor com Pedrinho Robertinho Camargo.

📅 Data de início:
2026-07-28

🏢 Setor:
Norte

👤 Líder responsável:
Joãozinho

🪪 CRECI:
12345

📄 CPF:
999.999.999-99

📱 Telefone:
4724678295

📚 Integração
A integração será agendada posteriormente pelo Recursos Humanos. Assim que a data e o horário forem definidos, todos os envolvidos serão comunicados.

Em caso de dúvidas, permanecemos à disposição.

Atenciosamente,
Recursos Humanos"""

EMAIL_CLT = """🎉 Nova contratação confirmada
Olá,

Temos uma ótima notícia para compartilhar! ✨

Fechamos a posição de Assistente de Recursos Humanos - RH com a candidata Augusta Da Silva Sauro.

📅 Data de início:
2026-08-03

Ela iniciará suas atividades práticas na empresa nessa data, passará pela integração no nosso corporativo e, ao final, será direcionada para sua área.

🤝 Madrinha:
Mariazinha da Silva de Souza

A madrinha será responsável por dar as boas-vindas, apresentar o time e o ambiente, além de oferecer todo o suporte necessário nesse início de jornada.

Permaneço à disposição.

Atenciosamente,
Recursos Humanos"""


def test_extrai_todos_os_campos_do_email_de_corretor():
    vaga = parse_vaga_email(EMAIL_CORRETOR)

    assert vaga.cargo == "Corretor"
    assert vaga.candidato == "Pedrinho Robertinho Camargo"
    assert vaga.data_inicio == "2026-07-28"
    assert vaga.setor == "Norte"
    assert vaga.lider_responsavel == "Joãozinho"
    assert vaga.creci == "12345"
    assert vaga.cpf == "999.999.999-99"
    assert vaga.telefone == "4724678295"
    assert vaga.madrinha is None


def test_creci_ausente_nao_quebra_e_fica_none():
    email_sem_creci = EMAIL_CORRETOR.replace("🪪 CRECI:\n12345\n\n", "")

    vaga = parse_vaga_email(email_sem_creci)

    assert vaga.creci is None
    assert vaga.cargo == "Corretor"


def test_corretor_sem_campo_obrigatorio_levanta_erro_citando_o_campo():
    email_sem_setor = EMAIL_CORRETOR.replace("🏢 Setor:\nNorte\n\n", "")

    try:
        parse_vaga_email(email_sem_setor)
        assert False, "deveria ter levantado EmailParseError"
    except EmailParseError as exc:
        assert "setor" in str(exc)


def test_corretor_sem_cpf_levanta_erro():
    email_sem_cpf = EMAIL_CORRETOR.replace("📄 CPF:\n999.999.999-99\n\n", "")

    try:
        parse_vaga_email(email_sem_cpf)
        assert False, "deveria ter levantado EmailParseError"
    except EmailParseError as exc:
        assert "cpf" in str(exc)


def test_data_inicio_malformada_levanta_erro():
    email_data_invalida = EMAIL_CORRETOR.replace("2026-07-28", "28/07/2026")

    try:
        parse_vaga_email(email_data_invalida)
        assert False, "deveria ter levantado EmailParseError"
    except EmailParseError as exc:
        assert "Data de início" in str(exc)


def test_modelo_clt_sem_campos_de_corretor_nao_quebra():
    vaga = parse_vaga_email(EMAIL_CLT)

    assert vaga.cargo == "Assistente de Recursos Humanos - RH"
    assert vaga.candidato == "Augusta Da Silva Sauro"
    assert vaga.data_inicio == "2026-08-03"
    assert vaga.madrinha == "Mariazinha da Silva de Souza"
    assert vaga.setor is None
    assert vaga.lider_responsavel is None
    assert vaga.cpf is None
    assert vaga.telefone is None
    assert vaga.creci is None


def test_clt_sem_data_inicio_levanta_erro():
    email_sem_data = EMAIL_CLT.replace("📅 Data de início:\n2026-08-03\n\n", "")

    try:
        parse_vaga_email(email_sem_data)
        assert False, "deveria ter levantado EmailParseError"
    except EmailParseError as exc:
        assert "data_inicio" in str(exc)
