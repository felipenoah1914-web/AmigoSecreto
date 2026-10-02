import kivy

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty

import api_client


# ==========================================
# CONFIGURACOES
# ==========================================

# Mantido no mesmo formato do seu app anterior:
# 400 x 700 = proporcao de celular no PC.
Window.size = (400, 700)
Window.clearcolor = (0.96, 0.95, 0.93, 1)


# ==========================================
# TEMA VISUAL
# ==========================================

COR_FUNDO = (0.96, 0.95, 0.93, 1)       # creme claro
COR_CARTAO = (1, 1, 1, 1)                # branco
COR_VERMELHO = (0.55, 0.10, 0.12, 1)    # vinho/vermelho
COR_VERDE = (0.15, 0.45, 0.29, 1)       # verde
COR_TEXTO = (0.12, 0.11, 0.11, 1)
COR_TEXTO_SECUNDARIO = (0.40, 0.38, 0.37, 1)
COR_BORDA = (0.88, 0.85, 0.82, 1)
COR_ERRO = (0.72, 0.13, 0.16, 1)


# ==========================================
# COMPONENTES VISUAIS
# ==========================================

class Fundo(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*COR_FUNDO)
            self.fundo = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self._atualizar_fundo,
            size=self._atualizar_fundo
        )

    def _atualizar_fundo(self, *args):
        self.fundo.pos = self.pos
        self.fundo.size = self.size


class Botao(Button):

    cor = ListProperty(COR_VERMELHO)

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(54))
        kwargs.setdefault("font_size", dp(16))
        kwargs.setdefault("color", (1, 1, 1, 1))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))

        super().__init__(**kwargs)

        self._desenhar()

        self.bind(
            pos=self._atualizar_fundo,
            size=self._atualizar_fundo,
            cor=self._desenhar,
            disabled=self._desenhar
        )

    def _desenhar(self, *args):
        self.canvas.before.clear()

        if self.disabled:
            cor = (0.76, 0.74, 0.72, 1)
        else:
            cor = self.cor

        with self.canvas.before:
            Color(*cor)
            self.fundo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

    def _atualizar_fundo(self, *args):
        if hasattr(self, "fundo"):
            self.fundo.pos = self.pos
            self.fundo.size = self.size


class Cartao(BoxLayout):

    def __init__(self, **kwargs):
        kwargs.setdefault("padding", dp(18))
        kwargs.setdefault("spacing", dp(10))

        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*COR_CARTAO)

            self.fundo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )

            Color(*COR_BORDA)

            self.borda = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(16)
                ),
                width=1
            )

        self.bind(
            pos=self._atualizar,
            size=self._atualizar
        )

    def _atualizar(self, *args):
        self.fundo.pos = self.pos
        self.fundo.size = self.size

        self.borda.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(16)
        )


def titulo_label(texto, tamanho=28):

    return Label(
        text=texto,
        font_size=dp(tamanho),
        color=COR_TEXTO,
        bold=True,
        size_hint_y=None,
        height=dp(52),
        halign="center",
        valign="middle"
    )


def subtitulo_label(texto, tamanho=16):

    return Label(
        text=texto,
        font_size=dp(tamanho),
        color=COR_TEXTO_SECUNDARIO,
        size_hint_y=None,
        height=dp(42),
        halign="center",
        valign="middle"
    )


def campo_texto(hint, senha=False):

    return TextInput(
        hint_text=hint,
        password=senha,
        multiline=False,
        size_hint_y=None,
        height=dp(52),
        padding=[dp(16), dp(14)],
        font_size=dp(16),
        foreground_color=COR_TEXTO,
        hint_text_color=COR_TEXTO_SECUNDARIO,
        background_normal="",
        background_active="",
        background_color=(1, 1, 1, 1),
        cursor_color=COR_VERMELHO,
        write_tab=False
    )


def mostrar_mensagem(
    titulo,
    mensagem,
    cor=COR_VERMELHO
):

    conteudo = BoxLayout(
        orientation="vertical",
        padding=dp(18),
        spacing=dp(12)
    )

    texto = Label(
        text=mensagem,
        color=COR_TEXTO,
        halign="center",
        valign="middle"
    )

    botao = Botao(
        text="OK",
        height=dp(48),
        cor=cor
    )

    conteudo.add_widget(texto)
    conteudo.add_widget(botao)

    popup = Popup(
        title=titulo,
        content=conteudo,
        size_hint=(0.84, 0.36),
        separator_color=cor,
        background_color=COR_CARTAO,
        title_color=COR_TEXTO,
        title_size=dp(18)
    )

    botao.bind(
        on_press=popup.dismiss
    )

    popup.open()


# ==========================================
# TELA INICIAL
# ==========================================

class TelaInicial(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(30), dp(30)],
            spacing=dp(14)
        )

        topo = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(155),
            spacing=dp(4)
        )

        topo.add_widget(
            Label(
                text="AMIGO SECRETO",
                font_size=dp(31),
                bold=True,
                color=COR_VERMELHO,
                size_hint_y=None,
                height=dp(62)
            )
        )

        topo.add_widget(
            Label(
                text="DA FAMÍLIA",
                font_size=dp(21),
                bold=True,
                color=COR_VERDE,
                size_hint_y=None,
                height=dp(42)
            )
        )

        topo.add_widget(
            subtitulo_label(
                "Um presente, uma surpresa, uma família.",
                15
            )
        )

        layout.add_widget(topo)
        layout.add_widget(Label())

        card = Cartao(
            orientation="vertical",
            size_hint_y=None,
            height=dp(270),
            padding=[dp(22), dp(22)],
            spacing=dp(12)
        )

        card.add_widget(
            Label(
                text="Bem-vindo!",
                font_size=dp(21),
                bold=True,
                color=COR_TEXTO,
                size_hint_y=None,
                height=dp(35)
            )
        )

        card.add_widget(
            Label(
                text=(
                    "Entre na sua conta ou crie uma nova\n"
                    "para participar do Amigo Secreto."
                ),
                color=COR_TEXTO_SECUNDARIO,
                halign="center",
                valign="middle"
            )
        )

        botao_login = Botao(
            text="ENTRAR",
            height=dp(52),
            cor=COR_VERMELHO
        )

        botao_cadastro = Botao(
            text="CRIAR CONTA",
            height=dp(52),
            cor=COR_VERDE
        )

        card.add_widget(botao_login)
        card.add_widget(botao_cadastro)

        layout.add_widget(card)
        layout.add_widget(Label())

        layout.add_widget(
            Label(
                text="Amigo Secreto da Família",
                color=COR_TEXTO_SECUNDARIO,
                font_size=dp(12),
                size_hint_y=None,
                height=dp(25)
            )
        )

        botao_login.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "login"
            )
        )

        botao_cadastro.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "cadastro"
            )
        )

        self.add_widget(layout)


# ==========================================
# CADASTRO
# ==========================================

class TelaCadastro(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(28), dp(24)],
            spacing=dp(12)
        )

        layout.add_widget(
            titulo_label("CRIAR CONTA", 27)
        )

        layout.add_widget(
            subtitulo_label(
                "Crie sua conta para participar.",
                15
            )
        )

        card = Cartao(
            orientation="vertical",
            size_hint_y=None,
            height=dp(305),
            padding=dp(18),
            spacing=dp(12)
        )

        nome = campo_texto("Nome")
        senha = campo_texto("Senha", senha=True)

        senha_confirmacao = campo_texto(
            "Confirmar senha",
            senha=True
        )

        botao_cadastrar = Botao(
            text="CRIAR CONTA",
            height=dp(54),
            cor=COR_VERDE
        )

        card.add_widget(nome)
        card.add_widget(senha)
        card.add_widget(senha_confirmacao)
        card.add_widget(botao_cadastrar)

        layout.add_widget(card)
        layout.add_widget(Label())

        botao_voltar = Botao(
            text="VOLTAR",
            height=dp(48),
            cor=COR_TEXTO_SECUNDARIO
        )

        layout.add_widget(botao_voltar)

        botao_cadastrar.bind(
            on_press=lambda x: self.cadastrar(
                nome,
                senha,
                senha_confirmacao
            )
        )

        botao_voltar.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "inicio"
            )
        )

        self.add_widget(layout)

    def cadastrar(
        self,
        nome,
        senha,
        senha_confirmacao
    ):

        nome_usuario = nome.text.strip()
        senha_usuario = senha.text
        confirmacao = senha_confirmacao.text

        if not nome_usuario:

            mostrar_mensagem(
                "Atenção",
                "Digite seu nome."
            )

            return

        if not senha_usuario:

            mostrar_mensagem(
                "Atenção",
                "Digite uma senha."
            )

            return

        if senha_usuario != confirmacao:

            mostrar_mensagem(
                "Atenção",
                "As senhas não são iguais."
            )

            return

        sucesso = api_client.cadastrar(
            nome_usuario,
            senha_usuario
        ).status_code == 200

        if sucesso:

            mostrar_mensagem(
                "Conta criada!",
                f"Conta de {nome_usuario} criada com sucesso.",
                COR_VERDE
            )

            nome.text = ""
            senha.text = ""
            senha_confirmacao.text = ""

            self.manager.current = "login"

        else:

            mostrar_mensagem(
                "Nome indisponível",
                "Esse nome já está cadastrado."
            )


# ==========================================
# LOGIN
# ==========================================

class TelaLogin(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(28), dp(24)],
            spacing=dp(12)
        )

        layout.add_widget(
            titulo_label("ENTRAR", 27)
        )

        layout.add_widget(
            subtitulo_label(
                "Acesse sua conta.",
                15
            )
        )

        card = Cartao(
            orientation="vertical",
            size_hint_y=None,
            height=dp(220),
            padding=dp(18),
            spacing=dp(14)
        )

        nome = campo_texto("Nome")
        senha = campo_texto(
            "Senha",
            senha=True
        )

        botao_entrar = Botao(
            text="ENTRAR",
            height=dp(54),
            cor=COR_VERMELHO
        )

        card.add_widget(nome)
        card.add_widget(senha)
        card.add_widget(botao_entrar)

        layout.add_widget(card)
        layout.add_widget(Label())

        botao_voltar = Botao(
            text="VOLTAR",
            height=dp(48),
            cor=COR_TEXTO_SECUNDARIO
        )

        layout.add_widget(botao_voltar)

        botao_entrar.bind(
            on_press=lambda x: self.fazer_login(
                nome,
                senha
            )
        )

        botao_voltar.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "inicio"
            )
        )

        self.add_widget(layout)

    def fazer_login(self, nome, senha):

        nome_usuario = nome.text.strip()
        senha_usuario = senha.text

        if not nome_usuario or not senha_usuario:

            mostrar_mensagem(
                "Atenção",
                "Preencha nome e senha."
            )

            return

        resposta = api_client.login(
            nome_usuario,
            senha_usuario
        )

        dados = resposta.json() if resposta.status_code == 200 else None
        usuario = dados.get("usuario") if dados else None

        if usuario:

            self.manager.usuario_id = usuario["id"]
            self.manager.usuario_nome = usuario["nome"]
            self.manager.usuario_tipo = usuario["tipo"]

            nome.text = ""
            senha.text = ""

            if usuario["tipo"] == "dev":

                self.manager.current = "dev"

            else:

                self.manager.current = "perfil"

        else:

            mostrar_mensagem(
                "Não foi possível entrar",
                "Nome ou senha incorretos."
            )


# ==========================================
# MEU PERFIL
# ==========================================

class TelaPerfil(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(18)],
            spacing=dp(10)
        )

        self.nome = Label(
            text="MEU PERFIL",
            font_size=dp(27),
            bold=True,
            color=COR_VERMELHO,
            size_hint_y=None,
            height=dp(55)
        )

        layout.add_widget(self.nome)

        titulo_sugestoes = Label(
            text="Minhas sugestões",
            font_size=dp(19),
            bold=True,
            color=COR_TEXTO,
            size_hint_y=None,
            height=dp(42)
        )

        layout.add_widget(titulo_sugestoes)

        scroll = ScrollView(
            bar_width=dp(5),
            scroll_type=["bars", "content"]
        )

        self.lista_sugestoes = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        self.lista_sugestoes.bind(
            minimum_height=self.lista_sugestoes.setter(
                "height"
            )
        )

        scroll.add_widget(self.lista_sugestoes)
        layout.add_widget(scroll)

        botao_adicionar = Botao(
            text="ADICIONAR SUGESTÃO",
            height=dp(54),
            cor=COR_VERDE
        )

        botao_amigo = Botao(
            text="MEU AMIGO SECRETO",
            height=dp(54),
            cor=COR_VERMELHO
        )

        botao_sair = Botao(
            text="SAIR",
            height=dp(46),
            cor=COR_TEXTO_SECUNDARIO
        )

        layout.add_widget(botao_adicionar)
        layout.add_widget(botao_amigo)
        layout.add_widget(botao_sair)

        botao_adicionar.bind(
            on_press=self.abrir_adicionar
        )

        botao_amigo.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "meu_amigo"
            )
        )

        botao_sair.bind(
            on_press=self.sair
        )

        self.add_widget(layout)

    def on_enter(self):

        nome = self.manager.usuario_nome

        self.nome.text = nome.upper()

        self.carregar_sugestoes()

    def carregar_sugestoes(self):

        self.lista_sugestoes.clear_widgets()

        resposta = api_client.listar_sugestoes(
            self.manager.usuario_id
        )
        sugestoes = resposta.json() if resposta.status_code == 200 else []

        if not sugestoes:

            self.lista_sugestoes.add_widget(
                Label(
                    text="Nenhuma sugestão adicionada ainda.",
                    color=COR_TEXTO_SECUNDARIO,
                    size_hint_y=None,
                    height=dp(80),
                    halign="center",
                    valign="middle"
                )
            )

            return

        for sugestao in sugestoes:

            sugestao_id = sugestao["id"]
            texto_sugestao = sugestao["sugestao"]

            linha = Cartao(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(58),
                padding=[dp(14), dp(8)]
            )

            texto = Label(
                text=texto_sugestao,
                color=COR_TEXTO,
                font_size=dp(16),
                halign="left",
                valign="middle"
            )

            remover = Botao(
                text="REMOVER",
                size_hint_x=None,
                width=dp(92),
                height=dp(40),
                font_size=dp(12),
                cor=COR_ERRO
            )

            remover.bind(
                on_press=lambda btn,
                sid=sugestao_id:
                self.remover_sugestao(sid)
            )

            linha.add_widget(texto)
            linha.add_widget(remover)

            self.lista_sugestoes.add_widget(linha)

    def abrir_adicionar(self, instance):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12)
        )

        entrada = campo_texto(
            "Ex.: Patinete"
        )

        botao = Botao(
            text="ADICIONAR",
            height=dp(50),
            cor=COR_VERDE
        )

        layout.add_widget(
            Label(
                text="O que você gostaria de ganhar?",
                color=COR_TEXTO,
                size_hint_y=None,
                height=dp(40)
            )
        )

        layout.add_widget(entrada)
        layout.add_widget(botao)

        popup = Popup(
            title="Nova sugestão",
            content=layout,
            size_hint=(0.86, 0.40),
            separator_color=COR_VERDE,
            background_color=COR_CARTAO,
            title_color=COR_TEXTO,
            title_size=dp(18)
        )

        botao.bind(
            on_press=lambda x:
            self.adicionar_sugestao(
                entrada,
                popup
            )
        )

        popup.open()

    def adicionar_sugestao(
        self,
        entrada,
        popup
    ):

        sugestao = entrada.text.strip()

        if not sugestao:

            mostrar_mensagem(
                "Atenção",
                "Digite uma sugestão."
            )

            return

        resposta = api_client.adicionar_sugestao(
            self.manager.usuario_id,
            sugestao
        )

        if resposta.status_code != 200:
            mostrar_mensagem("Erro", "Não foi possível adicionar a sugestão.")
            return

        popup.dismiss()

        self.carregar_sugestoes()

    def remover_sugestao(self, sugestao_id):

        api_client.remover_sugestao(
            sugestao_id
        )

        self.carregar_sugestoes()

    def sair(self, instance):

        self.manager.usuario_id = None
        self.manager.usuario_nome = None
        self.manager.usuario_tipo = None

        self.manager.current = "inicio"


# ==========================================
# MEU AMIGO SECRETO
# ==========================================

class TelaMeuAmigo(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(22), dp(24)],
            spacing=dp(14)
        )

        layout.add_widget(
            titulo_label(
                "SEU AMIGO SECRETO",
                25
            )
        )

        layout.add_widget(
            subtitulo_label(
                "Sua surpresa está aqui.",
                15
            )
        )

        card = Cartao(
            orientation="vertical",
            size_hint_y=None,
            height=dp(230),
            padding=dp(22),
            spacing=dp(10)
        )

        self.nome_amigo = Label(
            text="",
            font_size=dp(27),
            bold=True,
            color=COR_VERMELHO,
            halign="center",
            valign="middle"
        )

        self.status = Label(
            text="",
            font_size=dp(15),
            color=COR_TEXTO_SECUNDARIO,
            halign="center",
            valign="middle"
        )

        card.add_widget(self.nome_amigo)
        card.add_widget(self.status)

        layout.add_widget(card)
        layout.add_widget(Label())

        botao_perfil = Botao(
            text="VER PERFIL",
            height=dp(54),
            cor=COR_VERDE
        )

        botao_voltar = Botao(
            text="VOLTAR",
            height=dp(46),
            cor=COR_TEXTO_SECUNDARIO
        )

        layout.add_widget(botao_perfil)
        layout.add_widget(botao_voltar)

        botao_perfil.bind(
            on_press=self.ver_perfil
        )

        botao_voltar.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "perfil"
            )
        )

        self.add_widget(layout)

        self.amigo_id = None

    def on_enter(self):

        self.amigo_id = None

        if not api_client.sorteio_ja_realizado():

            self.nome_amigo.text = "AINDA NÃO"

            self.status.text = (
                "O sorteio ainda não foi realizado."
            )

            return

        resposta = api_client.obter_amigo(
            self.manager.usuario_id
        )
        resultado = resposta.json() if resposta.status_code == 200 else None

        if not resultado:

            self.nome_amigo.text = "SEM RESULTADO"

            self.status.text = (
                "Não foi encontrado um resultado "
                "para sua conta."
            )

            return

        self.amigo_id = resultado["id"]

        nome = resultado["nome"]

        self.nome_amigo.text = (
            f"Você tirou:\n{nome}"
        )

        self.status.text = (
            "Abra o perfil para ver as sugestões "
            "de presente."
        )

    def ver_perfil(self, instance):

        if self.amigo_id is None:

            mostrar_mensagem(
                "Atenção",
                "O perfil ainda não está disponível."
            )

            return

        self.manager.perfil_visitado_id = self.amigo_id

        self.manager.current = "perfil_amigo"


# ==========================================
# PERFIL DO AMIGO
# ==========================================

class TelaPerfilAmigo(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(18)],
            spacing=dp(10)
        )

        self.nome = Label(
            text="PERFIL",
            font_size=dp(27),
            bold=True,
            color=COR_VERMELHO,
            size_hint_y=None,
            height=dp(55)
        )

        layout.add_widget(self.nome)

        titulo = Label(
            text="Sugestões de presente",
            font_size=dp(19),
            bold=True,
            color=COR_TEXTO,
            size_hint_y=None,
            height=dp(42)
        )

        layout.add_widget(titulo)

        scroll = ScrollView(
            bar_width=dp(5),
            scroll_type=["bars", "content"]
        )

        self.lista = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        self.lista.bind(
            minimum_height=self.lista.setter(
                "height"
            )
        )

        scroll.add_widget(self.lista)

        layout.add_widget(scroll)

        botao_voltar = Botao(
            text="VOLTAR",
            height=dp(48),
            cor=COR_TEXTO_SECUNDARIO
        )

        layout.add_widget(botao_voltar)

        botao_voltar.bind(
            on_press=lambda x: setattr(
                self.manager,
                "current",
                "meu_amigo"
            )
        )

        self.add_widget(layout)

    def on_enter(self):

        self.lista.clear_widgets()

        usuario_id = self.manager.perfil_visitado_id

        resposta = api_client.obter_usuario(
            usuario_id
        )
        usuario = resposta.json() if resposta.status_code == 200 else None

        if not usuario:

            self.nome.text = "USUÁRIO NÃO ENCONTRADO"

            return

        nome = usuario["nome"]

        self.nome.text = nome.upper()

        resposta = api_client.obter_sugestoes_publicas(
            usuario_id
        )
        sugestoes = resposta.json() if resposta.status_code == 200 else []

        if not sugestoes:

            self.lista.add_widget(
                Label(
                    text=(
                        "Essa pessoa ainda não "
                        "adicionou sugestões."
                    ),
                    color=COR_TEXTO_SECUNDARIO,
                    size_hint_y=None,
                    height=dp(80),
                    halign="center",
                    valign="middle"
                )
            )

            return

        for sugestao in sugestoes:

            texto = sugestao["sugestao"]

            linha = Cartao(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(58),
                padding=[dp(15), dp(8)]
            )

            linha.add_widget(
                Label(
                    text=texto,
                    color=COR_TEXTO,
                    font_size=dp(17),
                    halign="left",
                    valign="middle"
                )
            )

            self.lista.add_widget(linha)


# ==========================================
# PAINEL DEV
# ==========================================

class TelaDev(Fundo):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(18)],
            spacing=dp(9)
        )

        self.titulo = Label(
            text="PAINEL DEV",
            font_size=dp(27),
            bold=True,
            color=COR_VERMELHO,
            size_hint_y=None,
            height=dp(55)
        )

        self.layout.add_widget(self.titulo)

        self.info = Label(
            text="Escolha quem participa do sorteio.",
            color=COR_TEXTO_SECUNDARIO,
            size_hint_y=None,
            height=dp(35)
        )

        self.layout.add_widget(self.info)

        self.scroll = ScrollView(
            bar_width=dp(5),
            scroll_type=["bars", "content"]
        )

        self.lista = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        self.lista.bind(
            minimum_height=self.lista.setter("height")
        )

        self.scroll.add_widget(self.lista)

        self.layout.add_widget(self.scroll)

        self.botao_sorteio = Botao(
            text="REALIZAR SORTEIO",
            height=dp(54),
            cor=COR_VERMELHO
        )

        self.botao_sorteio.bind(
            on_press=self.confirmar_sorteio
        )

        self.layout.add_widget(self.botao_sorteio)

        self.botao_novo_sorteio = Botao(
            text="NOVO SORTEIO",
            height=dp(54),
            cor=COR_VERDE
        )

        self.botao_novo_sorteio.bind(
            on_press=self.confirmar_novo_sorteio
        )

        self.layout.add_widget(self.botao_novo_sorteio)

        self.botao_sair = Botao(
            text="SAIR",
            height=dp(44),
            cor=COR_TEXTO_SECUNDARIO
        )

        self.botao_sair.bind(
            on_press=self.sair
        )

        self.layout.add_widget(self.botao_sair)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.carregar_usuarios()

    def carregar_usuarios(self):

        self.lista.clear_widgets()

        resposta = api_client.listar_usuarios_admin()
        usuarios = resposta.json() if resposta.status_code == 200 else []

        if not usuarios:

            self.lista.add_widget(
                Label(
                    text="Nenhum usuário cadastrado ainda.",
                    color=COR_TEXTO_SECUNDARIO,
                    size_hint_y=None,
                    height=dp(70)
                )
            )

        for usuario in usuarios:

            usuario_id = usuario["id"]
            nome = usuario["nome"]
            participa = usuario["participa"]

            linha = Cartao(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(58),
                padding=[dp(12), dp(7)]
            )

            checkbox = CheckBox(
                active=bool(participa),
                size_hint_x=None,
                width=dp(45)
            )

            checkbox.bind(
                active=lambda checkbox,
                valor,
                uid=usuario_id:
                api_client.definir_participacao(
                    uid,
                    bool(valor)
                )
            )

            nome_label = Label(
                text=nome,
                color=COR_TEXTO,
                font_size=dp(16),
                halign="left",
                valign="middle"
            )

            linha.add_widget(checkbox)
            linha.add_widget(nome_label)

            self.lista.add_widget(linha)

        sorteio_realizado = api_client.sorteio_ja_realizado()

        self.botao_sorteio.disabled = sorteio_realizado

        self.botao_novo_sorteio.disabled = (
            not sorteio_realizado
        )

    def confirmar_sorteio(self, instance):

        resposta = api_client.listar_usuarios_admin()
        usuarios_admin = resposta.json() if resposta.status_code == 200 else []

        participantes = [
            usuario
            for usuario in usuarios_admin
            if usuario["participa"]
        ]

        if len(participantes) < 2:

            mostrar_mensagem(
                "Participantes insuficientes",
                "É necessário ter pelo menos 2 participantes."
            )

            return

        conteudo = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12)
        )

        mensagem = Label(
            text=(
                "Tem certeza que deseja realizar o sorteio?\n\n"
                "Depois disso, os participantes não poderão "
                "ser alterados até um novo sorteio."
            ),
            color=COR_TEXTO,
            halign="center",
            valign="middle"
        )

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        sim = Botao(
            text="CONFIRMAR",
            height=dp(50),
            cor=COR_VERDE
        )

        nao = Botao(
            text="CANCELAR",
            height=dp(50),
            cor=COR_TEXTO_SECUNDARIO
        )

        botoes.add_widget(sim)
        botoes.add_widget(nao)

        conteudo.add_widget(mensagem)
        conteudo.add_widget(botoes)

        popup = Popup(
            title="Confirmar sorteio",
            content=conteudo,
            size_hint=(0.88, 0.44),
            separator_color=COR_VERMELHO,
            background_color=COR_CARTAO,
            title_color=COR_TEXTO,
            title_size=dp(18)
        )

        nao.bind(
            on_press=popup.dismiss
        )

        sim.bind(
            on_press=lambda instance:
            self.realizar_sorteio(popup)
        )

        popup.open()

    def realizar_sorteio(self, popup):

        popup.dismiss()

        resultado = api_client.realizar_sorteio()

        if resultado.status_code == 200:

            mostrar_mensagem(
                "Sorteio realizado!",
                "O sorteio foi realizado com sucesso.\n\n"
                "Cada participante poderá ver apenas "
                "o próprio resultado.",
                COR_VERDE
            )

            self.carregar_usuarios()

    def confirmar_novo_sorteio(self, instance):

        conteudo = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12)
        )

        mensagem = Label(
            text=(
                "NOVO SORTEIO\n\n"
                "Isso irá apagar SOMENTE os resultados "
                "do sorteio anterior.\n\n"
                "As contas e sugestões serão mantidas.\n\n"
                "Deseja continuar?"
            ),
            color=COR_TEXTO,
            halign="center",
            valign="middle"
        )

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        sim = Botao(
            text="CONFIRMAR",
            height=dp(50),
            cor=COR_VERDE
        )

        nao = Botao(
            text="CANCELAR",
            height=dp(50),
            cor=COR_TEXTO_SECUNDARIO
        )

        botoes.add_widget(sim)
        botoes.add_widget(nao)

        conteudo.add_widget(mensagem)
        conteudo.add_widget(botoes)

        popup = Popup(
            title="Novo sorteio",
            content=conteudo,
            size_hint=(0.88, 0.50),
            separator_color=COR_VERDE,
            background_color=COR_CARTAO,
            title_color=COR_TEXTO,
            title_size=dp(18)
        )

        nao.bind(
            on_press=popup.dismiss
        )

        sim.bind(
            on_press=lambda instance:
            self.novo_sorteio(popup)
        )

        popup.open()

    def novo_sorteio(self, popup):

        popup.dismiss()

        api_client.resetar_sorteio()

        mostrar_mensagem(
            "Novo sorteio preparado",
            "As contas e sugestões foram mantidas.\n\n"
            "Agora escolha novamente quem participa.",
            COR_VERDE
        )

        self.carregar_usuarios()

    def sair(self, instance):
        self.manager.current = "login"


# ==========================================
# GERENCIADOR
# ==========================================

class GerenciadorTelas(ScreenManager):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.usuario_id = None
        self.usuario_nome = None
        self.usuario_tipo = None
        self.perfil_visitado_id = None

        self.add_widget(
            TelaInicial(name="inicio")
        )

        self.add_widget(
            TelaCadastro(name="cadastro")
        )

        self.add_widget(
            TelaLogin(name="login")
        )

        self.add_widget(
            TelaPerfil(name="perfil")
        )

        self.add_widget(
            TelaMeuAmigo(name="meu_amigo")
        )

        self.add_widget(
            TelaPerfilAmigo(name="perfil_amigo")
        )

        self.add_widget(
            TelaDev(name="dev")
        )


# ==========================================
# APLICATIVO
# ==========================================

class AmigoSecretoApp(App):

    def build(self):

        self.title = "Amigo Secreto da Família"

        return GerenciadorTelas()


# ==========================================
# INICIAR
# ==========================================

if __name__ == "__main__":
    AmigoSecretoApp().run()
