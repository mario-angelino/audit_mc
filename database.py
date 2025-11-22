"""
database.py -> módulo responsável pela conexão com o banco de dados PostgreSQL

Funções disponíveis:
- conectar()
- desconectar()

"""

import psycopg2
from configs import Settings


def conectar():
    """
    Conecta ao banco de dados Supabase (PostgreSQL)
    
    Returns:
        connection: Objeto de conexão do psycopg2
    """
    try:
        conn = psycopg2.connect(
            host=Settings.DB_HOST,
            port=Settings.DB_PORT,
            database=Settings.DB_NAME,
            user=Settings.DB_USER,
            password=Settings.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        raise


def desconectar(conn):
    """
    Fecha a conexão com o banco de dados
    
    Args:
        conn: Objeto de conexão do psycopg2
    """
    if conn:
        conn.close()