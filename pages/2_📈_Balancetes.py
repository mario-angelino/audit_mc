import streamlit as st
from utils.auth import require_authentication, get_current_user
from utils.balancete_processor import processar_balancete
from utils.empresa_db import listar_empresas
from utils.balancete_db import importar_balancete_completo
from utils.balancete_db import listar_balancetes

import pandas as pd
from datetime import datetime
import sys

import warnings
warnings.filterwarnings('ignore')

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

    # Buscar empresas e anos únicos para os filtros
    with st.spinner("Carregando dados..."):

        # Buscar todas as empresas para o filtro
        df_empresas = listar_empresas()
        empresas_lista = [
            "Todas"] + sorted(df_empresas["Razão Social"].tolist()) if not df_empresas.empty else ["Todas"]

        # Buscar todos os balancetes para extrair anos únicos
        df_todos = listar_balancetes()
        anos_unicos = ["Todos"] + sorted(df_todos["Ano"].unique(
        ).tolist(), reverse=True) if not df_todos.empty else ["Todos"]

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_empresa = st.selectbox(
            "Empresa",
            empresas_lista
        )

    with col2:
        filtro_ano = st.selectbox(
            "Ano",
            anos_unicos
        )

    with col3:
        filtro_mes = st.selectbox(
            "Mês",
            ["Todos", "01", "02", "03", "04", "05",
                "06", "07", "08", "09", "10", "11", "12"]
        )

    st.markdown("---")

    # Buscar balancetes com filtros aplicados
    df_balancetes = listar_balancetes(
        empresa=filtro_empresa,
        ano=filtro_ano,
        mes=filtro_mes
    )

    if df_balancetes.empty:
        st.warning("⚠️ Nenhum balancete encontrado com os filtros selecionados.")
    else:
        # Formatar data de importação
        df_balancetes["Data Importação"] = pd.to_datetime(
            df_balancetes["Data Importação"]
        ).dt.strftime("%d/%m/%Y %H:%M")

        # Formatar mês com zero à esquerda
        df_balancetes["Mês"] = df_balancetes["Mês"].apply(
            lambda x: str(x).zfill(2))

        # Exibir tabela
        st.dataframe(df_balancetes, width="stretch", hide_index=True)

        # Botões de ação
        col1, col2 = st.columns([1, 5])
        with col1:
            st.button("📥 Exportar", width="stretch")

# Tab 2: Upload
with tab2:
    st.subheader("📤 Upload de Balancetes")

    # Inicializar session_state para armazenar dados processados
    if 'df_processado' not in st.session_state:
        st.session_state.df_processado = None
        st.session_state.empresa_selecionada = None
        st.session_state.mes_selecionado = None
        st.session_state.ano_selecionado = None
        st.session_state.arquivo_processado = None
        # ← NOVO: contador para resetar file_uploader
        st.session_state.file_uploader_key = 0

    # Buscar empresas do banco
    with st.spinner("Carregando empresas..."):
        df_empresas = listar_empresas()

    if df_empresas.empty:
        st.warning("⚠️ Nenhuma empresa cadastrada. Cadastre empresas primeiro.")
    else:
        # Extrair apenas razões sociais
        empresas_lista = df_empresas["Razão Social"].tolist()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            empresa = st.selectbox("Selecione a Empresa *", empresas_lista)

        with col2:
            ano_ref = st.selectbox("Ano de Referência *",
                                   ["2025", "2024", "2023", "2022"])

        with col3:
            mes_ref = st.selectbox(
                "Mês de Referência *", ["01", "02", "03", "04",
                                        "05", "06", "07", "08", "09", "10", "11", "12"])

        with col4:
            formato = st.selectbox(
                "Formato do Arquivo *", ["CSV (.csv)", "Excel (.xlsx)", "PDF (.pdf)"])

        st.markdown("---")

        # st.write(
        #    f"🔑 DEBUG — key atual do uploader: file_uploader_{st.session_state.file_uploader_key}")
        # st.write(
        #    f"🧮 DEBUG — session_state keys: {list(st.session_state.keys())}")
        # st.write(f"🧮 DEBUG — session_state: {list(st.session_state.values())}")

        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Selecione o arquivo do balancete",
            type=["xlsx", "xls", "csv", "txt", "pdf"],
            help="Formatos aceitos: Excel, CSV, TXT, PDF",
            # ← NOVO: key dinâmica
            key=f"file_uploader_{st.session_state.file_uploader_key}"
        )

        # if uploaded_file is not None:
        #    st.write(f"🧮 DEBUG — uploaded_file: {uploaded_file.__dict__}")

        # CRÍTICO: Limpar dados processados se contexto mudou
        # Comparar SOMENTE empresa/mês/ano (não arquivo, pois ele vira None no reload do botão)
        if st.session_state.df_processado is not None:
            contexto_mudou = (
                st.session_state.empresa_selecionada != empresa or
                st.session_state.mes_selecionado != int(mes_ref) or
                st.session_state.ano_selecionado != int(ano_ref)
            )

            if contexto_mudou:
                st.session_state.df_processado = None
                st.session_state.empresa_selecionada = None
                st.session_state.mes_selecionado = None
                st.session_state.ano_selecionado = None
                st.session_state.arquivo_processado = None

        # NOVO: Limpar se não há arquivo uploaded mas há dados processados
        # Isso acontece quando usuário entra na página pela primeira vez
        # ou quando navega entre páginas/abas
        if uploaded_file is None and st.session_state.df_processado is not None:
            st.session_state.df_processado = None
            st.session_state.empresa_selecionada = None
            st.session_state.mes_selecionado = None
            st.session_state.ano_selecionado = None
            st.session_state.arquivo_processado = None

        if uploaded_file:
            st.success(
                f"✅ Arquivo **{uploaded_file.name}** carregado com sucesso!")

            # Mostrar informações selecionadas
            st.info(
                f"📊 **Empresa:** {empresa} | **Período:** {mes_ref}/{ano_ref}")

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("🚀 Processar", width="stretch", type="primary", key="processar_balancete"):
                    print(f"🔍 [BOTÃO PROCESSAR CLICADO]")
                    with st.spinner("Processando balancete..."):

                        # Processar arquivo (validar, limpar, converter)
                        sucesso, mensagem, df_processado = processar_balancete(
                            uploaded_file)

                        if not sucesso:
                            st.error(mensagem)
                            st.session_state.df_processado = None
                        else:
                            st.success(mensagem)
                            # Armazenar dados processados no session_state
                            st.session_state.df_processado = df_processado
                            st.session_state.empresa_selecionada = empresa
                            st.session_state.mes_selecionado = int(mes_ref)
                            st.session_state.ano_selecionado = int(ano_ref)
                            st.session_state.arquivo_processado = uploaded_file.name

                            # st.write(
                            #    f"🧮 DEBUG — session_state keys: {list(st.session_state.keys())}")
                            # st.write(
                            #    f"🧮 DEBUG — session_state: {list(st.session_state.values())}")

        # CRÍTICO: Mostrar dados processados FORA do if uploaded_file
        # Isso permite que o botão seja renderizado mesmo quando uploaded_file = None
        if st.session_state.df_processado is not None:
            st.markdown("---")
            st.subheader("📊 Dados Processados - Prévia")

            st.dataframe(
                st.session_state.df_processado,
                width="stretch",
                hide_index=True
            )

            st.info(
                f"📈 **Total de registros:** {len(st.session_state.df_processado)}")

            st.markdown("---")

            # Botão para gravar no banco
            col1, col2 = st.columns([1, 5])
            with col1:
                botao_gravar_clicado = st.button(
                    "💾 Gravar Dados", width="stretch", type="primary", key="gravar_balancete")

            # FORA das colunas - ocupa largura total
            if botao_gravar_clicado:
                print(f"🔍 ===== BOTÃO GRAVAR CLICADO =====")

                with st.spinner("Gravando no banco de dados..."):

                    # Obter email do usuário logado
                    user = get_current_user()
                    user_email = user.get(
                        'email', 'sem_email@unknown.com') if user else 'sem_email@unknown.com'

                    print(f"🔍 Gravando para: {user_email}")

                    try:
                        sucesso_import, msg_import = importar_balancete_completo(
                            razao_social=st.session_state.empresa_selecionada,
                            mes=st.session_state.mes_selecionado,
                            ano=st.session_state.ano_selecionado,
                            df_itens=st.session_state.df_processado,
                            user_email=user_email
                        )

                        print(f"🔍 Resultado: sucesso={sucesso_import}")

                        if sucesso_import:
                            # Layout profissional de sucesso
                            st.markdown("---")

                            # Card de sucesso customizado
                            st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    padding: 30px;
                                    border-radius: 12px;
                                    text-align: center;
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                    margin: 20px 0;
                                ">
                                    <h1 style="color: white; margin: 0 0 10px 0; font-size: 48px;">
                                        ✅
                                    </h1>
                                    <h2 style="color: white; margin: 0 0 20px 0;">
                                        Importação Concluída com Sucesso!
                                    </h2>
                                    <p style="color: #f0f0f0; font-size: 18px; margin: 0;">
                                        {msg_import}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)

                            # Informações adicionais
                            col_info1, col_info2, col_info3 = st.columns(3)

                            with col_info1:
                                st.markdown(f"""
                                    <div style="
                                        background-color: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 8px;
                                        text-align: center;
                                        border: 1px solid #dee2e6;
                                    ">
                                        <p style="color: #6c757d; margin: 0; font-size: 14px;">EMPRESA</p>
                                        <p style="color: #212529; margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                                            {st.session_state.empresa_selecionada}
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)

                            with col_info2:
                                st.markdown(f"""
                                    <div style="
                                        background-color: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 8px;
                                        text-align: center;
                                        border: 1px solid #dee2e6;
                                    ">
                                        <p style="color: #6c757d; margin: 0; font-size: 14px;">PERÍODO</p>
                                        <p style="color: #212529; margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                                            {str(st.session_state.mes_selecionado).zfill(2)}/{st.session_state.ano_selecionado}
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)

                            with col_info3:
                                st.markdown(f"""
                                    <div style="
                                        background-color: #f8f9fa;
                                        padding: 20px;
                                        border-radius: 8px;
                                        text-align: center;
                                        border: 1px solid #dee2e6;
                                    ">
                                        <p style="color: #6c757d; margin: 0; font-size: 14px;">IMPORTADO POR</p>
                                        <p style="color: #212529; margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                                            👤 {user_email}
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)

                            st.balloons()

                            st.markdown("<br>", unsafe_allow_html=True)

                            # st.write(
                            #    "DEBUG — AQUI DEVERIA RENDERIZAR O BOTÃO DE NOVA IMPORTAÇÃO")

                            # Botão "Nova Importação" grande e centralizado
                            col_btn1, col_btn2, col_btn3 = st.columns(
                                [1, 1, 1])
                            with col_btn2:

                                botao_nova_importacao = st.button(
                                    "🔄 Nova Importação", width="stretch", type="primary", key="nova_importacao")

                                if botao_nova_importacao:
                                    print("\n\n===== DEBUG RESET START =====")
                                    print("Antes de resetar:")
                                    print("file_uploader_key =",
                                          st.session_state.file_uploader_key)
                                    print("session_state keys =", list(
                                        st.session_state.keys()))

                                    key_atual = f"file_uploader_{st.session_state.file_uploader_key}"
                                    print("key_atual =", key_atual)
                                    print("key existe?",
                                          key_atual in st.session_state)

                                    # Zera estados internos da aplicação
                                    st.session_state.df_processado = None
                                    st.session_state.empresa_selecionada = None
                                    st.session_state.mes_selecionado = None
                                    st.session_state.ano_selecionado = None
                                    st.session_state.arquivo_processado = None

                                    # ====== RESET REAL DO FILE UPLOADER ======
                                    # 1. Remove estado interno do uploader
                                    key_atual = f"file_uploader_{st.session_state.file_uploader_key}"
                                    if key_atual in st.session_state:
                                        del st.session_state[key_atual]

                                    # 2. Gera nova key para recriar o widget
                                    st.session_state.file_uploader_key += 1

                                    print("\nDepois de resetar:")
                                    print("file_uploader_key =",
                                          st.session_state.file_uploader_key)
                                    print("session_state keys =", list(
                                        st.session_state.keys()))
                                    print("===== DEBUG RESET END =====\n\n")

                                    # 3. Recarrega página
                                    # sys.stdout.flush()
                                    # st.rerun()

                            # st.write(
                            #    "DEBUG — SAIU DO IF DO BOTÃO DE NOVA IMPORTAÇÃO")

                        else:
                            st.error(msg_import)
                    except Exception as e:
                        print(f"❌ EXCEÇÃO: {e}")
                        import traceback
                        traceback.print_exc()
                        st.error(f"❌ Erro: {str(e)}")

                if uploaded_file is not None and st.session_state.df_processado is not None:
                    st.session_state.df_processado = None
                    st.session_state.empresa_selecionada = None
                    st.session_state.mes_selecionado = None
                    st.session_state.ano_selecionado = None
                    st.session_state.arquivo_processado = None

                    key_atual = f"file_uploader_{st.session_state.file_uploader_key}"
                    if key_atual in st.session_state:
                        del st.session_state[key_atual]

                    # 2. Gera nova key para recriar o widget
                    st.session_state.file_uploader_key += 1


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
