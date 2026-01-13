# Deploy no Streamlit Cloud

Guia passo a passo para publicar o sistema na nuvem.

## Passo 1: Criar Repositorio no GitHub

1. Acesse [github.com](https://github.com) e faca login
2. Clique em **"New repository"** (botao verde)
3. Preencha:
   - **Repository name**: `maternidade-system`
   - **Description**: Sistema de gestao para maternidade
   - **Visibility**: Public
4. **NAO** marque "Add a README file"
5. Clique em **"Create repository"**

## Passo 2: Enviar Codigo para o GitHub

Abra o terminal (Git Bash ou PowerShell) e execute:

```bash
# Navegar para a pasta do projeto
cd c:/Projetos/estudos/maternidade_system

# Inicializar repositorio Git
git init

# Adicionar todos os arquivos
git add .

# Criar primeiro commit
git commit -m "Sistema de Maternidade - versao inicial"

# Definir branch principal
git branch -M main

# Conectar ao GitHub (substitua SEU_USUARIO pelo seu username)
git remote add origin https://github.com/SEU_USUARIO/maternidade-system.git

# Enviar para o GitHub
git push -u origin main
```

## Passo 3: Deploy no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **"Sign in"** e use sua conta GitHub
3. Clique em **"New app"**
4. Configure:
   - **Repository**: `seu-usuario/maternidade-system`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Clique em **"Deploy!"**

## Passo 4: Aguardar Deploy

O Streamlit Cloud ira automaticamente:

1. Clonar seu repositorio
2. Criar ambiente Python
3. Instalar dependencias (requirements.txt)
4. Iniciar a aplicacao

**Tempo estimado**: 2-5 minutos

## Passo 5: Acessar seu App

Apos o deploy, seu app estara disponivel em:

```
https://seu-usuario-maternidade-system.streamlit.app
```

Voce pode compartilhar este link com qualquer pessoa!

---

## Atualizacoes Automaticas

Sempre que voce fizer `git push` para o GitHub, o Streamlit Cloud atualiza automaticamente:

```bash
# Fazer alteracoes no codigo
# ...

# Enviar atualizacoes
git add .
git commit -m "Descricao da alteracao"
git push
```

---

## Solucao de Problemas

### Erro de Import
Se aparecer erro de import, verifique se todos os arquivos estao no repositorio.

### Erro de Dependencias
Verifique se o `requirements.txt` esta correto e inclui todas as bibliotecas.

### App nao atualiza
Va em Settings > Reboot app no painel do Streamlit Cloud.

---

## Configuracoes Avancadas

### Secrets (Variaveis de Ambiente)

Se precisar de senhas ou API keys:

1. No Streamlit Cloud, va em **Settings > Secrets**
2. Adicione no formato TOML:

```toml
[database]
host = "seu-host"
password = "sua-senha"
```

3. No codigo, acesse com:

```python
import streamlit as st
host = st.secrets["database"]["host"]
```

### Dominio Customizado

Voce pode configurar um dominio proprio nas configuracoes do app.

---

## Links Uteis

- [Documentacao Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Docs](https://docs.github.com)
- [Streamlit Forum](https://discuss.streamlit.io)
