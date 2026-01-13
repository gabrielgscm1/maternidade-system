# Sistema de Gestao para Maternidade

Sistema completo de gestao hospitalar para maternidades desenvolvido com Streamlit.

## Funcionalidades

### Dashboard
- Visao geral com KPIs principais
- Indicadores de ocupacao de leitos
- Alertas de pacientes em trabalho de parto
- Estatisticas de partos e convenios

### Gestao de Pacientes
- Cadastro completo de gestantes
- Dados obstetricos (G/P/A, DUM, DPP, IG)
- Busca avancada com filtros
- Historico de comorbidades e alergias

### Prontuario Eletronico
- Evolucoes medicas com sinais vitais
- Registro de exames laboratoriais
- Historico obstetrico completo
- Curva de crescimento fetal
- Nova evolucao com dados obstetricos

### Registro de Partos
- Cadastro completo do parto
- Dados do recem-nascido (peso, Apgar, etc)
- Estatisticas de tipos de parto
- Taxa de cesarea por medico

### Gestao de Leitos
- Mapa visual de ocupacao
- Internacao de pacientes
- Transferencia entre setores
- Alta hospitalar com checklist

### Relatorios
- Indicadores hospitalares
- Relatorio de producao
- Indicadores de qualidade (ANVISA)
- Exportacao para Excel/CSV

## Instalacao

1. Criar ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Executar o sistema:
```bash
streamlit run app.py
```

4. Acessar no navegador: http://localhost:8501

## Estrutura do Projeto

```
maternidade_system/
├── app.py                 # Aplicacao principal
├── dados.py               # Geracao de dados simulados
├── requirements.txt       # Dependencias
├── README.md              # Este arquivo
└── paginas/
    ├── __init__.py
    ├── dashboard.py       # Dashboard principal
    ├── pacientes.py       # Gestao de pacientes
    ├── prontuario.py      # Prontuario eletronico
    ├── partos.py          # Registro de partos
    ├── internacoes.py     # Gestao de leitos
    └── relatorios.py      # Relatorios e exportacoes
```

## Tecnologias Utilizadas

- **Streamlit**: Framework web
- **Pandas**: Manipulacao de dados
- **Plotly**: Graficos interativos
- **Faker**: Geracao de dados ficticios
- **OpenPyXL**: Exportacao Excel

## Dados Simulados

O sistema gera automaticamente 50 pacientes ficticias com:
- Dados pessoais (nome, CPF, endereco)
- Dados obstetricos (gestacoes, partos, abortos)
- Evolucoes medicas
- Exames laboratoriais
- Registros de parto
- Dados de recem-nascidos

## Setores Disponiveis

| Setor | Leitos | Tipo |
|-------|--------|------|
| Pre-parto | 10 | Enfermaria |
| Centro Obstetrico | 5 | Sala de Parto |
| Alojamento Conjunto | 20 | Apartamento |
| UTI Neonatal | 10 | UTI |
| UTI Materna | 5 | UTI |

## Indicadores Monitorados

- Taxa de cesarea
- Taxa de ocupacao de leitos
- Tempo medio de internacao
- Taxa de infeccao puerperal
- Taxa de aleitamento materno
- Apgar dos recem-nascidos

## Proximas Melhorias

- [ ] Autenticacao de usuarios
- [ ] Banco de dados persistente (PostgreSQL)
- [ ] Integracao com laboratorio
- [ ] Modulo de prescricao medica
- [ ] Notificacoes por email/SMS
- [ ] App mobile para medicos

## Licenca

Projeto desenvolvido para fins educacionais.

---
*Desenvolvido com Streamlit - Janeiro 2026*
