from __future__ import annotations

import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

import discord
from discord.ext import commands, tasks


# ============================================================
# CONFIGURAÇÕES
# ============================================================

COR_SORTEIO = discord.Color.from_rgb(128, 0, 255)
COR_LOG = discord.Color.blurple()
COR_SUCESSO = discord.Color.green()
COR_ERRO = discord.Color.red()
COR_AVISO = discord.Color.orange()

PASTA_DATA = Path("data")
PASTA_DATA.mkdir(parents=True, exist_ok=True)

ARQUIVO_SORTEIOS = PASTA_DATA / "sorteios.json"
ARQUIVO_CONFIG = PASTA_DATA / "sorteios_config.json"

BANNER_SORTEIO = ""


# ============================================================
# JSON
# ============================================================

def carregar_json(arquivo, padrao):
    if not arquivo.exists():
        return padrao

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return padrao


def salvar_json(arquivo, dados):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except OSError as erro:
        print(f"[SORTEIOS] Erro ao salvar: {erro}")


def formatar_dias(dias: int) -> str:
    return "1 dia" if dias == 1 else f"{dias} dias"


def parse_ids(texto: str | None) -> list[int]:
    """Aceita IDs separados por vírgula, espaços ou quebras de linha."""
    if not texto:
        return []

    texto = texto.replace(",", " ").replace("\n", " ")
    ids = []

    for parte in texto.split():
        parte = parte.strip()
        if not parte:
            continue

        if parte.startswith("<@&") and parte.endswith(">"):
            parte = parte[3:-1]

        try:
            valor = int(parte)
        except ValueError:
            continue

        if valor not in ids:
            ids.append(valor)

    return ids


# ============================================================
# VIEW DE PARTICIPAÇÃO
# ============================================================

class ParticiparView(discord.ui.View):
    def __init__(self, cog, sorteio_id):
        super().__init__(timeout=None)

        self.cog = cog
        self.sorteio_id = str(sorteio_id)

        participar = discord.ui.Button(
            label="Participar",
            emoji="🎟️",
            style=discord.ButtonStyle.success,
            custom_id=f"sorteio_participar:{self.sorteio_id}",
        )
        participar.callback = self.participar
        self.add_item(participar)

        atualizar = discord.ui.Button(
            label="Atualizar",
            emoji="🔄",
            style=discord.ButtonStyle.primary,
            custom_id=f"sorteio_atualizar:{self.sorteio_id}",
        )
        atualizar.callback = self.atualizar
        self.add_item(atualizar)

    async def participar(self, interaction: discord.Interaction):
        sorteio = self.cog.sorteios.get(self.sorteio_id)

        if sorteio is None:
            await interaction.response.send_message(
                "❌ Este sorteio não existe mais.",
                ephemeral=True,
            )
            return

        if sorteio.get("encerrado", False):
            await interaction.response.send_message(
                "🔴 Este sorteio já foi encerrado.",
                ephemeral=True,
            )
            return

        agora = datetime.now(timezone.utc).timestamp()

        if agora >= float(sorteio["fim"]):
            await interaction.response.send_message(
                "⏰ O tempo deste sorteio acabou.",
                ephemeral=True,
            )
            await self.cog.encerrar_sorteio(self.sorteio_id)
            return

        usuario_id = interaction.user.id
        participantes = sorteio.setdefault("participantes", [])

        entrou = usuario_id not in participantes

        if entrou:
            participantes.append(usuario_id)
            mensagem = "🎉 Você entrou no sorteio!"
            emoji_log = "🎟️"
            cor_log = COR_SUCESSO
            acao = "entrou"
        else:
            participantes.remove(usuario_id)
            mensagem = "🎟️ Você saiu do sorteio."
            emoji_log = "🚪"
            cor_log = COR_AVISO
            acao = "saiu"

        self.cog.salvar_sorteios()

        await interaction.response.send_message(
            mensagem,
            ephemeral=True,
        )

        await self.cog.enviar_log(
            interaction.guild,
            f"Participante {acao}",
            (
                f"👤 **Usuário:** {interaction.user.mention}\n\n"
                f"🎁 **Prêmio:** {sorteio['premio']}\n\n"
                f"🆔 **Sorteio:** `{self.sorteio_id}`"
            ),
            emoji_log,
            cor_log,
        )

        await self.cog.atualizar_mensagem(self.sorteio_id)

    async def atualizar(self, interaction: discord.Interaction):
        sorteio = self.cog.sorteios.get(self.sorteio_id)

        if sorteio is None:
            await interaction.response.send_message(
                "❌ Este sorteio não existe mais.",
                ephemeral=True,
            )
            return

        await self.cog.atualizar_mensagem(self.sorteio_id)

        await interaction.response.send_message(
            "🔄 Sorteio atualizado!",
            ephemeral=True,
        )


# ============================================================
# COG SORTEIOS
# ============================================================

class Sorteios(commands.Cog):
    """
    Sistema de sorteios.

    A criação/configuração agora é feita por slash/prefixo:
        /sorteio criar
        !sorteio criar

    Os botões continuam somente onde fazem sentido para o público:
        🎟️ Participar
        🔄 Atualizar
    """

    def __init__(self, bot):
        self.bot = bot
        self.sorteios = carregar_json(ARQUIVO_SORTEIOS, {})
        self.config = carregar_json(ARQUIVO_CONFIG, {})
        self._views_restauradas = False
        self.tarefa_sorteios.start()

    def cog_unload(self):
        self.tarefa_sorteios.cancel()

    # ========================================================
    # RESTAURAR BOTÕES DE PARTICIPAÇÃO
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):
        if self._views_restauradas:
            return

        self._views_restauradas = True

        for sorteio_id, sorteio in self.sorteios.items():
            if sorteio.get("encerrado", False):
                continue

            try:
                self.bot.add_view(
                    ParticiparView(self, sorteio_id)
                )
            except Exception as erro:
                print(
                    f"[SORTEIOS] Erro ao restaurar "
                    f"{sorteio_id}: {erro}"
                )

    # ========================================================
    # SALVAR
    # ========================================================

    def salvar_sorteios(self):
        salvar_json(
            ARQUIVO_SORTEIOS,
            self.sorteios,
        )

    def salvar_config(self):
        salvar_json(
            ARQUIVO_CONFIG,
            self.config,
        )

    # ========================================================
    # LOGS
    # ========================================================

    def obter_canal_logs(self, guild):
        if guild is None:
            return None

        configuracao = self.config.get(
            str(guild.id),
            {},
        )

        canal_id = configuracao.get("canal_logs")

        if not canal_id:
            return None

        return guild.get_channel(int(canal_id))

    async def enviar_log(
        self,
        guild,
        titulo,
        descricao,
        emoji="📜",
        cor=COR_LOG,
    ):
        canal = self.obter_canal_logs(guild)

        if canal is None:
            return

        embed = discord.Embed(
            title=f"{emoji} {titulo}",
            description=descricao,
            color=cor,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(
            text="Royalt Giveaway Logging System"
        )

        try:
            await canal.send(embed=embed)
        except discord.Forbidden:
            print(
                f"[SORTEIOS] Sem permissão para enviar "
                f"logs em {guild.name}."
            )
        except discord.HTTPException as erro:
            print(f"[SORTEIOS] Erro no log: {erro}")

    # ========================================================
    # EMBED DO SORTEIO
    # ========================================================

    def criar_embed(self, sorteio):
        participantes = len(
            sorteio.get("participantes", [])
        )

        fim = int(float(sorteio["fim"]))

        descricao = sorteio.get(
            "descricao",
            "Sem descrição.",
        )

        if not sorteio.get("encerrado", False):
            embed = discord.Embed(
                title="🎉 ROYALT • SORTEIO",
                description=(
                    f"## 🎁 {sorteio['premio']}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📝 **Descrição**\n{descricao}\n\n"
                    f"🏆 **Vencedores:** **{sorteio['vencedores']}**\n\n"
                    f"👥 **Participantes:** **{participantes}**\n\n"
                    f"⏰ **Termina:** <t:{fim}:R>\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🎟️ Clique em **Participar** para entrar!"
                ),
                color=COR_SORTEIO,
            )
        else:
            embed = discord.Embed(
                title="🏆 ROYALT • SORTEIO ENCERRADO",
                description=(
                    f"## 🎁 {sorteio['premio']}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📝 **Descrição**\n{descricao}\n\n"
                    "🔴 **Este sorteio foi encerrado.**\n\n"
                    f"👥 **Participantes:** **{participantes}**"
                ),
                color=COR_ERRO,
            )

            vencedores = sorteio.get("vencedores_ids", [])

            if vencedores:
                mencoes = " ".join(
                    f"<@{uid}>"
                    for uid in vencedores
                )
                embed.add_field(
                    name="🏆 Vencedor(es)",
                    value=mencoes,
                    inline=False,
                )

        embed.add_field(
            name="👤 Organizador",
            value=f"<@{sorteio['criador']}>",
            inline=True,
        )

        embed.add_field(
            name="🆔 ID do sorteio",
            value=f"`{sorteio['id']}`",
            inline=True,
        )

        bonus_cargos = sorteio.get("bonus_cargos", {})

        if bonus_cargos:
            linhas_bonus = []

            for role_id, dados in bonus_cargos.items():
                linhas_bonus.append(
                    f"<@&{role_id}> → "
                    f"+{dados.get('percentual', 0)}% "
                    f"| +{dados.get('entradas', 0)} entrada(s)"
                )

            embed.add_field(
                name="🎯 Chances por cargo",
                value="\n".join(linhas_bonus)[:1024],
                inline=False,
            )

        requisitos = sorteio.get("requisitos", {})
        requisitos_texto = []

        cargos = requisitos.get("cargos", [])

        if cargos:
            requisitos_texto.append(
                "🎭 Cargos: "
                + " ".join(
                    f"<@&{role_id}>"
                    for role_id in cargos
                )
            )

        idade_conta = int(
            requisitos.get("idade_conta_dias", 0)
        )

        if idade_conta > 0:
            requisitos_texto.append(
                f"👤 Conta: {formatar_dias(idade_conta)}"
            )

        idade_servidor = int(
            requisitos.get("idade_servidor_dias", 0)
        )

        if idade_servidor > 0:
            requisitos_texto.append(
                f"🏠 Servidor: {formatar_dias(idade_servidor)}"
            )

        if requisitos_texto:
            embed.add_field(
                name="📋 Requisitos",
                value="\n".join(requisitos_texto)[:1024],
                inline=False,
            )

        if BANNER_SORTEIO:
            embed.set_image(url=BANNER_SORTEIO)

        embed.set_footer(
            text="Royalt Giveaway System"
        )

        return embed

    # ========================================================
    # CRIAR SORTEIO
    # ========================================================

    @commands.hybrid_group(
        name="sorteio",
        description="Sistema completo de sorteios.",
    )
    async def sorteio(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "🎁 Use `/sorteio criar` ou `!sorteio criar`."
            )

    @sorteio.command(
        name="criar",
        description="Cria um sorteio sem painel de botões.",
    )
    @commands.has_permissions(manage_guild=True)
    async def criar(
        self,
        ctx,
        premio: str,
        descricao: str,
        duracao_minutos: int,
        vencedores: int = 1,
        bonus_cargo: discord.Role = None,
        bonus_percentual: float = 0.0,
        entradas_extras: int = 0,
        cargos_requisitos: str = "",
        idade_conta_dias: int = 0,
        idade_servidor_dias: int = 0,
    ):
        if ctx.guild is None:
            await ctx.send(
                "❌ O sorteio precisa ser criado dentro de um servidor."
            )
            return

        if duracao_minutos <= 0:
            await ctx.send(
                "❌ A duração precisa ser maior que 0 minutos."
            )
            return

        if vencedores <= 0:
            await ctx.send(
                "❌ A quantidade de vencedores precisa ser maior que 0."
            )
            return

        if bonus_percentual < 0:
            await ctx.send(
                "❌ O bônus percentual não pode ser negativo."
            )
            return

        if entradas_extras < 0:
            await ctx.send(
                "❌ As entradas extras não podem ser negativas."
            )
            return

        if idade_conta_dias < 0 or idade_servidor_dias < 0:
            await ctx.send(
                "❌ As idades precisam ser 0 ou maiores."
            )
            return

        requisitos_cargos = parse_ids(cargos_requisitos)

        # Se o cargo citado não existir no servidor, não criamos
        # uma configuração que depois parecerá quebrada.
        for role_id in requisitos_cargos:
            if ctx.guild.get_role(role_id) is None:
                await ctx.send(
                    f"❌ O cargo `{role_id}` não existe neste servidor."
                )
                return

        if bonus_cargo is not None and bonus_cargo.is_default():
            await ctx.send(
                "❌ Não é possível usar @everyone como cargo de bônus."
            )
            return

        sorteio_id = str(
            random.randint(100000, 999999)
        )

        while sorteio_id in self.sorteios:
            sorteio_id = str(
                random.randint(100000, 999999)
            )

        agora = datetime.now(timezone.utc)
        fim = (
            agora
            + timedelta(minutes=duracao_minutos)
        ).timestamp()

        bonus_cargos = {}

        if bonus_cargo is not None:
            bonus_cargos[str(bonus_cargo.id)] = {
                "percentual": bonus_percentual,
                "entradas": entradas_extras,
            }

        sorteio = {
            "id": sorteio_id,
            "guild": ctx.guild.id,
            "canal": ctx.channel.id,
            "mensagem": 0,
            "criador": ctx.author.id,
            "premio": premio,
            "descricao": descricao,
            "vencedores": vencedores,
            "participantes": [],
            "vencedores_ids": [],
            "inicio": agora.timestamp(),
            "fim": fim,
            "encerrado": False,
            "bonus_cargos": bonus_cargos,
            "requisitos": {
                "cargos": requisitos_cargos,
                "idade_conta_dias": idade_conta_dias,
                "idade_servidor_dias": idade_servidor_dias,
            },
        }

        self.sorteios[sorteio_id] = sorteio

        try:
            mensagem = await ctx.channel.send(
                embed=self.criar_embed(sorteio),
                view=ParticiparView(self, sorteio_id),
            )
        except discord.Forbidden:
            self.sorteios.pop(sorteio_id, None)
            await ctx.send(
                "❌ Não tenho permissão para enviar mensagens ou embeds neste canal."
            )
            return
        except discord.HTTPException as erro:
            self.sorteios.pop(sorteio_id, None)
            print(
                f"[SORTEIOS] Erro ao publicar: {erro}"
            )
            await ctx.send(
                "❌ Ocorreu um erro ao publicar o sorteio."
            )
            return

        sorteio["mensagem"] = mensagem.id
        self.salvar_sorteios()

        await ctx.send(
            embed=discord.Embed(
                title="✅ ROYALT • SORTEIO CRIADO",
                description=(
                    f"🎁 **Prêmio:** {premio}\n"
                    f"⏰ **Duração:** {duracao_minutos} minuto(s)\n"
                    f"🏆 **Vencedores:** {vencedores}\n"
                    f"🆔 **ID:** `{sorteio_id}`\n\n"
                    "O sorteio já foi publicado neste canal."
                ),
                color=COR_SUCESSO,
            )
        )

        await self.enviar_log(
            ctx.guild,
            "Sorteio criado",
            (
                f"🎁 **Prêmio:** {premio}\n\n"
                f"📝 **Descrição:** {descricao}\n\n"
                f"🆔 **ID:** `{sorteio_id}`\n\n"
                f"🏆 **Vencedores:** **{vencedores}**\n\n"
                f"⏰ **Duração:** **{duracao_minutos} minutos**\n\n"
                f"🎯 **Cargos com bônus:** **{len(bonus_cargos)}**\n\n"
                f"📋 **Cargos obrigatórios:** **{len(requisitos_cargos)}**\n\n"
                f"👤 **Criador:** {ctx.author.mention}\n\n"
                f"📁 **Canal:** {ctx.channel.mention}"
            ),
            "🎁",
            COR_SORTEIO,
        )

    # ========================================================
    # ENCERRAR
    # ========================================================

    @sorteio.command(
        name="encerrar",
        description="Encerra um sorteio pelo ID.",
    )
    @commands.has_permissions(manage_guild=True)
    async def encerrar(self, ctx, sorteio_id: str):
        sorteio = self.sorteios.get(str(sorteio_id))

        if sorteio is None:
            await ctx.send("❌ Sorteio não encontrado.")
            return

        if sorteio.get("encerrado", False):
            await ctx.send("🔴 Este sorteio já foi encerrado.")
            return

        await self.encerrar_sorteio(str(sorteio_id))
        await ctx.send(
            "🏆 Sorteio encerrado com sucesso!"
        )

    # ========================================================
    # REROLL
    # ========================================================

    @sorteio.command(
        name="reroll",
        description="Escolhe novamente um vencedor.",
    )
    @commands.has_permissions(manage_guild=True)
    async def reroll(self, ctx, sorteio_id: str):
        sorteio = self.sorteios.get(str(sorteio_id))

        if sorteio is None:
            await ctx.send("❌ Sorteio não encontrado.")
            return

        participantes = sorteio.get("participantes", [])

        if not participantes:
            await ctx.send(
                "❌ Não existem participantes."
            )
            return

        if ctx.guild is None:
            await ctx.send(
                "❌ Este comando só funciona em servidores."
            )
            return

        candidatos = []

        for usuario_id in participantes:
            membro = ctx.guild.get_member(int(usuario_id))
            if membro:
                candidatos.append(membro)

        antigos = {
            int(uid)
            for uid in sorteio.get("vencedores_ids", [])
        }

        candidatos = [
            membro
            for membro in candidatos
            if membro.id not in antigos
        ] or candidatos

        while candidatos:
            novo_vencedor = self.escolher_vencedor(
                candidatos,
                sorteio,
            )

            if novo_vencedor is None:
                break

            atende, motivos = self.verificar_requisitos(
                novo_vencedor,
                sorteio,
            )

            if atende:
                sorteio["vencedores_ids"] = [
                    novo_vencedor.id
                ]
                self.salvar_sorteios()

                dm = await self.enviar_dm_vencedor(
                    novo_vencedor.id,
                    sorteio,
                )

                await ctx.send(
                    "🎲 **Reroll realizado!**\n\n"
                    f"🏆 Novo vencedor: {novo_vencedor.mention}\n"
                    f"📩 DM: {'✅ enviada' if dm else '⚠️ não enviada'}"
                )

                await self.enviar_log(
                    ctx.guild,
                    "Reroll realizado",
                    (
                        f"🎁 **Prêmio:** {sorteio['premio']}\n\n"
                        f"🆔 **Sorteio:** `{sorteio_id}`\n\n"
                        f"🏆 **Novo vencedor:** {novo_vencedor.mention}\n\n"
                        f"📩 **DM:** {'✅ Enviada' if dm else '⚠️ Não enviada'}\n\n"
                        f"👤 **Moderador:** {ctx.author.mention}"
                    ),
                    "🎲",
                    COR_SUCESSO,
                )
                return

            await self.enviar_dm_requisito(
                novo_vencedor,
                sorteio,
                motivos,
            )
            candidatos.remove(novo_vencedor)

        await ctx.send(
            "❌ Não foi possível encontrar outro participante "
            "que cumpra os requisitos."
        )

    # ========================================================
    # LOGCANAL
    # ========================================================

    @sorteio.command(
        name="logcanal",
        description="Define o canal de logs dos sorteios.",
    )
    @commands.has_permissions(manage_guild=True)
    async def logcanal(
        self,
        ctx,
        canal: discord.TextChannel,
    ):
        guild_id = str(ctx.guild.id)

        self.config.setdefault(guild_id, {})
        self.config[guild_id]["canal_logs"] = canal.id
        self.salvar_config()

        embed = discord.Embed(
            title="📁 ROYALT • LOGS DE SORTEIOS",
            description=(
                "## ✅ Configuração concluída!\n\n"
                f"📁 **Canal:** {canal.mention}\n\n"
                "As ações futuras do sistema de sorteios "
                "serão registradas neste canal."
            ),
            color=COR_SUCESSO,
        )
        embed.set_footer(
            text="Royalt Giveaway Logging System"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # VERLOG
    # ========================================================

    @sorteio.command(
        name="verlog",
        description="Mostra o canal de logs dos sorteios.",
    )
    @commands.has_permissions(manage_guild=True)
    async def verlog(self, ctx):
        canal = self.obter_canal_logs(ctx.guild)

        if canal is None:
            await ctx.send(
                "📭 Nenhum canal de logs foi configurado.\n"
                "Use `/sorteio logcanal`."
            )
            return

        embed = discord.Embed(
            title="📁 ROYALT • CANAL DE LOGS",
            description=(
                f"📜 **Canal configurado:** {canal.mention}"
            ),
            color=COR_LOG,
        )
        embed.set_footer(
            text="Royalt Giveaway Logging System"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # PESO
    # ========================================================

    def calcular_peso(self, membro, sorteio):
        peso = 1.0

        bonus_cargos = sorteio.get(
            "bonus_cargos",
            {},
        )

        for role in membro.roles:
            dados = bonus_cargos.get(str(role.id))

            if dados is None:
                continue

            percentual = float(
                dados.get("percentual", 0)
            )
            entradas = int(
                dados.get("entradas", 0)
            )

            peso *= 1 + percentual / 100
            peso += entradas

        return max(peso, 1.0)

    def escolher_vencedor(self, candidatos, sorteio):
        if not candidatos:
            return None

        pesos = [
            self.calcular_peso(membro, sorteio)
            for membro in candidatos
        ]

        return random.choices(
            candidatos,
            weights=pesos,
            k=1,
        )[0]

    # ========================================================
    # REQUISITOS
    # ========================================================

    def verificar_requisitos(self, membro, sorteio):
        requisitos = sorteio.get(
            "requisitos",
            {},
        )

        motivos = []

        cargos_obrigatorios = requisitos.get(
            "cargos",
            [],
        )

        cargos_membro = {
            role.id
            for role in membro.roles
        }

        faltando = [
            int(role_id)
            for role_id in cargos_obrigatorios
            if int(role_id) not in cargos_membro
        ]

        if faltando:
            motivos.append(
                "🎭 Você não possui os cargos obrigatórios: "
                + " ".join(
                    f"<@&{role_id}>"
                    for role_id in faltando
                )
            )

        idade_conta_dias = int(
            requisitos.get(
                "idade_conta_dias",
                0,
            )
        )

        if idade_conta_dias > 0:
            agora = datetime.now(timezone.utc)
            dias_conta = (
                agora - membro.created_at
            ).days

            if dias_conta < idade_conta_dias:
                motivos.append(
                    "👤 Sua conta precisa ter pelo menos "
                    f"**{idade_conta_dias} dias**."
                )

        idade_servidor_dias = int(
            requisitos.get(
                "idade_servidor_dias",
                0,
            )
        )

        if idade_servidor_dias > 0:
            if membro.joined_at is None:
                motivos.append(
                    "🏠 Não foi possível verificar "
                    "quando você entrou no servidor."
                )
            else:
                agora = datetime.now(timezone.utc)
                dias_servidor = (
                    agora - membro.joined_at
                ).days

                if dias_servidor < idade_servidor_dias:
                    motivos.append(
                        "🏠 Você precisa estar no servidor "
                        f"há pelo menos **{idade_servidor_dias} dias**."
                    )

        return (False, motivos) if motivos else (True, [])

    # ========================================================
    # DMS
    # ========================================================

    async def enviar_dm_requisito(
        self,
        membro,
        sorteio,
        motivos,
    ):
        try:
            embed = discord.Embed(
                title="🎲 ROYALT • REROLL",
                description=(
                    "Você foi selecionado inicialmente como vencedor, "
                    "porém **não cumpriu os requisitos deste sorteio**.\n\n"
                    f"🎁 **Prêmio:** {sorteio['premio']}\n\n"
                    f"🆔 **Sorteio:** `{sorteio['id']}`\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    "❌ **Requisitos não cumpridos:**\n"
                    + "\n".join(motivos)
                    + "\n\n"
                    "🔄 O Royalt realizou um **reroll automático**."
                ),
                color=COR_ERRO,
            )

            if BANNER_SORTEIO:
                embed.set_image(url=BANNER_SORTEIO)

            embed.set_footer(
                text="Royalt Giveaway System"
            )

            await membro.send(embed=embed)
            return True

        except (discord.Forbidden, discord.HTTPException):
            return False

    async def enviar_dm_vencedor(
        self,
        usuario_id,
        sorteio,
    ):
        try:
            usuario = self.bot.get_user(
                int(usuario_id)
            )

            if usuario is None:
                usuario = await self.bot.fetch_user(
                    int(usuario_id)
                )

            guild = self.bot.get_guild(
                int(sorteio["guild"])
            )

            nome_servidor = (
                guild.name
                if guild
                else "Servidor"
            )

            embed = discord.Embed(
                title="🎉 ROYALT • VOCÊ GANHOU!",
                description=(
                    "## 🏆 Parabéns!\n\n"
                    "Você foi selecionado como **vencedor** de um sorteio!\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🎁 **Prêmio**\n{sorteio['premio']}\n\n"
                    f"📝 **Descrição**\n"
                    f"{sorteio.get('descricao', 'Sem descrição.')}\n\n"
                    f"🆔 **ID do sorteio**\n`{sorteio['id']}`\n\n"
                    f"🏠 **Servidor**\n{nome_servidor}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Entre no servidor e procure a equipe responsável "
                    "pelo sorteio para receber as instruções do prêmio."
                ),
                color=COR_SUCESSO,
            )

            if BANNER_SORTEIO:
                embed.set_image(url=BANNER_SORTEIO)

            embed.set_footer(
                text="Royalt Giveaway System"
            )

            await usuario.send(embed=embed)
            return True

        except (discord.Forbidden, discord.HTTPException):
            return False
        except Exception as erro:
            print(
                f"[SORTEIOS] Erro na DM de "
                f"{usuario_id}: {erro}"
            )
            return False

    # ========================================================
    # ATUALIZAR MENSAGEM
    # ========================================================

    async def atualizar_mensagem(self, sorteio_id):
        sorteio = self.sorteios.get(str(sorteio_id))

        if sorteio is None:
            return

        canal = self.bot.get_channel(
            int(sorteio["canal"])
        )

        if canal is None:
            return

        try:
            mensagem = await canal.fetch_message(
                int(sorteio["mensagem"])
            )
        except (discord.NotFound, discord.HTTPException):
            return

        view = None

        if not sorteio.get("encerrado", False):
            view = ParticiparView(
                self,
                sorteio_id,
            )

        try:
            await mensagem.edit(
                embed=self.criar_embed(sorteio),
                view=view,
            )
        except discord.HTTPException:
            pass

    # ========================================================
    # ENCERRAR
    # ========================================================

    async def encerrar_sorteio(self, sorteio_id):
        sorteio = self.sorteios.get(str(sorteio_id))

        if sorteio is None:
            return

        if sorteio.get("encerrado", False):
            return

        sorteio["encerrado"] = True

        participantes_ids = list(
            sorteio.get("participantes", [])
        )

        guild = self.bot.get_guild(
            int(sorteio["guild"])
        )

        if guild is None:
            self.salvar_sorteios()
            return

        candidatos = []

        for usuario_id in participantes_ids:
            membro = guild.get_member(
                int(usuario_id)
            )

            if membro:
                candidatos.append(membro)

        quantidade_desejada = min(
            int(sorteio["vencedores"]),
            len(candidatos),
        )

        vencedores = []
        candidatos_restantes = list(candidatos)
        invalidados = []

        while (
            len(vencedores) < quantidade_desejada
            and candidatos_restantes
        ):
            vencedor = self.escolher_vencedor(
                candidatos_restantes,
                sorteio,
            )

            if vencedor is None:
                break

            candidatos_restantes.remove(vencedor)

            atende, motivos = self.verificar_requisitos(
                vencedor,
                sorteio,
            )

            if atende:
                vencedores.append(vencedor)
            else:
                invalidados.append(
                    {
                        "membro": vencedor,
                        "motivos": motivos,
                    }
                )

        sorteio["vencedores_ids"] = [
            membro.id
            for membro in vencedores
        ]

        status_rerolls = []

        for item in invalidados:
            membro = item["membro"]
            motivos = item["motivos"]

            dm_enviada = await self.enviar_dm_requisito(
                membro,
                sorteio,
                motivos,
            )

            status_rerolls.append(
                f"<@{membro.id}>: "
                f"❌ requisito não cumprido | "
                f"DM {'✅' if dm_enviada else '⚠️'}"
            )

        status_dms = []

        for vencedor in vencedores:
            enviada = await self.enviar_dm_vencedor(
                vencedor.id,
                sorteio,
            )

            status_dms.append(
                f"<@{vencedor.id}>: "
                f"{'✅ DM enviada' if enviada else '⚠️ DM não enviada'}"
            )

        self.salvar_sorteios()

        canal = self.bot.get_channel(
            int(sorteio["canal"])
        )

        if canal:
            try:
                mensagem = await canal.fetch_message(
                    int(sorteio["mensagem"])
                )

                await mensagem.edit(
                    embed=self.criar_embed(sorteio),
                    view=None,
                )
            except (discord.NotFound, discord.HTTPException):
                pass

            if vencedores:
                mencoes = " ".join(
                    f"<@{membro.id}>"
                    for membro in vencedores
                )

                await canal.send(
                    "🎉 **SORTEIO ENCERRADO!**\n\n"
                    f"🎁 **Prêmio:** {sorteio['premio']}\n\n"
                    f"🏆 **Vencedor(es):** {mencoes}"
                )
            else:
                await canal.send(
                    "📭 **Sorteio encerrado!**\n\n"
                    "Não foi possível encontrar vencedores "
                    "que cumprissem todos os requisitos."
                )

        vencedores_texto = (
            " ".join(
                f"<@{membro.id}>"
                for membro in vencedores
            )
            if vencedores
            else "Nenhum vencedor"
        )

        rerolls_texto = (
            "\n".join(status_rerolls)
            if status_rerolls
            else "Nenhum reroll automático."
        )

        dms_texto = (
            "\n".join(status_dms)
            if status_dms
            else "Nenhuma DM necessária."
        )

        await self.enviar_log(
            guild,
            "Sorteio encerrado",
            (
                f"🎁 **Prêmio:**\n{sorteio['premio']}\n\n"
                f"📝 **Descrição:**\n"
                f"{sorteio.get('descricao', 'Sem descrição.')}\n\n"
                f"🆔 **ID:** `{sorteio_id}`\n\n"
                f"👥 **Participantes:** **{len(participantes_ids)}**\n\n"
                f"🏆 **Vencedor(es):**\n{vencedores_texto}\n\n"
                f"🔄 **Rerolls automáticos:**\n{rerolls_texto}\n\n"
                f"📩 **DM dos vencedores:**\n{dms_texto}"
            ),
            "🏆",
            COR_SUCESSO,
        )

    # ========================================================
    # LOOP AUTOMÁTICO
    # ========================================================

    @tasks.loop(seconds=15)
    async def tarefa_sorteios(self):
        agora = datetime.now(
            timezone.utc
        ).timestamp()

        for sorteio_id, sorteio in list(
            self.sorteios.items()
        ):
            if sorteio.get("encerrado", False):
                continue

            try:
                fim = float(sorteio["fim"])
            except (KeyError, ValueError, TypeError):
                continue

            if agora >= fim:
                await self.encerrar_sorteio(
                    sorteio_id
                )

    @tarefa_sorteios.before_loop
    async def antes_tarefa(self):
        await self.bot.wait_until_ready()


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Sorteios(bot))
