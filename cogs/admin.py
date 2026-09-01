# ============================================================
# AIRA • ADMIN
# ============================================================
# Painel administrativo principal da Aira
#
# Acesso:
#   !admin
#
# Somente:
#   • Dono do servidor
#   • Owner da Aira
#
# Configurações:
#   • Canais
#   • Cargos autorizados
#   • Membros autorizados
#
# Sistemas:
#   • Updates
#   • Update Logger
#   • Sorteios
#   • Tickets
#   • Desabafos
#   • Desabafos Config
#   • Desabafos Pesquisa
#   • Moderation
#
# ============================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

CONFIG_FILE = DATA_DIR / "admin_config.json"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# OWNER DA AIRA
# ============================================================

AIRA_OWNER_ID = 1527022875444379751


# ============================================================
# CONFIGURAÇÃO PADRÃO
# ============================================================

CONFIG_PADRAO = {
    "guilds": {}
}


# ============================================================
# EMBED BASE
# ============================================================

def embed_base(
    titulo: str,
    descricao: str,
    cor: discord.Color = discord.Color.blurple()
) -> discord.Embed:

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor
    )

    embed.set_footer(
        text="Aira • Painel Administrativo"
    )

    return embed


# ============================================================
# ADMIN
# ============================================================

class Admin(commands.Cog):

    def __init__(
        self,
        bot: commands.Bot
    ):

        self.bot = bot

        self.config = self.carregar_config()

        print(
            "✅ Aira Admin carregado."
        )


    # ========================================================
    # CARREGAR CONFIGURAÇÃO
    # ========================================================

    def carregar_config(self) -> dict:

        if not CONFIG_FILE.exists():

            dados = {
                "guilds": {}
            }

            self.config = dados

            self.salvar_config()

            return dados

        try:

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(
                    arquivo
                )

            if not isinstance(
                dados,
                dict
            ):

                return {
                    "guilds": {}
                }

            dados.setdefault(
                "guilds",
                {}
            )

            return dados

        except Exception as erro:

            print(
                f"⚠️ [ADMIN] Erro carregando configuração: {erro}"
            )

            return {
                "guilds": {}
            }


    # ========================================================
    # SALVAR CONFIGURAÇÃO
    # ========================================================

    def salvar_config(
        self,
        dados: Optional[dict] = None
    ) -> None:

        if dados is not None:

            self.config = dados

        try:

            with open(
                CONFIG_FILE,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    self.config,
                    arquivo,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as erro:

            print(
                f"⚠️ [ADMIN] Erro salvando configuração: {erro}"
            )


    # ========================================================
    # CONFIGURAÇÃO DO SERVIDOR
    # ========================================================

    def config_guild(
        self,
        guild_id: int
    ) -> dict:

        guilds = self.config.setdefault(
            "guilds",
            {}
        )

        guild = guilds.setdefault(
            str(guild_id),
            {}
        )

        guild.setdefault(
            "canais",
            {}
        )

        guild.setdefault(
            "permissoes",
            {}
        )

        return guild


    # ========================================================
    # CONFIGURAÇÃO DO SISTEMA
    # ========================================================

    def config_sistema(
        self,
        guild_id: int,
        sistema: str
    ) -> dict:

        guild = self.config_guild(
            guild_id
        )

        permissoes = guild.setdefault(
            "permissoes",
            {}
        )

        sistema_config = permissoes.setdefault(
            sistema,
            {}
        )

        sistema_config.setdefault(
            "roles",
            []
        )

        sistema_config.setdefault(
            "users",
            []
        )

        return sistema_config


    # ========================================================
    # OWNER DA AIRA
    # ========================================================

    async def eh_owner_aira(
        self,
        user: discord.abc.User
    ) -> bool:

        # Seu ID
        if user.id == AIRA_OWNER_ID:

            return True

        # Owner configurado no bot
        try:

            if await self.bot.is_owner(
                user
            ):

                return True

        except Exception:
            pass

        return False


    # ========================================================
    # DONO DO SERVIDOR
    # ========================================================

    def eh_dono_servidor(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if not interaction.guild:

            return False

        return (
            interaction.guild.owner_id
            == interaction.user.id
        )


    # ========================================================
    # AUTORIZAÇÃO DE INTERAÇÃO
    # ========================================================

    async def usuario_autorizado(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if not interaction.guild:

            return False

        # Dono do servidor
        if self.eh_dono_servidor(
            interaction
        ):

            return True

        # Owner da Aira
        if await self.eh_owner_aira(
            interaction.user
        ):

            return True

        return False


    # ========================================================
    # AUTORIZAÇÃO DO !ADMIN
    # ========================================================

    async def membro_autorizado(
        self,
        ctx: commands.Context
    ) -> bool:

        if not ctx.guild:

            return False

        # Dono do servidor
        if ctx.guild.owner_id == ctx.author.id:

            return True

        # Owner da Aira
        if await self.eh_owner_aira(
            ctx.author
        ):

            return True

        return False


    # ========================================================
    # NOME DOS SISTEMAS
    # ========================================================

    def nome_sistema(
        self,
        sistema: str
    ) -> tuple[str, str]:

        sistemas = {

            "updates": (
                "🛠️ Updates",
                "Gerenciamento das atualizações da Aira."
            ),

            "update_logger": (
                "📋 Update Logger",
                "Gerenciamento do registro automático de atualizações."
            ),

            "sorteios": (
                "🎉 Sorteios",
                "Gerenciamento do sistema de sorteios."
            ),

            "tickets": (
                "🎫 Tickets",
                "Gerenciamento do sistema de tickets."
            ),

            "desabafos": (
                "💭 Desabafos",
                "Gerenciamento do sistema de desabafos."
            ),

            "desabafos_config": (
                "⚙️ Desabafos Config",
                "Configurações administrativas dos desabafos."
            ),

            "desabafos_pesquisa": (
                "🔎 Desabafos Pesquisa",
                "Pesquisa e consulta dos desabafos."
            ),

            "moderation": (
                "🛡️ Moderation",
                "Gerenciamento das funções de moderação."
            )
        }

        return sistemas.get(
            sistema,
            (
                "📦 Sistema",
                "Configuração do sistema."
            )
        )


    # ========================================================
    # EMBED PRINCIPAL
    # ========================================================

    def criar_embed_principal(
        self,
        guild: Optional[discord.Guild]
    ) -> discord.Embed:

        nome_servidor = (
            guild.name
            if guild
            else "Servidor"
        )

        embed = embed_base(
            "⚙️ AIRA • PAINEL ADMINISTRATIVO",
            (
                "Configure e consulte os sistemas da Aira "
                "para este servidor.\n\n"

                "🔐 **Acesso**\n"
                "Somente o **dono do servidor** e o "
                "**owner da Aira** podem administrar este painel.\n\n"

                "📚 **Sistemas disponíveis**\n"
                "Selecione um sistema abaixo para visualizar "
                "e configurar suas opções.\n\n"

                "💡 **Como usar**\n"
                "Selecione um sistema no menu abaixo."
            ),
            discord.Color.blurple()
        )

        embed.add_field(
            name="👑 Servidor",
            value=f"**{nome_servidor}**",
            inline=True
        )

        embed.add_field(
            name="🔐 Permissão",
            value=(
                "Dono do servidor\n"
                "+ Owner da Aira"
            ),
            inline=True
        )

        embed.add_field(
            name="🛠️ O que pode ser configurado?",
            value=(
                "📢 Canais dos sistemas\n"
                "👥 Cargos da Staff\n"
                "👤 Membros autorizados\n"
                "🔐 Permissões específicas"
            ),
            inline=False
        )

        return embed


    # ========================================================
    # EMBED DO SISTEMA
    # ========================================================

    def criar_embed_sistema(
        self,
        guild: discord.Guild,
        sistema: str
    ) -> discord.Embed:

        titulo, descricao = self.nome_sistema(
            sistema
        )

        guild_config = self.config_guild(
            guild.id
        )

        canais = guild_config.get(
            "canais",
            {}
        )

        permissoes = guild_config.get(
            "permissoes",
            {}
        )

        config_sistema = permissoes.get(
            sistema,
            {}
        )

        # ====================================================
        # CANAL
        # ====================================================

        canal_id = canais.get(
            sistema
        )

        if canal_id:

            canal = guild.get_channel(
                canal_id
            )

            if canal:

                canal_texto = canal.mention

            else:

                canal_texto = (
                    f"`{canal_id}`\n"
                    "⚠️ Canal não encontrado."
                )

        else:

            canal_texto = (
                "❌ Nenhum canal configurado."
            )

        # ====================================================
        # CARGOS
        # ====================================================

        cargos = config_sistema.get(
            "roles",
            []
        )

        lista_cargos = []

        for role_id in cargos:

            role = guild.get_role(
                role_id
            )

            if role:

                lista_cargos.append(
                    role.mention
                )

        if lista_cargos:

            cargos_texto = "\n".join(
                lista_cargos
            )

        else:

            cargos_texto = (
                "❌ Nenhum cargo configurado."
            )

        # ====================================================
        # MEMBROS
        # ====================================================

        membros = config_sistema.get(
            "users",
            []
        )

        lista_membros = []

        for user_id in membros:

            membro = guild.get_member(
                user_id
            )

            if membro:

                lista_membros.append(
                    membro.mention
                )

        if lista_membros:

            membros_texto = "\n".join(
                lista_membros
            )

        else:

            membros_texto = (
                "❌ Nenhum membro configurado."
            )

        # ====================================================
        # EMBED
        # ====================================================

        embed = embed_base(
            titulo,
            (
                f"{descricao}\n\n"
                "Configure abaixo quem pode utilizar "
                "as funções administrativas deste sistema."
            )
        )

        embed.add_field(
            name="📢 Canal",
            value=canal_texto,
            inline=False
        )

        embed.add_field(
            name="👥 Cargos Staff",
            value=cargos_texto,
            inline=False
        )

        embed.add_field(
            name="👤 Membros autorizados",
            value=membros_texto,
            inline=False
        )

        embed.add_field(
            name="🔐 Como funciona",
            value=(
                "Os cargos e membros definidos aqui poderão "
                "ser utilizados pelos respectivos cogs como "
                "permissões administrativas do sistema."
            ),
            inline=False
        )

        return embed


    # ========================================================
    # EMBED AJUDA
    # ========================================================

    def criar_embed_ajuda(self) -> discord.Embed:

        return embed_base(
            "❓ AIRA • AJUDA",
            (
                "Este painel controla as configurações "
                "administrativas dos sistemas da Aira.\n\n"

                "👑 **Quem pode abrir?**\n"
                "• Dono do servidor\n"
                "• Owner da Aira\n\n"

                "📢 **Configurar Canal**\n"
                "Define o canal utilizado pelo sistema.\n\n"

                "👥 **Cargos Staff**\n"
                "Define quais cargos possuem autorização "
                "para as funções administrativas daquele sistema.\n\n"

                "👤 **Membros**\n"
                "Permite adicionar pessoas específicas à Staff "
                "do sistema.\n\n"

                "🛠️ **Importante**\n"
                "Cada sistema poderá consultar estas configurações "
                "para decidir quem possui acesso às suas funções."
            )
        )


    # ========================================================
    # !ADMIN
    # ========================================================

    @commands.command(
        name="admin"
    )
    async def admin(
        self,
        ctx: commands.Context
    ):

        if not await self.membro_autorizado(
            ctx
        ):

            await ctx.send(
                "❌ Somente o **dono do servidor** ou o "
                "**owner da Aira** pode abrir o painel administrativo."
            )

            return

        embed = self.criar_embed_principal(
            ctx.guild
        )

        await ctx.send(
            embed=embed,
            view=AdminPrincipalView(
                self
            )
        )


# ============================================================
# VIEW PRINCIPAL
# ============================================================

class AdminPrincipalView(
    discord.ui.View
):

    def __init__(
        self,
        cog: Admin
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog

        self.add_item(
            AdminSistemaSelect(
                cog
            )
        )


    # ========================================================
    # AJUDA
    # ========================================================

    @discord.ui.button(
        label="Ajuda",
        emoji="❓",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def ajuda(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_ajuda(),
            view=AdminAjudaView(
                self.cog
            )
        )


    # ========================================================
    # FECHAR
    # ========================================================

    @discord.ui.button(
        label="Fechar",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def fechar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        for item in self.children:

            item.disabled = True

        await interaction.response.edit_message(
            content="🔒 Painel administrativo fechado.",
            embed=None,
            view=self
        )


# ============================================================
# SELECT DE SISTEMAS
# ============================================================

class AdminSistemaSelect(
    discord.ui.Select
):

    def __init__(
        self,
        cog: Admin
    ):

        self.cog = cog

        options = [

            discord.SelectOption(
                label="Updates",
                value="updates",
                emoji="🛠️",
                description="Gerenciamento das atualizações."
            ),

            discord.SelectOption(
                label="Update Logger",
                value="update_logger",
                emoji="📋",
                description="Registro automático das atualizações."
            ),

            discord.SelectOption(
                label="Sorteios",
                value="sorteios",
                emoji="🎉",
                description="Configuração dos sorteios."
            ),

            discord.SelectOption(
                label="Tickets",
                value="tickets",
                emoji="🎫",
                description="Configuração do sistema de tickets."
            ),

            discord.SelectOption(
                label="Desabafos",
                value="desabafos",
                emoji="💭",
                description="Configuração dos desabafos."
            ),

            discord.SelectOption(
                label="Desabafos Config",
                value="desabafos_config",
                emoji="⚙️",
                description="Configurações administrativas."
            ),

            discord.SelectOption(
                label="Desabafos Pesquisa",
                value="desabafos_pesquisa",
                emoji="🔎",
                description="Pesquisa dos desabafos."
            ),

            discord.SelectOption(
                label="Moderation",
                value="moderation",
                emoji="🛡️",
                description="Funções de moderação."
            )
        ]

        super().__init__(
            placeholder="📚 Selecione um sistema para configurar...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        sistema = self.values[0]

        embed = self.cog.criar_embed_sistema(
            interaction.guild,
            sistema
        )

        await interaction.response.edit_message(
            embed=embed,
            view=AdminSistemaView(
                self.cog,
                sistema
            )
        )


# ============================================================
# VIEW DO SISTEMA
# ============================================================

class AdminSistemaView(
    discord.ui.View
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog
        self.sistema = sistema


    # ========================================================
    # CONFIGURAR CANAL
    # ========================================================

    @discord.ui.button(
        label="Configurar Canal",
        emoji="📢",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def configurar_canal(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=embed_base(
                "📢 Configurar Canal",
                (
                    f"Escolha o canal que será utilizado pelo sistema "
                    f"**{self.sistema}**.\n\n"
                    "Selecione um canal abaixo."
                )
            ),
            view=AdminCanalView(
                self.cog,
                self.sistema
            )
        )


    # ========================================================
    # CARGOS STAFF
    # ========================================================

    @discord.ui.button(
        label="Cargos Staff",
        emoji="👥",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def cargos(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=embed_base(
                "👥 Cargos Staff",
                (
                    f"Selecione os cargos que terão acesso às "
                    f"funções administrativas de **{self.sistema}**.\n\n"
                    "Você pode selecionar mais de um cargo."
                )
            ),
            view=AdminCargosView(
                self.cog,
                self.sistema
            )
        )


    # ========================================================
    # MEMBROS
    # ========================================================

    @discord.ui.button(
        label="Membros",
        emoji="👤",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def membros(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=embed_base(
                "👤 Membros Autorizados",
                (
                    f"Selecione os membros que terão acesso às "
                    f"funções administrativas de **{self.sistema}**.\n\n"
                    "Você pode selecionar mais de uma pessoa."
                )
            ),
            view=AdminMembrosView(
                self.cog,
                self.sistema
            )
        )


    # ========================================================
    # VER CONFIGURAÇÃO
    # ========================================================

    @discord.ui.button(
        label="Ver Config",
        emoji="🔎",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def ver_config(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_sistema(
                interaction.guild,
                self.sistema
            ),
            view=self
        )


    # ========================================================
    # VOLTAR
    # ========================================================

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_principal(
                interaction.guild
            ),
            view=AdminPrincipalView(
                self.cog
            )
        )


# ============================================================
# VIEW CONFIGURAR CANAL
# ============================================================

class AdminCanalView(
    discord.ui.View
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog
        self.sistema = sistema

        # ====================================================
        # SELECT REAL DE CANAIS
        # ====================================================

        self.add_item(
            AdminCanalSelect(
                cog,
                sistema
            )
        )


    # ========================================================
    # LIMPAR CANAL
    # ========================================================

    @discord.ui.button(
        label="Limpar Canal",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def limpar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        guild_config = self.cog.config_guild(
            interaction.guild.id
        )

        guild_config["canais"].pop(
            self.sistema,
            None
        )

        self.cog.salvar_config()

        await interaction.response.edit_message(
            embed=embed_base(
                "✅ Canal removido",
                (
                    f"O canal configurado para "
                    f"**{self.sistema}** foi removido."
                ),
                discord.Color.green()
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


    # ========================================================
    # VOLTAR
    # ========================================================

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_sistema(
                interaction.guild,
                self.sistema
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


# ============================================================
# SELECT REAL DE CANAIS
# ============================================================

class AdminCanalSelect(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        self.cog = cog
        self.sistema = sistema

        super().__init__(
            placeholder="📢 Selecione o canal...",
            min_values=1,
            max_values=1,
            channel_types=[
                discord.ChannelType.text
            ],
            row=0
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        canal = self.values[0]

        guild_config = self.cog.config_guild(
            interaction.guild.id
        )

        guild_config["canais"][
            self.sistema
        ] = canal.id

        self.cog.salvar_config()

        await interaction.response.edit_message(
            embed=embed_base(
                "✅ Canal configurado",
                (
                    f"**Sistema:** `{self.sistema}`\n"
                    f"**Canal:** {canal.mention}\n\n"
                    "O canal foi salvo com sucesso."
                ),
                discord.Color.green()
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


# ============================================================
# VIEW CARGOS
# ============================================================

class AdminCargosView(
    discord.ui.View
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog
        self.sistema = sistema

        self.add_item(
            AdminCargoSelect(
                cog,
                sistema
            )
        )


    # ========================================================
    # LIMPAR CARGOS
    # ========================================================

    @discord.ui.button(
        label="Limpar Cargos",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def limpar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        config = self.cog.config_sistema(
            interaction.guild.id,
            self.sistema
        )

        config["roles"] = []

        self.cog.salvar_config()

        await interaction.response.edit_message(
            embed=embed_base(
                "✅ Cargos removidos",
                (
                    f"Todos os cargos autorizados de "
                    f"**{self.sistema}** foram removidos."
                ),
                discord.Color.green()
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


    # ========================================================
    # VOLTAR
    # ========================================================

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_sistema(
                interaction.guild,
                self.sistema
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


# ============================================================
# SELECT REAL DE CARGOS
# ============================================================

class AdminCargoSelect(
    discord.ui.RoleSelect
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        self.cog = cog
        self.sistema = sistema

        super().__init__(
            placeholder="👥 Selecione os cargos da Staff...",
            min_values=1,
            max_values=25,
            row=0
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        cargos = self.values

        config = self.cog.config_sistema(
            interaction.guild.id,
            self.sistema
        )

        config["roles"] = [
            role.id
            for role in cargos
        ]

        self.cog.salvar_config()

        lista = "\n".join(
            role.mention
            for role in cargos
        )

        await interaction.response.edit_message(
            embed=embed_base(
                "✅ Cargos configurados",
                (
                    f"**Sistema:** `{self.sistema}`\n\n"
                    f"**Cargos autorizados:**\n"
                    f"{lista}\n\n"
                    "Os cargos foram salvos com sucesso."
                ),
                discord.Color.green()
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


# ============================================================
# VIEW MEMBROS
# ============================================================

class AdminMembrosView(
    discord.ui.View
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog
        self.sistema = sistema

        self.add_item(
            AdminMembroSelect(
                cog,
                sistema
            )
        )


    # ========================================================
    # LIMPAR MEMBROS
    # ========================================================

    @discord.ui.button(
        label="Limpar Membros",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def limpar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        config = self.cog.config_sistema(
            interaction.guild.id,
            self.sistema
        )

        config["users"] = []

        self.cog.salvar_config()

        await interaction.response.edit_message(
            embed=embed_base(
                "✅ Membros removidos",
                (
                    f"Todos os membros autorizados de "
                    f"**{self.sistema}** foram removidos."
                ),
                discord.Color.green()
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


    # ========================================================
    # VOLTAR
    # ========================================================

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_sistema(
                interaction.guild,
                self.sistema
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


# ============================================================
# SELECT REAL DE MEMBROS
# ============================================================

class AdminMembroSelect(
    discord.ui.UserSelect
):

    def __init__(
        self,
        cog: Admin,
        sistema: str
    ):

        self.cog = cog
        self.sistema = sistema

        super().__init__(
            placeholder="👤 Selecione os membros da Staff...",
            min_values=1,
            max_values=25,
            row=0
        )


    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        membros = self.values

        config = self.cog.config_sistema(
            interaction.guild.id,
            self.sistema
        )

        config["users"] = [
            membro.id
            for membro in membros
        ]

        self.cog.salvar_config()

        lista = []

        for membro in membros:

            lista.append(
                membro.mention
            )

        lista_texto = "\n".join(
            lista
        )

        await interaction.response.edit_message(
            embed=embed_base(
                "✅ Membros configurados",
                (
                    f"**Sistema:** `{self.sistema}`\n\n"
                    f"**Membros autorizados:**\n"
                    f"{lista_texto}\n\n"
                    "Os membros foram salvos com sucesso."
                ),
                discord.Color.green()
            ),
            view=AdminSistemaView(
                self.cog,
                self.sistema
            )
        )


# ============================================================
# VIEW AJUDA
# ============================================================

class AdminAjudaView(
    discord.ui.View
):

    def __init__(
        self,
        cog: Admin
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog


    # ========================================================
    # VOLTAR
    # ========================================================

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary
    )
    async def voltar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.cog.usuario_autorizado(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_principal(
                interaction.guild
            ),
            view=AdminPrincipalView(
                self.cog
            )
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot: commands.Bot
):

    await bot.add_cog(
        Admin(bot)
    )

    print(
        "✅ Aira Admin carregado."
    )