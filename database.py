import sqlite3
import hashlib

BANCO = "amigo_secreto.db"


def conectar():
    return sqlite3.connect(BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            participa INTEGER DEFAULT 1,
            tipo TEXT NOT NULL DEFAULT 'usuario'
        )
    """)

    # Compatibilidade com banco antigo
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    if "tipo" not in colunas:
        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN tipo TEXT NOT NULL DEFAULT 'usuario'
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sugestoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            sugestao TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sorteio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL UNIQUE,
            amigo_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (amigo_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracao (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO configuracao (chave, valor)
        VALUES ('sorteio_realizado', '0')
    """)

    conexao.commit()
    conexao.close()


def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def cadastrar_usuario(nome, senha):
    conexao = conectar()
    cursor = conexao.cursor()

    senha_hash = criptografar_senha(senha)

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, senha, tipo, participa)
            VALUES (?, ?, 'usuario', 1)
        """, (nome, senha_hash))

        conexao.commit()
        resultado = True

    except sqlite3.IntegrityError:
        resultado = False

    conexao.close()
    return resultado


def criar_conta_dev(nome, senha):
    conexao = conectar()
    cursor = conexao.cursor()

    senha_hash = criptografar_senha(senha)

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, senha, tipo, participa)
            VALUES (?, ?, 'dev', 0)
        """, (nome, senha_hash))

        conexao.commit()
        resultado = True

    except sqlite3.IntegrityError:
        resultado = False

    conexao.close()
    return resultado


def login(nome, senha):
    conexao = conectar()
    cursor = conexao.cursor()

    senha_hash = criptografar_senha(senha)

    cursor.execute("""
        SELECT id, nome, participa, tipo
        FROM usuarios
        WHERE nome = ? AND senha = ?
    """, (nome, senha_hash))

    usuario = cursor.fetchone()

    conexao.close()
    return usuario


def listar_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, participa
        FROM usuarios
        ORDER BY nome
    """)

    usuarios = cursor.fetchall()

    conexao.close()
    return usuarios


def listar_usuarios_admin():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, participa, tipo
        FROM usuarios
        WHERE tipo = 'usuario'
        ORDER BY nome
    """)

    usuarios = cursor.fetchall()

    conexao.close()
    return usuarios


def definir_participacao(usuario_id, participa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET participa = ?
        WHERE id = ?
        AND tipo = 'usuario'
    """, (participa, usuario_id))

    conexao.commit()
    conexao.close()


def adicionar_sugestao(usuario_id, sugestao):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO sugestoes (usuario_id, sugestao)
        VALUES (?, ?)
    """, (usuario_id, sugestao))

    conexao.commit()
    conexao.close()


def listar_sugestoes(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, sugestao
        FROM sugestoes
        WHERE usuario_id = ?
        ORDER BY id
    """, (usuario_id,))

    sugestoes = cursor.fetchall()

    conexao.close()
    return sugestoes


def remover_sugestao(sugestao_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM sugestoes
        WHERE id = ?
    """, (sugestao_id,))

    conexao.commit()
    conexao.close()


def sorteio_ja_realizado():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT valor
        FROM configuracao
        WHERE chave = 'sorteio_realizado'
    """)

    resultado = cursor.fetchone()

    conexao.close()

    return resultado[0] == "1"


def marcar_sorteio_realizado():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE configuracao
        SET valor = '1'
        WHERE chave = 'sorteio_realizado'
    """)

    conexao.commit()
    conexao.close()


def salvar_sorteio(usuario_id, amigo_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO sorteio (usuario_id, amigo_id)
        VALUES (?, ?)
    """, (usuario_id, amigo_id))

    conexao.commit()
    conexao.close()


def obter_amigo(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT u.id, u.nome
        FROM sorteio s
        JOIN usuarios u ON u.id = s.amigo_id
        WHERE s.usuario_id = ?
    """, (usuario_id,))

    amigo = cursor.fetchone()

    conexao.close()
    return amigo


def obter_usuario(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, participa
        FROM usuarios
        WHERE id = ?
    """, (usuario_id,))

    usuario = cursor.fetchone()

    conexao.close()
    return usuario


def obter_sugestoes_publicas(usuario_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, sugestao
        FROM sugestoes
        WHERE usuario_id = ?
        ORDER BY id
    """, (usuario_id,))

    sugestoes = cursor.fetchall()

    conexao.close()
    return sugestoes

def resetar_sorteio():
    conexao = conectar()
    cursor = conexao.cursor()

    # Apaga somente os resultados do sorteio anterior
    cursor.execute("DELETE FROM sorteio")

    # Marca que ainda não existe sorteio realizado
    cursor.execute("""
        UPDATE configuracao
        SET valor = '0'
        WHERE chave = 'sorteio_realizado'
    """)

    # No começo de cada novo ano, todos os usuários
    # voltam a ser participantes.
    cursor.execute("""
        UPDATE usuarios
        SET participa = 1
        WHERE tipo = 'usuario'
    """)

    conexao.commit()
    conexao.close()

criar_banco()