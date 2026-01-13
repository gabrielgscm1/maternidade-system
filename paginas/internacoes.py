"""
Página de Gestão de Internações e Leitos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from paginas.utils import get_dados


def render():
    st.markdown('<h1 class="main-header">🛏️ Gestão de Internações e Leitos</h1>', unsafe_allow_html=True)

    dados = get_dados()
    pacientes = dados['pacientes']
    leitos = dados['leitos']

    # ========================================================================
    # TABS
    # ========================================================================

    tab_mapa, tab_internacao, tab_transferencia, tab_alta = st.tabs([
        "🗺️ Mapa de Leitos",
        "➕ Nova Internação",
        "🔄 Transferência",
        "📤 Alta Hospitalar"
    ])

    # ========================================================================
    # TAB: MAPA DE LEITOS
    # ========================================================================

    with tab_mapa:
        st.subheader("🗺️ Mapa de Ocupação de Leitos")

        # Resumo geral
        total_leitos = len(leitos)
        leitos_ocupados = len(pacientes[pacientes['leito'].notna()])
        leitos_livres = total_leitos - leitos_ocupados
        taxa_ocupacao = (leitos_ocupados / total_leitos * 100) if total_leitos > 0 else 0

        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        col_res1.metric("Total de Leitos", total_leitos)
        col_res2.metric("Ocupados", leitos_ocupados)
        col_res3.metric("Livres", leitos_livres)
        col_res4.metric("Taxa Ocupação", f"{taxa_ocupacao:.1f}%")

        st.markdown("---")

        # Filtro por setor
        setor_selecionado = st.selectbox(
            "Selecione o Setor",
            ['Todos', 'Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']
        )

        # Mapa visual por setor
        setores = ['Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']

        if setor_selecionado != 'Todos':
            setores = [setor_selecionado]

        for setor in setores:
            st.markdown(f"### 🏥 {setor}")

            leitos_setor = leitos[leitos['setor'] == setor]
            leitos_ids = leitos_setor['id'].tolist()

            # Determinar ocupação
            pacientes_setor = pacientes[pacientes['leito'].isin(leitos_ids)]

            # Criar grid de leitos
            num_colunas = 5
            cols = st.columns(num_colunas)

            for idx, leito_row in leitos_setor.iterrows():
                leito_id = leito_row['id']
                col_idx = idx % num_colunas

                # Verificar se ocupado
                paciente_leito = pacientes[pacientes['leito'] == leito_id]

                with cols[col_idx]:
                    if len(paciente_leito) > 0:
                        p = paciente_leito.iloc[0]
                        status_emoji = {
                            'Internada': '🟢',
                            'Em trabalho de parto': '🟠',
                            'Pós-parto': '🔵',
                            'UTI': '🔴'
                        }
                        emoji = status_emoji.get(p['status'], '⚪')

                        st.markdown(f"""
                        <div style="
                            background-color: #FFEBEE;
                            border: 2px solid #E91E63;
                            border-radius: 10px;
                            padding: 10px;
                            margin: 5px 0;
                            text-align: center;
                        ">
                            <strong>{leito_id}</strong><br>
                            {emoji} {p['status']}<br>
                            <small>{p['nome'].split()[0]}</small><br>
                            <small>IG: {p['semanas_gestacao']}sem</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="
                            background-color: #E8F5E9;
                            border: 2px solid #4CAF50;
                            border-radius: 10px;
                            padding: 10px;
                            margin: 5px 0;
                            text-align: center;
                        ">
                            <strong>{leito_id}</strong><br>
                            ✅ Livre<br>
                            <small>{leito_row['tipo']}</small>
                        </div>
                        """, unsafe_allow_html=True)

            # Estatísticas do setor
            ocupados_setor = len(pacientes_setor)
            total_setor = len(leitos_setor)
            taxa_setor = (ocupados_setor / total_setor * 100) if total_setor > 0 else 0

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.write(f"**Total:** {total_setor}")
            col_s2.write(f"**Ocupados:** {ocupados_setor}")
            col_s3.write(f"**Taxa:** {taxa_setor:.0f}%")

            st.markdown("---")

        # Gráfico de ocupação por setor
        st.subheader("📊 Ocupação por Setor")

        ocupacao_data = []
        for setor in ['Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']:
            leitos_setor = leitos[leitos['setor'] == setor]['id'].tolist()
            ocupados = len(pacientes[pacientes['leito'].isin(leitos_setor)])
            total = len(leitos_setor)
            ocupacao_data.append({
                'Setor': setor,
                'Ocupados': ocupados,
                'Livres': total - ocupados
            })

        df_ocup = pd.DataFrame(ocupacao_data)

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Ocupados', x=df_ocup['Setor'], y=df_ocup['Ocupados'], marker_color='#E91E63'))
        fig.add_trace(go.Bar(name='Livres', x=df_ocup['Setor'], y=df_ocup['Livres'], marker_color='#4CAF50'))
        fig.update_layout(barmode='stack', xaxis_tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # TAB: NOVA INTERNAÇÃO
    # ========================================================================

    with tab_internacao:
        st.subheader("➕ Registrar Nova Internação")

        # Pacientes não internadas
        pacientes_disponiveis = pacientes[pacientes['leito'].isna()]

        if len(pacientes_disponiveis) == 0:
            st.info("Todas as pacientes já estão internadas ou não há pacientes cadastradas.")
        else:
            with st.form("form_internacao"):
                st.markdown("**👩 Selecionar Paciente**")

                paciente_id = st.selectbox(
                    "Paciente",
                    options=pacientes_disponiveis['id'].tolist(),
                    format_func=lambda x: f"{x} - {pacientes_disponiveis[pacientes_disponiveis['id'] == x]['nome'].values[0]}"
                )

                st.markdown("---")
                st.markdown("**🛏️ Selecionar Leito**")

                # Leitos disponíveis
                leitos_ocupados = pacientes[pacientes['leito'].notna()]['leito'].tolist()
                leitos_livres = leitos[~leitos['id'].isin(leitos_ocupados)]

                setor_internacao = st.selectbox(
                    "Setor",
                    options=['Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']
                )

                leitos_setor_livres = leitos_livres[leitos_livres['setor'] == setor_internacao]

                if len(leitos_setor_livres) == 0:
                    st.warning(f"⚠️ Não há leitos disponíveis no setor {setor_internacao}")
                    leito_id = None
                else:
                    leito_id = st.selectbox(
                        "Leito",
                        options=leitos_setor_livres['id'].tolist(),
                        format_func=lambda x: f"{x} ({leitos_setor_livres[leitos_setor_livres['id'] == x]['tipo'].values[0]})"
                    )

                st.markdown("---")
                st.markdown("**📋 Dados da Internação**")

                col_int1, col_int2 = st.columns(2)

                with col_int1:
                    data_internacao = st.date_input("Data de Internação", value=datetime.now())
                    hora_internacao = st.time_input("Hora", value=datetime.now().time())

                with col_int2:
                    motivo_internacao = st.selectbox(
                        "Motivo da Internação",
                        ['Trabalho de parto', 'Cesárea eletiva', 'Indução de parto',
                         'Pré-eclâmpsia', 'Diabetes descompensada', 'Sangramento', 'Outros']
                    )

                medico_internacao = st.selectbox(
                    "Médico Responsável",
                    ['Dr. Carlos Alberto Silva', 'Dra. Maria Fernanda Costa', 'Dr. Roberto Santos']
                )

                observacoes = st.text_area("Observações", placeholder="Informações relevantes sobre a internação...")

                submitted = st.form_submit_button("💾 Registrar Internação", type="primary")

                if submitted and leito_id:
                    st.success(f"✅ Internação registrada com sucesso! Leito: {leito_id}")
                    st.balloons()

    # ========================================================================
    # TAB: TRANSFERÊNCIA
    # ========================================================================

    with tab_transferencia:
        st.subheader("🔄 Transferência de Leito")

        # Pacientes internadas
        pacientes_internadas = pacientes[pacientes['leito'].notna()]

        if len(pacientes_internadas) == 0:
            st.info("Não há pacientes internadas para transferir.")
        else:
            with st.form("form_transferencia"):
                st.markdown("**👩 Paciente a Transferir**")

                paciente_transf = st.selectbox(
                    "Paciente",
                    options=pacientes_internadas['id'].tolist(),
                    format_func=lambda x: f"{x} - {pacientes_internadas[pacientes_internadas['id'] == x]['nome'].values[0]} (Leito atual: {pacientes_internadas[pacientes_internadas['id'] == x]['leito'].values[0]})"
                )

                # Leito atual
                paciente_data = pacientes_internadas[pacientes_internadas['id'] == paciente_transf].iloc[0]
                leito_atual = paciente_data['leito']

                st.info(f"📍 Leito atual: **{leito_atual}**")

                st.markdown("---")
                st.markdown("**🛏️ Novo Leito**")

                setor_destino = st.selectbox(
                    "Setor de Destino",
                    options=['Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna'],
                    key="setor_transf"
                )

                # Leitos disponíveis no setor destino (excluindo o atual)
                leitos_ocupados = pacientes[pacientes['leito'].notna()]['leito'].tolist()
                leitos_livres = leitos[~leitos['id'].isin(leitos_ocupados)]
                leitos_destino = leitos_livres[leitos_livres['setor'] == setor_destino]

                if len(leitos_destino) == 0:
                    st.warning(f"⚠️ Não há leitos disponíveis no setor {setor_destino}")
                    novo_leito = None
                else:
                    novo_leito = st.selectbox(
                        "Novo Leito",
                        options=leitos_destino['id'].tolist()
                    )

                motivo_transf = st.text_area("Motivo da Transferência", placeholder="Ex: Paciente em trabalho de parto ativo, transferida para Centro Obstétrico")

                submitted = st.form_submit_button("🔄 Realizar Transferência", type="primary")

                if submitted and novo_leito:
                    st.success(f"✅ Transferência realizada! De {leito_atual} para {novo_leito}")

    # ========================================================================
    # TAB: ALTA HOSPITALAR
    # ========================================================================

    with tab_alta:
        st.subheader("📤 Alta Hospitalar")

        # Pacientes que podem receber alta (pós-parto ou internada)
        pacientes_alta = pacientes[
            (pacientes['leito'].notna()) &
            (pacientes['status'].isin(['Pós-parto', 'Internada']))
        ]

        if len(pacientes_alta) == 0:
            st.info("Não há pacientes elegíveis para alta no momento.")
        else:
            with st.form("form_alta"):
                st.markdown("**👩 Paciente**")

                paciente_alta_id = st.selectbox(
                    "Paciente",
                    options=pacientes_alta['id'].tolist(),
                    format_func=lambda x: f"{x} - {pacientes_alta[pacientes_alta['id'] == x]['nome'].values[0]} (Leito: {pacientes_alta[pacientes_alta['id'] == x]['leito'].values[0]})"
                )

                # Dados da paciente
                p_alta = pacientes_alta[pacientes_alta['id'] == paciente_alta_id].iloc[0]

                col_a1, col_a2 = st.columns(2)

                with col_a1:
                    st.write(f"**Nome:** {p_alta['nome']}")
                    st.write(f"**Leito:** {p_alta['leito']}")
                    st.write(f"**Internação:** {p_alta['data_internacao']}")

                with col_a2:
                    st.write(f"**Status:** {p_alta['status']}")
                    st.write(f"**Médico:** {p_alta['medico_responsavel']}")

                st.markdown("---")
                st.markdown("**📋 Dados da Alta**")

                tipo_alta = st.selectbox(
                    "Tipo de Alta",
                    ['Alta médica', 'Alta a pedido', 'Transferência', 'Óbito']
                )

                data_alta = st.date_input("Data da Alta", value=datetime.now())

                condicoes_alta = st.selectbox(
                    "Condições de Alta",
                    ['Boas', 'Estável', 'Melhorado', 'Inalterado']
                )

                st.markdown("---")
                st.markdown("**📝 Orientações de Alta**")

                orientacoes = st.text_area(
                    "Orientações",
                    value="""- Retorno em consulta de puerpério em 7-10 dias
- Manter aleitamento materno exclusivo
- Sinais de alarme: febre, sangramento intenso, dor abdominal intensa
- Consulta pediátrica do RN em 5-7 dias
- Realizar teste do pezinho até o 5º dia de vida""",
                    height=150
                )

                receitas = st.text_area(
                    "Prescrições de Alta",
                    placeholder="Medicamentos prescritos para uso domiciliar...",
                    height=100
                )

                st.markdown("---")
                st.markdown("**✅ Checklist de Alta**")

                col_check1, col_check2 = st.columns(2)

                with col_check1:
                    check1 = st.checkbox("Sumário de alta preenchido")
                    check2 = st.checkbox("Declaração de nascido vivo entregue")
                    check3 = st.checkbox("Cartão de vacinas do RN preenchido")

                with col_check2:
                    check4 = st.checkbox("Orientações de amamentação realizadas")
                    check5 = st.checkbox("Teste do pezinho agendado/realizado")
                    check6 = st.checkbox("Retorno agendado")

                submitted = st.form_submit_button("📤 Confirmar Alta", type="primary")

                if submitted:
                    if all([check1, check2, check3, check4, check5, check6]):
                        st.success(f"✅ Alta hospitalar registrada com sucesso!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Complete todos os itens do checklist antes de confirmar a alta.")
