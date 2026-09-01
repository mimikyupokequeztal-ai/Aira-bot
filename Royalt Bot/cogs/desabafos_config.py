import discord

from discord.ext import commands

from pathlib import Path
from datetime import datetime, timezone

import json


# ============================================================
# CORES
# ============================================================

COR_DESABAFOS = discord.Color.from_rgb(
    128,
    0,
    255
)

COR_SUCESSO = discord.Color.green()
COR_ERRO = discord.Color.red()
COR_AVISO = discord.Color.orange()
COR_INFO = discord.Color.blurple()


# ============================================================
# BANNER PADRÃO
# ============================================================

BANNER_DESABAFOS = ""


# ============================================================
# ARQUIVOS
# ============================================================

PASTA_DATA = Path(
    "data"
)

ARQUIVO_CONFIG = (
    PASTA_DATA / "desabafos_config.json"
)

PASTA_DATA.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURAÇÃO PADRÃO
# ============================================================

def configuracao_padrao():

    return {

        # ----------------------------------------------------
        # Estrutura
        # ----------------------------------------------------

        "categoria_id": None,

        "cargo_staff_id": None,

        "canal_logs_id": None,

        # ----------------------------------------------------
        # Painel
        # ----------------------------------------------------

        "painel_canal_id": None,

        "painel_mensagem_id": None,

        "painel_titulo": (
            "🫂 ROYALT • ESPAÇO DE DESABAFOS"
        ),

        "painel_descricao": (
            "Precisa conversar?\n\n"

            "Você pode abrir uma conversa "
            "privada com uma pessoa escolhida "
            "por você.\n\n"

            "Também pode conversar de forma "
            "anônima com o Royalt."
        ),

        "painel_banner": BANNER_DESABAFOS,

        # ----------------------------------------------------
        # Privacidade
        # ----------------------------------------------------

        # True:
        # o participante pode escolher desativar
        # a transcrição dentro do atendimento.
        #
        # False:
        # nenhum atendimento poderá criar
        # transcrição pelo sistema.
        #

        "transcricao_permitida": True,

        # ----------------------------------------------------
        # Estatísticas
        # ----------------------------------------------------

        "contador": 0
    }


# ============================================================
# CARREGAR
# ============================================================

def carregar_config():

    if not ARQUIVO_CONFIG.exists():

        return {}

    try:

        with open(
            ARQUIVO_CONFIG,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(
                arquivo
            )

            if isinstance(
                dados,
                dict
            ):

                return dados

            return {}

    except (
        json.JSONDecodeError,
        OSError
    ) as erro:

        print(
            "[DESABAFOS-CONFIG] "
            f"Erro carregando configuração: {erro}"
        )

        return {}


# ============================================================
# SALVAR
# ============================================================

def salvar_config(
    dados
):

    try:

        with open(
            ARQUIVO_CONFIG,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    except OSError as erro:

        print(
            "[DESABAFOS-CONFIG] "
            f"Erro salvando configuração: {erro}"
        )


# ============================================================
# PEGAR CONFIGURAÇÃO DO SERVIDOR
# ============================================================

def obter_configuracao(
    configuracoes,
    guild
):

    guild_id = str(
        guild.id
    )

    padrao = configuracao_padrao()

    if guild_id not in configuracoes:

        configuracoes[
            guild_id
        ] = padrao.copy()

    config = configuracoes[
        guild_id
    ]

    # --------------------------------------------------------
    # Compatibilidade com configurações antigas
    # --------------------------------------------------------

    for chave, valor in padrao.items():

        if chave not in config:

            config[
                chave
            ] = valor

    return config


# ============================================================
# VIEW PRINCIPAL
# ============================================================

class DesabafosConfigView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        autor
    ):

        super().__init__(
            timeout=600
        )

        self.cog = cog
        self.autor = autor

    # ========================================================
    # SEGURANÇA
    # ========================================================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.autor.id:

            await interaction.response.send_message(
                "❌ Apenas o administrador que abriu "
                "este painel pode utilizá-lo.",
                ephemeral=True
            )

            return False

        if not (
            interaction.user.guild_permissions.manage_guild
            or interaction.user.guild_permissions.administrator
        ):

            await interaction.response.send_message(
                "❌ Você não possui permissão "
                "**Gerenciar Servidor**.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # CANAL DE LOGS
    # ========================================================

    @discord.ui.button(
        label="Canal de Logs",
        emoji="📁",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def canal_logs(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="📁 CANAL DE LOGS",
            description=(
                "Selecione o canal que receberá "
                "os eventos administrativos.\n\n"

                "🔐 **Privacidade**\n"
                "O sistema não envia as mensagens "
                "normais da conversa para os logs "
                "durante o atendimento."
            ),
            color=COR_INFO
        )

        await interaction.response.send_message(
            embed=embed,
            view=SelecionarLogsView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # CATEGORIA
    # ========================================================

    @discord.ui.button(
        label="Categoria",
        emoji="🗂️",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def categoria(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🗂️ CATEGORIA DOS DESABAFOS",
            description=(
                "Selecione a categoria onde "
                "os canais privados serão criados."
            ),
            color=COR_INFO
        )

        await interaction.response.send_message(
            embed=embed,
            view=SelecionarCategoriaView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # EQUIPE
    # ========================================================

    @discord.ui.button(
        label="Equipe",
        emoji="👥",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def equipe(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="👥 EQUIPE DE ATENDIMENTO",
            description=(
                "Selecione o cargo que poderá "
                "atender os desabafos normais.\n\n"

                "🔐 **Importante:**\n"
                "Desabafos privados e anônimos "
                "não adicionam esse cargo "
                "automaticamente."
            ),
            color=COR_INFO
        )

        await interaction.response.send_message(
            embed=embed,
            view=SelecionarStaffView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # EDITAR PAINEL
    # ========================================================

    @discord.ui.button(
        label="Editar Painel",
        emoji="📝",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def editar_painel(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            EditarPainelModal(
                self.cog,
                interaction.guild
            )
        )

    # ========================================================
    # PRÉ-VISUALIZAR
    # ========================================================

    @discord.ui.button(
        label="Pré-visualizar",
        emoji="👁️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def preview(
        self,
        interaction,
        button
    ):

        # ----------------------------------------------------
        # Pega o Cog real dos atendimentos
        # ----------------------------------------------------

        cog_desabafos = (
            self.cog.bot.get_cog(
                "Desabafos"
            )
        )

        if cog_desabafos is None:

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ SISTEMA NÃO CARREGADO",
                    description=(
                        "O `desabafos.py` não está "
                        "carregado neste momento."
                    ),
                    color=COR_ERRO
                ),
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Criar a View real
        # ----------------------------------------------------

        try:

            from cogs.desabafos import (
                PainelDesabafoView
            )

            view = PainelDesabafoView(
                cog_desabafos
            )

        except Exception as erro:

            print(
                "[DESABAFOS-CONFIG] "
                f"Erro criando preview: {erro}"
            )

            await interaction.response.send_message(
                "❌ Não foi possível gerar "
                "a pré-visualização.",
                ephemeral=True
            )

            return

        embed = (
            cog_desabafos
            .criar_embed_painel(
                interaction.guild
            )
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

    # ========================================================
    # TRANSCRIÇÃO
    # ========================================================

    @discord.ui.button(
        label="Transcrição",
        emoji="📄",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def transcricao(
        self,
        interaction,
        button
    ):

        config = self.cog.obter_config(
            interaction.guild
        )

        atual = config.get(
            "transcricao_permitida",
            True
        )

        novo_estado = not atual

        config[
            "transcricao_permitida"
        ] = novo_estado

        self.cog.salvar()

        if novo_estado:

            estado = "✅ Permitida"

            explicacao = (
                "Os participantes poderão "
                "escolher desativar a transcrição "
                "dentro do próprio atendimento."
            )

            cor = COR_SUCESSO

        else:

            estado = "❌ Desativada"

            explicacao = (
                "Nenhum atendimento poderá "
                "gerar transcrição pelo sistema."
            )

            cor = COR_AVISO

        embed = discord.Embed(
            title="📄 CONFIGURAÇÃO DE TRANSCRIÇÃO",
            description=(
                f"**Estado:** {estado}\n\n"
                f"{explicacao}\n\n"

                "🔐 Essa configuração não registra "
                "o conteúdo da conversa em logs "
                "administrativos."
            ),
            color=cor
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

        await self.cog.registrar_evento_config(
            interaction.guild,
            "Configuração de transcrição alterada",
            (
                f"📄 **Estado:** {estado}\n\n"
                f"👤 **Administrador:** "
                f"{interaction.user.mention}"
            ),
            "📄",
            cor
        )

    # ========================================================
    # PUBLICAR
    # ========================================================

    @discord.ui.button(
        label="Publicar Painel",
        emoji="📢",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def publicar(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            embed=discord.Embed(
                title="📢 PUBLICAR PAINEL",
                description=(
                    "Selecione o canal onde o painel "
                    "de desabafos será publicado."
                ),
                color=COR_INFO
            ),
            view=SelecionarPublicacaoView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # CONFIGURAÇÃO
    # ========================================================

    @discord.ui.button(
        label="Ver Configuração",
        emoji="⚙️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def configuracao(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            embed=self.cog.criar_embed_config(
                interaction.guild
            ),
            ephemeral=True
        )

    # ========================================================
    # FECHAR
    # ========================================================

    @discord.ui.button(
        label="Fechar",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def fechar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="⚙️ Painel de configuração fechado.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# SELECT DE LOGS
# ============================================================

class SelecionarLogsView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=120
        )

        self.add_item(
            SelecionarLogs(
                cog
            )
        )


class SelecionarLogs(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Selecione o canal de logs...",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        canal = interaction.guild.get_channel(
            self.values[0].id
        )

        if canal is None:

            await interaction.response.send_message(
                "❌ Canal não encontrado.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        config[
            "canal_logs_id"
        ] = canal.id

        self.cog.salvar()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ LOGS CONFIGURADOS",
                description=(
                    f"Os eventos administrativos "
                    f"serão enviados para "
                    f"{canal.mention}."
                ),
                color=COR_SUCESSO
            ),
            ephemeral=True
        )

        await self.cog.registrar_evento_config(
            interaction.guild,
            "Canal de logs alterado",
            (
                f"📁 **Novo canal:** "
                f"{canal.mention}\n\n"
                f"👤 **Administrador:** "
                f"{interaction.user.mention}"
            ),
            "📁",
            COR_INFO
        )


# ============================================================
# SELECT DE CATEGORIA
# ============================================================

class SelecionarCategoriaView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=120
        )

        self.add_item(
            SelecionarCategoria(
                cog
            )
        )


class SelecionarCategoria(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Selecione a categoria...",
            channel_types=[
                discord.ChannelType.category
            ],
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        categoria = interaction.guild.get_channel(
            self.values[0].id
        )

        if categoria is None:

            await interaction.response.send_message(
                "❌ Categoria não encontrada.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        config[
            "categoria_id"
        ] = categoria.id

        self.cog.salvar()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ CATEGORIA CONFIGURADA",
                description=(
                    "Os novos atendimentos serão "
                    f"criados em **{categoria.name}**."
                ),
                color=COR_SUCESSO
            ),
            ephemeral=True
        )

        await self.cog.registrar_evento_config(
            interaction.guild,
            "Categoria alterada",
            (
                f"🗂️ **Categoria:** "
                f"**{categoria.name}**\n\n"
                f"👤 **Administrador:** "
                f"{interaction.user.mention}"
            ),
            "🗂️",
            COR_INFO
        )


# ============================================================
# SELECT DE STAFF
# ============================================================

class SelecionarStaffView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=120
        )

        self.add_item(
            SelecionarStaff(
                cog
            )
        )


class SelecionarStaff(
    discord.ui.RoleSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Selecione o cargo da equipe...",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        cargo = self.values[0]

        if cargo.is_default():

            await interaction.response.send_message(
                "❌ @everyone não pode ser "
                "utilizado como equipe.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        config[
            "cargo_staff_id"
        ] = cargo.id

        self.cog.salvar()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ EQUIPE CONFIGURADA",
                description=(
                    f"O cargo responsável agora é "
                    f"{cargo.mention}."
                ),
                color=COR_SUCESSO
            ),
            ephemeral=True
        )

        await self.cog.registrar_evento_config(
            interaction.guild,
            "Equipe de atendimento alterada",
            (
                f"👥 **Cargo:** "
                f"{cargo.mention}\n\n"
                f"👤 **Administrador:** "
                f"{interaction.user.mention}"
            ),
            "👥",
            COR_INFO
        )


# ============================================================
# SELECT DE PUBLICAÇÃO
# ============================================================

class SelecionarPublicacaoView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=120
        )

        self.add_item(
            SelecionarPublicacao(
                cog
            )
        )


class SelecionarPublicacao(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Selecione o canal do painel...",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        canal = interaction.guild.get_channel(
            self.values[0].id
        )

        if canal is None:

            await interaction.response.send_message(
                "❌ Canal não encontrado.",
                ephemeral=True
            )

            return

        sucesso = await self.cog.publicar_painel(
            interaction.guild,
            canal
        )

        if sucesso:

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="✅ PAINEL PUBLICADO",
                    description=(
                        f"O painel de desabafos "
                        f"foi publicado em "
                        f"{canal.mention}."
                    ),
                    color=COR_SUCESSO
                ),
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ FALHA AO PUBLICAR",
                    description=(
                        "Não consegui publicar o painel.\n\n"
                        "Verifique minhas permissões "
                        "de enviar mensagens, embeds "
                        "e usar componentes."
                    ),
                    color=COR_ERRO
                ),
                ephemeral=True
            )


# ============================================================
# MODAL DO PAINEL
# ============================================================

class EditarPainelModal(
    discord.ui.Modal
):

    def __init__(
        self,
        cog,
        guild
    ):

        super().__init__(
            title="📝 EDITAR PAINEL"
        )

        self.cog = cog
        self.guild = guild

        config = cog.obter_config(
            guild
        )

        self.titulo = discord.ui.TextInput(
            label="Título",
            default=config.get(
                "painel_titulo",
                "🫂 ROYALT • ESPAÇO DE DESABAFOS"
            ),
            placeholder="Título do painel",
            max_length=256,
            required=True
        )

        self.descricao = discord.ui.TextInput(
            label="Descrição",
            default=config.get(
                "painel_descricao",
                ""
            ),
            placeholder="Explique como funciona",
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True
        )

        self.banner = discord.ui.TextInput(
            label="URL do Banner",
            default=config.get(
                "painel_banner",
                ""
            ),
            placeholder="https://...",
            max_length=1000,
            required=False
        )

        self.add_item(
            self.titulo
        )

        self.add_item(
            self.descricao
        )

        self.add_item(
            self.banner
        )

    async def on_submit(
        self,
        interaction
    ):

        config = self.cog.obter_config(
            interaction.guild
        )

        titulo = self.titulo.value.strip()
        descricao = self.descricao.value.strip()
        banner = self.banner.value.strip()

        if not titulo:

            await interaction.response.send_message(
                "❌ O título não pode ficar vazio.",
                ephemeral=True
            )

            return

        if not descricao:

            await interaction.response.send_message(
                "❌ A descrição não pode ficar vazia.",
                ephemeral=True
            )

            return

        config[
            "painel_titulo"
        ] = titulo

        config[
            "painel_descricao"
        ] = descricao

        config[
            "painel_banner"
        ] = banner

        self.cog.salvar()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ PAINEL ATUALIZADO",
                description=(
                    "O conteúdo do painel foi "
                    "atualizado com sucesso.\n\n"

                    "Use **Pré-visualizar** para "
                    "conferir antes de publicar."
                ),
                color=COR_SUCESSO
            ),
            ephemeral=True
        )

        await self.cog.registrar_evento_config(
            interaction.guild,
            "Painel atualizado",
            (
                f"📝 **Título:** "
                f"{titulo}\n\n"

                f"👤 **Administrador:** "
                f"{interaction.user.mention}"
            ),
            "📝",
            COR_INFO
        )


# ============================================================
# COG
# ============================================================

class DesabafosConfig(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.configuracoes = (
            carregar_config()
        )

    # ========================================================
    # SALVAR
    # ========================================================

    def salvar(
        self
    ):

        salvar_config(
            self.configuracoes
        )

    # ========================================================
    # PEGAR CONFIG
    # ========================================================

    def obter_config(
        self,
        guild
    ):

        config = obter_configuracao(
            self.configuracoes,
            guild
        )

        self.salvar()

        return config

    # ========================================================
    # CANAL DE LOGS
    # ========================================================

    def obter_canal_logs(
        self,
        guild
    ):

        config = self.obter_config(
            guild
        )

        canal_id = config.get(
            "canal_logs_id"
        )

        if not canal_id:

            return None

        canal = guild.get_channel(
            int(canal_id)
        )

        if isinstance(
            canal,
            discord.TextChannel
        ):

            return canal

        return None

    # ========================================================
    # LOG ADMINISTRATIVO
    # ========================================================

    async def registrar_evento_config(
        self,
        guild,
        titulo,
        descricao,
        emoji="📜",
        cor=COR_INFO
    ):

        canal = self.obter_canal_logs(
            guild
        )

        if canal is None:

            return

        embed = discord.Embed(
            title=f"{emoji} {titulo}",
            description=descricao,
            color=cor,
            timestamp=datetime.now(
                timezone.utc
            )
        )

        embed.set_footer(
            text=(
                "Royalt Desabafos "
                "• Configuration Logs"
            )
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                "[DESABAFOS-CONFIG] "
                "Sem permissão para enviar logs."
            )

        except discord.HTTPException as erro:

            print(
                f"[DESABAFOS-CONFIG] "
                f"Erro no log: {erro}"
            )

    # ========================================================
    # EMBED DE CONFIGURAÇÃO
    # ========================================================

    def criar_embed_config(
        self,
        guild
    ):

        config = self.obter_config(
            guild
        )

        categoria = None
        staff = None
        logs = None
        painel = None

        if config.get(
            "categoria_id"
        ):

            categoria = guild.get_channel(
                int(
                    config[
                        "categoria_id"
                    ]
                )
            )

        if config.get(
            "cargo_staff_id"
        ):

            staff = guild.get_role(
                int(
                    config[
                        "cargo_staff_id"
                    ]
                )
            )

        if config.get(
            "canal_logs_id"
        ):

            logs = guild.get_channel(
                int(
                    config[
                        "canal_logs_id"
                    ]
                )
            )

        if config.get(
            "painel_canal_id"
        ):

            painel = guild.get_channel(
                int(
                    config[
                        "painel_canal_id"
                    ]
                )
            )

        transcricao = config.get(
            "transcricao_permitida",
            True
        )

        transcricao_texto = (
            "✅ Permitida"
            if transcricao
            else "❌ Desativada"
        )

        embed = discord.Embed(
            title=(
                "⚙️ ROYALT • "
                "CONFIGURAÇÃO DE DESABAFOS"
            ),
            description=(
                "Painel administrativo do "
                "Espaço de Desabafos.\n\n"

                "🔐 **Privacidade:** "
                "o conteúdo das conversas "
                "não é enviado para logs "
                "durante o atendimento."
            ),
            color=COR_DESABAFOS
        )

        embed.add_field(
            name="🗂️ Categoria",
            value=(
                categoria.mention
                if categoria
                else "❌ Não configurada"
            ),
            inline=False
        )

        embed.add_field(
            name="👥 Equipe",
            value=(
                staff.mention
                if staff
                else "❌ Não configurada"
            ),
            inline=False
        )

        embed.add_field(
            name="📁 Canal de Logs",
            value=(
                logs.mention
                if logs
                else "❌ Não configurado"
            ),
            inline=False
        )

        embed.add_field(
            name="📢 Painel",
            value=(
                painel.mention
                if painel
                else "❌ Não publicado"
            ),
            inline=False
        )

        embed.add_field(
            name="📄 Transcrição",
            value=transcricao_texto,
            inline=True
        )

        embed.add_field(
            name="🔢 Atendimentos",
            value=(
                f"**{config.get('contador', 0)}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🟢 Sistema",
            value="Ativo",
            inline=True
        )

        embed.set_footer(
            text="Royalt • Desabafos Config"
        )

        return embed

    # ========================================================
    # EMBED DO PAINEL
    # ========================================================

    def criar_embed_painel(
        self,
        guild
    ):

        config = self.obter_config(
            guild
        )

        embed = discord.Embed(
            title=config.get(
                "painel_titulo",
                "🫂 ROYALT • ESPAÇO DE DESABAFOS"
            ),
            description=config.get(
                "painel_descricao",
                "Precisa conversar?"
            ),
            color=COR_DESABAFOS
        )

        banner = config.get(
            "painel_banner",
            BANNER_DESABAFOS
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.add_field(
            name="🫂 Desabafo Privado",
            value=(
                "Escolha uma pessoa específica "
                "para participar da conversa."
            ),
            inline=False
        )

        embed.add_field(
            name="🕶️ Desabafo Anônimo",
            value=(
                "Converse com o Royalt em um "
                "espaço privado."
            ),
            inline=False
        )

        embed.set_footer(
            text="Royalt • Espaço de Desabafos"
        )

        return embed

    # ========================================================
    # CRIAR VIEW DO PAINEL
    # ========================================================

    def criar_view_painel(
        self
    ):

        cog_desabafos = (
            self.bot.get_cog(
                "Desabafos"
            )
        )

        if cog_desabafos is None:

            return None

        try:

            from cogs.desabafos import (
                PainelDesabafoView
            )

            return PainelDesabafoView(
                cog_desabafos
            )

        except Exception as erro:

            print(
                "[DESABAFOS-CONFIG] "
                f"Erro criando View: {erro}"
            )

            return None

    # ========================================================
    # PUBLICAR PAINEL
    # ========================================================

    async def publicar_painel(
        self,
        guild,
        canal
    ):

        view = self.criar_view_painel()

        if view is None:

            print(
                "[DESABAFOS-CONFIG] "
                "Desabafos não está carregado."
            )

            return False

        embed = self.criar_embed_painel(
            guild
        )

        try:

            mensagem = await canal.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            print(
                "[DESABAFOS-CONFIG] "
                "Sem permissão para publicar painel."
            )

            return False

        except discord.HTTPException as erro:

            print(
                "[DESABAFOS-CONFIG] "
                f"Erro publicando painel: {erro}"
            )

            return False

        config = self.obter_config(
            guild
        )

        config[
            "painel_canal_id"
        ] = canal.id

        config[
            "painel_mensagem_id"
        ] = mensagem.id

        self.salvar()

        await self.registrar_evento_config(
            guild,
            "Painel de desabafos publicado",
            (
                f"📢 **Canal:** "
                f"{canal.mention}\n\n"

                f"🆔 **Mensagem:** "
                f"`{mensagem.id}`"
            ),
            "📢",
            COR_SUCESSO
        )

        return True

    # ========================================================
    # COMANDO
    # ========================================================

    @commands.command(
        name="desabafosconfig",
        aliases=[
            "desabafoconfig",
            "configdesabafos"
        ],
        description=(
            "Abre a configuração do sistema "
            "de desabafos."
        )
    )
    @commands.guild_only()
    @commands.has_permissions(
        manage_guild=True
    )
    async def desabafosconfig(
        self,
        ctx
    ):

        embed = self.criar_embed_config(
            ctx.guild
        )

        view = DesabafosConfigView(
            self,
            ctx.author
        )

        await ctx.send(
            embed=embed,
            view=view
        )


# ============================================================
# ERRO DO COMANDO
# ============================================================

async def tratar_erro(
    ctx,
    erro
):

    if isinstance(
        erro,
        commands.MissingPermissions
    ):

        await ctx.send(
            embed=discord.Embed(
                title="❌ SEM PERMISSÃO",
                description=(
                    "Você precisa de "
                    "**Gerenciar Servidor** "
                    "para usar esse comando."
                ),
                color=COR_ERRO
            )
        )

        return

    if isinstance(
        erro,
        commands.NoPrivateMessage
    ):

        await ctx.send(
            "❌ Esse comando só funciona em servidores."
        )

        return

    raise erro


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        DesabafosConfig(
            bot
        )
    )