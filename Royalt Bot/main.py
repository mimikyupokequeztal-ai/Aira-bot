import asyncio
import os
import sys
import threading
import time

from pathlib import Path

import discord
from discord.ext import commands

from dotenv import load_dotenv

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

COGS_DIR = BASE_DIR / "cogs"

ARQUIVO_ENV = BASE_DIR / ".env"


# ============================================================
# CARREGAR .ENV
# ============================================================

load_dotenv(
    dotenv_path=ARQUIVO_ENV
)


# ============================================================
# TOKEN
# ============================================================

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)


# ============================================================
# CONFIGURAÇÕES DO AUTO-RELOAD
# ============================================================

IGNORAR_PASTAS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
    "env",
    ".env"
}

IGNORAR_EXTENSOES = {
    ".pyc",
    ".pyo",
    ".tmp"
}

REINICIAR_EVENTO = threading.Event()


# ============================================================
# VERIFICAR SE O ARQUIVO DEVE SER MONITORADO
# ============================================================

def deve_observar(caminho):

    caminho = Path(caminho)

    # --------------------------------------------------------
    # Somente arquivos Python
    # --------------------------------------------------------

    if caminho.suffix.lower() != ".py":
        return False

    # --------------------------------------------------------
    # Arquivos ignorados
    # --------------------------------------------------------

    if caminho.suffix.lower() in IGNORAR_EXTENSOES:
        return False

    if caminho.name.startswith("."):
        return False

    # --------------------------------------------------------
    # Pastas ignoradas
    # --------------------------------------------------------

    for parte in caminho.parts:

        if parte in IGNORAR_PASTAS:
            return False

    return True


# ============================================================
# WATCHDOG
# ============================================================

class CodigoAlteradoHandler(FileSystemEventHandler):

    def __init__(self):

        super().__init__()

        self.ultimo_evento = 0.0

        self.arquivo_pendente = None

    # ========================================================
    # REGISTRAR ALTERAÇÃO
    # ========================================================

    def registrar(self, caminho):

        if not deve_observar(caminho):
            return

        agora = time.monotonic()

        # ----------------------------------------------------
        # Evita múltiplos eventos do VS Code
        # ----------------------------------------------------

        if agora - self.ultimo_evento < 1.0:
            return

        self.ultimo_evento = agora

        self.arquivo_pendente = str(
            Path(caminho).resolve()
        )

        print(
            "\n" + "=" * 64
        )

        print(
            "🔄 ALTERAÇÃO DE CÓDIGO DETECTADA"
        )

        print(
            f"📄 Arquivo: {Path(caminho).name}"
        )

        print(
            "♻️ Preparando reinicialização do Royalt..."
        )

        print(
            "=" * 64
        )

        REINICIAR_EVENTO.set()

    # ========================================================
    # ARQUIVO MODIFICADO
    # ========================================================

    def on_modified(self, event):

        if event.is_directory:
            return

        self.registrar(
            event.src_path
        )

    # ========================================================
    # ARQUIVO CRIADO
    # ========================================================

    def on_created(self, event):

        if event.is_directory:
            return

        self.registrar(
            event.src_path
        )

    # ========================================================
    # ARQUIVO MOVIDO
    # ========================================================

    def on_moved(self, event):

        if event.is_directory:
            return

        self.registrar(
            event.dest_path
        )


# ============================================================
# BOT
# ============================================================

class Royalt(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents
        )

        self.observer = None

        self.monitorando = False

        self.reinicio_iniciado = False

        # ----------------------------------------------------
        # Evita sincronizações repetidas desnecessárias
        # ----------------------------------------------------

        self.slash_sincronizado = False

    # ========================================================
    # SETUP HOOK
    # ========================================================

    async def setup_hook(self):

        print(
            "\n" + "=" * 64
        )

        print(
            "🔧 ROYALT • CARREGANDO SISTEMAS"
        )

        print(
            "=" * 64
        )

        extensoes = [

            "cogs.moderation",
            "cogs.antiraid",
            "cogs.logs",
            "cogs.help",
            "cogs.updates",
            "cogs.sorteios",
            "cogs.tickets",
            "cogs.desabafos",
            "cogs.desabafos_config",
            "cogs.desabafos_pesquisa",
            "cogs.ship",
            "cogs.economia",
            "cogs.pokemon",
            "cogs.update_logger",

            # ------------------------------------------------
            # ADMIN
            # ------------------------------------------------

            "cogs.admin",
        ]

        carregados = 0

        falhas = 0

        # ====================================================
        # CARREGAR COGS
        # ====================================================

        for extensao in extensoes:

            try:

                await self.load_extension(
                    extensao
                )

                carregados += 1

                print(
                    f"✅ {extensao}"
                )

            except Exception as erro:

                falhas += 1

                print(
                    f"❌ {extensao}"
                )

                print(
                    f"   ↳ {type(erro).__name__}: {erro}"
                )

        print(
            "\n" + "-" * 64
        )

        print(
            f"📦 Cogs carregados: {carregados}"
        )

        print(
            f"⚠️ Cogs com erro: {falhas}"
        )

        print(
            "-" * 64
        )

        # ====================================================
        # SLASH COMMANDS
        # ====================================================
        #
        # IMPORTANTE:
        #
        # Não fazemos sync global toda vez que o arquivo é
        # alterado.
        #
        # O bot reinicia pelo Watchdog e isso poderia causar:
        #
        # PUT /applications/.../commands
        #
        # repetidamente, gerando erro 429.
        #
        # ====================================================

        print(
            "🌐 Slash commands carregados na árvore."
        )

        print(
            f"📌 Comandos locais registrados: "
            f"{len(self.tree.get_commands())}"
        )

        print(
            "=" * 64
        )

    # ========================================================
    # READY
    # ========================================================

    async def on_ready(self):

        print(
            "\n" + "=" * 64
        )

        print(
            "👑 ROYALT ONLINE"
        )

        print(
            "=" * 64
        )

        print(
            f"🤖 Usuário: {self.user}"
        )

        print(
            f"🆔 ID: {self.user.id}"
        )

        print(
            f"🌐 Servidores: {len(self.guilds)}"
        )

        print(
            f"📦 Cogs carregados: {len(self.cogs)}"
        )

        print(
            f"⚡ Slash commands: "
            f"{len(self.tree.get_commands())}"
        )

        print(
            "=" * 64
        )

        # ----------------------------------------------------
        # Iniciar auto-reload uma única vez
        # ----------------------------------------------------

        if not self.monitorando:

            self.iniciar_monitoramento()

            self.monitorando = True

            print(
                "👀 Auto-reload ativado."
            )

            print(
                "💾 Salve um arquivo .py "
                "para reiniciar automaticamente."
            )

    # ========================================================
    # INICIAR MONITORAMENTO
    # ========================================================

    def iniciar_monitoramento(self):

        if self.observer is not None:
            return

        handler = CodigoAlteradoHandler()

        observer = Observer()

        self.observer = observer

        observer.schedule(
            handler,
            str(BASE_DIR),
            recursive=True
        )

        observer.start()

        asyncio.create_task(
            self.monitorar_reinicio()
        )

    # ========================================================
    # MONITORAR REINÍCIO
    # ========================================================

    async def monitorar_reinicio(self):

        while not self.is_closed():

            if REINICIAR_EVENTO.is_set():

                if self.reinicio_iniciado:

                    await asyncio.sleep(
                        0.5
                    )

                    continue

                self.reinicio_iniciado = True

                REINICIAR_EVENTO.clear()

                print(
                    "\n" + "=" * 64
                )

                print(
                    "🛑 ENCERRANDO ROYALT"
                )

                print(
                    "♻️ Reinício automático iniciado..."
                )

                print(
                    "=" * 64
                )

                # ------------------------------------------------
                # Parar Watchdog
                # ------------------------------------------------

                if self.observer is not None:

                    try:

                        self.observer.stop()

                        self.observer.join(
                            timeout=3
                        )

                    except Exception as erro:

                        print(
                            "⚠️ Erro encerrando Watchdog: "
                            f"{erro}"
                        )

                    self.observer = None

                # ------------------------------------------------
                # Fechar Discord
                # ------------------------------------------------

                try:

                    await self.close()

                except Exception as erro:

                    print(
                        "⚠️ Erro fechando Royalt: "
                        f"{erro}"
                    )

                # ------------------------------------------------
                # Aguardar um pouco
                # ------------------------------------------------

                await asyncio.sleep(
                    1
                )

                print(
                    "♻️ Reiniciando processo Python..."
                )

                print(
                    "=" * 64
                )

                # ------------------------------------------------
                # Reiniciar processo
                # ------------------------------------------------

                try:

                    os.execv(
                        sys.executable,
                        [
                            sys.executable,
                            *sys.argv
                        ]
                    )

                except Exception as erro:

                    print(
                        "💥 Não foi possível "
                        "reiniciar o processo:"
                    )

                    print(
                        f"{type(erro).__name__}: {erro}"
                    )

                    self.reinicio_iniciado = False

                    return

                return

            await asyncio.sleep(
                0.5
            )

    # ========================================================
    # FECHAR
    # ========================================================

    async def close(self):

        # ----------------------------------------------------
        # Parar Watchdog
        # ----------------------------------------------------

        if self.observer is not None:

            try:

                self.observer.stop()

                self.observer.join(
                    timeout=3
                )

            except Exception as erro:

                print(
                    "⚠️ Erro encerrando Watchdog: "
                    f"{erro}"
                )

            self.observer = None

        # ----------------------------------------------------
        # Fechar Discord
        # ----------------------------------------------------

        await super().close()


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print(
        "=" * 64
    )

    print(
        "👑 ROYALT • MODO DESENVOLVIMENTO"
    )

    print(
        "=" * 64
    )

    print(
        f"📂 Projeto: {BASE_DIR}"
    )

    print(
        f"📦 Cogs: {COGS_DIR}"
    )

    print(
        f"📄 .env: {ARQUIVO_ENV}"
    )

    print(
        f"🔐 .env encontrado: "
        f"{'SIM' if ARQUIVO_ENV.exists() else 'NÃO'}"
    )

    print(
        "💾 Salve qualquer arquivo .py "
        "para reiniciar automaticamente."
    )

    print(
        "=" * 64
    )

    # ========================================================
    # VERIFICAR TOKEN
    # ========================================================

    if not TOKEN:

        print(
            "\n❌ DISCORD_TOKEN não foi configurado."
        )

        print(
            "\n📄 Arquivo esperado:"
        )

        print(
            f"{ARQUIVO_ENV}"
        )

        print(
            "\n📝 O arquivo .env precisa conter:"
        )

        print(
            "DISCORD_TOKEN=SEU_NOVO_TOKEN"
        )

        print(
            "\n⚠️ Não coloque o token diretamente "
            "neste arquivo."
        )

        return

    print(
        "✅ Token carregado do .env."
    )

    # ========================================================
    # CRIAR BOT
    # ========================================================

    bot = Royalt()

    # ========================================================
    # EXECUTAR
    # ========================================================

    try:

        bot.run(
            TOKEN
        )

    except KeyboardInterrupt:

        print(
            "\n🛑 Royalt encerrado manualmente."
        )

    except discord.LoginFailure:

        print(
            "\n❌ Falha de login no Discord."
        )

        print(
            "🔐 Verifique se o token informado "
            "é válido."
        )

    except Exception as erro:

        print(
            "\n💥 O Royalt encontrou um erro:"
        )

        print(
            f"{type(erro).__name__}: {erro}"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()