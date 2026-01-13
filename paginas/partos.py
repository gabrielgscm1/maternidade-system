"""
Página de Registro de Partos e Recém-Nascidos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from paginas.utils import get_dados


def render():
    st.markdown('<h1 class="main-header">👶 Registro de Partos</h1>', unsafe_allow_html=True)

    dados = get_dados()
    pacientes = dados['pacientes']
    partos = dados['partos']
    recem_nascidos = dados['recem_nascidos']

    # ========================================================================
    # TABS
    # ========================================================================

    tab_lista, tab_registro, tab_rn, tab_estatisticas = st.tabs([
        "📋 Partos Realizados",
        "➕ Registrar Parto",
        "👶 Recém-Nascidos",
        "📊 Estatísticas"
    ])

    # ========================================================================
    # TAB: LISTA DE PARTOS
    # ========================================================================

    with tab_lista:
        st.subheader("📋 Partos Realizados")

        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            periodo = st.date_input(
                "Período",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="periodo_partos"
            )

        with col_f2:
            tipo_filtro = st.multiselect(
                "Tipo de Parto",
                options=['Normal', 'Cesárea', 'Fórceps', 'Vácuo-extração'],
                default=['Normal', 'Cesárea', 'Fórceps', 'Vácuo-extração']
            )

        with col_f3:
            medico_filtro = st.selectbox(
                "Obstetra",
                options=['Todos'] + partos['obstetra'].unique().tolist()
            )

        # Aplicar filtros
        df_partos = partos.copy()

        if len(periodo) == 2:
            df_partos = df_partos[
                (df_partos['data_parto'] >= periodo[0]) &
                (df_partos['data_parto'] <= periodo[1])
            ]

        if tipo_filtro:
            df_partos = df_partos[df_partos['tipo_parto'].isin(tipo_filtro)]

        if medico_filtro != 'Todos':
            df_partos = df_partos[df_partos['obstetra'] == medico_filtro]

        st.write(f"**{len(df_partos)}** parto(s) no período")

        # Tabela de partos
        if len(df_partos) > 0:
            df_exibir = df_partos[[
                'id', 'nome_paciente', 'data_parto', 'hora_parto',
                'tipo_parto', 'obstetra', 'intercorrencias'
            ]].copy()

            df_exibir.columns = ['ID', 'Paciente', 'Data', 'Hora', 'Tipo', 'Obstetra', 'Intercorrências']

            st.dataframe(df_exibir, use_container_width=True, hide_index=True)

            # Detalhes do parto selecionado
            st.markdown("---")
            st.subheader("📄 Detalhes do Parto")

            parto_id = st.selectbox(
                "Selecione o parto:",
                options=df_partos['id'].tolist(),
                format_func=lambda x: f"{x} - {partos[partos['id'] == x]['nome_paciente'].values[0]} ({partos[partos['id'] == x]['data_parto'].values[0]})"
            )

            if parto_id:
                parto = partos[partos['id'] == parto_id].iloc[0]

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**👩 Dados da Mãe**")
                    st.write(f"**Paciente:** {parto['nome_paciente']}")
                    st.write(f"**Data/Hora:** {parto['data_parto']} às {parto['hora_parto']}")

                with col2:
                    st.markdown("**🏥 Dados do Parto**")
                    st.write(f"**Tipo:** {parto['tipo_parto']}")
                    st.write(f"**Anestesia:** {parto['anestesia']}")
                    st.write(f"**Duração TP:** {parto['duracao_trabalho_parto']}")

                    if parto['tipo_parto'] == 'Cesárea':
                        st.write(f"**Indicação:** {parto['indicacao_cesarea']}")

                with col3:
                    st.markdown("**👨‍⚕️ Equipe**")
                    st.write(f"**Obstetra:** {parto['obstetra']}")
                    st.write(f"**Pediatra:** {parto['pediatra']}")
                    st.write(f"**Anestesista:** {parto['anestesista']}")

                # Intercorrências
                if parto['intercorrencias'] != 'Nenhuma':
                    st.error(f"⚠️ **Intercorrência:** {parto['intercorrencias']}")

                st.write(f"**Perda Sanguínea Estimada:** {parto['perda_sanguinea_estimada']}")

                # RN associado
                rn = recem_nascidos[recem_nascidos['id_mae'] == parto['id_paciente']]
                if len(rn) > 0:
                    rn = rn.iloc[0]
                    st.markdown("---")
                    st.markdown("### 👶 Recém-Nascido")

                    col_rn1, col_rn2, col_rn3 = st.columns(3)

                    with col_rn1:
                        st.write(f"**Sexo:** {rn['sexo']}")
                        st.write(f"**Peso:** {rn['peso']}g")
                        st.write(f"**Comprimento:** {rn['comprimento']}cm")

                    with col_rn2:
                        st.write(f"**PC:** {rn['perimetro_cefalico']}cm")
                        st.write(f"**Apgar:** {rn['apgar_1min']}/{rn['apgar_5min']}/{rn['apgar_10min']}")

                    with col_rn3:
                        st.write(f"**Reanimação:** {rn['reanimacao']}")
                        ac = "✅ Sim" if rn['alojamento_conjunto'] else "❌ Não"
                        st.write(f"**Aloj. Conjunto:** {ac}")
        else:
            st.info("Nenhum parto encontrado no período selecionado.")

    # ========================================================================
    # TAB: REGISTRAR PARTO
    # ========================================================================

    with tab_registro:
        st.subheader("➕ Registrar Novo Parto")

        # Listar apenas pacientes internadas/em trabalho de parto
        pacientes_elegiveis = pacientes[
            pacientes['status'].isin(['Internada', 'Em trabalho de parto'])
        ]

        if len(pacientes_elegiveis) == 0:
            st.warning("Não há pacientes internadas para registro de parto.")
        else:
            with st.form("form_parto"):
                st.markdown("**👩 Identificação**")

                paciente_id = st.selectbox(
                    "Paciente",
                    options=pacientes_elegiveis['id'].tolist(),
                    format_func=lambda x: f"{x} - {pacientes_elegiveis[pacientes_elegiveis['id'] == x]['nome'].values[0]} (IG: {pacientes_elegiveis[pacientes_elegiveis['id'] == x]['semanas_gestacao'].values[0]} sem)"
                )

                col1, col2 = st.columns(2)

                with col1:
                    data_parto = st.date_input("Data do Parto", value=datetime.now())
                    hora_parto = st.time_input("Hora do Parto", value=datetime.now().time())

                with col2:
                    tipo_parto = st.selectbox("Tipo de Parto", ['Normal', 'Cesárea', 'Fórceps', 'Vácuo-extração'])
                    anestesia = st.selectbox("Anestesia", ['Raquidiana', 'Peridural', 'Combinada', 'Local', 'Nenhuma'])

                # Indicação de cesárea (se aplicável)
                if tipo_parto == 'Cesárea':
                    indicacao = st.selectbox(
                        "Indicação da Cesárea",
                        ['Desproporção cefalopélvica', 'Sofrimento fetal', 'Falha de indução',
                         'Cesárea anterior', 'Apresentação pélvica', 'Placenta prévia', 'Outra']
                    )
                else:
                    indicacao = 'Não se aplica'

                st.markdown("---")
                st.markdown("**👨‍⚕️ Equipe**")

                col_eq1, col_eq2, col_eq3 = st.columns(3)

                with col_eq1:
                    obstetra = st.selectbox(
                        "Obstetra",
                        ['Dr. Carlos Alberto Silva', 'Dra. Maria Fernanda Costa', 'Dr. Roberto Santos']
                    )

                with col_eq2:
                    pediatra = st.selectbox("Pediatra", ['Dra. Ana Paula Oliveira'])

                with col_eq3:
                    anestesista = st.selectbox("Anestesista", ['Dr. Fernando Lima', 'Não aplicável'])

                st.markdown("---")
                st.markdown("**📝 Dados do Trabalho de Parto**")

                col_tp1, col_tp2 = st.columns(2)

                with col_tp1:
                    duracao_tp = st.text_input("Duração do Trabalho de Parto", placeholder="Ex: 8 horas")
                    perda_sanguinea = st.number_input("Perda Sanguínea Estimada (mL)", min_value=0, max_value=5000, value=300)

                with col_tp2:
                    intercorrencias = st.selectbox(
                        "Intercorrências",
                        ['Nenhuma', 'Atonia uterina', 'Laceração perineal', 'Hemorragia pós-parto',
                         'Retenção placentária', 'Inversão uterina', 'Outra']
                    )

                st.markdown("---")
                st.markdown("**👶 Dados do Recém-Nascido**")

                col_rn1, col_rn2 = st.columns(2)

                with col_rn1:
                    sexo_rn = st.radio("Sexo", ['Masculino', 'Feminino'], horizontal=True)
                    peso_rn = st.number_input("Peso (g)", min_value=500, max_value=6000, value=3200)
                    comprimento_rn = st.number_input("Comprimento (cm)", min_value=30.0, max_value=60.0, value=49.0)
                    pc_rn = st.number_input("Perímetro Cefálico (cm)", min_value=25.0, max_value=45.0, value=34.0)

                with col_rn2:
                    apgar_1 = st.number_input("Apgar 1º minuto", min_value=0, max_value=10, value=8)
                    apgar_5 = st.number_input("Apgar 5º minuto", min_value=0, max_value=10, value=9)
                    apgar_10 = st.number_input("Apgar 10º minuto", min_value=0, max_value=10, value=10)
                    reanimacao = st.selectbox("Reanimação", ['Não necessária', 'O2 inalatório', 'VPP', 'Intubação'])

                aloj_conjunto = st.checkbox("Encaminhar para Alojamento Conjunto", value=True)

                observacoes_rn = st.text_area("Observações do RN", placeholder="Condições ao nascer, malformações, etc.")

                submitted = st.form_submit_button("💾 Registrar Parto", type="primary")

                if submitted:
                    st.success("✅ Parto registrado com sucesso!")
                    st.balloons()

                    # Resumo
                    st.markdown("### 📋 Resumo do Registro")
                    paciente_nome = pacientes_elegiveis[pacientes_elegiveis['id'] == paciente_id]['nome'].values[0]
                    st.write(f"**Paciente:** {paciente_nome}")
                    st.write(f"**Tipo de Parto:** {tipo_parto}")
                    st.write(f"**RN:** {sexo_rn}, {peso_rn}g, Apgar {apgar_1}/{apgar_5}/{apgar_10}")

    # ========================================================================
    # TAB: RECÉM-NASCIDOS
    # ========================================================================

    with tab_rn:
        st.subheader("👶 Recém-Nascidos")

        # Filtros
        col_rn_f1, col_rn_f2 = st.columns(2)

        with col_rn_f1:
            sexo_filtro = st.multiselect(
                "Sexo",
                options=['Masculino', 'Feminino'],
                default=['Masculino', 'Feminino']
            )

        with col_rn_f2:
            ac_filtro = st.radio(
                "Alojamento Conjunto",
                options=['Todos', 'Sim', 'Não'],
                horizontal=True
            )

        # Aplicar filtros
        df_rn = recem_nascidos.copy()

        if sexo_filtro:
            df_rn = df_rn[df_rn['sexo'].isin(sexo_filtro)]

        if ac_filtro == 'Sim':
            df_rn = df_rn[df_rn['alojamento_conjunto'] == True]
        elif ac_filtro == 'Não':
            df_rn = df_rn[df_rn['alojamento_conjunto'] == False]

        st.write(f"**{len(df_rn)}** recém-nascido(s)")

        # Cards de RNs
        for _, rn in df_rn.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"**{rn['nome']}**")
                    st.write(f"Mãe: {rn['nome_mae']}")

                with col2:
                    emoji_sexo = "👦" if rn['sexo'] == 'Masculino' else "👧"
                    st.write(f"{emoji_sexo} {rn['sexo']}")
                    st.write(f"📅 {rn['data_nascimento'].strftime('%d/%m/%Y') if hasattr(rn['data_nascimento'], 'strftime') else rn['data_nascimento']}")

                with col3:
                    st.write(f"⚖️ {rn['peso']}g")
                    st.write(f"📏 {rn['comprimento']}cm")

                with col4:
                    st.write(f"Apgar: {rn['apgar_1min']}/{rn['apgar_5min']}")
                    if rn['alojamento_conjunto']:
                        st.success("AC")
                    else:
                        st.warning("UTI")

                st.markdown("---")

    # ========================================================================
    # TAB: ESTATÍSTICAS
    # ========================================================================

    with tab_estatisticas:
        st.subheader("📊 Estatísticas de Partos")

        col_stat1, col_stat2 = st.columns(2)

        with col_stat1:
            # Tipos de parto
            st.markdown("### 🏥 Tipos de Parto")
            tipos = partos['tipo_parto'].value_counts()

            fig_tipos = px.pie(
                values=tipos.values,
                names=tipos.index,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            fig_tipos.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_tipos, use_container_width=True)

            # Taxa de cesárea
            taxa_ces = (len(partos[partos['tipo_parto'] == 'Cesárea']) / len(partos) * 100) if len(partos) > 0 else 0
            st.metric("Taxa de Cesárea", f"{taxa_ces:.1f}%")

            if taxa_ces > 55:
                st.warning("⚠️ Taxa acima da recomendação OMS (10-15%)")

        with col_stat2:
            # Distribuição por sexo
            st.markdown("### 👶 Sexo dos RNs")
            sexos = recem_nascidos['sexo'].value_counts()

            fig_sexo = px.pie(
                values=sexos.values,
                names=sexos.index,
                color_discrete_map={'Masculino': '#2196F3', 'Feminino': '#E91E63'},
                hole=0.4
            )
            fig_sexo.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_sexo, use_container_width=True)

        # Indicações de cesárea
        st.markdown("### 📋 Indicações de Cesárea")
        cesareas = partos[partos['tipo_parto'] == 'Cesárea']

        if len(cesareas) > 0:
            indicacoes = cesareas['indicacao_cesarea'].value_counts()

            fig_ind = px.bar(
                x=indicacoes.index,
                y=indicacoes.values,
                color=indicacoes.index,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_ind.update_layout(
                showlegend=False,
                xaxis_tickangle=-45,
                margin=dict(t=0, b=100)
            )
            st.plotly_chart(fig_ind, use_container_width=True)

        # Peso dos RNs
        st.markdown("### ⚖️ Distribuição de Peso ao Nascer")

        fig_peso = px.histogram(
            recem_nascidos,
            x='peso',
            nbins=20,
            color_discrete_sequence=['#E91E63']
        )
        fig_peso.update_layout(
            xaxis_title="Peso (g)",
            yaxis_title="Frequência",
            margin=dict(t=0, b=0)
        )
        st.plotly_chart(fig_peso, use_container_width=True)

        # Estatísticas descritivas
        col_desc1, col_desc2, col_desc3 = st.columns(3)

        with col_desc1:
            st.metric("Peso Médio", f"{recem_nascidos['peso'].mean():.0f}g")

        with col_desc2:
            st.metric("Peso Mínimo", f"{recem_nascidos['peso'].min()}g")

        with col_desc3:
            st.metric("Peso Máximo", f"{recem_nascidos['peso'].max()}g")
