"""
Página de Prontuário Eletrônico
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from paginas.utils import get_dados, adicionar_evolucao


def render():
    st.markdown('<h1 class="main-header">📋 Prontuário Eletrônico</h1>', unsafe_allow_html=True)

    dados = get_dados()
    pacientes = dados['pacientes']
    evolucoes = dados['evolucoes']
    exames = dados['exames']

    # ========================================================================
    # SELEÇÃO DE PACIENTE
    # ========================================================================

    st.subheader("🔍 Selecionar Paciente")

    # Verificar se há paciente pré-selecionado
    paciente_pre = st.session_state.get('paciente_prontuario', None)

    col_sel1, col_sel2 = st.columns([3, 1])

    with col_sel1:
        paciente_id = st.selectbox(
            "Paciente",
            options=pacientes['id'].tolist(),
            index=pacientes['id'].tolist().index(paciente_pre) if paciente_pre and paciente_pre in pacientes['id'].tolist() else 0,
            format_func=lambda x: f"{x} - {pacientes[pacientes['id'] == x]['nome'].values[0]} ({pacientes[pacientes['id'] == x]['status'].values[0]})"
        )

    with col_sel2:
        st.write("")
        st.write("")
        if st.button("🔄 Atualizar"):
            st.rerun()

    if not paciente_id:
        st.warning("Selecione uma paciente para visualizar o prontuário.")
        return

    paciente = pacientes[pacientes['id'] == paciente_id].iloc[0]

    # ========================================================================
    # CABEÇALHO DO PRONTUÁRIO
    # ========================================================================

    st.markdown("---")

    # Informações resumidas
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)

    with col_h1:
        st.markdown(f"### {paciente['nome']}")
        st.write(f"📅 {paciente['idade']} anos | 🩸 {paciente['tipo_sanguineo']}")

    with col_h2:
        st.metric("IG", f"{paciente['semanas_gestacao']} sem")

    with col_h3:
        st.metric("DPP", str(paciente['dpp']))

    with col_h4:
        status_emoji = {
            'Internada': '🟢',
            'Em trabalho de parto': '🟠',
            'Pós-parto': '🔵',
            'Alta': '⚪',
            'UTI': '🔴'
        }
        st.metric("Status", f"{status_emoji.get(paciente['status'], '')} {paciente['status']}")

    # Alertas importantes
    if paciente['comorbidades'] != 'Nenhuma' or paciente['alergias'] != 'Nenhuma':
        alert_col1, alert_col2 = st.columns(2)
        with alert_col1:
            if paciente['comorbidades'] != 'Nenhuma':
                st.error(f"⚠️ **Comorbidade:** {paciente['comorbidades']}")
        with alert_col2:
            if paciente['alergias'] != 'Nenhuma':
                st.error(f"💊 **Alergia:** {paciente['alergias']}")

    st.markdown("---")

    # ========================================================================
    # TABS DO PRONTUÁRIO
    # ========================================================================

    tab_evolucao, tab_exames, tab_historico, tab_nova_evolucao = st.tabs([
        "📝 Evoluções",
        "🔬 Exames",
        "📚 Histórico Obstétrico",
        "➕ Nova Evolução"
    ])

    # ========================================================================
    # TAB: EVOLUÇÕES
    # ========================================================================

    with tab_evolucao:
        st.subheader("📝 Evoluções Médicas")

        # Filtrar evoluções da paciente
        evolucoes_paciente = evolucoes[evolucoes['id_paciente'] == paciente_id].sort_values(
            'data_hora', ascending=False
        )

        if len(evolucoes_paciente) == 0:
            st.info("Nenhuma evolução registrada para esta paciente.")
        else:
            for _, ev in evolucoes_paciente.iterrows():
                with st.expander(
                    f"📅 {ev['data_hora'].strftime('%d/%m/%Y %H:%M')} - {ev['tipo']} | {ev['medico']}",
                    expanded=True if _ == evolucoes_paciente.index[0] else False
                ):
                    # Sinais vitais
                    sv = ev['sinais_vitais']
                    col_sv1, col_sv2, col_sv3, col_sv4 = st.columns(4)
                    col_sv1.metric("PA", sv['pa'])
                    col_sv2.metric("FC", f"{sv['fc']} bpm")
                    col_sv3.metric("Temp", f"{sv['temp']}°C")
                    col_sv4.metric("FR", f"{sv['fr']} irpm")

                    st.markdown("**Descrição:**")
                    st.write(ev['descricao'])

                    st.markdown("**Conduta:**")
                    st.info(ev['conduta'])

    # ========================================================================
    # TAB: EXAMES
    # ========================================================================

    with tab_exames:
        st.subheader("🔬 Exames Laboratoriais e de Imagem")

        # Filtrar exames da paciente
        exames_paciente = exames[exames['id_paciente'] == paciente_id].sort_values(
            'data_solicitacao', ascending=False
        )

        # Filtro por status
        col_ex1, col_ex2 = st.columns([1, 3])
        with col_ex1:
            filtro_status_exame = st.selectbox(
                "Filtrar por status",
                ['Todos', 'Concluído', 'Pendente']
            )

        if filtro_status_exame != 'Todos':
            exames_paciente = exames_paciente[exames_paciente['status'] == filtro_status_exame]

        if len(exames_paciente) == 0:
            st.info("Nenhum exame encontrado.")
        else:
            # Agrupar por tipo
            for tipo in exames_paciente['tipo'].unique():
                exames_tipo = exames_paciente[exames_paciente['tipo'] == tipo]

                with st.expander(f"🔬 {tipo} ({len(exames_tipo)} registro(s))"):
                    for _, ex in exames_tipo.iterrows():
                        col_e1, col_e2, col_e3 = st.columns([2, 3, 1])

                        with col_e1:
                            st.write(f"**Solicitação:** {ex['data_solicitacao']}")
                            st.write(f"**Resultado:** {ex['data_resultado']}")
                            st.write(f"**Solicitante:** {ex['solicitante']}")

                        with col_e2:
                            st.markdown("**Resultado:**")
                            st.code(ex['resultado'])

                        with col_e3:
                            if ex['status'] == 'Concluído':
                                st.success("✅ Concluído")
                            else:
                                st.warning("⏳ Pendente")

                        st.markdown("---")

        # Botão para solicitar novo exame
        st.markdown("---")
        if st.button("➕ Solicitar Novo Exame"):
            st.session_state['solicitar_exame'] = True

        if st.session_state.get('solicitar_exame'):
            with st.form("form_novo_exame"):
                st.subheader("Solicitar Exame")

                tipo_exame = st.selectbox(
                    "Tipo de Exame",
                    ['Hemograma Completo', 'Glicemia', 'Urina Tipo I', 'Urocultura',
                     'Ultrassonografia Obstétrica', 'Cardiotocografia', 'Doppler',
                     'Teste de Tolerância à Glicose', 'Sorologia HIV', 'Sorologia Hepatite B']
                )

                urgencia = st.radio("Urgência", ['Rotina', 'Urgente'], horizontal=True)

                observacoes = st.text_area("Observações/Indicação Clínica")

                if st.form_submit_button("✅ Solicitar"):
                    st.success(f"Exame **{tipo_exame}** solicitado com sucesso!")
                    st.session_state['solicitar_exame'] = False

    # ========================================================================
    # TAB: HISTÓRICO OBSTÉTRICO
    # ========================================================================

    with tab_historico:
        st.subheader("📚 Histórico Obstétrico")

        col_hist1, col_hist2 = st.columns(2)

        with col_hist1:
            st.markdown("### 🤰 Gestação Atual")

            st.write(f"**Data Última Menstruação (DUM):** {paciente['dum']}")
            st.write(f"**Data Provável do Parto (DPP):** {paciente['dpp']}")
            st.write(f"**Idade Gestacional:** {paciente['semanas_gestacao']} semanas")

            st.markdown("---")

            st.markdown("### 📊 Paridade")
            st.write(f"**Gestações (G):** {paciente['num_gestacoes']}")
            st.write(f"**Partos (P):** {paciente['num_partos']}")
            st.write(f"**Abortos (A):** {paciente['num_abortos']}")

            # Fórmula obstétrica
            g = paciente['num_gestacoes']
            p = paciente['num_partos']
            a = paciente['num_abortos']
            st.info(f"**Fórmula Obstétrica:** G{g}P{p}A{a}")

        with col_hist2:
            st.markdown("### 📏 Dados Antropométricos")

            peso_pre = paciente['peso_pre_gestacional']
            altura = paciente['altura']
            imc = peso_pre / (altura ** 2)

            st.write(f"**Peso Pré-Gestacional:** {peso_pre} kg")
            st.write(f"**Altura:** {altura} m")
            st.write(f"**IMC Pré-Gestacional:** {imc:.1f} kg/m²")

            # Classificação do IMC
            if imc < 18.5:
                st.warning("Baixo peso")
            elif imc < 25:
                st.success("Peso normal")
            elif imc < 30:
                st.warning("Sobrepeso")
            else:
                st.error("Obesidade")

            st.markdown("---")

            st.markdown("### ⚠️ Fatores de Risco")

            riscos = []
            if paciente['idade'] >= 35:
                riscos.append("Idade materna avançada (≥35 anos)")
            if paciente['comorbidades'] != 'Nenhuma':
                riscos.append(f"Comorbidade: {paciente['comorbidades']}")
            if paciente['num_abortos'] >= 2:
                riscos.append("Abortamento de repetição")
            if imc >= 30:
                riscos.append("Obesidade")

            if riscos:
                for risco in riscos:
                    st.error(f"• {risco}")
            else:
                st.success("✅ Sem fatores de risco identificados")

        # Gráfico de evolução da gestação
        st.markdown("---")
        st.markdown("### 📈 Curva de Crescimento Fetal (Simulado)")

        import plotly.graph_objects as go
        import numpy as np

        semanas = list(range(20, paciente['semanas_gestacao'] + 1))
        peso_estimado = [300 + (s - 20) * 180 + np.random.randint(-50, 50) for s in semanas]

        # Percentis de referência
        p10 = [250 + (s - 20) * 150 for s in semanas]
        p50 = [300 + (s - 20) * 175 for s in semanas]
        p90 = [350 + (s - 20) * 200 for s in semanas]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=semanas, y=p10, mode='lines', name='P10', line=dict(dash='dash', color='gray')))
        fig.add_trace(go.Scatter(x=semanas, y=p50, mode='lines', name='P50', line=dict(dash='dash', color='blue')))
        fig.add_trace(go.Scatter(x=semanas, y=p90, mode='lines', name='P90', line=dict(dash='dash', color='gray')))
        fig.add_trace(go.Scatter(x=semanas, y=peso_estimado, mode='lines+markers', name='Peso Estimado', line=dict(color='#E91E63', width=3)))

        fig.update_layout(
            title="Peso Fetal Estimado x Idade Gestacional",
            xaxis_title="Semanas",
            yaxis_title="Peso (g)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # TAB: NOVA EVOLUÇÃO
    # ========================================================================

    with tab_nova_evolucao:
        st.subheader("➕ Registrar Nova Evolução")

        with st.form("form_evolucao"):
            st.markdown("**📅 Data e Tipo**")
            col_ev1, col_ev2 = st.columns(2)

            with col_ev1:
                data_evolucao = st.date_input("Data", value=datetime.now())
                hora_evolucao = st.time_input("Hora", value=datetime.now().time())

            with col_ev2:
                tipo_evolucao = st.selectbox(
                    "Tipo de Registro",
                    ['Evolução', 'Admissão', 'Intercorrência', 'Pré-Anestésico', 'Pré-Parto', 'Pós-Parto', 'Alta']
                )

            st.markdown("---")
            st.markdown("**🩺 Sinais Vitais**")
            col_sv1, col_sv2, col_sv3, col_sv4 = st.columns(4)

            with col_sv1:
                pa_sistolica = st.number_input("PA Sistólica", min_value=60, max_value=250, value=120)
                pa_diastolica = st.number_input("PA Diastólica", min_value=30, max_value=150, value=80)

            with col_sv2:
                fc = st.number_input("FC (bpm)", min_value=40, max_value=200, value=80)

            with col_sv3:
                temp = st.number_input("Temperatura (°C)", min_value=34.0, max_value=42.0, value=36.5, step=0.1)

            with col_sv4:
                fr = st.number_input("FR (irpm)", min_value=8, max_value=40, value=18)

            st.markdown("---")
            st.markdown("**🤰 Dados Obstétricos**")
            col_ob1, col_ob2, col_ob3 = st.columns(3)

            with col_ob1:
                au = st.number_input("Altura Uterina (cm)", min_value=10, max_value=45, value=30)
                bcf = st.number_input("BCF (bpm)", min_value=100, max_value=180, value=140)

            with col_ob2:
                dinamica = st.text_input("Dinâmica Uterina", placeholder="Ex: 2 em 10 min")
                dilatacao = st.number_input("Dilatação (cm)", min_value=0, max_value=10, value=0)

            with col_ob3:
                apresentacao = st.selectbox("Apresentação", ['Cefálica', 'Pélvica', 'Córmica'])
                bolsa = st.selectbox("Bolsa", ['Íntegra', 'Rota', 'Amniotomia'])

            st.markdown("---")
            st.markdown("**📝 Descrição e Conduta**")

            descricao = st.text_area(
                "Descrição/Evolução",
                height=150,
                placeholder="Descreva o estado da paciente, queixas, exame físico..."
            )

            conduta = st.text_area(
                "Conduta",
                height=100,
                placeholder="Prescrições, orientações, encaminhamentos..."
            )

            submitted = st.form_submit_button("💾 Salvar Evolução", type="primary")

            if submitted:
                if descricao:
                    nova_ev = {
                        'id_paciente': paciente_id,
                        'nome_paciente': paciente['nome'],
                        'data_hora': datetime.combine(data_evolucao, hora_evolucao),
                        'medico': 'Dr. Carlos Alberto Silva',  # Usuário logado
                        'tipo': tipo_evolucao,
                        'descricao': descricao,
                        'sinais_vitais': {
                            'pa': f"{pa_sistolica}/{pa_diastolica}",
                            'fc': fc,
                            'temp': temp,
                            'fr': fr
                        },
                        'conduta': conduta
                    }
                    adicionar_evolucao(nova_ev)
                    st.success("✅ Evolução registrada com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Preencha a descrição da evolução.")
