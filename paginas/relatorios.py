"""
Página de Relatórios e Exportações
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

from paginas.utils import get_dados


def render():
    st.markdown('<h1 class="main-header">📈 Relatórios e Exportações</h1>', unsafe_allow_html=True)

    dados = get_dados()
    pacientes = dados['pacientes']
    partos = dados['partos']
    recem_nascidos = dados['recem_nascidos']
    evolucoes = dados['evolucoes']
    exames = dados['exames']

    # ========================================================================
    # TABS
    # ========================================================================

    tab_indicadores, tab_producao, tab_qualidade, tab_exportar = st.tabs([
        "📊 Indicadores",
        "🏥 Produção",
        "⭐ Qualidade",
        "📥 Exportar Dados"
    ])

    # ========================================================================
    # TAB: INDICADORES
    # ========================================================================

    with tab_indicadores:
        st.subheader("📊 Indicadores Hospitalares")

        # Filtro de período
        col_periodo1, col_periodo2 = st.columns(2)
        with col_periodo1:
            data_inicio = st.date_input("Data Início", value=datetime.now() - timedelta(days=30), key="ind_inicio")
        with col_periodo2:
            data_fim = st.date_input("Data Fim", value=datetime.now(), key="ind_fim")

        st.markdown("---")

        # KPIs principais
        st.markdown("### 📈 KPIs Principais")

        col1, col2, col3, col4 = st.columns(4)

        # Total de partos
        total_partos = len(partos)
        col1.metric("Total de Partos", total_partos, delta="+15% vs mês anterior")

        # Taxa de cesárea
        cesareas = len(partos[partos['tipo_parto'] == 'Cesárea'])
        taxa_cesarea = (cesareas / total_partos * 100) if total_partos > 0 else 0
        col2.metric("Taxa de Cesárea", f"{taxa_cesarea:.1f}%", delta="-3%", delta_color="inverse")

        # Taxa de ocupação média
        col3.metric("Ocupação Média", "78%", delta="+5%")

        # Tempo médio de internação
        col4.metric("Tempo Médio Internação", "2.5 dias", delta="-0.3 dias", delta_color="inverse")

        st.markdown("---")

        # Gráficos de tendência
        st.markdown("### 📉 Tendências")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("**Partos por Semana**")

            # Simular dados semanais
            semanas = pd.date_range(end=datetime.now(), periods=12, freq='W')
            partos_semana = [15 + i % 5 for i in range(12)]

            fig_tendencia = px.line(
                x=semanas,
                y=partos_semana,
                markers=True,
                color_discrete_sequence=['#E91E63']
            )
            fig_tendencia.update_layout(
                xaxis_title="Semana",
                yaxis_title="Partos",
                margin=dict(t=0, b=0)
            )
            st.plotly_chart(fig_tendencia, use_container_width=True)

        with col_g2:
            st.markdown("**Taxa de Cesárea Mensal**")

            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][:datetime.now().month]
            taxas = [55, 52, 48, 50, 47, 45, 48, 52, 50, 48, 46, 45][:datetime.now().month]

            fig_taxa = px.bar(
                x=meses,
                y=taxas,
                color_discrete_sequence=['#2196F3']
            )
            fig_taxa.add_hline(y=55, line_dash="dash", line_color="red", annotation_text="Meta OMS: 15%")
            fig_taxa.update_layout(
                xaxis_title="Mês",
                yaxis_title="Taxa (%)",
                margin=dict(t=0, b=0)
            )
            st.plotly_chart(fig_taxa, use_container_width=True)

        # Indicadores por médico
        st.markdown("---")
        st.markdown("### 👨‍⚕️ Indicadores por Médico")

        medicos_stats = partos.groupby('obstetra').agg({
            'id': 'count',
            'tipo_parto': lambda x: (x == 'Cesárea').sum()
        }).reset_index()
        medicos_stats.columns = ['Médico', 'Total Partos', 'Cesáreas']
        medicos_stats['Taxa Cesárea'] = (medicos_stats['Cesáreas'] / medicos_stats['Total Partos'] * 100).round(1)
        medicos_stats['Partos Normais'] = medicos_stats['Total Partos'] - medicos_stats['Cesáreas']

        st.dataframe(medicos_stats, use_container_width=True, hide_index=True)

    # ========================================================================
    # TAB: PRODUÇÃO
    # ========================================================================

    with tab_producao:
        st.subheader("🏥 Relatório de Produção")

        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            mes_producao = st.selectbox(
                "Mês",
                options=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
                index=datetime.now().month - 1
            )
        with col_f2:
            ano_producao = st.selectbox("Ano", options=[2024, 2025, 2026], index=2)

        st.markdown("---")

        # Resumo de produção
        st.markdown("### 📋 Resumo de Produção")

        col_p1, col_p2, col_p3 = st.columns(3)

        with col_p1:
            st.markdown("**Partos**")
            st.write(f"• Partos Normais: **{len(partos[partos['tipo_parto'] == 'Normal'])}**")
            st.write(f"• Cesáreas: **{len(partos[partos['tipo_parto'] == 'Cesárea'])}**")
            st.write(f"• Fórceps: **{len(partos[partos['tipo_parto'] == 'Fórceps'])}**")
            st.write(f"• Total: **{len(partos)}**")

        with col_p2:
            st.markdown("**Internações**")
            st.write(f"• Total Internações: **{len(pacientes)}**")
            st.write(f"• Pacientes Atuais: **{len(pacientes[pacientes['status'] != 'Alta'])}**")
            st.write(f"• Altas no Período: **{len(pacientes[pacientes['status'] == 'Alta'])}**")

        with col_p3:
            st.markdown("**Recém-Nascidos**")
            st.write(f"• Total RNs: **{len(recem_nascidos)}**")
            st.write(f"• Masculinos: **{len(recem_nascidos[recem_nascidos['sexo'] == 'Masculino'])}**")
            st.write(f"• Femininos: **{len(recem_nascidos[recem_nascidos['sexo'] == 'Feminino'])}**")
            st.write(f"• Em Aloj. Conjunto: **{len(recem_nascidos[recem_nascidos['alojamento_conjunto']])}**")

        st.markdown("---")

        # Produção por convênio
        st.markdown("### 💳 Produção por Convênio")

        producao_convenio = pacientes.groupby('convenio').size().reset_index(name='Quantidade')

        fig_conv = px.pie(
            producao_convenio,
            values='Quantidade',
            names='convenio',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_conv.update_layout(margin=dict(t=0, b=0))

        col_conv1, col_conv2 = st.columns([2, 1])

        with col_conv1:
            st.plotly_chart(fig_conv, use_container_width=True)

        with col_conv2:
            st.dataframe(producao_convenio, use_container_width=True, hide_index=True)

        # Produção diária
        st.markdown("---")
        st.markdown("### 📅 Produção Diária")

        # Simular dados diários
        dias = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        producao_diaria = pd.DataFrame({
            'Data': dias,
            'Partos': [2 + i % 4 for i in range(len(dias))],
            'Internações': [3 + i % 5 for i in range(len(dias))],
            'Altas': [2 + i % 4 for i in range(len(dias))]
        })

        fig_diario = px.line(
            producao_diaria,
            x='Data',
            y=['Partos', 'Internações', 'Altas'],
            color_discrete_map={'Partos': '#E91E63', 'Internações': '#2196F3', 'Altas': '#4CAF50'}
        )
        fig_diario.update_layout(margin=dict(t=0, b=0))
        st.plotly_chart(fig_diario, use_container_width=True)

    # ========================================================================
    # TAB: QUALIDADE
    # ========================================================================

    with tab_qualidade:
        st.subheader("⭐ Indicadores de Qualidade")

        st.markdown("---")

        # Indicadores de qualidade
        st.markdown("### 📊 Indicadores ANVISA")

        col_q1, col_q2, col_q3, col_q4 = st.columns(4)

        col_q1.metric(
            "Taxa de Infecção Puerperal",
            "0.8%",
            delta="-0.2%",
            delta_color="inverse",
            help="Meta: < 1.5%"
        )

        col_q2.metric(
            "Taxa de Infecção de Sítio Cirúrgico",
            "1.2%",
            delta="+0.1%",
            help="Meta: < 2%"
        )

        col_q3.metric(
            "Taxa de Hemorragia Pós-Parto",
            "2.5%",
            delta="-0.5%",
            delta_color="inverse",
            help="Meta: < 5%"
        )

        col_q4.metric(
            "Taxa de Reinternação",
            "0.5%",
            delta="0%",
            help="Meta: < 2%"
        )

        st.markdown("---")

        # Indicadores obstétricos
        st.markdown("### 🤰 Indicadores Obstétricos")

        col_o1, col_o2 = st.columns(2)

        with col_o1:
            indicadores_obst = {
                'Indicador': [
                    'Taxa de Cesárea',
                    'Taxa de Cesárea em Primíparas',
                    'Taxa de Episiotomia',
                    'Taxa de Indução',
                    'Taxa de Kristeller',
                    'Taxa de Aleitamento na 1ª hora'
                ],
                'Resultado': ['48%', '42%', '15%', '22%', '3%', '85%'],
                'Meta': ['<15%', '<20%', '<10%', '<25%', '0%', '>90%'],
                'Status': ['🔴', '🔴', '🟡', '🟢', '🟢', '🟡']
            }

            df_obst = pd.DataFrame(indicadores_obst)
            st.dataframe(df_obst, use_container_width=True, hide_index=True)

        with col_o2:
            # Gráfico radar de indicadores
            categorias = ['Cesárea', 'Episiotomia', 'Indução', 'Aleitamento', 'Pele-a-pele', 'Parto Humanizado']
            valores = [48, 15, 22, 85, 90, 75]
            metas = [15, 10, 25, 90, 95, 80]

            fig_radar = go.Figure()

            fig_radar.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias,
                fill='toself',
                name='Resultado'
            ))

            fig_radar.add_trace(go.Scatterpolar(
                r=metas,
                theta=categorias,
                fill='toself',
                name='Meta',
                opacity=0.3
            ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                margin=dict(t=30, b=30)
            )

            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        # Indicadores neonatais
        st.markdown("### 👶 Indicadores Neonatais")

        col_n1, col_n2, col_n3, col_n4 = st.columns(4)

        col_n1.metric("Apgar < 7 no 5º min", "2.1%", help="Meta: < 5%")
        col_n2.metric("Peso < 2500g", "8.5%", help="Baixo peso ao nascer")
        col_n3.metric("Prematuridade", "10.2%", help="< 37 semanas")
        col_n4.metric("Internação UTI Neo", "5.3%", help="Meta: < 10%")

        # Distribuição de Apgar
        st.markdown("---")
        st.markdown("**Distribuição de Apgar 5º minuto**")

        apgar_dist = recem_nascidos['apgar_5min'].value_counts().sort_index()

        fig_apgar = px.bar(
            x=apgar_dist.index,
            y=apgar_dist.values,
            color=apgar_dist.index,
            color_continuous_scale='RdYlGn'
        )
        fig_apgar.update_layout(
            xaxis_title="Apgar 5º minuto",
            yaxis_title="Quantidade",
            showlegend=False,
            margin=dict(t=0, b=0)
        )
        st.plotly_chart(fig_apgar, use_container_width=True)

    # ========================================================================
    # TAB: EXPORTAR DADOS
    # ========================================================================

    with tab_exportar:
        st.subheader("📥 Exportar Dados")

        st.markdown("Selecione os dados que deseja exportar:")

        st.markdown("---")

        # Opções de exportação
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            st.markdown("### 📊 Dados Disponíveis")

            exp_pacientes = st.checkbox("Pacientes", value=True)
            exp_partos = st.checkbox("Partos", value=True)
            exp_rn = st.checkbox("Recém-Nascidos", value=True)
            exp_evolucoes = st.checkbox("Evoluções", value=False)
            exp_exames = st.checkbox("Exames", value=False)

        with col_exp2:
            st.markdown("### ⚙️ Opções")

            formato = st.radio("Formato", ['Excel (.xlsx)', 'CSV (.csv)'], horizontal=True)

            periodo_exp = st.date_input(
                "Período",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                key="periodo_export"
            )

            anonimizar = st.checkbox("Anonimizar dados sensíveis (CPF, nome)", value=False)

        st.markdown("---")

        if st.button("📥 Gerar Exportação", type="primary"):
            # Criar arquivo de exportação
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if exp_pacientes:
                    df_pac = pacientes.copy()
                    if anonimizar:
                        df_pac['nome'] = df_pac['nome'].apply(lambda x: x.split()[0] + ' ***')
                        df_pac['cpf'] = '***.***.***-**'
                    df_pac.to_excel(writer, sheet_name='Pacientes', index=False)

                if exp_partos:
                    df_par = partos.copy()
                    if anonimizar:
                        df_par['nome_paciente'] = df_par['nome_paciente'].apply(lambda x: x.split()[0] + ' ***')
                    df_par.to_excel(writer, sheet_name='Partos', index=False)

                if exp_rn:
                    df_rn = recem_nascidos.copy()
                    if anonimizar:
                        df_rn['nome_mae'] = df_rn['nome_mae'].apply(lambda x: x.split()[0] + ' ***')
                    df_rn.to_excel(writer, sheet_name='Recem_Nascidos', index=False)

                if exp_evolucoes:
                    df_ev = evolucoes.copy()
                    if anonimizar:
                        df_ev['nome_paciente'] = df_ev['nome_paciente'].apply(lambda x: x.split()[0] + ' ***')
                    df_ev.to_excel(writer, sheet_name='Evolucoes', index=False)

                if exp_exames:
                    df_ex = exames.copy()
                    if anonimizar:
                        df_ex['nome_paciente'] = df_ex['nome_paciente'].apply(lambda x: x.split()[0] + ' ***')
                    df_ex.to_excel(writer, sheet_name='Exames', index=False)

            output.seek(0)

            st.download_button(
                label="⬇️ Baixar Arquivo Excel",
                data=output,
                file_name=f"relatorio_maternidade_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Arquivo gerado com sucesso!")

        st.markdown("---")

        # Relatórios pré-definidos
        st.markdown("### 📄 Relatórios Pré-definidos")

        col_rel1, col_rel2, col_rel3 = st.columns(3)

        with col_rel1:
            if st.button("📊 Relatório Mensal de Partos"):
                st.info("Gerando relatório mensal de partos...")

        with col_rel2:
            if st.button("📈 Indicadores de Qualidade"):
                st.info("Gerando relatório de indicadores...")

        with col_rel3:
            if st.button("🏥 Censo Hospitalar"):
                st.info("Gerando censo hospitalar...")
