"""
from supabase import create_client, Client
from configs import Settings

def get_supabase_client() -> Client:
    
    #Retorna instância do cliente Supabase para autenticação
    
    return create_client(Settings.SUPABASE_URL, Settings.SUPABASE_ANON_KEY)


# Instância global
supabase: Client = get_supabase_client()
"""

import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """
    Retorna instância do cliente Supabase utilizando credenciais
    seguras armazenadas no .streamlit/secrets.toml
    """
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]  # Pode ser ANON ou SERVICE KEY

    return create_client(supabase_url, supabase_key)


# Instância global
supabase: Client = get_supabase_client()
