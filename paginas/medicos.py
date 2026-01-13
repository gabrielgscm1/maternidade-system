"""
Página de Gestão de Médicos
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from paginas.utils import (
    get_dados, get_medicos, adicionar_medico,
    atualizar_medico, remover_medico, reativar_medico, get_medico_por_id
)

ESPECIALIDADES = ['Obstetrícia', 'Neonatologia', 'Anestesiologia', 'Pediatria', 'Ginecologia']


def render():
    st.markdown('<h1 class="main-header">👨‍⚕️ Gestão de Médicos</h1>', unsafe_allow_html=True)

    # ========================================================================
    # TABS DE NAVEGAÇÃO
    # ========================================================================

    tab_lista, tab_cadastro, tab_editar = st.tabs([
        "📋 Lista de Médicos",
        "➕ Novo Médico",
        "✏️ Editar/Remover"
    ])

    # ========================================================================
    # TAB: LISTA DE MÉDICOS
    # ========================================================================

    with tab_lista:
        st.subheader("📋 Médicos Cadastrados")

        medicos = get_medicos()

        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            filtro_especialidade = st.multiselect(
                "Especialidade",
                options=ESPECIALIDADES,
                default=[]
            )

        with col_f2:
            filtro_status = st.radio(
                "Status",
                options=['Todos', 'Ativos', 'Inativos'],
                horizontal=True
            )

        with col_f3:
            busca_nome = st.text_input("Buscar por nome", placeholder="Digite o nome...")

        # Aplicar filtros
        df_medicos = medicos.copy()

        # Garantir que a coluna 'ativo' existe
        if 'ativo' not in df_medicos.columns:
            df_medicos['ativo'] = True

        if filtro_especialidade:
            df_medicos = df_medicos[df_medicos['especialidade'].isin(filtro_especialidade)]

        if filtro_status == 'Ativos':
            df_medicos = df_medicos[df_medicos['ativo'] == True]
        elif filtro_status == 'Inativos':
            df_medicos = df_medicos[df_medicos['ativo'] == False]

        if busca_nome:
            df_medicos = df_medicos[df_medicos['nome'].str.contains(busca_nome, case=False, na=False)]

        # Estatísticas
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        total_medicos = len(medicos)
        ativos = len(medicos[medicos.get('ativo', True) == True]) if 'ativo' in medicos.columns else total_medicos

        col_stat1.metric("Total de Médicos", total_medicos)
        col_stat2.metric("Ativos", ativos)
        col_stat3.metric("Obstetras", len(medicos[medicos['especialidade'] == 'Obstetrícia']))
        col_stat4.metric("Neonatologistas", len(medicos[medicos['especialidade'] == 'Neonatologia']))

        st.markdown("---")

        # Exibir lista
        st.write(f"**{len(df_medicos)}** médico(s) encontrado(s)")

        if len(df_medicos) > 0:
            # Preparar colunas para exibição
            colunas_exibir = ['id', 'nome', 'crm', 'especialidade']
            if 'telefone' in df_medicos.columns:
                colunas_exibir.append('telefone')
            if 'ativo' in df_medicos.columns:
                colunas_exibir.append('ativo')

            df_exibir = df_medicos[colunas_exibir].copy()

            # Renomear colunas
            col_names = {'id': 'ID', 'nome': 'Nome', 'crm': 'CRM', 'especialidade': 'Especialidade'}
            if 'telefone' in df_exibir.columns:
                col_names['telefone'] = 'Telefone'
            if 'ativo' in df_exibir.columns:
                col_names['ativo'] = 'Ativo'

            df_exibir = df_exibir.rename(columns=col_names)

            st.dataframe(df_exibir, use_container_width=True, hide_index=True)

            # Detalhes do médico selecionado
            st.markdown("---")
            st.subheader("📄 Detalhes do Médico")

            medico_id = st.selectbox(
                "Selecione o médico:",
                options=df_medicos['id'].tolist(),
                format_func=lambda x: f"{x} - {df_medicos[df_medicos['id'] == x]['nome'].values[0]}"
            )

            if medico_id:
                medico = df_medicos[df_medicos['id'] == medico_id].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**👤 Informações Pessoais**")
                    st.write(f"**Nome:** {medico['nome']}")
                    st.write(f"**CRM:** {medico['crm']}")
                    st.write(f"**Especialidade:** {medico['especialidade']}")

                with col2:
                    st.markdown("**📞 Contato**")
                    telefone = medico.get('telefone', '-')
                    email = medico.get('email', '-')
                    st.write(f"**Telefone:** {telefone if telefone else '-'}")
                    st.write(f"**Email:** {email if email else '-'}")

                    ativo = medico.get('ativo', True)
                    if ativo:
                        st.success("✅ Médico Ativo")
                    else:
                        st.error("❌ Médico Inativo")
        else:
            st.info("Nenhum médico encontrado com os filtros aplicados.")

    # ========================================================================
    # TAB: CADASTRO DE NOVO MÉDICO
    # ========================================================================

    with tab_cadastro:
        st.subheader("➕ Cadastrar Novo Médico")

        with st.form("form_novo_medico", clear_on_submit=True):
            st.markdown("**👤 Dados do Médico**")

            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome Completo *", placeholder="Dr./Dra. Nome Sobrenome")
                crm = st.text_input("CRM *", placeholder="12345-SP")
                especialidade = st.selectbox("Especialidade *", options=ESPECIALIDADES)

            with col2:
                telefone = st.text_input("Telefone", placeholder="(11) 99999-9999")
                email = st.text_input("Email", placeholder="medico@email.com")

            st.markdown("---")

            submitted = st.form_submit_button("💾 Cadastrar Médico", type="primary")

            if submitted:
                # Validações
                erros = []
                if not nome or len(nome.strip()) < 5:
                    erros.append("Nome deve ter pelo menos 5 caracteres")
                if not crm or len(crm.strip()) < 5:
                    erros.append("CRM inválido")

                # Verificar CRM duplicado
                medicos = get_medicos()
                if crm in medicos['crm'].values:
                    erros.append("CRM já cadastrado no sistema")

                if erros:
                    for erro in erros:
                        st.error(f"❌ {erro}")
                else:
                    # Cadastrar médico
                    novo_id = adicionar_medico(
                        nome=nome.strip(),
                        crm=crm.strip(),
                        especialidade=especialidade,
                        telefone=telefone.strip(),
                        email=email.strip()
                    )
                    st.success(f"✅ Médico **{nome}** cadastrado com sucesso! (ID: {novo_id})")
                    st.balloons()

    # ========================================================================
    # TAB: EDITAR/REMOVER MÉDICO
    # ========================================================================

    with tab_editar:
        st.subheader("✏️ Editar ou Remover Médico")

        medicos = get_medicos()

        if len(medicos) == 0:
            st.warning("Nenhum médico cadastrado.")
        else:
            # Selecionar médico
            medico_edit_id = st.selectbox(
                "Selecione o médico para editar:",
                options=medicos['id'].tolist(),
                format_func=lambda x: f"{x} - {medicos[medicos['id'] == x]['nome'].values[0]}",
                key="select_edit_medico"
            )

            if medico_edit_id:
                medico = medicos[medicos['id'] == medico_edit_id].iloc[0]

                st.markdown("---")

                # Formulário de edição
                with st.form("form_editar_medico"):
                    st.markdown("**✏️ Editar Dados**")

                    col1, col2 = st.columns(2)

                    with col1:
                        edit_nome = st.text_input("Nome Completo", value=medico['nome'])
                        edit_crm = st.text_input("CRM", value=medico['crm'])
                        edit_especialidade = st.selectbox(
                            "Especialidade",
                            options=ESPECIALIDADES,
                            index=ESPECIALIDADES.index(medico['especialidade']) if medico['especialidade'] in ESPECIALIDADES else 0
                        )

                    with col2:
                        edit_telefone = st.text_input("Telefone", value=medico.get('telefone', ''))
                        edit_email = st.text_input("Email", value=medico.get('email', ''))

                    submitted_edit = st.form_submit_button("💾 Salvar Alterações", type="primary")

                    if submitted_edit:
                        dados_atualizados = {
                            'nome': edit_nome.strip(),
                            'crm': edit_crm.strip(),
                            'especialidade': edit_especialidade,
                            'telefone': edit_telefone.strip(),
                            'email': edit_email.strip()
                        }
                        if atualizar_medico(medico_edit_id, dados_atualizados):
                            st.success("✅ Dados atualizados com sucesso!")
                        else:
                            st.error("❌ Erro ao atualizar dados.")

                st.markdown("---")

                # Ações de ativar/desativar
                st.markdown("**⚠️ Ações**")

                col_acao1, col_acao2 = st.columns(2)

                ativo = medico.get('ativo', True)

                with col_acao1:
                    if ativo:
                        if st.button("🚫 Desativar Médico", type="secondary", key="btn_desativar"):
                            if remover_medico(medico_edit_id):
                                st.warning(f"Médico **{medico['nome']}** desativado.")
                                st.rerun()
                    else:
                        if st.button("✅ Reativar Médico", type="primary", key="btn_reativar"):
                            if reativar_medico(medico_edit_id):
                                st.success(f"Médico **{medico['nome']}** reativado.")
                                st.rerun()

                with col_acao2:
                    st.info("💡 Médicos desativados não aparecem nas listas de seleção, mas seu histórico é mantido.")
