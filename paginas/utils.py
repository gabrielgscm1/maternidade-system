"""
Módulo utilitário para imports compatíveis com Streamlit Cloud
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao path para imports funcionarem
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Agora importa os dados
from dados import get_dados, atualizar_paciente, adicionar_evolucao

__all__ = ['get_dados', 'atualizar_paciente', 'adicionar_evolucao']
