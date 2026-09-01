import discord
from discord.ext import commands

from datetime import datetime, timezone
from pathlib import Path
import json


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_DATA = Path("data")
ARQUIVO_LOGS = PASTA_DATA / "logs.json"

COR_LOGS = discord.Color.from_rgb(128, 0, 255)

NOME_FOOTER = "Royalt Logging System"


# ============================================================
# GARANTIR PASTA
# ============================================================

PASTA_DATA.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FUNÇÕES DE DATA
# ============================================================

def agora():
    return datetime.now(timezone.utc)


# ============================================================
# PAINEL DE LOGS
# ============================================================

class LogsView(discord.ui.View):

    def __init__(self, cog, autor):

        super().__init__(
            timeout=180
        )

        self.cog = cog
        self.autor = autor

    # ========================================================
    # VERIFICAR USUÁRIO
    # ========================================================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.autor.id:

            await interaction.response.send_message(
                "❌ Apenas quem abriu este painel "
                "pode utilizar os botões.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # PAINEL PRINCIPAL
    # ========================================================

    def painel(self):

        guild = self.autor.guild

        canal = self.cog.obter_canal_logs(
            guild
        )

        if canal:

            canal_texto = canal.mention

            status = (
                "🟢 **Sistema configurado**\n"
                f"📁 Canal: {canal_texto}"
            )

        else:

            status = (
                "🔴 **Sistema não configurado**\n"
                "Nenhum canal de logs foi definido."
            )

        embed = discord.Embed(
            title="👑 ROYALT • SISTEMA DE LOGS",
            description=(
                "Configure o sistema de registros do Royalt "
                "para este servidor.\n\n"
                f"{status}\n\n"
                "Os logs podem registrar eventos como:\n\n"
                "👤 Entrada e saída de membros\n"
                "💬 Mensagens apagadas/editadas\n"
                "🎭 Alterações de cargos\n"
                "🤖 Entrada de bots\n"
                "🛡️ Ações de moderação\n"
                "⚠️ Advertências"
            ),
            color=COR_LOGS,
            timestamp=agora()
        )

        embed.set_footer(
            text=NOME_FOOTER
        )

        return embed

    # ========================================================
    # BOTÃO CONFIGURAR
    # ========================================================

    @discord.ui.button(
        label="Configurar",
        emoji="⚙️",
        style=discord.ButtonStyle.primary
    )
    async def configurar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="⚙️ CONFIGURAR LOGS",
            description=(
                "Para configurar o canal de logs, utilize:\n\n"
                "`!setlogs #canal`\n\n"
                "Exemplo:\n"
                "`!setlogs #logs-servidor`\n\n"
                "Depois de configurar, todas as funções "
                "do sistema passarão a utilizar o canal escolhido."
            ),
            color=COR_LOGS
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # BOTÃO TESTAR
    # ========================================================

    @discord.ui.button(
        label="Testar",
        emoji="🧪",
        style=discord.ButtonStyle.success
    )
    async def testar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        canal = self.cog.obter_canal_logs(
            interaction.guild
        )

        if canal is None:

            await interaction.response.send_message(
                "❌ Nenhum canal de logs foi configurado.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="🧪 TESTE DO SISTEMA DE LOGS",
            description=(
                "✅ O sistema de logs do Royalt "
                "está funcionando corretamente!\n\n"
                f"👑 **Administrador:** "
                f"{interaction.user.mention}\n"
                f"📁 **Canal:** {canal.mention}"
            ),
            color=COR_LOGS,
            timestamp=agora()
        )

        embed.set_footer(
            text=NOME_FOOTER
        )

        try:

            await canal.send(
                embed=embed
            )

            await interaction.response.send_message(
                f"✅ Teste enviado para {canal.mention}.",
                ephemeral=True
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Não tenho permissão para enviar "
                "mensagens nesse canal.",
                ephemeral=True
            )

    # ========================================================
    # BOTÃO REMOVER
    # ========================================================

    @discord.ui.button(
        label="Remover",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def remover(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild_id = str(
            interaction.guild.id
        )

        if guild_id not in self.cog.configuracoes:

            await interaction.response.send_message(
                "❌ Este servidor não possui "
                "um canal de logs configurado.",
                ephemeral=True
            )

            return

        del self.cog.configuracoes[
            guild_id
        ]

        self.cog.salvar_configuracoes()

        await interaction.response.edit_message(
            embed=self.painel(),
            view=self
        )

        await interaction.followup.send(
            "🗑️ Canal de logs removido com sucesso.",
            ephemeral=True
        )

    # ========================================================
    # BOTÃO ATUALIZAR
    # ========================================================

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.secondary
    )
    async def atualizar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=self.painel(),
            view=self
        )


# ============================================================
# COG LOGS
# ============================================================

class Logs(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.configuracoes = {}

        self.carregar_configuracoes()

    # ========================================================
    # CARREGAR CONFIGURAÇÕES
    # ========================================================

    def carregar_configuracoes(self):

        if not ARQUIVO_LOGS.exists():

            self.configuracoes = {}

            self.salvar_configuracoes()

            return

        try:

            with open(
                ARQUIVO_LOGS,
                "r",
                encoding="utf-8"
            ) as arquivo:

                self.configuracoes = json.load(
                    arquivo
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            print(
                "[LOGS] Não foi possível carregar "
                "logs.json."
            )

            self.configuracoes = {}

    # ========================================================
    # SALVAR CONFIGURAÇÕES
    # ========================================================

    def salvar_configuracoes(self):

        try:

            with open(
                ARQUIVO_LOGS,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    self.configuracoes,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError as erro:

            print(
                f"[LOGS] Erro ao salvar configurações: {erro}"
            )

    # ========================================================
    # OBTER CANAL
    # ========================================================

    def obter_canal_logs(
        self,
        guild
    ):

        if guild is None:
            return None

        guild_id = str(
            guild.id
        )

        canal_id = self.configuracoes.get(
            guild_id
        )

        if canal_id is None:
            return None

        try:

            canal_id = int(
                canal_id
            )

        except (
            ValueError,
            TypeError
        ):

            return None

        canal = guild.get_channel(
            canal_id
        )

        if isinstance(
            canal,
            discord.TextChannel
        ):

            return canal

        return None

    # ========================================================
    # ENVIAR LOG
    # ========================================================

    async def enviar_log(
        self,
        guild,
        titulo,
        descricao,
        emoji="📜",
        cor=COR_LOGS
    ):

        if guild is None:
            return

        canal = self.obter_canal_logs(
            guild
        )

        if canal is None:
            return

        embed = discord.Embed(
            title=f"{emoji} {titulo}",
            description=descricao,
            color=cor,
            timestamp=agora()
        )

        embed.set_footer(
            text=NOME_FOOTER
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                f"[LOGS] Sem permissão para enviar "
                f"mensagens em {canal.name}."
            )

        except discord.HTTPException as erro:

            print(
                f"[LOGS] Erro ao enviar log: {erro}"
            )

    # ========================================================
    # SETLOGS
    # ========================================================

    @commands.hybrid_command(
        name="setlogs",
        description="Define o canal onde os logs serão enviados."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    @commands.bot_has_permissions(
        send_messages=True,
        embed_links=True
    )
    async def setlogs(
        self,
        ctx,
        canal: discord.TextChannel
    ):

        self.configuracoes[
            str(ctx.guild.id)
        ] = canal.id

        self.salvar_configuracoes()

        embed = discord.Embed(
            title="✅ CANAL DE LOGS CONFIGURADO",
            description=(
                "O sistema de logs do Royalt "
                "foi configurado com sucesso.\n\n"
                f"📁 **Canal:** {canal.mention}\n"
                f"🛡️ **Configurado por:** "
                f"{ctx.author.mention}"
            ),
            color=discord.Color.green(),
            timestamp=agora()
        )

        embed.set_footer(
            text=NOME_FOOTER
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Canal de logs configurado",
            (
                f"📁 **Canal:** {canal.mention}\n"
                f"🛡️ **Administrador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{canal.id}`"
            ),
            "⚙️",
            discord.Color.green()
        )

    # ========================================================
    # PAINEL
    # ========================================================

    @commands.hybrid_command(
        name="logs",
        description="Abre o painel de configuração dos logs."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def logs(
        self,
        ctx
    ):

        view = LogsView(
            self,
            ctx.author
        )

        await ctx.send(
            embed=view.painel(),
            view=view
        )

    # ========================================================
    # TESTLOG
    # ========================================================

    @commands.hybrid_command(
        name="testlog",
        description="Testa o sistema de logs."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def testlog(
        self,
        ctx
    ):

        canal = self.obter_canal_logs(
            ctx.guild
        )

        if canal is None:

            await ctx.send(
                "❌ Nenhum canal de logs foi configurado.\n\n"
                "Use `!setlogs #canal` primeiro."
            )

            return

        embed = discord.Embed(
            title="🧪 TESTE DO SISTEMA DE LOGS",
            description=(
                "✅ O sistema de logs está funcionando!\n\n"
                f"👑 **Administrador:** "
                f"{ctx.author.mention}\n"
                f"📁 **Canal:** {canal.mention}"
            ),
            color=COR_LOGS,
            timestamp=agora()
        )

        embed.set_footer(
            text=NOME_FOOTER
        )

        try:

            await canal.send(
                embed=embed
            )

            await ctx.send(
                f"✅ Teste enviado para {canal.mention}."
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para enviar "
                "mensagens nesse canal."
            )

    # ========================================================
    # MEMBRO ENTROU
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        await self.enviar_log(
            member.guild,
            "Membro entrou",
            (
                f"👤 **Usuário:** {member.mention}\n"
                f"📝 **Nome:** `{member}`\n"
                f"🆔 **ID:** `{member.id}`\n"
                f"🤖 **Bot:** "
                f"{'Sim' if member.bot else 'Não'}"
            ),
            "📥",
            discord.Color.green()
        )

    # ========================================================
    # MEMBRO SAIU
    # ========================================================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):

        await self.enviar_log(
            member.guild,
            "Membro saiu",
            (
                f"👤 **Usuário:** `{member}`\n"
                f"🆔 **ID:** `{member.id}`"
            ),
            "📤",
            discord.Color.orange()
        )

    # ========================================================
    # ALTERAÇÃO DE CARGOS
    # ========================================================

    @commands.Cog.listener()
    async def on_member_update(
        self,
        antes,
        depois
    ):

        cargos_antes = {
            cargo.id
            for cargo in antes.roles
        }

        cargos_depois = {
            cargo.id
            for cargo in depois.roles
        }

        adicionados = (
            cargos_depois
            - cargos_antes
        )

        removidos = (
            cargos_antes
            - cargos_depois
        )

        # ----------------------------------------------------
        # CARGOS ADICIONADOS
        # ----------------------------------------------------

        if adicionados:

            nomes = []

            for cargo in depois.roles:

                if cargo.id in adicionados:

                    nomes.append(
                        cargo.name
                    )

            await self.enviar_log(
                depois.guild,
                "Cargo adicionado",
                (
                    f"👤 **Usuário:** "
                    f"{depois.mention}\n"
                    f"🎭 **Cargo(s):** "
                    f"{', '.join(nomes)}"
                ),
                "🎭",
                discord.Color.green()
            )

        # ----------------------------------------------------
        # CARGOS REMOVIDOS
        # ----------------------------------------------------

        if removidos:

            nomes = []

            for cargo in antes.roles:

                if cargo.id in removidos:

                    nomes.append(
                        cargo.name
                    )

            await self.enviar_log(
                depois.guild,
                "Cargo removido",
                (
                    f"👤 **Usuário:** "
                    f"{depois.mention}\n"
                    f"🎭 **Cargo(s):** "
                    f"{', '.join(nomes)}"
                ),
                "🎭",
                discord.Color.red()
            )

    # ========================================================
    # MENSAGEM APAGADA
    # ========================================================

    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message
    ):

        if message.author.bot:
            return

        if message.guild is None:
            return

        conteudo = message.content

        if not conteudo:

            conteudo = (
                "*Mensagem sem texto ou "
                "conteúdo não disponível.*"
            )

        await self.enviar_log(
            message.guild,
            "Mensagem apagada",
            (
                f"👤 **Autor:** "
                f"{message.author.mention}\n"
                f"🆔 **ID:** `{message.author.id}`\n"
                f"📍 **Canal:** "
                f"{message.channel.mention}\n\n"
                f"💬 **Conteúdo:**\n"
                f"```{conteudo[:1500]}```"
            ),
            "🗑️",
            discord.Color.red()
        )

    # ========================================================
    # MENSAGEM EDITADA
    # ========================================================

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        antes,
        depois
    ):

        if antes.author.bot:
            return

        if antes.guild is None:
            return

        if antes.content == depois.content:
            return

        await self.enviar_log(
            antes.guild,
            "Mensagem editada",
            (
                f"👤 **Autor:** "
                f"{antes.author.mention}\n"
                f"🆔 **ID:** `{antes.author.id}`\n"
                f"📍 **Canal:** "
                f"{antes.channel.mention}\n\n"
                f"📝 **Antes:**\n"
                f"```{antes.content[:700]}```\n\n"
                f"📝 **Depois:**\n"
                f"```{depois.content[:700]}```"
            ),
            "✏️",
            discord.Color.orange()
        )

    # ========================================================
    # BOT ENTRANDO
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join_bot(
        self,
        member
    ):

        if not member.bot:
            return

        await self.enviar_log(
            member.guild,
            "Bot detectado",
            (
                f"🤖 **Bot:** {member.mention}\n"
                f"🆔 **ID:** `{member.id}`\n\n"
                f"⚠️ O Royalt registrou a entrada "
                f"deste bot no servidor."
            ),
            "🤖",
            discord.Color.blurple()
        )


# ============================================================
# CARREGAMENTO DA COG
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Logs(bot)
    )