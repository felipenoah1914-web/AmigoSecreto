import os
import random
from datetime import datetime, timedelta, timezone

import jwt

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pwdlib import PasswordHash

from API.supabase_client import supabase


# =========================================================
# API
# =========================================================

app = FastAPI(
    title="Amigo Secreto API",
    description="API do Amigo Secreto da Família",
    version="1.0.0"
)


# =========================================================
# SENHAS
# =========================================================

password_hash = PasswordHash.recommended()


# =========================================================
# JWT
# =========================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY não foi configurada no arquivo .env"
    )

JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer(auto_error=False)


# =========================================================
# MODELOS
# =========================================================

class CadastroRequest(BaseModel):
    nome: str
    senha: str


class LoginRequest(BaseModel):
    nome: str
    senha: str


class SugestaoRequest(BaseModel):
    usuario_id: int
    sugestao: str


class ParticipacaoRequest(BaseModel):
    usuario_id: int
    participa: bool


# =========================================================
# JWT - CRIAR TOKEN
# =========================================================

def criar_token(usuario):
    agora = datetime.now(timezone.utc)

    payload = {
        "sub": str(usuario["id"]),
        "nome": usuario["nome"],
        "tipo": usuario["tipo"],
        "iat": agora,
        "exp": agora + timedelta(days=TOKEN_EXPIRE_DAYS)
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


# =========================================================
# JWT - USUÁRIO ATUAL
# =========================================================

def obter_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Você precisa estar logado."
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Sua sessão expirou. Faça login novamente."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )

    return payload


# =========================================================
# SOMENTE DEV
# =========================================================

def exigir_dev(usuario=Depends(obter_usuario_atual)):
    if usuario.get("tipo") != "dev":
        raise HTTPException(
            status_code=403,
            detail="Acesso permitido somente ao Dev."
        )

    return usuario


# =========================================================
# ROTAS BÁSICAS
# =========================================================

@app.get("/")
def inicio():
    return {
        "status": "online",
        "mensagem": "API do Amigo Secreto funcionando!"
    }


@app.get("/teste")
def teste():
    return {
        "sucesso": True,
        "mensagem": "Conexão com a API funcionando!"
    }


# =========================================================
# CADASTRO
# =========================================================

@app.post("/cadastro")
def cadastrar_usuario(dados: CadastroRequest):

    nome = dados.nome.strip()
    senha = dados.senha

    if not nome:
        raise HTTPException(
            status_code=400,
            detail="O nome não pode estar vazio."
        )

    if not senha:
        raise HTTPException(
            status_code=400,
            detail="A senha não pode estar vazia."
        )

    existente = (
        supabase
        .table("usuarios")
        .select("id")
        .eq("nome", nome)
        .limit(1)
        .execute()
    )

    if existente.data:
        raise HTTPException(
            status_code=409,
            detail="Esse nome de usuário já existe."
        )

    senha_hash = password_hash.hash(senha)

    novo_usuario = (
        supabase
        .table("usuarios")
        .insert({
            "nome": nome,
            "senha_hash": senha_hash,
            "participa": True,
            "tipo": "usuario"
        })
        .execute()
    )

    if not novo_usuario.data:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível cadastrar o usuário."
        )

    usuario = novo_usuario.data[0]

    return {
        "sucesso": True,
        "mensagem": "Usuário cadastrado com sucesso!",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"]
        }
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def fazer_login(dados: LoginRequest):

    nome = dados.nome.strip()
    senha = dados.senha

    if not nome or not senha:
        raise HTTPException(
            status_code=400,
            detail="Nome e senha são obrigatórios."
        )

    resposta = (
        supabase
        .table("usuarios")
        .select(
            "id, nome, senha_hash, participa, tipo"
        )
        .eq("nome", nome)
        .limit(1)
        .execute()
    )

    if not resposta.data:
        raise HTTPException(
            status_code=401,
            detail="Nome ou senha incorretos."
        )

    usuario = resposta.data[0]

    if not password_hash.verify(
        senha,
        usuario["senha_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Nome ou senha incorretos."
        )

    token = criar_token(usuario)

    return {
        "sucesso": True,
        "mensagem": "Login realizado com sucesso!",
        "token": token,
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "participa": usuario["participa"],
            "tipo": usuario["tipo"]
        }
    }


# =========================================================
# USUÁRIOS
# =========================================================

@app.get("/usuarios")
def listar_usuarios(
    usuario_atual=Depends(obter_usuario_atual)
):

    resposta = (
        supabase
        .table("usuarios")
        .select("id, nome, participa, tipo")
        .order("nome")
        .execute()
    )

    return resposta.data


@app.get("/usuarios/admin")
def listar_usuarios_admin(
    usuario_atual=Depends(exigir_dev)
):

    resposta = (
        supabase
        .table("usuarios")
        .select("id, nome, participa, tipo")
        .eq("tipo", "usuario")
        .order("nome")
        .execute()
    )

    return resposta.data


@app.get("/usuarios/{usuario_id}")
def obter_usuario(
    usuario_id: int,
    usuario_atual=Depends(obter_usuario_atual)
):

    resposta = (
        supabase
        .table("usuarios")
        .select("id, nome, participa, tipo")
        .eq("id", usuario_id)
        .limit(1)
        .execute()
    )

    if not resposta.data:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return resposta.data[0]


# =========================================================
# PARTICIPAÇÃO
# =========================================================

@app.put("/usuarios/participacao")
def definir_participacao(
    dados: ParticipacaoRequest,
    usuario_atual=Depends(exigir_dev)
):

    resposta = (
        supabase
        .table("usuarios")
        .update({
            "participa": dados.participa
        })
        .eq("id", dados.usuario_id)
        .eq("tipo", "usuario")
        .execute()
    )

    if not resposta.data:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return {
        "sucesso": True,
        "mensagem": "Participação atualizada!"
    }


# =========================================================
# SUGESTÕES
# =========================================================

@app.post("/sugestoes")
def adicionar_sugestao(
    dados: SugestaoRequest,
    usuario_atual=Depends(obter_usuario_atual)
):

    usuario_id_token = int(usuario_atual["sub"])

    # Só pode adicionar sugestão para a própria conta
    if usuario_id_token != dados.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode alterar suas próprias sugestões."
        )

    sugestao = dados.sugestao.strip()

    if not sugestao:
        raise HTTPException(
            status_code=400,
            detail="A sugestão não pode estar vazia."
        )

    usuario = (
        supabase
        .table("usuarios")
        .select("id")
        .eq("id", dados.usuario_id)
        .limit(1)
        .execute()
    )

    if not usuario.data:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    resposta = (
        supabase
        .table("sugestoes")
        .insert({
            "usuario_id": dados.usuario_id,
            "sugestao": sugestao
        })
        .execute()
    )

    return {
        "sucesso": True,
        "mensagem": "Sugestão adicionada!",
        "sugestao": resposta.data[0]
    }


@app.get("/sugestoes/{usuario_id}")
def listar_sugestoes(
    usuario_id: int,
    usuario_atual=Depends(obter_usuario_atual)
):

    usuario_id_token = int(usuario_atual["sub"])

    if usuario_id_token != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode acessar suas próprias sugestões."
        )

    resposta = (
        supabase
        .table("sugestoes")
        .select("id, sugestao")
        .eq("usuario_id", usuario_id)
        .order("id")
        .execute()
    )

    return resposta.data


@app.delete("/sugestoes/{sugestao_id}")
def remover_sugestao(
    sugestao_id: int,
    usuario_atual=Depends(obter_usuario_atual)
):

    usuario_id = int(usuario_atual["sub"])

    sugestao = (
        supabase
        .table("sugestoes")
        .select("id, usuario_id")
        .eq("id", sugestao_id)
        .limit(1)
        .execute()
    )

    if not sugestao.data:
        raise HTTPException(
            status_code=404,
            detail="Sugestão não encontrada."
        )

    if sugestao.data[0]["usuario_id"] != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode remover suas próprias sugestões."
        )

    (
        supabase
        .table("sugestoes")
        .delete()
        .eq("id", sugestao_id)
        .execute()
    )

    return {
        "sucesso": True,
        "mensagem": "Sugestão removida!"
    }


# =========================================================
# SORTEIO
# =========================================================

@app.get("/sorteio/status")
def status_sorteio(
    usuario_atual=Depends(obter_usuario_atual)
):

    resposta = (
        supabase
        .table("sorteios")
        .select("id, realizado")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if not resposta.data:
        return {
            "realizado": False
        }

    return {
        "realizado": resposta.data[0]["realizado"]
    }


@app.get("/sorteio/amigo/{usuario_id}")
def obter_amigo(
    usuario_id: int,
    usuario_atual=Depends(obter_usuario_atual)
):

    usuario_id_token = int(usuario_atual["sub"])

    # Usuário normal só pode ver o próprio resultado
    if usuario_atual.get("tipo") != "dev":
        if usuario_id_token != usuario_id:
            raise HTTPException(
                status_code=403,
                detail="Você só pode acessar seu próprio resultado."
            )

    sorteio = (
        supabase
        .table("sorteios")
        .select("id, realizado")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if not sorteio.data:
        raise HTTPException(
            status_code=404,
            detail="Nenhum sorteio foi realizado."
        )

    sorteio_atual = sorteio.data[0]

    if not sorteio_atual["realizado"]:
        raise HTTPException(
            status_code=404,
            detail="O sorteio ainda não foi realizado."
        )

    resultado = (
        supabase
        .table("sorteio_resultados")
        .select(
            "amigo_id, usuarios!sorteio_resultados_amigo_id_fkey(id, nome)"
        )
        .eq("sorteio_id", sorteio_atual["id"])
        .eq("usuario_id", usuario_id)
        .limit(1)
        .execute()
    )

    if not resultado.data:
        raise HTTPException(
            status_code=404,
            detail="Resultado não encontrado."
        )

    amigo = resultado.data[0]["usuarios"]

    return {
        "id": amigo["id"],
        "nome": amigo["nome"]
    }


# =========================================================
# SUGESTÕES PÚBLICAS
# =========================================================

@app.get("/usuarios/{usuario_id}/sugestoes")
def obter_sugestoes_publicas(
    usuario_id: int,
    usuario_atual=Depends(obter_usuario_atual)
):

    resposta = (
        supabase
        .table("sugestoes")
        .select("id, sugestao")
        .eq("usuario_id", usuario_id)
        .order("id")
        .execute()
    )

    return resposta.data


# =========================================================
# CRIAR DEV
# =========================================================

@app.post("/dev/criar")
def criar_conta_dev(
    dados: CadastroRequest,
    usuario_atual=Depends(exigir_dev)
):

    nome = dados.nome.strip()
    senha = dados.senha

    if not nome or not senha:
        raise HTTPException(
            status_code=400,
            detail="Nome e senha são obrigatórios."
        )

    existente = (
        supabase
        .table("usuarios")
        .select("id")
        .eq("nome", nome)
        .limit(1)
        .execute()
    )

    if existente.data:
        raise HTTPException(
            status_code=409,
            detail="Esse nome de usuário já existe."
        )

    senha_hash = password_hash.hash(senha)

    resposta = (
        supabase
        .table("usuarios")
        .insert({
            "nome": nome,
            "senha_hash": senha_hash,
            "participa": False,
            "tipo": "dev"
        })
        .execute()
    )

    return {
        "sucesso": True,
        "mensagem": "Conta Dev criada com sucesso!",
        "usuario": {
            "id": resposta.data[0]["id"],
            "nome": resposta.data[0]["nome"],
            "tipo": "dev"
        }
    }


# =========================================================
# RESET DO SORTEIO
# =========================================================

@app.post("/dev/resetar-sorteio")
def resetar_sorteio(
    usuario_atual=Depends(exigir_dev)
):

    sorteio = (
        supabase
        .table("sorteios")
        .select("id")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if sorteio.data:

        sorteio_id = sorteio.data[0]["id"]

        (
            supabase
            .table("sorteio_resultados")
            .delete()
            .eq("sorteio_id", sorteio_id)
            .execute()
        )

        (
            supabase
            .table("sorteios")
            .delete()
            .eq("id", sorteio_id)
            .execute()
        )

    (
        supabase
        .table("usuarios")
        .update({"participa": True})
        .eq("tipo", "usuario")
        .execute()
    )

    return {
        "sucesso": True,
        "mensagem": "Sorteio resetado com sucesso!"
    }


# =========================================================
# REALIZAR SORTEIO
# =========================================================

@app.post("/dev/sorteio")
def realizar_sorteio(
    usuario_atual=Depends(exigir_dev)
):

    # -----------------------------------------------------
    # Verifica se já existe um sorteio realizado
    # -----------------------------------------------------

    sorteio_atual = (
        supabase
        .table("sorteios")
        .select("id, realizado")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if sorteio_atual.data:

        ultimo_sorteio = sorteio_atual.data[0]

        if ultimo_sorteio["realizado"]:
            raise HTTPException(
                status_code=400,
                detail="O sorteio já foi realizado."
            )

        sorteio_id = ultimo_sorteio["id"]

    else:

        novo_sorteio = (
            supabase
            .table("sorteios")
            .insert({
                "realizado": False
            })
            .execute()
        )

        if not novo_sorteio.data:
            raise HTTPException(
                status_code=500,
                detail="Não foi possível criar o sorteio."
            )

        sorteio_id = novo_sorteio.data[0]["id"]

    # -----------------------------------------------------
    # Busca participantes
    # -----------------------------------------------------

    resposta = (
        supabase
        .table("usuarios")
        .select("id, nome")
        .eq("tipo", "usuario")
        .eq("participa", True)
        .execute()
    )

    participantes = resposta.data

    if len(participantes) < 2:
        raise HTTPException(
            status_code=400,
            detail="É necessário ter pelo menos 2 participantes."
        )

    # -----------------------------------------------------
    # Cria o sorteio
    # -----------------------------------------------------

    ids = [usuario["id"] for usuario in participantes]

    amigos = ids.copy()

    while True:

        random.shuffle(amigos)

        if all(
            usuario_id != amigo_id
            for usuario_id, amigo_id
            in zip(ids, amigos)
        ):
            break

    # -----------------------------------------------------
    # Salva os resultados
    # -----------------------------------------------------

    resultados = []

    for usuario_id, amigo_id in zip(ids, amigos):

        resultados.append({
            "sorteio_id": sorteio_id,
            "usuario_id": usuario_id,
            "amigo_id": amigo_id
        })

    try:

        (
            supabase
            .table("sorteio_resultados")
            .insert(resultados)
            .execute()
        )

    except Exception as erro:

        (
            supabase
            .table("sorteios")
            .delete()
            .eq("id", sorteio_id)
            .execute()
        )

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar o sorteio: {erro}"
        )

    # -----------------------------------------------------
    # Marca o sorteio como realizado
    # -----------------------------------------------------

    (
        supabase
        .table("sorteios")
        .update({
            "realizado": True
        })
        .eq("id", sorteio_id)
        .execute()
    )

    # -----------------------------------------------------
    # IMPORTANTE:
    # NUNCA retornamos os pares para o Dev.
    # -----------------------------------------------------

    return {
        "sucesso": True,
        "mensagem": "Sorteio realizado com sucesso!"
    }