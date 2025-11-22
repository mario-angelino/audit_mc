import streamlit as st
from utils.auth import require_authentication, get_current_user
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Balancetes - Audit MC",
    page_icon="📈",
    layout="wide"
)

# Verificar autenticação
require_authentication()

# Obter usuário atual
user = get_current_user()

# Header
st.title("📈 Gestão de Balancetes")
st.markdown(f"**Usuário:** {user['nome']}")
st.markdown("---")

# Abas
tab1, tab2, tab3 = st.tabs(
    ["📊 Balancetes Processados", "📤 Upload de Balancetes", "📋 Histórico"])

# Tab 1: Processados
with tab1:
    st.subheader("📊 Balancetes Processados")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_empresa = st.selectbox(
            "Empresa",
            ["Todas", "Empresa A", "Empresa B", "Empresa C"]
        )

    with col2:
        filtro_mes = st.selectbox(
            "Mês",
            ["Todos", "Jan/2025", "Dez/2024", "Nov/2024"]
        )

    with col3:
        filtro_status = st.selectbox(
            "Status",
            ["Todos", "✅ Aprovado", "⚠️ Pendente", "❌ Reprovado"]
        )

    st.markdown("---")

    # Tabela de balancetes
    df_balancetes = pd.DataFrame({
        "Data Upload": ["2025-01-22", "2025-01-21", "2025-01-20"],
        "Empresa": ["Empresa A", "Empresa B", "Empresa C"],
        "Mês Ref.": ["Jan/2025", "Dez/2024", "Jan/2025"],
        "Tipo": ["Analítico", "Sintético", "Analítico"],
        "Status": ["✅ Aprovado", "⚠️ Pendente", "✅ Aprovado"],
        "Usuário": ["admin@empresa.com", "admin@empresa.com", "admin@empresa.com"]
    })

    st.dataframe(df_balancetes, use_container_width=True, hide_index=True)

    # Botões de ação
    col1, col2 = st.columns([1, 5])
    with col1:
        st.button("📥 Exportar", use_container_width=True)

# Tab 2: Upload
with tab2:
    st.subheader("📤 Upload de Balancetes")

    # Buscar empresas do banco
    with st.spinner("Carregando empresas..."):
        from utils.empresa_db import listar_empresas
        df_empresas = listar_empresas()

    if df_empresas.empty:
        st.warning("⚠️ Nenhuma empresa cadastrada. Cadastre empresas primeiro.")
    else:
        # Extrair apenas razões sociais
        empresas_lista = df_empresas["Razão Social"].tolist()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            empresa = st.selectbox(
                "Selecione a Empresa *",
                empresas_lista
            )

        with col2:
            ano_ref = st.selectbox(
                "Ano de Referência *",
                ["2025", "2024", "2023", "2022"]
            )

        with col3:
            mes_ref = st.selectbox(
                "Mês de Referência *",
                ["01", "02", "03", "04", "05", "06",
                 "07", "08", "09", "10", "11", "12"]
            )

        with col4:
            formato = st.selectbox(
                "Formato do Arquivo *",
                ["CSV (.csv)", "Excel (.xlsx)", "PDF (.pdf)"]
            )

        st.markdown("---")

        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Selecione o arquivo do balancete",
            type=["xlsx", "xls", "csv", "txt", "pdf"],
            help="Formatos aceitos: Excel, CSV, TXT, PDF"
        )

        if uploaded_file:
            st.success(
                f"✅ Arquivo **{uploaded_file.name}** carregado com sucesso!")

            # Mostrar informações selecionadas
            st.info(
                f"📊 **Empresa:** {empresa} | **Período:** {mes_ref}/{ano_ref}")

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("🚀 Processar", use_container_width=True, type="primary"):
                    with st.spinner("Processando balancete..."):
                        import time
                        time.sleep(2)
                        st.success("✅ Balancete processado com sucesso!")
                        st.balloons()


# Tab 3: Histórico
with tab3:
    st.subheader("📋 Histórico Completo")

    # Filtro de data
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", datetime(2025, 1, 1))
    with col2:
        data_fim = st.date_input("Data Fim", datetime.now())

    st.markdown("---")

    # Timeline de atividades
    st.markdown("### 📅 Timeline de Atividades")

    activities = [
        {"data": "22/01/2025 14:30", "acao": "Upload de balancete",
            "empresa": "Empresa A", "usuario": "admin@empresa.com"},
        {"data": "21/01/2025 10:15", "acao": "Aprovação de balancete",
            "empresa": "Empresa B", "usuario": "admin@empresa.com"},
        {"data": "20/01/2025 16:45", "acao": "Upload de balancete",
            "empresa": "Empresa C", "usuario": "admin@empresa.com"}
    ]

    for act in activities:
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"**{act['data']}**")
            with col2:
                st.markdown(
                    f"**{act['acao']}** - {act['empresa']} _(por {act['usuario']})_")
            st.markdown("---")
