"""
Módulo de dados simulados para o sistema de maternidade.
Gera dados fictícios realistas para demonstração.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker('pt_BR')

# Seed para reprodutibilidade
random.seed(42)
np.random.seed(42)
Faker.seed(42)

# ============================================================================
# CONSTANTES
# ============================================================================

TIPOS_SANGUINEOS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
TIPOS_PARTO = ['Normal', 'Cesárea', 'Fórceps', 'Vácuo-extração']
STATUS_PACIENTE = ['Internada', 'Em trabalho de parto', 'Pós-parto', 'Alta', 'UTI']
SETORES = ['Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']
CONVENIOS = ['SUS', 'Unimed', 'Bradesco Saúde', 'Sul América', 'Amil', 'Particular']

COMORBIDADES = [
    'Nenhuma', 'Diabetes Gestacional', 'Hipertensão', 'Pré-eclâmpsia',
    'Placenta prévia', 'Anemia', 'Hipotireoidismo', 'Obesidade'
]

EXAMES = [
    'Hemograma Completo', 'Glicemia', 'Urina Tipo I', 'Urocultura',
    'Ultrassonografia Obstétrica', 'Cardiotocografia', 'Doppler',
    'Teste de Tolerância à Glicose', 'Sorologia HIV', 'Sorologia Hepatite B',
    'Tipagem Sanguínea', 'Coombs Indireto', 'TSH', 'T4 Livre'
]

MEDICOS = [
    {'id': 1, 'nome': 'Dr. Carlos Alberto Silva', 'crm': '12345-SP', 'especialidade': 'Obstetrícia', 'telefone': '(11) 99999-0001', 'email': 'carlos.silva@maternidade.com', 'ativo': True},
    {'id': 2, 'nome': 'Dra. Maria Fernanda Costa', 'crm': '23456-SP', 'especialidade': 'Obstetrícia', 'telefone': '(11) 99999-0002', 'email': 'maria.costa@maternidade.com', 'ativo': True},
    {'id': 3, 'nome': 'Dr. Roberto Santos', 'crm': '34567-SP', 'especialidade': 'Obstetrícia', 'telefone': '(11) 99999-0003', 'email': 'roberto.santos@maternidade.com', 'ativo': True},
    {'id': 4, 'nome': 'Dra. Ana Paula Oliveira', 'crm': '45678-SP', 'especialidade': 'Neonatologia', 'telefone': '(11) 99999-0004', 'email': 'ana.oliveira@maternidade.com', 'ativo': True},
    {'id': 5, 'nome': 'Dr. Fernando Lima', 'crm': '56789-SP', 'especialidade': 'Anestesiologia', 'telefone': '(11) 99999-0005', 'email': 'fernando.lima@maternidade.com', 'ativo': True},
]

ESPECIALIDADES = ['Obstetrícia', 'Neonatologia', 'Anestesiologia', 'Pediatria', 'Ginecologia']

LEITOS = [
    {'id': f'PP-{i:02d}', 'setor': 'Pré-parto', 'tipo': 'Enfermaria'} for i in range(1, 11)
] + [
    {'id': f'CO-{i:02d}', 'setor': 'Centro Obstétrico', 'tipo': 'Sala de Parto'} for i in range(1, 6)
] + [
    {'id': f'AC-{i:02d}', 'setor': 'Alojamento Conjunto', 'tipo': 'Apartamento'} for i in range(1, 21)
] + [
    {'id': f'UN-{i:02d}', 'setor': 'UTI Neonatal', 'tipo': 'UTI'} for i in range(1, 11)
] + [
    {'id': f'UM-{i:02d}', 'setor': 'UTI Materna', 'tipo': 'UTI'} for i in range(1, 6)
]


# ============================================================================
# FUNÇÕES DE GERAÇÃO DE DADOS
# ============================================================================

def gerar_paciente(id_paciente: int) -> dict:
    """Gera dados de uma paciente gestante."""
    data_nascimento = fake.date_of_birth(minimum_age=18, maximum_age=45)
    idade = (datetime.now().date() - data_nascimento).days // 365

    # Data da última menstruação (DUM) - para calcular idade gestacional
    semanas_gestacao = random.randint(28, 42)
    dum = datetime.now() - timedelta(weeks=semanas_gestacao)
    dpp = dum + timedelta(weeks=40)  # Data provável do parto

    return {
        'id': id_paciente,
        'nome': fake.name_female(),
        'cpf': fake.cpf(),
        'data_nascimento': data_nascimento,
        'idade': idade,
        'tipo_sanguineo': random.choice(TIPOS_SANGUINEOS),
        'telefone': fake.phone_number(),
        'endereco': fake.address(),
        'convenio': random.choice(CONVENIOS),
        'num_gestacoes': random.randint(1, 5),
        'num_partos': random.randint(0, 4),
        'num_abortos': random.randint(0, 2),
        'dum': dum.date(),
        'dpp': dpp.date(),
        'semanas_gestacao': semanas_gestacao,
        'comorbidades': random.choice(COMORBIDADES),
        'alergias': random.choice(['Nenhuma', 'Dipirona', 'Penicilina', 'Látex', 'Iodo']),
        'peso_pre_gestacional': round(random.uniform(50, 90), 1),
        'altura': round(random.uniform(1.50, 1.80), 2),
        'medico_responsavel': random.choice(MEDICOS)['nome'],
        'status': random.choice(STATUS_PACIENTE),
        'data_internacao': (datetime.now() - timedelta(days=random.randint(0, 5))).date() if random.random() > 0.3 else None,
        'leito': random.choice(LEITOS)['id'] if random.random() > 0.3 else None,
    }


def gerar_recem_nascido(id_rn: int, id_mae: int, nome_mae: str, data_parto: datetime) -> dict:
    """Gera dados de um recém-nascido."""
    sexo = random.choice(['Masculino', 'Feminino'])

    return {
        'id': id_rn,
        'id_mae': id_mae,
        'nome_mae': nome_mae,
        'nome': f"RN de {nome_mae.split()[0]}",
        'sexo': sexo,
        'data_nascimento': data_parto,
        'hora_nascimento': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
        'peso': random.randint(2500, 4200),  # gramas
        'comprimento': round(random.uniform(45, 55), 1),  # cm
        'perimetro_cefalico': round(random.uniform(32, 38), 1),  # cm
        'apgar_1min': random.randint(6, 10),
        'apgar_5min': random.randint(7, 10),
        'apgar_10min': random.randint(8, 10),
        'tipo_parto': random.choice(TIPOS_PARTO),
        'reanimacao': random.choice(['Não necessária', 'O2 inalatório', 'VPP', 'Intubação']),
        'alojamento_conjunto': random.choice([True, True, True, False]),  # 75% vai para AC
        'observacoes': random.choice(['Sem intercorrências', 'Icterícia leve', 'Hipoglicemia transitória', '']),
    }


def gerar_evolucao(id_evolucao: int, id_paciente: int, nome_paciente: str, data_base: datetime) -> dict:
    """Gera registro de evolução médica."""
    return {
        'id': id_evolucao,
        'id_paciente': id_paciente,
        'nome_paciente': nome_paciente,
        'data_hora': data_base + timedelta(hours=random.randint(0, 72)),
        'medico': random.choice(MEDICOS)['nome'],
        'tipo': random.choice(['Admissão', 'Evolução', 'Intercorrência', 'Alta']),
        'descricao': random.choice([
            'Paciente em bom estado geral, sem queixas.',
            'Contrações uterinas regulares, 3 em 10 minutos.',
            'Dilatação cervical de 6cm, bolsa íntegra.',
            'Puérpera em bom estado, amamentação efetiva.',
            'Queixa de dor em região abdominal, prescrito analgesia.',
            'BCF presente e regular, movimentos fetais presentes.',
            'Pressão arterial elevada, iniciado sulfato de magnésio.',
            'Paciente em trabalho de parto ativo.',
        ]),
        'sinais_vitais': {
            'pa': f"{random.randint(100, 140)}/{random.randint(60, 90)}",
            'fc': random.randint(70, 100),
            'temp': round(random.uniform(36.0, 37.5), 1),
            'fr': random.randint(16, 22),
        },
        'conduta': random.choice([
            'Manter observação', 'Solicitar exames', 'Iniciar ocitocina',
            'Preparar para cesárea', 'Alta hospitalar', 'Analgesia de parto'
        ])
    }


def gerar_exame(id_exame: int, id_paciente: int, nome_paciente: str) -> dict:
    """Gera resultado de exame."""
    tipo_exame = random.choice(EXAMES)
    data_exame = datetime.now() - timedelta(days=random.randint(0, 30))

    resultados = {
        'Hemograma Completo': f"Hb: {round(random.uniform(10, 14), 1)} | Ht: {random.randint(30, 42)}% | Leuc: {random.randint(5000, 15000)}",
        'Glicemia': f"{random.randint(70, 140)} mg/dL",
        'Urina Tipo I': random.choice(['Normal', 'Leucocitúria', 'Proteinúria +', 'Glicosúria']),
        'Ultrassonografia Obstétrica': f"Feto único, cefálico, ILA {round(random.uniform(8, 20), 1)}cm, peso estimado {random.randint(2000, 4000)}g",
        'Cardiotocografia': random.choice(['Categoria I - Normal', 'Categoria II - Indeterminado', 'Categoria I - Reativo']),
    }

    return {
        'id': id_exame,
        'id_paciente': id_paciente,
        'nome_paciente': nome_paciente,
        'tipo': tipo_exame,
        'data_solicitacao': data_exame.date(),
        'data_resultado': (data_exame + timedelta(days=random.randint(0, 3))).date(),
        'resultado': resultados.get(tipo_exame, 'Resultado dentro dos parâmetros normais'),
        'status': random.choice(['Concluído', 'Concluído', 'Concluído', 'Pendente']),
        'solicitante': random.choice(MEDICOS)['nome'],
    }


def gerar_parto(id_parto: int, paciente: dict) -> dict:
    """Gera registro de parto."""
    data_parto = datetime.now() - timedelta(days=random.randint(0, 30))

    return {
        'id': id_parto,
        'id_paciente': paciente['id'],
        'nome_paciente': paciente['nome'],
        'data_parto': data_parto.date(),
        'hora_parto': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
        'tipo_parto': random.choice(TIPOS_PARTO),
        'indicacao_cesarea': random.choice([
            'Não se aplica', 'Desproporção cefalopélvica', 'Sofrimento fetal',
            'Falha de indução', 'Cesárea anterior', 'Apresentação pélvica'
        ]) if random.random() > 0.5 else 'Não se aplica',
        'anestesia': random.choice(['Raquidiana', 'Peridural', 'Combinada', 'Local', 'Nenhuma']),
        'duracao_trabalho_parto': f"{random.randint(2, 18)} horas",
        'obstetra': random.choice([m for m in MEDICOS if m['especialidade'] == 'Obstetrícia'])['nome'],
        'pediatra': random.choice([m for m in MEDICOS if m['especialidade'] == 'Neonatologia'])['nome'],
        'anestesista': random.choice([m for m in MEDICOS if m['especialidade'] == 'Anestesiologia'])['nome'],
        'intercorrencias': random.choice([
            'Nenhuma', 'Nenhuma', 'Nenhuma',
            'Atonia uterina', 'Laceração perineal', 'Hemorragia pós-parto'
        ]),
        'perda_sanguinea_estimada': f"{random.randint(200, 800)} mL",
    }


# ============================================================================
# GERAÇÃO DO DATASET COMPLETO
# ============================================================================

def gerar_dados_completos(num_pacientes: int = 50):
    """Gera todos os dados do sistema."""

    pacientes = []
    recem_nascidos = []
    evolucoes = []
    exames = []
    partos = []

    id_evolucao = 1
    id_exame = 1
    id_rn = 1
    id_parto = 1

    for i in range(1, num_pacientes + 1):
        # Gerar paciente
        paciente = gerar_paciente(i)
        pacientes.append(paciente)

        # Gerar evoluções (2-5 por paciente)
        data_base = datetime.now() - timedelta(days=5)
        for _ in range(random.randint(2, 5)):
            evolucao = gerar_evolucao(id_evolucao, i, paciente['nome'], data_base)
            evolucoes.append(evolucao)
            id_evolucao += 1

        # Gerar exames (3-8 por paciente)
        for _ in range(random.randint(3, 8)):
            exame = gerar_exame(id_exame, i, paciente['nome'])
            exames.append(exame)
            id_exame += 1

        # 60% das pacientes já tiveram parto
        if random.random() > 0.4:
            parto = gerar_parto(id_parto, paciente)
            partos.append(parto)

            # Gerar recém-nascido
            rn = gerar_recem_nascido(
                id_rn, i, paciente['nome'],
                datetime.combine(parto['data_parto'], datetime.min.time())
            )
            recem_nascidos.append(rn)

            id_parto += 1
            id_rn += 1

    return {
        'pacientes': pd.DataFrame(pacientes),
        'recem_nascidos': pd.DataFrame(recem_nascidos),
        'evolucoes': pd.DataFrame(evolucoes),
        'exames': pd.DataFrame(exames),
        'partos': pd.DataFrame(partos),
        'medicos': pd.DataFrame(MEDICOS),
        'leitos': pd.DataFrame(LEITOS),
    }


# Cache dos dados para não regenerar a cada reload
_dados_cache = None

def get_dados():
    """Retorna os dados do sistema (com cache)."""
    global _dados_cache
    if _dados_cache is None:
        _dados_cache = gerar_dados_completos(50)
    return _dados_cache


def atualizar_paciente(id_paciente: int, dados_atualizados: dict):
    """Atualiza dados de um paciente."""
    global _dados_cache
    dados = get_dados()
    idx = dados['pacientes'][dados['pacientes']['id'] == id_paciente].index
    if len(idx) > 0:
        for key, value in dados_atualizados.items():
            dados['pacientes'].loc[idx[0], key] = value


def adicionar_evolucao(nova_evolucao: dict):
    """Adiciona nova evolução ao histórico."""
    global _dados_cache
    dados = get_dados()
    nova_evolucao['id'] = len(dados['evolucoes']) + 1
    dados['evolucoes'] = pd.concat([dados['evolucoes'], pd.DataFrame([nova_evolucao])], ignore_index=True)


# ============================================================================
# FUNÇÕES CRUD DE MÉDICOS
# ============================================================================

def get_medicos():
    """Retorna lista de médicos."""
    dados = get_dados()
    return dados['medicos']


def adicionar_medico(nome: str, crm: str, especialidade: str, telefone: str = "", email: str = ""):
    """Adiciona um novo médico ao sistema."""
    global _dados_cache
    dados = get_dados()

    # Gerar novo ID
    novo_id = int(dados['medicos']['id'].max() + 1) if len(dados['medicos']) > 0 else 1

    novo_medico = {
        'id': novo_id,
        'nome': nome,
        'crm': crm,
        'especialidade': especialidade,
        'telefone': telefone,
        'email': email,
        'ativo': True
    }

    dados['medicos'] = pd.concat([dados['medicos'], pd.DataFrame([novo_medico])], ignore_index=True)
    return novo_id


def atualizar_medico(id_medico: int, dados_atualizados: dict):
    """Atualiza dados de um médico."""
    global _dados_cache
    dados = get_dados()
    idx = dados['medicos'][dados['medicos']['id'] == id_medico].index
    if len(idx) > 0:
        for key, value in dados_atualizados.items():
            dados['medicos'].loc[idx[0], key] = value
        return True
    return False


def remover_medico(id_medico: int):
    """Remove (desativa) um médico do sistema."""
    global _dados_cache
    dados = get_dados()
    idx = dados['medicos'][dados['medicos']['id'] == id_medico].index
    if len(idx) > 0:
        dados['medicos'].loc[idx[0], 'ativo'] = False
        return True
    return False


def reativar_medico(id_medico: int):
    """Reativa um médico no sistema."""
    global _dados_cache
    dados = get_dados()
    idx = dados['medicos'][dados['medicos']['id'] == id_medico].index
    if len(idx) > 0:
        dados['medicos'].loc[idx[0], 'ativo'] = True
        return True
    return False


def get_medico_por_id(id_medico: int):
    """Retorna dados de um médico específico."""
    dados = get_dados()
    medico = dados['medicos'][dados['medicos']['id'] == id_medico]
    if len(medico) > 0:
        return medico.iloc[0].to_dict()
    return None
