import os

from pathlib import Path

import discord
from discord.ext import commands

from dotenv import load_dotenv


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
            "cogs.bot_status",
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

    # ========================================================
    # FECHAR
    # ========================================================

    async def close(self):

        await super().close()


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print(
        "=" * 64
    )

    print(
        "👑 ROYALT • MODO PRODUÇÃO"
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
        "✅ DISCORD_TOKEN encontrado nas variáveis de ambiente."
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