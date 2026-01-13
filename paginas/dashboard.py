"""
Página de Dashboard - Visão geral do sistema
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from paginas.utils import get_dados


def render():
    st.markdown('<h1 class="main-header">📊 Dashboard - Visão Geral</h1>', unsafe_allow_html=True)

    dados = get_dados()
    pacientes = dados['pacientes']
    partos = dados['partos']
    recem_nascidos = dados['recem_nascidos']
    leitos = dados['leitos']

    # ========================================================================
    # MÉTRICAS PRINCIPAIS
    # ========================================================================

    st.subheader("📈 Indicadores Principais")

    col1, col2, col3, col4, col5 = st.columns(5)

    # Total de pacientes internadas
    internadas = len(pacientes[pacientes['status'].isin(['Internada', 'Em trabalho de parto', 'Pós-parto'])])
    col1.metric(
        "Internadas",
        internadas,
        delta=f"+{internadas - 45}" if internadas > 45 else f"{internadas - 45}",
        delta_color="normal"
    )

    # Partos do mês
    partos_mes = len(partos[partos['data_parto'] >= (datetime.now() - timedelta(days=30)).date()])
    col2.metric("Partos (30 dias)", partos_mes, delta="+12%")

    # Taxa de cesárea
    cesarias = len(partos[partos['tipo_parto'] == 'Cesárea'])
    taxa_cesarea = (cesarias / len(partos) * 100) if len(partos) > 0 else 0
    col3.metric("Taxa Cesárea", f"{taxa_cesarea:.1f}%", delta="-2%", delta_color="inverse")

    # Leitos ocupados
    leitos_ocupados = len(pacientes[pacientes['leito'].notna()])
    total_leitos = len(leitos)
    col4.metric("Ocupação Leitos", f"{leitos_ocupados}/{total_leitos}", delta=f"{(leitos_ocupados/total_leitos*100):.0f}%")

    # RNs no alojamento conjunto
    rns_ac = len(recem_nascidos[recem_nascidos['alojamento_conjunto'] == True])
    col5.metric("RNs no AC", rns_ac)

    st.markdown("---")

    # ========================================================================
    # GRÁFICOS
    # ========================================================================

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("👶 Tipos de Parto (Últimos 30 dias)")

        if len(partos) > 0:
            tipos_parto = partos['tipo_parto'].value_counts()
            fig_parto = px.pie(
                values=tipos_parto.values,
                names=tipos_parto.index,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            fig_parto.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig_parto, use_container_width=True)
        else:
            st.info("Nenhum parto registrado no período.")

    with col_right:
        st.subheader("🏥 Ocupação por Setor")

        ocupacao_setor = []
        for setor in ['Pré-parto', 'Centro Obstétrico', 'Alojamento Conjunto', 'UTI Neonatal', 'UTI Materna']:
            leitos_setor = [l['id'] for l in leitos.to_dict('records') if l['setor'] == setor]
            ocupados = len(pacientes[pacientes['leito'].isin(leitos_setor)])
            total = len(leitos_setor)
            ocupacao_setor.append({
                'setor': setor,
                'ocupados': ocupados,
                'livres': total - ocupados,
                'total': total
            })

        df_ocupacao = pd.DataFrame(ocupacao_setor)

        fig_ocupacao = go.Figure()
        fig_ocupacao.add_trace(go.Bar(
            name='Ocupados',
            x=df_ocupacao['setor'],
            y=df_ocupacao['ocupados'],
            marker_color='#E91E63'
        ))
        fig_ocupacao.add_trace(go.Bar(
            name='Livres',
            x=df_ocupacao['setor'],
            y=df_ocupacao['livres'],
            marker_color='#4CAF50'
        ))
        fig_ocupacao.update_layout(
            barmode='stack',
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_ocupacao, use_container_width=True)

    st.markdown("---")

    # ========================================================================
    # ALERTAS E ATENÇÃO
    # ========================================================================

    col_alertas, col_lista = st.columns([1, 2])

    with col_alertas:
        st.subheader("⚠️ Alertas")

        # Pacientes em trabalho de parto
        em_tp = pacientes[pacientes['status'] == 'Em trabalho de parto']
        if len(em_tp) > 0:
            st.error(f"🚨 **{len(em_tp)} paciente(s) em trabalho de parto ativo**")
            for _, p in em_tp.iterrows():
                st.write(f"• {p['nome']} - Leito {p['leito']}")

        # Pacientes de alto risco (com comorbidades)
        alto_risco = pacientes[~pacientes['comorbidades'].isin(['Nenhuma'])]
        if len(alto_risco) > 0:
            st.warning(f"⚠️ **{len(alto_risco)} paciente(s) de alto risco**")

        # Gestações pós-termo
        pos_termo = pacientes[pacientes['semanas_gestacao'] > 41]
        if len(pos_termo) > 0:
            st.warning(f"📅 **{len(pos_termo)} gestação(ões) pós-termo (>41 sem)**")

    with col_lista:
        st.subheader("📋 Últimas Internações")

        internacoes_recentes = pacientes[pacientes['data_internacao'].notna()].sort_values(
            'data_internacao', ascending=False
        ).head(5)

        if len(internacoes_recentes) > 0:
            for _, p in internacoes_recentes.iterrows():
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                    c1.write(f"**{p['nome']}**")
                    c2.write(f"📅 {p['data_internacao']}")
                    c3.write(f"🛏️ {p['leito']}")

                    status_color = {
                        'Internada': '🟢',
                        'Em trabalho de parto': '🟠',
                        'Pós-parto': '🔵',
                        'Alta': '⚪',
                        'UTI': '🔴'
                    }
                    c4.write(f"{status_color.get(p['status'], '⚪')} {p['status']}")
        else:
            st.info("Nenhuma internação recente.")

    st.markdown("---")

    # ========================================================================
    # ESTATÍSTICAS DO MÊS
    # ========================================================================

    st.subheader("📊 Estatísticas do Mês")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**👶 Nascimentos por Sexo**")
        if len(recem_nascidos) > 0:
            sexo_counts = recem_nascidos['sexo'].value_counts()
            fig_sexo = px.pie(
                values=sexo_counts.values,
                names=sexo_counts.index,
                color_discrete_map={'Masculino': '#2196F3', 'Feminino': '#E91E63'}
            )
            fig_sexo.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
            st.plotly_chart(fig_sexo, use_container_width=True)

    with col2:
        st.markdown("**💳 Convênios**")
        convenio_counts = pacientes['convenio'].value_counts()
        fig_conv = px.bar(
            x=convenio_counts.index,
            y=convenio_counts.values,
            color=convenio_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_conv.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_conv, use_container_width=True)

    with col3:
        st.markdown("**📈 Indicadores de Qualidade**")
        indicadores = {
            'Taxa de Aleitamento': 92,
            'Satisfação': 88,
            'Tempo Médio Internação': 75,
            'Taxa de Infecção': 95,
        }
        for nome, valor in indicadores.items():
            st.progress(valor / 100, text=f"{nome}: {valor}%")
