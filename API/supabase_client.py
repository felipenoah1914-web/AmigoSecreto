import os

from dotenv import load_dotenv
from supabase import create_client, Client


# Carrega o arquivo .env
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")


# Verifica se as configurações existem
if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL não foi configurada no .env")

if not SUPABASE_SECRET_KEY:
    raise RuntimeError("SUPABASE_SECRET_KEY não foi configurada no .env")


# Cria a conexão com o Supabase
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)


print("Conexão com o Supabase configurada!")