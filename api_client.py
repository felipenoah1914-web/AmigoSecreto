import requests


# =========================================================
# CONFIGURAÇÃO
# =========================================================

API_URL = "http://127.0.0.1:8000"

TOKEN = None
USUARIO_ATUAL = None


# =========================================================
# CABEÇALHOS
# =========================================================

def headers():
    if TOKEN:
        return {
            "Authorization": f"Bearer {TOKEN}"
        }

    return {}


# =========================================================
# SESSÃO
# =========================================================

def limpar_sessao():
    global TOKEN
    global USUARIO_ATUAL

    TOKEN = None
    USUARIO_ATUAL = None


# =========================================================
# CADASTRO
# =========================================================

def cadastrar(nome, senha):
    return requests.post(
        f"{API_URL}/cadastro",
        json={
            "nome": nome,
            "senha": senha
        }
    )


# =========================================================
# LOGIN
# =========================================================

def login(nome, senha):

    global TOKEN
    global USUARIO_ATUAL

    resposta = requests.post(
        f"{API_URL}/login",
        json={
            "nome": nome,
            "senha": senha
        }
    )

    if resposta.status_code == 200:

        try:
            dados = resposta.json()

            TOKEN = dados.get("token")
            USUARIO_ATUAL = dados.get("usuario")

        except Exception:
            limpar_sessao()

    else:
        limpar_sessao()

    return resposta


# =========================================================
# USUÁRIOS
# =========================================================

def listar_usuarios():
    return requests.get(
        f"{API_URL}/usuarios",
        headers=headers()
    )


def listar_usuarios_admin():
    return requests.get(
        f"{API_URL}/usuarios/admin",
        headers=headers()
    )


def obter_usuario(usuario_id):
    return requests.get(
        f"{API_URL}/usuarios/{usuario_id}",
        headers=headers()
    )


def definir_participacao(usuario_id, participa):
    return requests.put(
        f"{API_URL}/usuarios/participacao",
        json={
            "usuario_id": usuario_id,
            "participa": participa
        },
        headers=headers()
    )


# =========================================================
# SUGESTÕES
# =========================================================

def adicionar_sugestao(usuario_id, sugestao):
    return requests.post(
        f"{API_URL}/sugestoes",
        json={
            "usuario_id": usuario_id,
            "sugestao": sugestao
        },
        headers=headers()
    )


def listar_sugestoes(usuario_id):
    return requests.get(
        f"{API_URL}/sugestoes/{usuario_id}",
        headers=headers()
    )


def obter_sugestoes_publicas(usuario_id):
    return requests.get(
        f"{API_URL}/usuarios/{usuario_id}/sugestoes",
        headers=headers()
    )


def remover_sugestao(sugestao_id):
    return requests.delete(
        f"{API_URL}/sugestoes/{sugestao_id}",
        headers=headers()
    )


# =========================================================
# SORTEIO
# =========================================================

def sorteio_ja_realizado():

    resposta = requests.get(
        f"{API_URL}/sorteio/status",
        headers=headers()
    )

    if resposta.status_code != 200:
        return False

    return resposta.json().get(
        "realizado",
        False
    )


def obter_amigo(usuario_id):
    return requests.get(
        f"{API_URL}/sorteio/amigo/{usuario_id}",
        headers=headers()
    )


# =========================================================
# DEV
# =========================================================

def realizar_sorteio():
    return requests.post(
        f"{API_URL}/dev/sorteio",
        headers=headers()
    )


def criar_conta_dev(nome, senha):
    return requests.post(
        f"{API_URL}/dev/criar",
        json={
            "nome": nome,
            "senha": senha
        },
        headers=headers()
    )


def resetar_sorteio():
    return requests.post(
        f"{API_URL}/dev/resetar-sorteio",
        headers=headers()
    )


# =========================================================
# TESTE
# =========================================================

def testar_api():

    try:

        return requests.get(
            f"{API_URL}/teste",
            timeout=5
        )

    except requests.RequestException as erro:

        return {
            "sucesso": False,
            "detail": str(erro)
        }