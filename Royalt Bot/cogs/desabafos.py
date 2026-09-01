import asyncio
import discord

from discord.ext import commands

from pathlib import Path
from datetime import datetime, timezone

import io
import json
import re


# ============================================================
# CORES
# ============================================================

COR_DESABAFO = discord.Color.from_rgb(
    128,
    0,
    255
)

COR_ANONIMO = discord.Color.dark_purple()

COR_SUCESSO = discord.Color.green()

COR_ERRO = discord.Color.red()

COR_AVISO = discord.Color.orange()

COR_INFO = discord.Color.blurple()


# ============================================================
# BANNER
# ============================================================

BANNER_DESABAFOS = ""


# ============================================================
# ARQUIVOS
# ============================================================

PASTA_DATA = Path(
    "data"
)

ARQUIVO_DESABAFOS = (
    PASTA_DATA / "desabafos.json"
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

        "categoria_id": None,

        "cargo_staff_id": None,

        "canal_logs_id": None,

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

        "transcricao_permitida": True,

        "contador": 0
    }


# ============================================================
# JSON
# ============================================================

def carregar_json(
    arquivo,
    padrao
):

    if not arquivo.exists():

        return padrao

    try:

        with open(
            arquivo,
            "r",
            encoding="utf-8"
        ) as arquivo_json:

            dados = json.load(
                arquivo_json
            )

            return dados

    except (
        json.JSONDecodeError,
        OSError
    ) as erro:

        print(
            f"[DESABAFOS] Erro lendo "
            f"{arquivo}: {erro}"
        )

        return padrao


def salvar_json(
    arquivo,
    dados
):

    try:

        with open(
            arquivo,
            "w",
            encoding="utf-8"
        ) as arquivo_json:

            json.dump(
                dados,
                arquivo_json,
                ensure_ascii=False,
                indent=4
            )

    except OSError as erro:

        print(
            f"[DESABAFOS] Erro salvando "
            f"{arquivo}: {erro}"
        )


# ============================================================
# LIMPAR NOME
# ============================================================

def limpar_nome(
    nome
):

    nome = re.sub(
        r"[^a-zA-Z0-9_-]",
        "-",
        nome
    )

    nome = re.sub(
        r"-+",
        "-",
        nome
    )

    nome = nome.strip(
        "-"
    )

    if not nome:

        nome = "usuario"

    return nome.lower()[:24]


# ============================================================
# PAINEL PÚBLICO
# ============================================================

class PainelDesabafoView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=None
        )

        self.cog = cog

        # ----------------------------------------------------
        # DESABAFO PRIVADO
        # ----------------------------------------------------

        botao_privado = discord.ui.Button(
            label="Desabafo Privado",
            emoji="🫂",
            style=discord.ButtonStyle.success,
            custom_id="royalt_desabafo_privado"
        )

        botao_privado.callback = (
            self.abrir_privado
        )

        self.add_item(
            botao_privado
        )

        # ----------------------------------------------------
        # DESABAFO ANÔNIMO
        # ----------------------------------------------------

        botao_anonimo = discord.ui.Button(
            label="Desabafo Anônimo",
            emoji="🕶️",
            style=discord.ButtonStyle.secondary,
            custom_id="royalt_desabafo_anonimo"
        )

        botao_anonimo.callback = (
            self.abrir_anonimo
        )

        self.add_item(
            botao_anonimo
        )

    # ========================================================
    # PRIVADO
    # ========================================================

    async def abrir_privado(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="🫂 DESABAFO PRIVADO",
            description=(
                "Escolha a pessoa que você deseja "
                "adicionar à conversa.\n\n"

                "🔐 O canal será criado apenas "
                "para você, a pessoa escolhida "
                "e o Royalt.\n\n"

                "👥 O cargo da equipe **não será "
                "adicionado automaticamente**."
            ),
            color=COR_DESABAFO
        )

        await interaction.response.send_message(
            embed=embed,
            view=EscolherPessoaView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # ANÔNIMO
    # ========================================================

    async def abrir_anonimo(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="🕶️ DESABAFO ANÔNIMO",
            description=(
                "Você pode criar um espaço privado "
                "para conversar com o Royalt.\n\n"

                "🔐 Nenhum cargo de staff será "
                "adicionado ao canal.\n\n"

                "🤖 O Royalt poderá conversar "
                "com você e, quando necessário, "
                "utilizar o sistema de pesquisa."
            ),
            color=COR_ANONIMO
        )

        if BANNER_DESABAFOS:

            embed.set_image(
                url=BANNER_DESABAFOS
            )

        await interaction.response.send_message(
            embed=embed,
            view=ConfirmarAnonimoView(
                self.cog
            ),
            ephemeral=True
        )


# ============================================================
# ESCOLHER PESSOA
# ============================================================

class EscolherPessoaView(
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
            EscolherPessoaSelect(
                cog
            )
        )


class EscolherPessoaSelect(
    discord.ui.UserSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Escolha uma pessoa...",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        pessoa = self.values[0]

        if pessoa.id == interaction.user.id:

            await interaction.response.send_message(
                "❌ Você não pode escolher a si mesmo.",
                ephemeral=True
            )

            return

        await self.cog.criar_desabafo_privado(
            interaction,
            pessoa
        )


# ============================================================
# CONFIRMAÇÃO ANÔNIMO
# ============================================================

class ConfirmarAnonimoView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=120
        )

        self.cog = cog

    # ========================================================
    # CRIAR
    # ========================================================

    @discord.ui.button(
        label="Criar espaço",
        emoji="🕶️",
        style=discord.ButtonStyle.success
    )
    async def criar(
        self,
        interaction,
        button
    ):

        # IMPORTANTE:
        # Não usamos defer aqui.
        #
        # criar_desabafo_anonimo() verifica sozinho
        # se a Interaction já foi respondida.
        #

        await self.cog.criar_desabafo_anonimo(
            interaction
        )

        self.stop()

    # ========================================================
    # CANCELAR
    # ========================================================

    @discord.ui.button(
        label="Cancelar",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def cancelar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="↩️ Criação cancelada.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# VIEW DO DESABAFO
# ============================================================

class DesabafoView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        desabafo_id
    ):

        super().__init__(
            timeout=None
        )

        self.cog = cog

        self.desabafo_id = str(
            desabafo_id
        )

        # ----------------------------------------------------
        # ASSUMIR
        # ----------------------------------------------------

        self.adicionar_botao(
            label="Assumir",
            emoji="👤",
            estilo=discord.ButtonStyle.primary,
            custom_id=(
                f"royalt_desabafo_assumir:"
                f"{self.desabafo_id}"
            ),
            callback=self.assumir
        )

        # ----------------------------------------------------
        # ATENDIDO
        # ----------------------------------------------------

        self.adicionar_botao(
            label="Atendido",
            emoji="✅",
            estilo=discord.ButtonStyle.success,
            custom_id=(
                f"royalt_desabafo_atendido:"
                f"{self.desabafo_id}"
            ),
            callback=self.atendido
        )

        # ----------------------------------------------------
        # TRANSCRIÇÃO
        # ----------------------------------------------------

        self.adicionar_botao(
            label="Transcrição",
            emoji="📄",
            estilo=discord.ButtonStyle.secondary,
            custom_id=(
                f"royalt_desabafo_transcricao:"
                f"{self.desabafo_id}"
            ),
            callback=self.alternar_transcricao
        )

        # ----------------------------------------------------
        # ARQUIVAR
        # ----------------------------------------------------

        self.adicionar_botao(
            label="Arquivar",
            emoji="📦",
            estilo=discord.ButtonStyle.secondary,
            custom_id=(
                f"royalt_desabafo_arquivar:"
                f"{self.desabafo_id}"
            ),
            callback=self.arquivar
        )

        # ----------------------------------------------------
        # REABRIR
        # ----------------------------------------------------

        self.adicionar_botao(
            label="Reabrir",
            emoji="🔓",
            estilo=discord.ButtonStyle.primary,
            custom_id=(
                f"royalt_desabafo_reabrir:"
                f"{self.desabafo_id}"
            ),
            callback=self.reabrir
        )

        # ----------------------------------------------------
        # FINALIZAR
        # ----------------------------------------------------

        self.adicionar_botao(
            label="Finalizar",
            emoji="🔒",
            estilo=discord.ButtonStyle.danger,
            custom_id=(
                f"royalt_desabafo_finalizar:"
                f"{self.desabafo_id}"
            ),
            callback=self.finalizar
        )

    # ========================================================
    # ADICIONAR BOTÃO
    # ========================================================

    def adicionar_botao(
        self,
        label,
        emoji,
        estilo,
        custom_id,
        callback
    ):

        botao = discord.ui.Button(
            label=label,
            emoji=emoji,
            style=estilo,
            custom_id=custom_id
        )

        botao.callback = callback

        self.add_item(
            botao
        )

    # ========================================================
    # VERIFICAR PARTICIPANTE
    # ========================================================

    def eh_participante(
        self,
        interaction,
        desabafo
    ):

        participantes = [
            int(uid)
            for uid in desabafo.get(
                "participantes",
                []
            )
        ]

        return (
            interaction.user.id
            in participantes
        )

    # ========================================================
    # VERIFICAR STAFF
    # ========================================================

    async def verificar_staff(
        self,
        interaction
    ):

        if self.cog.usuario_equipe(
            interaction.user,
            interaction.guild
        ):

            return True

        await interaction.response.send_message(
            "❌ Esta ação é exclusiva da equipe.",
            ephemeral=True
        )

        return False

    # ========================================================
    # ASSUMIR
    # ========================================================

    async def assumir(
        self,
        interaction
    ):

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:

            await interaction.response.send_message(
                "❌ Atendimento não encontrado.",
                ephemeral=True
            )

            return

        if desabafo.get(
            "modo"
        ) in (
            "privado",
            "anonimo"
        ):

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔐 ATENDIMENTO PRIVADO",
                    description=(
                        "Este atendimento foi criado "
                        "sem acesso automático da staff.\n\n"

                        "O cargo da equipe não possui "
                        "acesso a esta conversa."
                    ),
                    color=COR_AVISO
                ),
                ephemeral=True
            )

            return

        if not await self.verificar_staff(
            interaction
        ):

            return

        desabafo[
            "responsavel"
        ] = interaction.user.id

        desabafo[
            "status"
        ] = "em_atendimento"

        desabafo[
            "assumido_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.cog.salvar_desabafos()

        await self.cog.atualizar_embed_desabafo(
            interaction.channel,
            self.desabafo_id
        )

        await interaction.response.send_message(
            f"👤 Atendimento assumido por "
            f"{interaction.user.mention}."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Atendimento assumido",
            (
                f"🆔 **Atendimento:** "
                f"`#{self.desabafo_id}`\n\n"

                f"👤 **Staff:** "
                f"{interaction.user.mention}"
            ),
            "👤",
            COR_INFO
        )

    # ========================================================
    # ATENDIDO
    # ========================================================

    async def atendido(
        self,
        interaction
    ):

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:
            return

        if not await self.verificar_staff(
            interaction
        ):

            return

        if desabafo.get(
            "modo"
        ) in (
            "privado",
            "anonimo"
        ):

            await interaction.response.send_message(
                "🔐 Este atendimento não utiliza "
                "o fluxo de atendimento da staff.",
                ephemeral=True
            )

            return

        desabafo[
            "status"
        ] = "atendido"

        desabafo[
            "responsavel"
        ] = interaction.user.id

        desabafo[
            "atendido_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.cog.salvar_desabafos()

        await self.cog.atualizar_embed_desabafo(
            interaction.channel,
            self.desabafo_id
        )

        await interaction.response.send_message(
            "✅ Atendimento marcado como atendido."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Atendimento marcado como atendido",
            (
                f"🆔 **Atendimento:** "
                f"`#{self.desabafo_id}`\n\n"

                f"👤 **Staff:** "
                f"{interaction.user.mention}"
            ),
            "✅",
            COR_SUCESSO
        )

    # ========================================================
    # TRANSCRIÇÃO
    # ========================================================

    async def alternar_transcricao(
        self,
        interaction
    ):

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:

            await interaction.response.send_message(
                "❌ Atendimento não encontrado.",
                ephemeral=True
            )

            return

        if not self.eh_participante(
            interaction,
            desabafo
        ):

            await interaction.response.send_message(
                "❌ Apenas um participante desta "
                "conversa pode alterar a transcrição.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        permitido = config.get(
            "transcricao_permitida",
            True
        )

        if not permitido:

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔒 TRANSCRIÇÃO BLOQUEADA",
                    description=(
                        "O servidor desativou o sistema "
                        "de transcrição.\n\n"

                        "O conteúdo desta conversa "
                        "não será enviado como "
                        "transcrição para os logs."
                    ),
                    color=COR_AVISO
                ),
                ephemeral=True
            )

            return

        atual = desabafo.get(
            "transcricao",
            True
        )

        novo_estado = not atual

        desabafo[
            "transcricao"
        ] = novo_estado

        self.cog.salvar_desabafos()

        if novo_estado:

            titulo = (
                "📄 TRANSCRIÇÃO ATIVADA"
            )

            descricao = (
                "A transcrição está ativada.\n\n"
                "Quando a conversa for finalizada, "
                "o histórico poderá ser enviado "
                "ao canal de logs configurado."
            )

            cor = COR_SUCESSO

        else:

            titulo = (
                "🔒 TRANSCRIÇÃO DESATIVADA"
            )

            descricao = (
                "A transcrição foi desativada.\n\n"
                "Quando a conversa for finalizada, "
                "o conteúdo do atendimento "
                "não será enviado aos logs."
            )

            cor = COR_AVISO

        await self.cog.atualizar_embed_desabafo(
            interaction.channel,
            self.desabafo_id
        )

        await interaction.response.send_message(
            embed=discord.Embed(
                title=titulo,
                description=descricao,
                color=cor
            ),
            ephemeral=True
        )

    # ========================================================
    # ARQUIVAR
    # ========================================================

    async def arquivar(
        self,
        interaction
    ):

        if not await self.verificar_staff(
            interaction
        ):

            return

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:
            return

        if desabafo.get(
            "modo"
        ) in (
            "privado",
            "anonimo"
        ):

            await interaction.response.send_message(
                "🔐 Este atendimento não pertence "
                "ao fluxo de arquivamento da staff.",
                ephemeral=True
            )

            return

        desabafo[
            "status"
        ] = "arquivado"

        desabafo[
            "arquivado_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.cog.salvar_desabafos()

        # ----------------------------------------------------
        # Bloquear mensagens do responsável/autor
        # ----------------------------------------------------

        autor = interaction.guild.get_member(
            int(
                desabafo[
                    "autor"
                ]
            )
        )

        if autor:

            try:

                await interaction.channel.set_permissions(
                    autor,
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )

            except discord.HTTPException:

                pass

        await self.cog.atualizar_embed_desabafo(
            interaction.channel,
            self.desabafo_id
        )

        await interaction.response.send_message(
            "📦 Atendimento arquivado."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Atendimento arquivado",
            (
                f"🆔 **Atendimento:** "
                f"`#{self.desabafo_id}`\n\n"

                f"👤 **Staff:** "
                f"{interaction.user.mention}"
            ),
            "📦",
            COR_AVISO
        )

    # ========================================================
    # REABRIR
    # ========================================================

    async def reabrir(
        self,
        interaction
    ):

        if not await self.verificar_staff(
            interaction
        ):

            return

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:
            return

        if desabafo.get(
            "modo"
        ) in (
            "privado",
            "anonimo"
        ):

            await interaction.response.send_message(
                "🔐 Este atendimento não utiliza "
                "o fluxo da staff.",
                ephemeral=True
            )

            return

        desabafo[
            "status"
        ] = "aberto"

        desabafo.pop(
            "arquivado_em",
            None
        )

        self.cog.salvar_desabafos()

        autor = interaction.guild.get_member(
            int(
                desabafo[
                    "autor"
                ]
            )
        )

        if autor:

            try:

                await interaction.channel.set_permissions(
                    autor,
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )

            except discord.HTTPException:

                pass

        await self.cog.atualizar_embed_desabafo(
            interaction.channel,
            self.desabafo_id
        )

        await interaction.response.send_message(
            "🔓 Atendimento reaberto."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Atendimento reaberto",
            (
                f"🆔 **Atendimento:** "
                f"`#{self.desabafo_id}`\n\n"

                f"👤 **Staff:** "
                f"{interaction.user.mention}"
            ),
            "🔓",
            COR_INFO
        )

    # ========================================================
    # FINALIZAR
    # ========================================================

    async def finalizar(
        self,
        interaction
    ):

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:

            await interaction.response.send_message(
                "❌ Atendimento não encontrado.",
                ephemeral=True
            )

            return

        participante = self.eh_participante(
            interaction,
            desabafo
        )

        staff = self.cog.usuario_equipe(
            interaction.user,
            interaction.guild
        )

        if desabafo.get(
            "modo"
        ) == "privado":

            permitido = participante

        elif desabafo.get(
            "modo"
        ) == "anonimo":

            permitido = participante

        else:

            permitido = (
                participante
                or staff
            )

        if not permitido:

            await interaction.response.send_message(
                "❌ Você não pode finalizar "
                "esta conversa.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔒 FINALIZAR CONVERSA?",
                description=(
                    "A conversa será encerrada.\n\n"

                    "📄 A transcrição será enviada "
                    "somente se estiver ativada.\n\n"

                    "🔐 Se estiver desativada, "
                    "o conteúdo não será enviado "
                    "ao canal de logs.\n\n"

                    "Deseja continuar?"
                ),
                color=COR_ERRO
            ),
            view=ConfirmarFechamentoView(
                self.cog,
                self.desabafo_id
            ),
            ephemeral=True
        )


# ============================================================
# CONFIRMAR FECHAMENTO
# ============================================================

class ConfirmarFechamentoView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        desabafo_id
    ):

        super().__init__(
            timeout=60
        )

        self.cog = cog

        self.desabafo_id = str(
            desabafo_id
        )

    # ========================================================
    # CONFIRMAR
    # ========================================================

    @discord.ui.button(
        label="Sim, finalizar",
        emoji="✅",
        style=discord.ButtonStyle.danger
    )
    async def confirmar(
        self,
        interaction,
        button
    ):

        desabafo = self.cog.desabafos.get(
            self.desabafo_id
        )

        if desabafo is None:

            await interaction.response.send_message(
                "❌ Atendimento não encontrado.",
                ephemeral=True
            )

            return

        participante = (
            interaction.user.id
            in [
                int(uid)
                for uid in desabafo.get(
                    "participantes",
                    []
                )
            ]
        )

        staff = self.cog.usuario_equipe(
            interaction.user,
            interaction.guild
        )

        if desabafo.get(
            "modo"
        ) in (
            "privado",
            "anonimo"
        ):

            permitido = participante

        else:

            permitido = (
                participante
                or staff
            )

        if not permitido:

            await interaction.response.send_message(
                "❌ Você não pode finalizar "
                "esta conversa.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content="🔒 Finalizando conversa...",
            embed=None,
            view=None
        )

        await self.cog.fechar_desabafo(
            interaction.channel,
            self.desabafo_id,
            interaction.user
        )

        self.stop()

    # ========================================================
    # CANCELAR
    # ========================================================

    @discord.ui.button(
        label="Cancelar",
        emoji="❌",
        style=discord.ButtonStyle.secondary
    )
    async def cancelar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="↩️ Encerramento cancelado.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# COG
# ============================================================

class Desabafos(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.desabafos = carregar_json(
            ARQUIVO_DESABAFOS,
            {}
        )

        self.config = carregar_json(
            ARQUIVO_CONFIG,
            {}
        )

        self._views_restauradas = False

    # ========================================================
    # SALVAR DESABAFOS
    # ========================================================

    def salvar_desabafos(
        self
    ):

        salvar_json(
            ARQUIVO_DESABAFOS,
            self.desabafos
        )

    # ========================================================
    # SALVAR CONFIG
    # ========================================================

    def salvar_config(
        self
    ):

        salvar_json(
            ARQUIVO_CONFIG,
            self.config
        )

    # ========================================================
    # CONFIG
    # ========================================================

    def obter_config(
        self,
        guild
    ):

        guild_id = str(
            guild.id
        )

        padrao = configuracao_padrao()

        if guild_id not in self.config:

            self.config[
                guild_id
            ] = padrao.copy()

        config = self.config[
            guild_id
        ]

        for chave, valor in padrao.items():

            config.setdefault(
                chave,
                valor
            )

        return config

    # ========================================================
    # STAFF
    # ========================================================

    def usuario_equipe(
        self,
        membro,
        guild
    ):

        if guild is None:

            return False

        if membro.guild_permissions.administrator:

            return True

        config = self.obter_config(
            guild
        )

        cargo_id = config.get(
            "cargo_staff_id"
        )

        if not cargo_id:

            return False

        return any(
            role.id == int(cargo_id)
            for role in membro.roles
        )

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
            int(
                canal_id
            )
        )

        if isinstance(
            canal,
            discord.TextChannel
        ):

            return canal

        return None

    # ========================================================
    # LOG
    # ========================================================

    async def enviar_log(
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
            text="Royalt Desabafos Logging System"
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                "[DESABAFOS] Sem permissão "
                "para enviar logs."
            )

        except discord.HTTPException as erro:

            print(
                f"[DESABAFOS] Erro no log: {erro}"
            )

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
            color=COR_DESABAFO
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
                "Converse de forma privada "
                "com o Royalt."
            ),
            inline=False
        )

        embed.add_field(
            name="🔐 Privacidade",
            value=(
                "O cargo da staff não é adicionado "
                "automaticamente aos atendimentos "
                "privados e anônimos."
            ),
            inline=False
        )

        embed.set_footer(
            text="Royalt • Espaço de Desabafos"
        )

        return embed

    # ========================================================
    # EMBED DO DESABAFO
    # ========================================================

    def criar_embed_desabafo(
        self,
        desabafo
    ):

        modo = desabafo.get(
            "modo",
            "privado"
        )

        transcricao = desabafo.get(
            "transcricao",
            True
        )

        status = desabafo.get(
            "status",
            "aberto"
        )

        if modo == "anonimo":

            titulo = (
                "🕶️ ROYALT • DESABAFO ANÔNIMO"
            )

            descricao_base = (
                "Esta conversa é privada "
                "entre você e o Royalt."
            )

            cor = COR_ANONIMO

        else:

            titulo = (
                "🫂 ROYALT • DESABAFO PRIVADO"
            )

            descricao_base = (
                "Esta conversa é privada "
                "entre as pessoas escolhidas."
            )

            cor = COR_DESABAFO

        status_map = {

            "aberto":
            "🟢 Aberto",

            "em_atendimento":
            "🟡 Em atendimento",

            "atendido":
            "✅ Atendido",

            "arquivado":
            "📦 Arquivado",

            "fechado":
            "🔒 Fechado"
        }

        status_texto = status_map.get(
            status,
            "🟢 Aberto"
        )

        transcricao_texto = (
            "✅ Ativada"
            if transcricao
            else "🔒 Desativada"
        )

        participantes = desabafo.get(
            "participantes",
            []
        )

        embed = discord.Embed(
            title=titulo,
            description=(
                f"## Espaço privado\n\n"

                f"{descricao_base}\n\n"

                f"📊 **Status:** "
                f"{status_texto}\n\n"

                f"📄 **Transcrição:** "
                f"{transcricao_texto}\n\n"

                f"👥 **Participantes:** "
                f"**{len(participantes)}**\n\n"

                f"🆔 **Atendimento:** "
                f"`#{desabafo['id']}`\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "Converse com respeito e compartilhe "
                "somente o necessário."
            ),
            color=cor
        )

        banner = desabafo.get(
            "banner",
            BANNER_DESABAFOS
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.set_footer(
            text="Royalt • Atendimento Privado"
        )

        return embed

    # ========================================================
    # ENCONTRAR ATENDIMENTO POR CANAL
    # ========================================================

    def obter_desabafo_por_canal(
        self,
        canal_id
    ):

        for desabafo in self.desabafos.values():

            if int(
                desabafo.get(
                    "canal",
                    0
                )
            ) == int(canal_id):

                return desabafo

        return None

    # ========================================================
    # ATENDIMENTO ABERTO DO USUÁRIO
    # ========================================================

    def obter_aberto_usuario(
        self,
        guild_id,
        usuario_id
    ):

        for desabafo in self.desabafos.values():

            if int(
                desabafo.get(
                    "guild",
                    0
                )
            ) != int(guild_id):

                continue

            participantes = [
                int(uid)
                for uid in desabafo.get(
                    "participantes",
                    []
                )
            ]

            if usuario_id not in participantes:

                continue

            if desabafo.get(
                "fechado",
                False
            ):

                continue

            return desabafo

        return None

    # ========================================================
    # RESTAURAR VIEWS
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        if self._views_restauradas:

            return

        self._views_restauradas = True

        # ----------------------------------------------------
        # Painel público
        # ----------------------------------------------------

        try:

            self.bot.add_view(
                PainelDesabafoView(
                    self
                )
            )

        except Exception as erro:

            print(
                "[DESABAFOS] Erro restaurando "
                f"painel: {erro}"
            )

        # ----------------------------------------------------
        # Atendimentos
        # ----------------------------------------------------

        for (
            desabafo_id,
            desabafo
        ) in self.desabafos.items():

            if desabafo.get(
                "fechado",
                False
            ):

                continue

            try:

                self.bot.add_view(
                    DesabafoView(
                        self,
                        desabafo_id
                    )
                )

            except Exception as erro:

                print(
                    "[DESABAFOS] Erro restaurando "
                    f"{desabafo_id}: {erro}"
                )

    # ========================================================
    # CRIAR PERMISSÕES PRIVADAS
    # ========================================================

    def criar_overwrites(
        self,
        guild,
        participantes
    ):

        overwrites = {

            guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            )
        }

        # ----------------------------------------------------
        # BOT
        # ----------------------------------------------------

        if guild.me:

            overwrites[
                guild.me
            ] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
                embed_links=True,
                attach_files=True
            )

        # ----------------------------------------------------
        # PARTICIPANTES
        # ----------------------------------------------------

        for membro in participantes:

            overwrites[
                membro
            ] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        return overwrites

    # ========================================================
    # CRIAR PRIVADO
    # ========================================================

    async def criar_desabafo_privado(
        self,
        interaction,
        pessoa
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Só funciona dentro de servidores.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Responder primeiro
        # ----------------------------------------------------

        if not interaction.response.is_done():

            await interaction.response.defer(
                ephemeral=True
            )

        # ----------------------------------------------------
        # Verificar atendimento existente
        # ----------------------------------------------------

        existente = self.obter_aberto_usuario(
            guild.id,
            interaction.user.id
        )

        if existente:

            canal_existente = guild.get_channel(
                int(
                    existente["canal"]
                )
            )

            if canal_existente:

                await interaction.followup.send(
                    embed=discord.Embed(
                        title="🫂 JÁ EXISTE UM ATENDIMENTO",
                        description=(
                            "Você já possui um "
                            "desabafo aberto:\n\n"
                            f"{canal_existente.mention}"
                        ),
                        color=COR_AVISO
                    ),
                    ephemeral=True
                )

                return

        # ----------------------------------------------------
        # Configuração
        # ----------------------------------------------------

        config = self.obter_config(
            guild
        )

        categoria = None

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

        # ----------------------------------------------------
        # Contador
        # ----------------------------------------------------

        config[
            "contador"
        ] += 1

        numero = config[
            "contador"
        ]

        self.salvar_config()

        desabafo_id = str(
            numero
        ).zfill(4)

        # ----------------------------------------------------
        # Nome
        # ----------------------------------------------------

        nome_usuario = limpar_nome(
            interaction.user.name
        )

        nome_pessoa = limpar_nome(
            pessoa.name
        )

        nome_canal = (
            f"🫂・privado-"
            f"{nome_usuario}-"
            f"{nome_pessoa}-"
            f"{desabafo_id}"
        )

        # ----------------------------------------------------
        # Permissões
        # ----------------------------------------------------

        overwrites = self.criar_overwrites(
            guild,
            [
                interaction.user,
                pessoa
            ]
        )

        # ----------------------------------------------------
        # Criar canal
        # ----------------------------------------------------

        try:

            canal = await guild.create_text_channel(
                name=nome_canal,
                overwrites=overwrites,
                category=categoria,
                reason=(
                    "Royalt • Desabafo privado"
                )
            )

        except discord.Forbidden:

            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ SEM PERMISSÃO",
                    description=(
                        "Não tenho permissão para "
                        "criar canais privados."
                    ),
                    color=COR_ERRO
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as erro:

            print(
                f"[DESABAFOS] Erro criando privado: "
                f"{erro}"
            )

            await interaction.followup.send(
                "❌ Não consegui criar a conversa.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Dados
        # ----------------------------------------------------

        desabafo = {

            "id": desabafo_id,

            "guild": guild.id,

            "canal": canal.id,

            "autor": interaction.user.id,

            "participantes": [
                interaction.user.id,
                pessoa.id
            ],

            "responsavel": None,

            "modo": "privado",

            "status": "aberto",

            "transcricao": config.get(
                "transcricao_permitida",
                True
            ),

            "criado_em": datetime.now(
                timezone.utc
            ).isoformat(),

            "assumido_em": None,

            "atendido_em": None,

            "arquivado_em": None,

            "fechado_em": None,

            "fechado": False,

            "banner": config.get(
                "painel_banner",
                BANNER_DESABAFOS
            )
        }

        self.desabafos[
            desabafo_id
        ] = desabafo

        self.salvar_desabafos()

        # ----------------------------------------------------
        # Embed
        # ----------------------------------------------------

        embed = self.criar_embed_desabafo(
            desabafo
        )

        try:

            await canal.send(
                content=(
                    f"{interaction.user.mention} "
                    f"{pessoa.mention}"
                ),
                embed=embed,
                view=DesabafoView(
                    self,
                    desabafo_id
                )
            )

        except discord.HTTPException as erro:

            print(
                "[DESABAFOS] Erro enviando "
                f"mensagem inicial: {erro}"
            )

        # ----------------------------------------------------
        # Resposta
        # ----------------------------------------------------

        await interaction.followup.send(
            embed=discord.Embed(
                title="🫂 CONVERSA CRIADA",
                description=(
                    "Seu desabafo privado foi criado.\n\n"

                    f"👥 **Pessoa escolhida:** "
                    f"{pessoa.mention}\n\n"

                    f"📁 **Canal:** "
                    f"{canal.mention}\n\n"

                    "🔐 O cargo da staff não "
                    "foi adicionado automaticamente."
                ),
                color=COR_SUCESSO
            ),
            ephemeral=True
        )

        # ----------------------------------------------------
        # Log sem conteúdo
        # ----------------------------------------------------

        await self.enviar_log(
            guild,
            "Desabafo privado criado",
            (
                f"🆔 **Atendimento:** "
                f"`#{desabafo_id}`\n\n"

                f"📁 **Canal:** "
                f"{canal.mention}\n\n"

                "🔐 **Conteúdo da conversa:** "
                "não incluído nos logs."
            ),
            "🫂",
            COR_SUCESSO
        )

    # ========================================================
    # CRIAR ANÔNIMO
    # ========================================================

    async def criar_desabafo_anonimo(
        self,
        interaction
    ):

        guild = interaction.guild

        if guild is None:

            if interaction.response.is_done():

                await interaction.followup.send(
                    "❌ Só funciona em servidores.",
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    "❌ Só funciona em servidores.",
                    ephemeral=True
                )

            return

        # ----------------------------------------------------
        # CORREÇÃO DO InteractionResponded
        # ----------------------------------------------------

        if not interaction.response.is_done():

            await interaction.response.defer(
                ephemeral=True
            )

        # ----------------------------------------------------
        # Verificar existente
        # ----------------------------------------------------

        existente = self.obter_aberto_usuario(
            guild.id,
            interaction.user.id
        )

        if existente:

            canal_existente = guild.get_channel(
                int(
                    existente["canal"]
                )
            )

            if canal_existente:

                await interaction.followup.send(
                    embed=discord.Embed(
                        title="🕶️ DESABAFO JÁ EXISTE",
                        description=(
                            "Você já possui um "
                            "desabafo aberto:\n\n"

                            f"{canal_existente.mention}"
                        ),
                        color=COR_AVISO
                    ),
                    ephemeral=True
                )

                return

        # ----------------------------------------------------
        # Configuração
        # ----------------------------------------------------

        config = self.obter_config(
            guild
        )

        categoria = None

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

        # ----------------------------------------------------
        # Contador
        # ----------------------------------------------------

        config[
            "contador"
        ] += 1

        numero = config[
            "contador"
        ]

        self.salvar_config()

        desabafo_id = str(
            numero
        ).zfill(4)

        # ----------------------------------------------------
        # Nome anônimo
        # ----------------------------------------------------

        nome_canal = (
            f"🕶️・anonimo-{desabafo_id}"
        )

        # ----------------------------------------------------
        # Permissões
        # ----------------------------------------------------

        overwrites = self.criar_overwrites(
            guild,
            [
                interaction.user
            ]
        )

        # ----------------------------------------------------
        # Criar canal
        # ----------------------------------------------------

        try:

            canal = await guild.create_text_channel(
                name=nome_canal,
                overwrites=overwrites,
                category=categoria,
                reason=(
                    "Royalt • Desabafo anônimo"
                )
            )

        except discord.Forbidden:

            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ SEM PERMISSÃO",
                    description=(
                        "Não tenho permissão para "
                        "criar o espaço privado."
                    ),
                    color=COR_ERRO
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as erro:

            print(
                f"[DESABAFOS] Erro criando anônimo: "
                f"{erro}"
            )

            await interaction.followup.send(
                "❌ Não consegui criar "
                "seu espaço anônimo.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Dados
        # ----------------------------------------------------

        desabafo = {

            "id": desabafo_id,

            "guild": guild.id,

            "canal": canal.id,

            "autor": interaction.user.id,

            "participantes": [
                interaction.user.id
            ],

            "responsavel": None,

            "modo": "anonimo",

            "status": "aberto",

            "transcricao": config.get(
                "transcricao_permitida",
                True
            ),

            "criado_em": datetime.now(
                timezone.utc
            ).isoformat(),

            "assumido_em": None,

            "atendido_em": None,

            "arquivado_em": None,

            "fechado_em": None,

            "fechado": False,

            "banner": config.get(
                "painel_banner",
                BANNER_DESABAFOS
            )
        }

        self.desabafos[
            desabafo_id
        ] = desabafo

        self.salvar_desabafos()

        # ----------------------------------------------------
        # Embed
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🕶️ ROYALT • DESABAFO ANÔNIMO",
            description=(
                "## Seu espaço privado está pronto.\n\n"

                "Aqui você pode conversar "
                "diretamente com o Royalt.\n\n"

                "🔐 **Privacidade**\n"
                "O cargo da staff não foi "
                "adicionado ao canal.\n\n"

                "🤖 **Atendimento**\n"
                "O Royalt poderá conversar com você "
                "e utilizar o sistema de pesquisa "
                "quando necessário.\n\n"

                f"📄 **Transcrição inicial:** "
                f"{'Ativada' if desabafo['transcricao'] else 'Desativada'}\n\n"

                f"🆔 **Atendimento:** "
                f"`#{desabafo_id}`"
            ),
            color=COR_ANONIMO
        )

        banner = desabafo.get(
            "banner"
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.set_footer(
            text="Royalt • Desabafo Anônimo"
        )

        try:

            await canal.send(
                embed=embed,
                view=DesabafoView(
                    self,
                    desabafo_id
                )
            )

        except discord.HTTPException as erro:

            print(
                "[DESABAFOS] Erro enviando "
                f"embed anônimo: {erro}"
            )

        # ----------------------------------------------------
        # Resposta privada
        # ----------------------------------------------------

        await interaction.followup.send(
            embed=discord.Embed(
                title="🕶️ DESABAFO ANÔNIMO CRIADO",
                description=(
                    "Seu espaço privado foi criado.\n\n"

                    f"📁 **Canal:** "
                    f"{canal.mention}\n\n"

                    "🔐 Nenhum cargo de staff "
                    "foi adicionado automaticamente."
                ),
                color=COR_SUCESSO
            ),
            ephemeral=True
        )

        # ----------------------------------------------------
        # Log sem identidade
        # ----------------------------------------------------

        await self.enviar_log(
            guild,
            "Desabafo anônimo criado",
            (
                f"🆔 **Atendimento:** "
                f"`#{desabafo_id}`\n\n"

                f"📁 **Canal:** "
                f"{canal.mention}\n\n"

                "🔐 **Conteúdo:** "
                "não incluído nos logs."
            ),
            "🕶️",
            COR_ANONIMO
        )

    # ========================================================
    # ATUALIZAR EMBED
    # ========================================================

    async def atualizar_embed_desabafo(
        self,
        canal,
        desabafo_id
    ):

        desabafo = self.desabafos.get(
            str(
                desabafo_id
            )
        )

        if desabafo is None:

            return

        try:

            async for mensagem in canal.history(
                limit=30,
                oldest_first=True
            ):

                if (
                    self.bot.user
                    and mensagem.author.id
                    == self.bot.user.id
                    and mensagem.embeds
                ):

                    await mensagem.edit(
                        embed=self.criar_embed_desabafo(
                            desabafo
                        ),
                        view=DesabafoView(
                            self,
                            desabafo_id
                        )
                    )

                    return

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass

    # ========================================================
    # TRANSCRIÇÃO
    # ========================================================

    async def gerar_transcricao(
        self,
        canal
    ):

        linhas = []

        try:

            async for mensagem in canal.history(
                limit=None,
                oldest_first=True
            ):

                data = mensagem.created_at.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )

                autor = (
                    mensagem.author
                )

                conteudo = (
                    mensagem.content
                    if mensagem.content
                    else "[Sem texto]"
                )

                if mensagem.embeds:

                    conteudo += (
                        f" "
                        f"[{len(mensagem.embeds)} embed(s)]"
                    )

                if mensagem.attachments:

                    nomes = ", ".join(
                        anexo.filename
                        for anexo in mensagem.attachments
                    )

                    conteudo += (
                        f" "
                        f"[Anexo(s): {nomes}]"
                    )

                linhas.append(
                    f"[{data}] "
                    f"{autor} "
                    f"({autor.id}): "
                    f"{conteudo}"
                )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            linhas.append(
                "[Não foi possível obter "
                "todo o histórico.]"
            )

        texto = "\n".join(
            linhas
        )

        return texto

    # ========================================================
    # FECHAR DESABAFO
    # ========================================================

    async def fechar_desabafo(
        self,
        canal,
        desabafo_id,
        fechador
    ):

        desabafo = self.desabafos.get(
            str(
                desabafo_id
            )
        )

        if desabafo is None:

            return

        if desabafo.get(
            "fechado",
            False
        ):

            return

        desabafo[
            "fechado"
        ] = True

        desabafo[
            "status"
        ] = "fechado"

        desabafo[
            "fechado_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.salvar_desabafos()

        # ====================================================
        # VERIFICAR TRANSCRIÇÃO
        # ====================================================

        transcricao_ativada = (
            desabafo.get(
                "transcricao",
                True
            )
        )

        canal_logs = self.obter_canal_logs(
            canal.guild
        )

        # ====================================================
        # TRANSCRIÇÃO
        # ====================================================

        if (
            transcricao_ativada
            and canal_logs is not None
        ):

            texto = await self.gerar_transcricao(
                canal
            )

            arquivo = discord.File(
                io.BytesIO(
                    texto.encode(
                        "utf-8"
                    )
                ),
                filename=(
                    f"desabafo-{desabafo_id}.txt"
                )
            )

            try:

                await canal_logs.send(
                    content=(
                        f"📄 **Transcrição do "
                        f"desabafo #{desabafo_id}**"
                    ),
                    file=arquivo
                )

            except (
                discord.Forbidden,
                discord.HTTPException
            ):

                pass

        # ====================================================
        # LOG ADMINISTRATIVO
        # ====================================================

        if transcricao_ativada:

            texto_transcricao = (
                "📄 Transcrição ativada"
            )

        else:

            texto_transcricao = (
                "🔒 Transcrição desativada"
            )

        await self.enviar_log(
            canal.guild,
            "Desabafo finalizado",
            (
                f"🆔 **Atendimento:** "
                f"`#{desabafo_id}`\n\n"

                f"🔒 **Finalizado por:** "
                f"{fechador.mention}\n\n"

                f"📄 **Transcrição:** "
                f"{texto_transcricao}"
            ),
            "🔒",
            COR_ERRO
        )

        # ====================================================
        # AVISO NO CANAL
        # ====================================================

        try:

            if transcricao_ativada:

                texto_aviso = (
                    "Esta conversa foi encerrada.\n\n"

                    "📄 A transcrição estava ativada "
                    "e foi enviada ao canal de logs "
                    "configurado.\n\n"

                    "🗑️ Este canal será removido."
                )

            else:

                texto_aviso = (
                    "Esta conversa foi encerrada.\n\n"

                    "🔐 A transcrição estava desativada.\n\n"

                    "📄 O conteúdo da conversa "
                    "não foi enviado aos logs.\n\n"

                    "🗑️ Este canal será removido."
                )

            await canal.send(
                embed=discord.Embed(
                    title="🔒 CONVERSA FINALIZADA",
                    description=texto_aviso,
                    color=(
                        COR_AVISO
                        if not transcricao_ativada
                        else COR_ERRO
                    )
                )
            )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass

        # ====================================================
        # ESPERA
        # ====================================================

        await asyncio.sleep(
            3
        )

        # ====================================================
        # DELETAR CANAL
        # ====================================================

        try:

            await canal.delete(
                reason=(
                    f"Royalt • "
                    f"Desabafo #{desabafo_id} finalizado"
                )
            )

        except discord.Forbidden:

            print(
                f"[DESABAFOS] Sem permissão "
                f"para apagar {canal.name}."
            )

        except discord.HTTPException as erro:

            print(
                f"[DESABAFOS] Erro apagando "
                f"{canal.name}: {erro}"
            )

    # ========================================================
    # !DESABAFOS
    # ========================================================

    @commands.command(
        name="desabafos",
        aliases=[
            "desabafo"
        ],
        description=(
            "Abre o Espaço de Desabafos do Royalt."
        )
    )
    @commands.guild_only()
    async def desabafos_comando(
        self,
        ctx
    ):

        embed = self.criar_embed_painel(
            ctx.guild
        )

        await ctx.send(
            embed=embed,
            view=PainelDesabafoView(
                self
            )
        )

    # ========================================================
    # !DESABAFOANONIMO
    # ========================================================

    @commands.command(
        name="desabafoanonimo",
        aliases=[
            "anonimodesabafo"
        ],
        description=(
            "Abre diretamente um desabafo anônimo."
        )
    )
    @commands.guild_only()
    async def desabafoanonimo(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="🕶️ ROYALT • DESABAFO ANÔNIMO",
            description=(
                "Você está prestes a criar "
                "um espaço privado.\n\n"

                "🔐 Nenhum cargo de staff "
                "será adicionado automaticamente.\n\n"

                "🤖 O Royalt poderá utilizar "
                "o sistema de pesquisa quando "
                "necessário."
            ),
            color=COR_ANONIMO
        )

        if BANNER_DESABAFOS:

            embed.set_image(
                url=BANNER_DESABAFOS
            )

        embed.set_footer(
            text="Royalt • Desabafo Anônimo"
        )

        await ctx.send(
            embed=embed,
            view=ConfirmarAnonimoView(
                self
            )
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Desabafos(
            bot
        )
    )