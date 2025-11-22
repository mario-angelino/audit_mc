from supabase import create_client, Client
from configs import Settings


def get_supabase_client() -> Client:
    """
    Retorna instância do cliente Supabase para autenticação
    """
    return create_client(Settings.SUPABASE_URL, Settings.SUPABASE_ANON_KEY)


# Instância global
supabase: Client = get_supabase_client()
