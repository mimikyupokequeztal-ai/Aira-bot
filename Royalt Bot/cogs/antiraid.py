# ============================================================
# AIRA • ANTI-RAID
# ============================================================
# Sistema de proteção Anti-Raid
#
# Comando:
#   !antiraid
#
# Recursos:
#   • Painel por botões
#   • Níveis 1, 2 e 3
#   • Desativação manual
#   • Configurações persistentes
#   • Canal de logs
#   • Cargos e membros autorizados
#   • Proteção contra bots suspeitos
#   • Detecção de entrada em massa
#   • Pontuação de risco
#   • Recuperação automática do risco
#   • Reset de risco
#   • Detecção de permissões perigosas em bots
#   • Toggles individuais de proteção
#
# Persistência:
#   • data/antiraid_config.json
#   • Ao reiniciar, todo servidor previamente configurado
#     volta ATIVO no NÍVEL 1 e com risco 0.
#
# ============================================================

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "antiraid_config.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# OWNER DA AIRA
# ============================================================

AIRA_OWNER_ID = 1527022875444379751


# ============================================================
# CONFIG PADRÃO
# ============================================================

CONFIG_PADRAO = {"guilds": {}}


# ============================================================
# HELPERS
# ============================================================

def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def embed_base(
    titulo: str,
    descricao: str,
    cor: discord.Color = discord.Color.blurple(),
) -> discord.Embed:
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor,
        timestamp=agora_utc(),
    )
    embed.set_footer(text="Aira • Anti-Raid Security")
    return embed


# ============================================================
# VIEW PRINCIPAL
# ============================================================

class AntiRaidView(discord.ui.View):

    def __init__(self, cog: "AntiRaid"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Nível 1",
        emoji="🟢",
        style=discord.ButtonStyle.success,
        custom_id="aira_antiraid_nivel_1",
        row=0,
    )
    async def nivel_1(self, interaction, button):
        await self.cog.ativar_nivel(interaction, 1)

    @discord.ui.button(
        label="Nível 2",
        emoji="🟡",
        style=discord.ButtonStyle.primary,
        custom_id="aira_antiraid_nivel_2",
        row=0,
    )
    async def nivel_2(self, interaction, button):
        await self.cog.ativar_nivel(interaction, 2)

    @discord.ui.button(
        label="Nível 3",
        emoji="🔴",
        style=discord.ButtonStyle.danger,
        custom_id="aira_antiraid_nivel_3",
        row=0,
    )
    async def nivel_3(self, interaction, button):
        await self.cog.ativar_nivel(interaction, 3)

    @discord.ui.button(
        label="Desativar",
        emoji="⛔",
        style=discord.ButtonStyle.secondary,
        custom_id="aira_antiraid_desativar",
        row=0,
    )
    async def desativar(self, interaction, button):
        await self.cog.desativar(interaction)

    @discord.ui.button(
        label="Configurações",
        emoji="⚙️",
        style=discord.ButtonStyle.secondary,
        custom_id="aira_antiraid_config",
        row=1,
    )
    async def configuracoes(self, interaction, button):
        if not await self.cog.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não possui acesso ao painel Anti-Raid.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_config(interaction.guild),
            view=AntiRaidConfigView(self.cog),
        )

    @discord.ui.button(
        label="Resetar risco",
        emoji="🔄",
        style=discord.ButtonStyle.secondary,
        custom_id="aira_antiraid_reset",
        row=1,
    )
    async def reset(self, interaction, button):
        await self.cog.resetar_risco(interaction)

    @discord.ui.button(
        label="Fechar",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="aira_antiraid_fechar",
        row=1,
    )
    async def fechar(self, interaction, button):
        if not await self.cog.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não possui acesso a este painel.",
                ephemeral=True,
            )
            return

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="🔒 Painel Anti-Raid fechado.",
            view=self,
        )


# ============================================================
# VIEW DE CONFIGURAÇÕES
# ============================================================

class AntiRaidConfigView(discord.ui.View):

    def __init__(self, cog: "AntiRaid"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        label="Canal de logs",
        emoji="📢",
        style=discord.ButtonStyle.primary,
        custom_id="aira_antiraid_config_canal",
        row=0,
    )
    async def canal(self, interaction, button):
        if not await self.cog.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não pode alterar esta configuração.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "📢 **Configurar canal de logs**\n\n"
            "Use:\n"
            "`!antiraid_canal #canal`",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Cargos Staff",
        emoji="👥",
        style=discord.ButtonStyle.success,
        custom_id="aira_antiraid_config_cargos",
        row=0,
    )
    async def cargos(self, interaction, button):
        if not await self.cog.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não pode alterar esta configuração.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "👥 **Cargos autorizados**\n\n"
            "Use:\n"
            "`!antiraid_cargo @cargo`",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Membros",
        emoji="👤",
        style=discord.ButtonStyle.success,
        custom_id="aira_antiraid_config_membros",
        row=0,
    )
    async def membros(self, interaction, button):
        if not await self.cog.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não pode alterar esta configuração.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "👤 **Membros autorizados**\n\n"
            "Use:\n"
            "`!antiraid_membro @membro`",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Alternar bots",
        emoji="🤖",
        style=discord.ButtonStyle.primary,
        custom_id="aira_antiraid_toggle_bots",
        row=1,
    )
    async def toggle_bots(self, interaction, button):
        await self.cog.alternar_config(
            interaction, "bots_protection", "proteção de bots"
        )

    @discord.ui.button(
        label="Alternar entradas",
        emoji="👥",
        style=discord.ButtonStyle.primary,
        custom_id="aira_antiraid_toggle_joins",
        row=1,
    )
    async def toggle_joins(self, interaction, button):
        await self.cog.alternar_config(
            interaction, "mass_join_protection", "proteção de entradas em massa"
        )

    @discord.ui.button(
        label="Ações automáticas",
        emoji="⚠️",
        style=discord.ButtonStyle.primary,
        custom_id="aira_antiraid_toggle_actions",
        row=1,
    )
    async def toggle_actions(self, interaction, button):
        await self.cog.alternar_config(
            interaction, "automatic_actions", "ações automáticas"
        )

    @discord.ui.button(
        label="Voltar",
        emoji="↩️",
        style=discord.ButtonStyle.secondary,
        custom_id="aira_antiraid_config_voltar",
        row=2,
    )
    async def voltar(self, interaction, button):
        if not await self.cog.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não pode utilizar este painel.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            embed=self.cog.criar_painel(interaction.guild),
            view=AntiRaidView(self.cog),
        )


# ============================================================
# COG
# ============================================================

class AntiRaid(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.joins = defaultdict(deque)
        self.risco = defaultdict(int)
        self.niveis = defaultdict(int)
        self.protecao = defaultdict(int)
        self.ativo = defaultdict(bool)
        self.ultima_atividade = {}

        self.JOIN_WINDOW = 30
        self.JOIN_SUSPEITO = 5
        self.JOIN_RAID = 10
        self.JOIN_CRITICO = 20

        self.RISCO_MAXIMO = 100
        self.RECUPERACAO_PONTOS = 2

        self.config = self.carregar_config()
        self.carregar_servidores()

        self.reduzir_risco.start()

    # ========================================================
    # UNLOAD
    # ========================================================

    def cog_unload(self):
        self.reduzir_risco.cancel()

    # ========================================================
    # CONFIG
    # ========================================================

    def carregar_config(self) -> dict:
        if not CONFIG_FILE.exists():
            dados = {"guilds": {}}
            self.config = dados
            self.salvar_config()
            return dados

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            if not isinstance(dados, dict):
                return {"guilds": {}}

            dados.setdefault("guilds", {})
            return dados

        except Exception as erro:
            print(f"⚠️ [ANTIRAID] Erro carregando configuração: {erro}")
            return {"guilds": {}}

    def salvar_config(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            temporario = CONFIG_FILE.with_suffix(".tmp")

            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(
                    self.config,
                    arquivo,
                    indent=4,
                    ensure_ascii=False,
                )

            temporario.replace(CONFIG_FILE)

        except Exception as erro:
            print(f"⚠️ [ANTIRAID] Erro salvando configuração: {erro}")

    def config_guild(self, guild_id: int) -> dict:
        guild = self.config.setdefault("guilds", {}).setdefault(
            str(guild_id), {}
        )

        guild.setdefault("ativo", True)
        guild.setdefault("protecao", 1)
        guild.setdefault("canal_logs", None)
        guild.setdefault("roles", [])
        guild.setdefault("users", [])
        guild.setdefault("bots_protection", True)
        guild.setdefault("mass_join_protection", True)
        guild.setdefault("automatic_actions", True)

        return guild

    def carregar_servidores(self):
        for guild_id, config in self.config.get("guilds", {}).items():
            try:
                gid = int(guild_id)
            except (ValueError, TypeError):
                continue

            # Regra solicitada:
            # servidor configurado sempre inicia ATIVO no NÍVEL 1.
            config["ativo"] = True
            config["protecao"] = 1

            self.ativo[gid] = True
            self.protecao[gid] = 1
            self.risco[gid] = 0
            self.niveis[gid] = 0

        self.salvar_config()

    # ========================================================
    # AUTORIZAÇÃO
    # ========================================================

    async def eh_owner_aira(self, user) -> bool:
        if user.id == AIRA_OWNER_ID:
            return True

        try:
            return await self.bot.is_owner(user)
        except Exception:
            return False

    def eh_dono_servidor(self, interaction) -> bool:
        return bool(
            interaction.guild
            and interaction.guild.owner_id == interaction.user.id
        )

    async def usuario_autorizado(self, interaction) -> bool:
        if not interaction.guild:
            return False

        if self.eh_dono_servidor(interaction):
            return True

        if await self.eh_owner_aira(interaction.user):
            return True

        config = self.config_guild(interaction.guild.id)

        if interaction.user.id in config.get("users", []):
            return True

        return any(
            role.id in config.get("roles", [])
            for role in getattr(interaction.user, "roles", [])
        )

    async def ctx_autorizado(self, ctx) -> bool:
        if not ctx.guild:
            return False

        if ctx.guild.owner_id == ctx.author.id:
            return True

        if await self.eh_owner_aira(ctx.author):
            return True

        config = self.config_guild(ctx.guild.id)

        if ctx.author.id in config.get("users", []):
            return True

        return any(
            role.id in config.get("roles", [])
            for role in getattr(ctx.author, "roles", [])
        )

    # ========================================================
    # NÍVEIS
    # ========================================================

    def calcular_nivel(self, risco: int) -> int:
        if risco >= 70:
            return 3
        if risco >= 40:
            return 2
        if risco >= 20:
            return 1
        return 0

    def nome_nivel(self, nivel: int) -> str:
        return {
            0: "NORMAL",
            1: "SUSPEITO",
            2: "ALTO RISCO",
            3: "CRÍTICO",
        }.get(nivel, "DESCONHECIDO")

    def emoji_nivel(self, nivel: int) -> str:
        return {
            0: "🟢",
            1: "🟡",
            2: "🟠",
            3: "🔴",
        }.get(nivel, "⚪")

    def nome_protecao(self, nivel: int) -> str:
        return {
            0: "⛔ DESATIVADA",
            1: "🟢 NÍVEL 1 • BAIXO",
            2: "🟡 NÍVEL 2 • ALTO",
            3: "🔴 NÍVEL 3 • MÁXIMO",
        }.get(nivel, "⛔ DESATIVADA")

    def explicacao_nivel(self, nivel: int) -> str:
        return {
            1:
                "👥 Monitoramento de entradas em massa.\n"
                "🤖 Monitoramento de bots recém-chegados.\n"
                "📊 Pontuação de risco automática.\n"
                "📁 Registro das ocorrências.\n"
                "ℹ️ Sem expulsão automática.",
            2:
                "👥 Monitoramento de entradas em massa.\n"
                "🤖 Análise de bots recém-chegados.\n"
                "⚠️ Verificação de permissões perigosas.\n"
                "🧹 Bots altamente suspeitos podem ser expulsos.\n"
                "📊 Pontuação de risco automática.\n"
                "📁 Registro das ações.",
            3:
                "🚨 Monitoramento máximo.\n"
                "👥 Detecção de entradas em massa.\n"
                "🤖 Análise rigorosa de bots.\n"
                "🔐 Verificação de permissões administrativas.\n"
                "🧹 Expulsão automática de bots perigosos.\n"
                "📊 Monitoramento contínuo do risco.\n"
                "🔔 Alertas críticos.\n"
                "📁 Registro completo.",
        }.get(nivel, "Nenhuma proteção configurada.")

    # ========================================================
    # EMBEDS
    # ========================================================

    def criar_embed_alerta(
        self,
        guild: discord.Guild,
        nivel: int,
        risco: int,
        motivo: str,
        titulo: str,
    ) -> discord.Embed:
        cor = {
            0: discord.Color.green(),
            1: discord.Color.gold(),
            2: discord.Color.orange(),
            3: discord.Color.red(),
        }.get(nivel, discord.Color.blurple())

        embed = embed_base(
            f"{self.emoji_nivel(nivel)} {titulo}",
            (
                f"**Servidor:** {guild.name}\n\n"
                f"🚨 **Ameaça:** Nível {nivel} • "
                f"{self.nome_nivel(nivel)}\n"
                f"📊 **Risco:** {risco}/100\n\n"
                f"📝 **Motivo:**\n{motivo}"
            ),
            cor,
        )
        return embed

    def criar_painel(self, guild: discord.Guild) -> discord.Embed:
        config = self.config_guild(guild.id)

        risco = self.risco[guild.id]
        nivel = self.calcular_nivel(risco)
        protecao = self.protecao[guild.id]
        ativo = self.ativo[guild.id]

        status = "🟢 **ATIVO**" if ativo else "🔴 **DESATIVADO**"

        canal_id = config.get("canal_logs")
        canal = guild.get_channel(canal_id) if canal_id else None
        canal_texto = canal.mention if canal else (
            f"`{canal_id}`" if canal_id else "❌ Não configurado"
        )

        embed = embed_base(
            "🛡️ AIRA • ANTI-RAID",
            (
                "Sistema de proteção contra atividades suspeitas "
                "e ataques de entrada em massa.\n\n"
                f"**Status:** {status}\n"
                f"**Proteção:** {self.nome_protecao(protecao)}"
            ),
        )

        embed.add_field(
            name="🚨 Nível de ameaça",
            value=(
                f"{self.emoji_nivel(nivel)} **Nível {nivel} • "
                f"{self.nome_nivel(nivel)}**"
            ),
            inline=True,
        )
        embed.add_field(name="📊 Risco", value=f"**{risco}/100**", inline=True)
        embed.add_field(name="📢 Logs", value=canal_texto, inline=True)

        embed.add_field(
            name="🤖 Bots",
            value="🟢 Ativo" if config["bots_protection"] else "🔴 Desativado",
            inline=True,
        )
        embed.add_field(
            name="👥 Entradas",
            value=(
                "🟢 Ativo"
                if config["mass_join_protection"]
                else "🔴 Desativado"
            ),
            inline=True,
        )
        embed.add_field(
            name="⚙️ Ações automáticas",
            value=(
                "🟢 Ativo"
                if config["automatic_actions"]
                else "🔴 Desativado"
            ),
            inline=True,
        )

        embed.add_field(
            name="👥 Staff",
            value=f"**{len(config['roles'])}** cargo(s)",
            inline=True,
        )
        embed.add_field(
            name="👤 Autorizados",
            value=f"**{len(config['users'])}** membro(s)",
            inline=True,
        )
        embed.add_field(
            name="📋 Proteção atual",
            value=self.explicacao_nivel(protecao),
            inline=False,
        )

        return embed

    def criar_embed_config(self, guild: discord.Guild) -> discord.Embed:
        config = self.config_guild(guild.id)

        canal_id = config.get("canal_logs")
        canal = guild.get_channel(canal_id) if canal_id else None
        canal_texto = canal.mention if canal else (
            "❌ Não configurado" if not canal_id else "Canal não encontrado"
        )

        roles_texto = []
        for role_id in config.get("roles", []):
            role = guild.get_role(role_id)
            if role:
                roles_texto.append(role.mention)

        users_texto = []
        for user_id in config.get("users", []):
            membro = guild.get_member(user_id)
            if membro:
                users_texto.append(membro.mention)

        embed = embed_base(
            "⚙️ ANTI-RAID • CONFIGURAÇÕES",
            "Configure o acesso administrativo e os módulos de proteção.",
        )

        embed.add_field(
            name="📢 Canal de logs",
            value=canal_texto,
            inline=False,
        )
        embed.add_field(
            name="👥 Cargos autorizados",
            value="\n".join(roles_texto) if roles_texto else "❌ Nenhum configurado.",
            inline=False,
        )
        embed.add_field(
            name="👤 Membros autorizados",
            value="\n".join(users_texto) if users_texto else "❌ Nenhum configurado.",
            inline=False,
        )
        embed.add_field(
            name="🤖 Proteção de bots",
            value="🟢 Ativa" if config["bots_protection"] else "🔴 Desativada",
            inline=True,
        )
        embed.add_field(
            name="👥 Entrada em massa",
            value="🟢 Ativa" if config["mass_join_protection"] else "🔴 Desativada",
            inline=True,
        )
        embed.add_field(
            name="⚠️ Ações automáticas",
            value="🟢 Ativas" if config["automatic_actions"] else "🔴 Desativadas",
            inline=True,
        )

        return embed

    # ========================================================
    # LOGS
    # ========================================================

    async def enviar_log(
        self,
        guild: discord.Guild,
        embed: discord.Embed,
        mencionar: bool = False,
    ):
        config = self.config_guild(guild.id)

        canal = None
        canal_id = config.get("canal_logs")

        if canal_id:
            canal = guild.get_channel(canal_id)

        if canal is None:
            canal = discord.utils.get(
                guild.text_channels,
                name="📁・logs",
            )

        if canal is None:
            return

        try:
            await canal.send(
                content="@here" if mencionar else None,
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    everyone=mencionar
                ),
            )
        except discord.Forbidden:
            print(
                f"[ANTIRAID] Sem permissão para enviar logs em {guild.name}"
            )
        except discord.HTTPException as erro:
            print(f"[ANTIRAID] Erro enviando log: {erro}")

    # ========================================================
    # AÇÕES
    # ========================================================

    async def ativar_nivel(self, interaction, nivel: int):
        if not await self.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não possui acesso para alterar o Anti-Raid.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if guild is None:
            return

        config = self.config_guild(guild.id)

        self.ativo[guild.id] = True
        self.protecao[guild.id] = nivel
        config["ativo"] = True
        config["protecao"] = nivel

        self.salvar_config()

        await interaction.response.edit_message(
            embed=self.criar_painel(guild),
            view=AntiRaidView(self),
        )

        await self.enviar_log(
            guild,
            embed_base(
                f"🛡️ ANTI-RAID ATIVADO • NÍVEL {nivel}",
                (
                    f"👤 **Responsável:** {interaction.user.mention}\n\n"
                    f"⚙️ **Proteção:** {self.nome_protecao(nivel)}\n\n"
                    f"📋 **O que este nível faz:**\n"
                    f"{self.explicacao_nivel(nivel)}"
                ),
                discord.Color.green(),
            ),
        )

    async def desativar(self, interaction):
        if not await self.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não possui acesso para alterar o Anti-Raid.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if guild is None:
            return

        config = self.config_guild(guild.id)

        self.ativo[guild.id] = False
        self.protecao[guild.id] = 0
        config["ativo"] = False
        config["protecao"] = 0

        self.salvar_config()

        await interaction.response.edit_message(
            embed=self.criar_painel(guild),
            view=AntiRaidView(self),
        )

        await self.enviar_log(
            guild,
            embed_base(
                "⛔ ANTI-RAID DESATIVADO",
                (
                    f"👤 **Responsável:** {interaction.user.mention}\n\n"
                    "⚠️ O Anti-Raid não realizará ações automáticas "
                    "enquanto estiver desativado."
                ),
                discord.Color.red(),
            ),
        )

    async def resetar_risco(self, interaction):
        if not await self.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não possui acesso para resetar o Anti-Raid.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if guild is None:
            return

        self.risco[guild.id] = 0
        self.niveis[guild.id] = 0
        self.ultima_atividade.pop(guild.id, None)
        self.joins[guild.id].clear()

        await interaction.response.edit_message(
            embed=self.criar_painel(guild),
            view=AntiRaidView(self),
        )

        await self.enviar_log(
            guild,
            embed_base(
                "🔄 RISCO ANTI-RAID RESETADO",
                (
                    f"👤 **Responsável:** {interaction.user.mention}\n\n"
                    "📊 Risco voltou para **0/100**.\n"
                    "🚨 Ameaça voltou para **Nível 0 • NORMAL**."
                ),
            ),
        )

    async def alternar_config(self, interaction, chave: str, nome: str):
        if not await self.usuario_autorizado(interaction):
            await interaction.response.send_message(
                "❌ Você não possui acesso para alterar esta configuração.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if guild is None:
            return

        config = self.config_guild(guild.id)
        config[chave] = not config.get(chave, True)
        self.salvar_config()

        estado = "🟢 ativada" if config[chave] else "🔴 desativada"

        await interaction.response.edit_message(
            embed=self.criar_embed_config(guild),
            view=AntiRaidConfigView(self),
        )

        await self.enviar_log(
            guild,
            embed_base(
                "⚙️ CONFIGURAÇÃO ANTI-RAID ALTERADA",
                (
                    f"👤 **Responsável:** {interaction.user.mention}\n"
                    f"🔧 **Configuração:** {nome}\n"
                    f"📌 **Estado:** {estado}"
                ),
            ),
        )

    # ========================================================
    # RISCO
    # ========================================================

    async def adicionar_risco(self, guild, pontos: int, motivo: str):
        if not self.ativo[guild.id]:
            return

        anterior = self.risco[guild.id]
        nivel_anterior = self.calcular_nivel(anterior)

        atual = min(self.RISCO_MAXIMO, anterior + max(0, pontos))
        self.risco[guild.id] = atual
        self.ultima_atividade[guild.id] = agora_utc()

        nivel_atual = self.calcular_nivel(atual)
        self.niveis[guild.id] = nivel_atual

        if nivel_atual != nivel_anterior:
            await self.enviar_log(
                guild,
                self.criar_embed_alerta(
                    guild,
                    nivel_atual,
                    atual,
                    motivo,
                    "⬆️ AUMENTO DE AMEAÇA",
                ),
                mencionar=nivel_atual == 3,
            )

    @tasks.loop(seconds=60)
    async def reduzir_risco(self):
        agora = agora_utc()

        for guild_id in list(self.risco.keys()):
            if not self.ativo[guild_id]:
                continue

            risco_atual = self.risco[guild_id]
            if risco_atual <= 0:
                continue

            ultima = self.ultima_atividade.get(guild_id)
            if ultima is None:
                continue

            if (agora - ultima).total_seconds() < 60:
                continue

            nivel_anterior = self.calcular_nivel(risco_atual)
            novo_risco = max(0, risco_atual - self.RECUPERACAO_PONTOS)

            self.risco[guild_id] = novo_risco
            nivel_atual = self.calcular_nivel(novo_risco)
            self.niveis[guild_id] = nivel_atual

            if nivel_atual < nivel_anterior:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    await self.enviar_log(
                        guild,
                        self.criar_embed_alerta(
                            guild,
                            nivel_atual,
                            novo_risco,
                            "📉 O servidor permaneceu sem novos eventos suspeitos.",
                            "📉 REDUÇÃO DE AMEAÇA",
                        ),
                    )

            if novo_risco == 0:
                self.ultima_atividade.pop(guild_id, None)

    @reduzir_risco.before_loop
    async def antes_reduzir_risco(self):
        await self.bot.wait_until_ready()

    # ========================================================
    # ANÁLISE DE BOT
    # ========================================================

    def bot_suspeito(self, membro: discord.Member):
        if not membro.bot:
            return False, []

        permissoes = membro.guild_permissions
        perigos = []

        if permissoes.administrator:
            perigos.append("Administrator")
        if permissoes.manage_guild:
            perigos.append("Manage Server")
        if permissoes.manage_channels:
            perigos.append("Manage Channels")
        if permissoes.manage_roles:
            perigos.append("Manage Roles")
        if permissoes.ban_members:
            perigos.append("Ban Members")
        if permissoes.kick_members:
            perigos.append("Kick Members")
        if permissoes.manage_webhooks:
            perigos.append("Manage Webhooks")

        if permissoes.administrator:
            return True, perigos

        return len(perigos) >= 3, perigos

    async def expulsar_bot(self, membro: discord.Member, motivo: str):
        guild = membro.guild

        try:
            await membro.kick(reason=motivo)

            await self.enviar_log(
                guild,
                embed_base(
                    "🤖 BOT EXPULSO PELO ANTI-RAID",
                    (
                        f"🤖 **Bot:** {membro.mention}\n"
                        f"🆔 **ID:** `{membro.id}`\n\n"
                        f"📝 **Motivo:**\n{motivo}\n\n"
                        f"📊 **Risco:** {self.risco[guild.id]}/100\n"
                        f"🛡️ **Proteção:** "
                        f"{self.nome_protecao(self.protecao[guild.id])}"
                    ),
                    discord.Color.red(),
                ),
                mencionar=True,
            )

        except discord.Forbidden:
            await self.enviar_log(
                guild,
                embed_base(
                    "❌ FALHA AO EXPULSAR BOT",
                    (
                        f"🤖 **Bot:** {membro.mention}\n\n"
                        "O Anti-Raid identificou o bot como suspeito, "
                        "mas não possui permissão para expulsá-lo."
                    ),
                    discord.Color.red(),
                ),
                mencionar=True,
            )
        except discord.HTTPException as erro:
            print(f"[ANTIRAID] Erro expulsando bot: {erro}")

    # ========================================================
    # EVENTO: ENTRADA
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        if not self.ativo[guild.id]:
            return

        config = self.config_guild(guild.id)
        agora = agora_utc()

        entradas = self.joins[guild.id]

        while entradas and agora - entradas[0] > timedelta(seconds=self.JOIN_WINDOW):
            entradas.popleft()

        entradas.append(agora)
        quantidade = len(entradas)

        if member.bot and config["bots_protection"]:
            suspeito, perigos = self.bot_suspeito(member)

            await self.adicionar_risco(
                guild,
                5,
                f"🤖 Um bot entrou no servidor: **{member}**",
            )

            if suspeito:
                pontos = 40 if member.guild_permissions.administrator else 25

                await self.adicionar_risco(
                    guild,
                    pontos,
                    (
                        "🚨 Bot com permissões potencialmente perigosas:\n"
                        f"🤖 **{member}**\n\n"
                        "🔐 **Permissões:**\n"
                        + "\n".join(f"• {p}" for p in perigos)
                    ),
                )

                if (
                    self.protecao[guild.id] >= 2
                    and config["automatic_actions"]
                ):
                    await self.expulsar_bot(
                        member,
                        (
                            "🤖 Bot recém-adicionado com permissões "
                            "potencialmente perigosas.\n\n"
                            "🔐 **Permissões:**\n"
                            + "\n".join(f"• {p}" for p in perigos)
                        ),
                    )

        if not config["mass_join_protection"]:
            return

        if quantidade >= self.JOIN_CRITICO:
            await self.adicionar_risco(
                guild,
                50,
                (
                    f"🚨 **{quantidade} membros** entraram em "
                    f"aproximadamente {self.JOIN_WINDOW} segundos."
                ),
            )
        elif quantidade >= self.JOIN_RAID:
            await self.adicionar_risco(
                guild,
                30,
                (
                    f"⚠️ **{quantidade} membros** entraram em "
                    f"aproximadamente {self.JOIN_WINDOW} segundos."
                ),
            )
        elif quantidade >= self.JOIN_SUSPEITO:
            await self.adicionar_risco(
                guild,
                10,
                (
                    f"👥 **{quantidade} membros** entraram em "
                    f"aproximadamente {self.JOIN_WINDOW} segundos."
                ),
            )

    # ========================================================
    # EVENTO: BOT RECEBE CARGO
    # ========================================================

    @commands.Cog.listener()
    async def on_member_update(self, antes: discord.Member, depois: discord.Member):
        guild = depois.guild

        if not self.ativo[guild.id] or not depois.bot:
            return

        config = self.config_guild(guild.id)
        if not config["bots_protection"]:
            return

        cargos_antes = {cargo.id for cargo in antes.roles}
        cargos_depois = {cargo.id for cargo in depois.roles}
        novos = cargos_depois - cargos_antes

        for cargo in depois.roles:
            if cargo.id not in novos:
                continue

            permissoes = cargo.permissions
            pontos = 0
            motivos = []

            if permissoes.administrator:
                pontos += 40
                motivos.append("⚠️ Administrator")
            if permissoes.manage_guild:
                pontos += 15
                motivos.append("⚠️ Manage Server")
            if permissoes.manage_channels:
                pontos += 10
                motivos.append("⚠️ Manage Channels")
            if permissoes.manage_roles:
                pontos += 10
                motivos.append("⚠️ Manage Roles")
            if permissoes.ban_members:
                pontos += 10
                motivos.append("⚠️ Ban Members")
            if permissoes.kick_members:
                pontos += 5
                motivos.append("⚠️ Kick Members")
            if permissoes.manage_webhooks:
                pontos += 5
                motivos.append("⚠️ Manage Webhooks")

            if pontos <= 0:
                continue

            await self.adicionar_risco(
                guild,
                pontos,
                (
                    f"🤖 O bot **{depois}** recebeu o cargo "
                    f"**{cargo.name}**.\n\n"
                    + "\n".join(motivos)
                ),
            )

            if (
                self.protecao[guild.id] >= 3
                and permissoes.administrator
                and config["automatic_actions"]
            ):
                await self.expulsar_bot(
                    depois,
                    (
                        "🚨 O Anti-Raid detectou um bot recebendo "
                        "um cargo com a permissão **Administrator**."
                    ),
                )

    # ========================================================
    # COMANDO PRINCIPAL
    # ========================================================

    @commands.command(name="antiraid")
    async def antiraid(self, ctx: commands.Context):
        if not await self.ctx_autorizado(ctx):
            await ctx.send("❌ Você não possui acesso ao painel Anti-Raid.")
            return

        await ctx.send(
            embed=self.criar_painel(ctx.guild),
            view=AntiRaidView(self),
        )

    # ========================================================
    # COMANDOS DE CONFIGURAÇÃO
    # ========================================================

    @commands.command(name="antiraid_canal")
    async def antiraid_canal(self, ctx, canal: discord.TextChannel):
        if not await self.ctx_autorizado(ctx):
            await ctx.send("❌ Você não possui acesso.")
            return

        config = self.config_guild(ctx.guild.id)
        config["canal_logs"] = canal.id
        self.salvar_config()

        await ctx.send(
            f"✅ Canal de logs do Anti-Raid definido para {canal.mention}."
        )

    @commands.command(name="antiraid_cargo")
    async def antiraid_cargo(self, ctx, cargo: discord.Role):
        if not await self.ctx_autorizado(ctx):
            await ctx.send("❌ Você não possui acesso.")
            return

        config = self.config_guild(ctx.guild.id)
        roles = config.setdefault("roles", [])

        if cargo.id in roles:
            await ctx.send("ℹ️ Esse cargo já está autorizado.")
            return

        roles.append(cargo.id)
        self.salvar_config()

        await ctx.send(
            f"✅ {cargo.mention} agora pode administrar o Anti-Raid."
        )

    @commands.command(name="antiraid_membro")
    async def antiraid_membro(self, ctx, membro: discord.Member):
        if not await self.ctx_autorizado(ctx):
            await ctx.send("❌ Você não possui acesso.")
            return

        config = self.config_guild(ctx.guild.id)
        users = config.setdefault("users", [])

        if membro.id in users:
            await ctx.send("ℹ️ Esse membro já está autorizado.")
            return

        users.append(membro.id)
        self.salvar_config()

        await ctx.send(
            f"✅ {membro.mention} agora pode administrar o Anti-Raid."
        )

    @commands.command(name="antiraid_reset")
    async def antiraid_reset(self, ctx):
        if not await self.ctx_autorizado(ctx):
            await ctx.send("❌ Você não possui acesso.")
            return

        self.risco[ctx.guild.id] = 0
        self.niveis[ctx.guild.id] = 0
        self.ultima_atividade.pop(ctx.guild.id, None)
        self.joins[ctx.guild.id].clear()

        await ctx.send(
            embed=embed_base(
                "🔄 ANTI-RAID",
                (
                    "🟢 **Pontuação resetada.**\n\n"
                    "📊 Risco: **0/100**\n"
                    "🚨 Ameaça: **Nível 0 • NORMAL**\n\n"
                    "🛡️ O nível de proteção não foi alterado."
                ),
            )
        )

    # ========================================================
    # ERROS
    # ========================================================

    @antiraid_canal.error
    async def antiraid_canal_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send("❌ Uso correto: `!antiraid_canal #canal`")

    @antiraid_cargo.error
    async def antiraid_cargo_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send("❌ Uso correto: `!antiraid_cargo @cargo`")

    @antiraid_membro.error
    async def antiraid_membro_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send("❌ Uso correto: `!antiraid_membro @membro`")


# ============================================================
# SETUP
# ============================================================

async def setup(bot: commands.Bot):
    cog = AntiRaid(bot)

    await bot.add_cog(cog)

    # Views persistentes:
    # timeout=None + custom_id em todos os botões.
    bot.add_view(AntiRaidView(cog))
    bot.add_view(AntiRaidConfigView(cog))

    print("✅ Aira Anti-Raid carregado.")
