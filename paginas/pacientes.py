"""
Página de Gestão de Pacientes
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from paginas.utils import get_dados, atualizar_paciente


def render():
    st.markdown('<h1 class="main-header">👩 Gestão de Pacientes</h1>', unsafe_allow_html=True)

    dados = get_dados()
    pacientes = dados['pacientes']

    # ========================================================================
    # TABS DE NAVEGAÇÃO
    # ========================================================================

    tab_lista, tab_cadastro, tab_busca = st.tabs([
        "📋 Lista de Pacientes",
        "➕ Novo Cadastro",
        "🔍 Busca Avançada"
    ])

    # ========================================================================
    # TAB: LISTA DE PACIENTES
    # ========================================================================

    with tab_lista:
        st.subheader("Pacientes Cadastradas")

        # Filtros rápidos
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

        with col_filtro1:
            filtro_status = st.multiselect(
                "Status",
                options=['Internada', 'Em trabalho de parto', 'Pós-parto', 'Alta', 'UTI'],
                default=['Internada', 'Em trabalho de parto', 'Pós-parto']
            )

        with col_filtro2:
            filtro_convenio = st.multiselect(
                "Convênio",
                options=pacientes['convenio'].unique().tolist(),
                default=[]
            )

        with col_filtro3:
            filtro_setor = st.selectbox(
                "Setor",
                options=['Todos', 'Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']
            )

        # Aplicar filtros
        df_filtrado = pacientes.copy()

        if filtro_status:
            df_filtrado = df_filtrado[df_filtrado['status'].isin(filtro_status)]

        if filtro_convenio:
            df_filtrado = df_filtrado[df_filtrado['convenio'].isin(filtro_convenio)]

        # Exibir contagem
        st.write(f"**{len(df_filtrado)}** pacientes encontradas")

        # Tabela de pacientes
        colunas_exibir = ['id', 'nome', 'idade', 'semanas_gestacao', 'convenio', 'status', 'leito', 'medico_responsavel']
        df_exibir = df_filtrado[colunas_exibir].copy()
        df_exibir.columns = ['ID', 'Nome', 'Idade', 'IG (sem)', 'Convênio', 'Status', 'Leito', 'Médico']

        # Configurar exibição com seleção
        st.dataframe(
            df_exibir,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(width="small"),
                "Nome": st.column_config.TextColumn(width="large"),
                "IG (sem)": st.column_config.NumberColumn(width="small"),
                "Status": st.column_config.TextColumn(width="medium"),
            }
        )

        # ====================================================================
        # DETALHES DO PACIENTE SELECIONADO
        # ====================================================================

        st.markdown("---")
        st.subheader("📄 Detalhes da Paciente")

        paciente_id = st.selectbox(
            "Selecione a paciente para ver detalhes:",
            options=df_filtrado['id'].tolist(),
            format_func=lambda x: f"{x} - {pacientes[pacientes['id'] == x]['nome'].values[0]}"
        )

        if paciente_id:
            paciente = pacientes[pacientes['id'] == paciente_id].iloc[0]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**📋 Dados Pessoais**")
                st.write(f"**Nome:** {paciente['nome']}")
                st.write(f"**CPF:** {paciente['cpf']}")
                st.write(f"**Data Nasc.:** {paciente['data_nascimento']}")
                st.write(f"**Idade:** {paciente['idade']} anos")
                st.write(f"**Telefone:** {paciente['telefone']}")
                st.write(f"**Tipo Sanguíneo:** {paciente['tipo_sanguineo']}")

            with col2:
                st.markdown("**🤰 Dados Obstétricos**")
                st.write(f"**Gestações:** {paciente['num_gestacoes']}")
                st.write(f"**Partos:** {paciente['num_partos']}")
                st.write(f"**Abortos:** {paciente['num_abortos']}")
                st.write(f"**DUM:** {paciente['dum']}")
                st.write(f"**DPP:** {paciente['dpp']}")
                st.write(f"**IG:** {paciente['semanas_gestacao']} semanas")

            with col3:
                st.markdown("**🏥 Dados de Internação**")
                st.write(f"**Status:** {paciente['status']}")
                st.write(f"**Leito:** {paciente['leito'] or 'Não internada'}")
                st.write(f"**Convênio:** {paciente['convenio']}")
                st.write(f"**Médico:** {paciente['medico_responsavel']}")
                st.write(f"**Data Int.:** {paciente['data_internacao'] or '-'}")

            # Alertas da paciente
            st.markdown("---")
            col_alert1, col_alert2 = st.columns(2)

            with col_alert1:
                st.markdown("**⚠️ Comorbidades**")
                if paciente['comorbidades'] != 'Nenhuma':
                    st.error(f"🔴 {paciente['comorbidades']}")
                else:
                    st.success("✅ Sem comorbidades")

            with col_alert2:
                st.markdown("**💊 Alergias**")
                if paciente['alergias'] != 'Nenhuma':
                    st.error(f"🔴 {paciente['alergias']}")
                else:
                    st.success("✅ Sem alergias conhecidas")

            # Ações rápidas
            st.markdown("---")
            st.markdown("**🔧 Ações Rápidas**")
            col_acao1, col_acao2, col_acao3, col_acao4 = st.columns(4)

            with col_acao1:
                if st.button("📋 Ver Prontuário", key="btn_prontuario"):
                    st.session_state['paciente_prontuario'] = paciente_id
                    st.info("Acesse a aba 'Prontuário' no menu lateral")

            with col_acao2:
                if st.button("✏️ Editar Cadastro", key="btn_editar"):
                    st.session_state['paciente_editar'] = paciente_id

            with col_acao3:
                if st.button("🛏️ Trocar Leito", key="btn_leito"):
                    st.session_state['paciente_leito'] = paciente_id

            with col_acao4:
                if st.button("📤 Alta Hospitalar", key="btn_alta"):
                    st.session_state['paciente_alta'] = paciente_id

    # ========================================================================
    # TAB: NOVO CADASTRO
    # ========================================================================

    with tab_cadastro:
        st.subheader("➕ Cadastrar Nova Paciente")

        with st.form("form_cadastro"):
            st.markdown("**📋 Dados Pessoais**")
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome Completo *")
                cpf = st.text_input("CPF *")
                data_nasc = st.date_input("Data de Nascimento *")
                telefone = st.text_input("Telefone")

            with col2:
                tipo_sang = st.selectbox("Tipo Sanguíneo", ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
                convenio = st.selectbox("Convênio", ['SUS', 'Unimed', 'Bradesco Saúde', 'Sul América', 'Amil', 'Particular'])
                endereco = st.text_area("Endereço", height=100)

            st.markdown("---")
            st.markdown("**🤰 Dados Obstétricos**")
            col3, col4 = st.columns(2)

            with col3:
                num_gestacoes = st.number_input("Número de Gestações", min_value=1, value=1)
                num_partos = st.number_input("Número de Partos", min_value=0, value=0)
                num_abortos = st.number_input("Número de Abortos", min_value=0, value=0)

            with col4:
                dum = st.date_input("Data da Última Menstruação (DUM)")
                peso = st.number_input("Peso Pré-Gestacional (kg)", min_value=30.0, max_value=200.0, value=60.0)
                altura = st.number_input("Altura (m)", min_value=1.0, max_value=2.2, value=1.60)

            st.markdown("---")
            st.markdown("**⚠️ Informações de Risco**")
            col5, col6 = st.columns(2)

            with col5:
                comorbidades = st.multiselect(
                    "Comorbidades",
                    ['Nenhuma', 'Diabetes Gestacional', 'Hipertensão', 'Pré-eclâmpsia',
                     'Placenta prévia', 'Anemia', 'Hipotireoidismo', 'Obesidade']
                )

            with col6:
                alergias = st.text_input("Alergias (separar por vírgula)")

            st.markdown("---")
            st.markdown("**👨‍⚕️ Responsável**")
            medico = st.selectbox(
                "Médico Responsável",
                ['Dr. Carlos Alberto Silva', 'Dra. Maria Fernanda Costa', 'Dr. Roberto Santos']
            )

            submitted = st.form_submit_button("💾 Cadastrar Paciente", type="primary")

            if submitted:
                if nome and cpf:
                    st.success(f"✅ Paciente **{nome}** cadastrada com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Preencha os campos obrigatórios (Nome e CPF)")

    # ========================================================================
    # TAB: BUSCA AVANÇADA
    # ========================================================================

    with tab_busca:
        st.subheader("🔍 Busca Avançada")

        col_busca1, col_busca2 = st.columns(2)

        with col_busca1:
            busca_nome = st.text_input("Buscar por Nome")
            busca_cpf = st.text_input("Buscar por CPF")

        with col_busca2:
            busca_leito = st.text_input("Buscar por Leito")
            busca_medico = st.selectbox(
                "Buscar por Médico",
                options=['Todos'] + pacientes['medico_responsavel'].unique().tolist()
            )

        # Filtros adicionais
        st.markdown("**Filtros Adicionais**")
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            filtro_ig_min = st.number_input("IG Mínima (semanas)", min_value=0, max_value=45, value=0)
            filtro_ig_max = st.number_input("IG Máxima (semanas)", min_value=0, max_value=45, value=45)

        with col_f2:
            filtro_idade_min = st.number_input("Idade Mínima", min_value=0, max_value=60, value=0)
            filtro_idade_max = st.number_input("Idade Máxima", min_value=0, max_value=60, value=60)

        with col_f3:
            filtro_alto_risco = st.checkbox("Apenas Alto Risco")
            filtro_internadas = st.checkbox("Apenas Internadas", value=True)

        if st.button("🔍 Buscar", type="primary"):
            df_resultado = pacientes.copy()

            if busca_nome:
                df_resultado = df_resultado[df_resultado['nome'].str.contains(busca_nome, case=False, na=False)]

            if busca_cpf:
                df_resultado = df_resultado[df_resultado['cpf'].str.contains(busca_cpf, na=False)]

            if busca_leito:
                df_resultado = df_resultado[df_resultado['leito'].str.contains(busca_leito, case=False, na=False)]

            if busca_medico != 'Todos':
                df_resultado = df_resultado[df_resultado['medico_responsavel'] == busca_medico]

            df_resultado = df_resultado[
                (df_resultado['semanas_gestacao'] >= filtro_ig_min) &
                (df_resultado['semanas_gestacao'] <= filtro_ig_max)
            ]

            df_resultado = df_resultado[
                (df_resultado['idade'] >= filtro_idade_min) &
                (df_resultado['idade'] <= filtro_idade_max)
            ]

            if filtro_alto_risco:
                df_resultado = df_resultado[~df_resultado['comorbidades'].isin(['Nenhuma'])]

            if filtro_internadas:
                df_resultado = df_resultado[df_resultado['status'].isin(['Internada', 'Em trabalho de parto', 'Pós-parto'])]

            st.write(f"**{len(df_resultado)}** resultado(s) encontrado(s)")

            if len(df_resultado) > 0:
                st.dataframe(
                    df_resultado[['id', 'nome', 'idade', 'semanas_gestacao', 'status', 'leito', 'medico_responsavel']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhuma paciente encontrada com os filtros aplicados.")
