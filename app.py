"""
Sistema de Gestão para Maternidade
Desenvolvido com Streamlit

Módulos:
- Dashboard: Visão geral e indicadores
- Pacientes: Cadastro e gestão de gestantes
- Prontuário: Histórico médico e evoluções
- Partos: Registro de nascimentos
- Internações: Gestão de leitos
- Relatórios: Exportação de dados
"""

import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sistema Maternidade",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    /* Estilo geral */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #E91E63;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }

    /* Cards de métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }

    /* Status badges */
    .status-internada { background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 15px; }
    .status-trabalho { background-color: #FF9800; color: white; padding: 3px 10px; border-radius: 15px; }
    .status-alta { background-color: #2196F3; color: white; padding: 3px 10px; border-radius: 15px; }

    /* Sidebar */
    .css-1d391kg { background-color: #FCE4EC; }

    /* Tabelas */
    .dataframe { font-size: 0.9rem; }

    /* Alertas customizados */
    .alert-urgente {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
        padding: 1rem;
        margin: 1rem 0;
    }

    .alert-atencao {
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Importar módulos de páginas
from paginas import dashboard, pacientes, prontuario, partos, internacoes, relatorios

# ============================================================================
# SIDEBAR - NAVEGAÇÃO
# ============================================================================

st.sidebar.markdown("## 🏥 Maternidade")
st.sidebar.markdown("---")

# Menu de navegação
pagina = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard",
        "👩 Pacientes",
        "📋 Prontuário",
        "👶 Partos",
        "🛏️ Internações",
        "📈 Relatórios"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Informações do usuário logado (simulado)
st.sidebar.markdown("### 👤 Usuário")
st.sidebar.info("""
**Dr. Carlos Alberto Silva**
CRM: 12345-SP
Obstetrícia
""")

st.sidebar.markdown("---")

# Data e hora atual
from datetime import datetime
st.sidebar.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
st.sidebar.markdown(f"🕐 {datetime.now().strftime('%H:%M')}")

# ============================================================================
# CONTEÚDO PRINCIPAL - ROTEAMENTO
# ============================================================================

if pagina == "📊 Dashboard":
    dashboard.render()

elif pagina == "👩 Pacientes":
    pacientes.render()

elif pagina == "📋 Prontuário":
    prontuario.render()

elif pagina == "👶 Partos":
    partos.render()

elif pagina == "🛏️ Internações":
    internacoes.render()

elif pagina == "📈 Relatórios":
    relatorios.render()

# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small>Sistema Maternidade v1.0<br>© 2026 - Todos os direitos reservados</small>",
    unsafe_allow_html=True
)
