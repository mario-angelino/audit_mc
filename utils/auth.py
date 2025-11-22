import streamlit as st
from utils.supabase_client import supabase


def login(email: str, password: str) -> dict:
    """
    Realiza login do usuário

    Args:
        email: Email do usuário
        password: Senha do usuário

    Returns:
        dict com 'success' (bool) e 'message' (str)
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user:
            # Armazena dados do usuário na sessão
            st.session_state.authenticated = True
            st.session_state.user = {
                "id": response.user.id,
                "email": response.user.email,
                "nome": response.user.user_metadata.get("nome_completo", email.split("@")[0])
            }
            return {"success": True, "message": "Login realizado com sucesso!"}
        else:
            return {"success": False, "message": "Erro ao realizar login."}

    except Exception as e:
        error_msg = str(e).lower()

        # Tratamento de erros comuns
        if "invalid login credentials" in error_msg or "invalid" in error_msg:
            return {"success": False, "message": "Email ou senha incorretos."}
        elif "email not confirmed" in error_msg:
            return {"success": False, "message": "Email não confirmado. Verifique sua caixa de entrada."}
        elif "user not found" in error_msg:
            return {"success": False, "message": "Usuário não encontrado."}
        else:
            return {"success": False, "message": f"Erro de autenticação: {str(e)}"}


def logout():
    """
    Realiza logout do usuário
    """
    try:
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao fazer logout: {str(e)}")


def check_authentication():
    """
    Verifica se o usuário está autenticado

    Returns:
        bool: True se autenticado, False caso contrário
    """
    return st.session_state.get("authenticated", False)


def get_current_user():
    """
    Retorna dados do usuário atual

    Returns:
        dict com dados do usuário ou None
    """
    return st.session_state.get("user", None)


def require_authentication():
    """
    Decorator/função para proteger páginas que requerem autenticação
    Redireciona para a página de login se não autenticado
    """
    if not check_authentication():
        st.warning("⚠️ Você precisa estar autenticado para acessar esta página.")
        st.info("👉 Retorne à página principal para fazer login.")
        st.stop()
