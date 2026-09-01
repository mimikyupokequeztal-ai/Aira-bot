import discord
from discord.ext import commands

from pathlib import Path
from datetime import datetime, timezone

import io
import json


# ============================================================
# CORES
# ============================================================

COR_TICKET = discord.Color.from_rgb(
    128,
    0,
    255
)

COR_SUCESSO = discord.Color.green()
COR_ERRO = discord.Color.red()
COR_AVISO = discord.Color.orange()
COR_INFO = discord.Color.blurple()
COR_AZUL = discord.Color.blue()


# ============================================================
# BANNER
# ============================================================

# Cole aqui uma imagem para usar como banner padrão.
#
# Exemplo:
#
# BANNER_TICKET = "https://cdn.discordapp.com/..."
#
# Também é possível configurar o banner pelo painel.

BANNER_TICKET = ""


# ============================================================
# PASTA E ARQUIVOS
# ============================================================

PASTA_DATA = Path(
    "data"
)

ARQUIVO_TICKETS = (
    PASTA_DATA / "tickets.json"
)

ARQUIVO_CONFIG = (
    PASTA_DATA / "tickets_config.json"
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
            "🎫 ROYALT • CENTRAL DE ATENDIMENTO"
        ),

        "painel_descricao": (
            "Precisa de ajuda?\n\n"
            "Clique no botão abaixo para abrir "
            "um ticket privado com a equipe."
        ),

        "painel_banner": BANNER_TICKET,

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

            return json.load(
                arquivo_json
            )

    except (
        json.JSONDecodeError,
        OSError
    ):

        print(
            f"[TICKETS] Não foi possível ler {arquivo}."
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
            f"[TICKETS] Erro ao salvar dados: {erro}"
        )


# ============================================================
# LIMPAR NOME DO CANAL
# ============================================================

def limpar_nome(
    nome
):

    proibidos = (
        " ",
        "#",
        "/",
        "\\",
        "@",
        ":"
    )

    for caractere in proibidos:

        nome = nome.replace(
            caractere,
            "-"
        )

    return nome.lower()[:30]


# ============================================================
# PAINEL PRINCIPAL DE TICKETS
# ============================================================

class PainelTicketView(
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
        # ABRIR TICKET
        # ----------------------------------------------------

        botao = discord.ui.Button(
            label="Abrir Ticket",
            emoji="🎫",
            style=discord.ButtonStyle.success,
            custom_id="royalt_ticket_abrir"
        )

        botao.callback = (
            self.abrir_ticket
        )

        self.add_item(
            botao
        )

    async def abrir_ticket(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "🎫 **Escolha a categoria do atendimento:**",
            view=CategoriaTicketView(
                self.cog
            ),
            ephemeral=True
        )


# ============================================================
# CATEGORIAS PARA ABERTURA
# ============================================================

class CategoriaTicketView(
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
            CategoriaSelect(
                cog
            )
        )


class CategoriaSelect(
    discord.ui.Select
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        opcoes = [

            discord.SelectOption(
                label="Suporte",
                value="suporte",
                emoji="🛠️",
                description="Problemas e dúvidas gerais"
            ),

            discord.SelectOption(
                label="Denúncia",
                value="denuncia",
                emoji="🚨",
                description="Relatar problemas ou usuários"
            ),

            discord.SelectOption(
                label="Parceria",
                value="parceria",
                emoji="🤝",
                description="Solicitações de parceria"
            ),

            discord.SelectOption(
                label="Compras",
                value="compras",
                emoji="🛒",
                description="Ajuda relacionada a compras"
            ),

            discord.SelectOption(
                label="Outros",
                value="outros",
                emoji="❓",
                description="Outros assuntos"
            )
        ]

        super().__init__(
            placeholder="Escolha uma categoria...",
            min_values=1,
            max_values=1,
            options=opcoes
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await self.cog.criar_ticket(
            interaction,
            self.values[0]
        )


# ============================================================
# SELECT PARA ADICIONAR MEMBRO
# ============================================================

class AdicionarMembroView(
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

        self.add_item(
            AdicionarMembroSelect(
                cog
            )
        )


class AdicionarMembroSelect(
    discord.ui.UserSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Selecione um membro...",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        usuario = self.values[0]

        ticket = (
            self.cog.obter_ticket_por_canal(
                interaction.channel.id
            )
        )

        if ticket is None:

            await interaction.response.send_message(
                "❌ Este canal não é um ticket.",
                ephemeral=True
            )

            return

        try:

            await interaction.channel.set_permissions(
                usuario,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        except discord.HTTPException:

            await interaction.response.send_message(
                "❌ Não consegui alterar as permissões.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"✅ {usuario.mention} foi adicionado ao ticket."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Membro adicionado",
            (
                f"🎫 **Ticket:** `#{ticket['id']}`\n\n"
                f"👤 **Membro:** {usuario.mention}\n\n"
                f"🛡️ **Staff:** {interaction.user.mention}"
            ),
            "➕",
            COR_INFO
        )


# ============================================================
# SELECT PARA REMOVER MEMBRO
# ============================================================

class RemoverMembroView(
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

        self.add_item(
            RemoverMembroSelect(
                cog
            )
        )


class RemoverMembroSelect(
    discord.ui.UserSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Selecione um membro...",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        usuario = self.values[0]

        ticket = (
            self.cog.obter_ticket_por_canal(
                interaction.channel.id
            )
        )

        if ticket is None:

            await interaction.response.send_message(
                "❌ Este canal não é um ticket.",
                ephemeral=True
            )

            return

        if usuario.id == int(
            ticket["autor"]
        ):

            await interaction.response.send_message(
                "❌ O autor do ticket não pode ser removido.",
                ephemeral=True
            )

            return

        if usuario.id == interaction.guild.default_role.id:

            await interaction.response.send_message(
                "❌ Não é possível remover @everyone.",
                ephemeral=True
            )

            return

        try:

            await interaction.channel.set_permissions(
                usuario,
                overwrite=None
            )

        except discord.HTTPException:

            await interaction.response.send_message(
                "❌ Não consegui alterar as permissões.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"✅ {usuario.mention} foi removido do ticket."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Membro removido",
            (
                f"🎫 **Ticket:** `#{ticket['id']}`\n\n"
                f"👤 **Membro:** {usuario.mention}\n\n"
                f"🛡️ **Staff:** {interaction.user.mention}"
            ),
            "➖",
            COR_AVISO
        )


# ============================================================
# VIEW DO TICKET
# ============================================================

class TicketView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        ticket_id
    ):

        super().__init__(
            timeout=None
        )

        self.cog = cog
        self.ticket_id = str(
            ticket_id
        )

        # ----------------------------------------------------
        # ASSUMIR
        # ----------------------------------------------------

        botao_assumir = discord.ui.Button(
            label="Assumir",
            emoji="👤",
            style=discord.ButtonStyle.primary,
            custom_id=(
                f"royalt_ticket_assumir:{self.ticket_id}"
            )
        )

        botao_assumir.callback = (
            self.assumir
        )

        self.add_item(
            botao_assumir
        )

        # ----------------------------------------------------
        # ATENDIDO
        # ----------------------------------------------------

        botao_atendido = discord.ui.Button(
            label="Atendido",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id=(
                f"royalt_ticket_atendido:{self.ticket_id}"
            )
        )

        botao_atendido.callback = (
            self.atendido
        )

        self.add_item(
            botao_atendido
        )

        # ----------------------------------------------------
        # ARQUIVAR
        # ----------------------------------------------------

        botao_arquivar = discord.ui.Button(
            label="Arquivar",
            emoji="📦",
            style=discord.ButtonStyle.secondary,
            custom_id=(
                f"royalt_ticket_arquivar:{self.ticket_id}"
            )
        )

        botao_arquivar.callback = (
            self.arquivar
        )

        self.add_item(
            botao_arquivar
        )

        # ----------------------------------------------------
        # REABRIR
        # ----------------------------------------------------

        botao_reabrir = discord.ui.Button(
            label="Reabrir",
            emoji="🔓",
            style=discord.ButtonStyle.primary,
            custom_id=(
                f"royalt_ticket_reabrir:{self.ticket_id}"
            )
        )

        botao_reabrir.callback = (
            self.reabrir
        )

        self.add_item(
            botao_reabrir
        )

        # ----------------------------------------------------
        # ADICIONAR
        # ----------------------------------------------------

        botao_adicionar = discord.ui.Button(
            label="Adicionar",
            emoji="➕",
            style=discord.ButtonStyle.secondary,
            custom_id=(
                f"royalt_ticket_adicionar:{self.ticket_id}"
            )
        )

        botao_adicionar.callback = (
            self.adicionar
        )

        self.add_item(
            botao_adicionar
        )

        # ----------------------------------------------------
        # REMOVER
        # ----------------------------------------------------

        botao_remover = discord.ui.Button(
            label="Remover",
            emoji="➖",
            style=discord.ButtonStyle.secondary,
            custom_id=(
                f"royalt_ticket_remover:{self.ticket_id}"
            )
        )

        botao_remover.callback = (
            self.remover
        )

        self.add_item(
            botao_remover
        )

        # ----------------------------------------------------
        # FINALIZAR
        # ----------------------------------------------------

        botao_finalizar = discord.ui.Button(
            label="Finalizar",
            emoji="🔒",
            style=discord.ButtonStyle.danger,
            custom_id=(
                f"royalt_ticket_finalizar:{self.ticket_id}"
            ),
            row=2
        )

        botao_finalizar.callback = (
            self.finalizar
        )

        self.add_item(
            botao_finalizar
        )

    # ========================================================
    # VERIFICAÇÃO STAFF
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
            "❌ Esta ação é exclusiva da staff.",
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

        if not await self.verificar_staff(
            interaction
        ):

            return

        ticket = self.cog.tickets.get(
            self.ticket_id
        )

        if ticket is None:

            await interaction.response.send_message(
                "❌ Ticket não encontrado.",
                ephemeral=True
            )

            return

        if ticket.get(
            "status"
        ) == "arquivado":

            await interaction.response.send_message(
                "❌ Este ticket está arquivado.",
                ephemeral=True
            )

            return

        ticket[
            "responsavel"
        ] = interaction.user.id

        ticket[
            "status"
        ] = "em_atendimento"

        ticket[
            "assumido_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.cog.salvar_tickets()

        await self.cog.atualizar_embed_ticket(
            interaction.channel,
            self.ticket_id
        )

        await interaction.response.send_message(
            f"👤 Ticket assumido por "
            f"{interaction.user.mention}."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Ticket assumido",
            (
                f"🎫 **Ticket:** `#{self.ticket_id}`\n\n"
                f"👤 **Staff:** {interaction.user.mention}"
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

        if not await self.verificar_staff(
            interaction
        ):

            return

        ticket = self.cog.tickets.get(
            self.ticket_id
        )

        if ticket is None:
            return

        ticket[
            "status"
        ] = "atendido"

        if not ticket.get(
            "responsavel"
        ):

            ticket[
                "responsavel"
            ] = interaction.user.id

        ticket[
            "atendido_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.cog.salvar_tickets()

        await self.cog.atualizar_embed_ticket(
            interaction.channel,
            self.ticket_id
        )

        await interaction.response.send_message(
            "✅ Ticket marcado como **atendido**."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Ticket atendido",
            (
                f"🎫 **Ticket:** `#{self.ticket_id}`\n\n"
                f"👤 **Staff:** {interaction.user.mention}"
            ),
            "✅",
            COR_SUCESSO
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

        ticket = self.cog.tickets.get(
            self.ticket_id
        )

        if ticket is None:
            return

        ticket[
            "status"
        ] = "arquivado"

        ticket[
            "arquivado_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.cog.salvar_tickets()

        autor = interaction.guild.get_member(
            int(
                ticket["autor"]
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

        await self.cog.atualizar_embed_ticket(
            interaction.channel,
            self.ticket_id
        )

        await interaction.response.send_message(
            "📦 Ticket arquivado."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Ticket arquivado",
            (
                f"🎫 **Ticket:** `#{self.ticket_id}`\n\n"
                f"👤 **Staff:** {interaction.user.mention}"
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

        ticket = self.cog.tickets.get(
            self.ticket_id
        )

        if ticket is None:
            return

        ticket[
            "status"
        ] = "aberto"

        ticket.pop(
            "arquivado_em",
            None
        )

        self.cog.salvar_tickets()

        autor = interaction.guild.get_member(
            int(
                ticket["autor"]
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

        await self.cog.atualizar_embed_ticket(
            interaction.channel,
            self.ticket_id
        )

        await interaction.response.send_message(
            "🔓 Ticket reaberto."
        )

        await self.cog.enviar_log(
            interaction.guild,
            "Ticket reaberto",
            (
                f"🎫 **Ticket:** `#{self.ticket_id}`\n\n"
                f"👤 **Staff:** {interaction.user.mention}"
            ),
            "🔓",
            COR_INFO
        )

    # ========================================================
    # ADICIONAR
    # ========================================================

    async def adicionar(
        self,
        interaction
    ):

        if not await self.verificar_staff(
            interaction
        ):

            return

        await interaction.response.send_message(
            "➕ Selecione o membro que deseja adicionar:",
            view=AdicionarMembroView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # REMOVER
    # ========================================================

    async def remover(
        self,
        interaction
    ):

        if not await self.verificar_staff(
            interaction
        ):

            return

        await interaction.response.send_message(
            "➖ Selecione o membro que deseja remover:",
            view=RemoverMembroView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # FINALIZAR
    # ========================================================

    async def finalizar(
        self,
        interaction
    ):

        ticket = self.cog.tickets.get(
            self.ticket_id
        )

        if ticket is None:

            await interaction.response.send_message(
                "❌ Ticket não encontrado.",
                ephemeral=True
            )

            return

        permitido = (
            interaction.user.id
            == int(
                ticket["autor"]
            )
            or self.cog.usuario_equipe(
                interaction.user,
                interaction.guild
            )
        )

        if not permitido:

            await interaction.response.send_message(
                "❌ Você não pode finalizar este ticket.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "🔒 Solicitação de encerramento enviada.",
            ephemeral=True
        )

        await interaction.channel.send(
            embed=discord.Embed(
                title="🔒 FINALIZAR TICKET?",
                description=(
                    "Este ticket será encerrado.\n\n"
                    "📄 Uma transcrição será enviada "
                    "para o canal de logs.\n\n"
                    "Tem certeza?"
                ),
                color=COR_ERRO
            ),
            view=ConfirmarFechamentoView(
                self.cog,
                self.ticket_id
            )
        )


# ============================================================
# CONFIRMAÇÃO
# ============================================================

class ConfirmarFechamentoView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        ticket_id
    ):

        super().__init__(
            timeout=60
        )

        self.cog = cog
        self.ticket_id = str(
            ticket_id
        )

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

        if not self.cog.usuario_equipe(
            interaction.user,
            interaction.guild
        ):

            await interaction.response.send_message(
                "❌ Apenas a staff pode confirmar.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            content="🔒 Finalizando ticket...",
            embed=None,
            view=None
        )

        await self.cog.fechar_ticket(
            interaction.channel,
            self.ticket_id,
            interaction.user
        )

        self.stop()

    @discord.ui.button(
        label="Não",
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
# MENU PRINCIPAL
# ============================================================

class MenuPrincipalTicketView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        autor
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.autor = autor

    async def interaction_check(
        self,
        interaction
    ):

        if interaction.user.id != self.autor.id:

            await interaction.response.send_message(
                "❌ Apenas quem abriu este painel "
                "pode utilizá-lo.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # PAINEL
    # ========================================================

    @discord.ui.button(
        label="Painel de Tickets",
        emoji="🎫",
        style=discord.ButtonStyle.success,
        row=0
    )
    async def painel(
        self,
        interaction,
        button
    ):

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ Você precisa da permissão "
                "**Gerenciar Servidor**.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        embed = discord.Embed(
            title=config.get(
                "painel_titulo"
            ),
            description=config.get(
                "painel_descricao"
            ),
            color=COR_TICKET
        )

        banner = config.get(
            "painel_banner",
            BANNER_TICKET
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.set_footer(
            text="Royalt Ticket System"
        )

        await interaction.response.send_message(
            embed=embed,
            view=PainelTicketView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # CONFIGURAR
    # ========================================================

    @discord.ui.button(
        label="Configurar",
        emoji="⚙️",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def configurar(
        self,
        interaction,
        button
    ):

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ Você precisa da permissão "
                "**Gerenciar Servidor**.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=self.cog.criar_embed_config(
                interaction.guild
            ),
            view=ConfigTicketView(
                self.cog,
                interaction.user
            ),
            ephemeral=True
        )

    # ========================================================
    # VER CONFIGURAÇÃO
    # ========================================================

    @discord.ui.button(
        label="Ver Configuração",
        emoji="📋",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def ver_config(
        self,
        interaction,
        button
    ):

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ Você precisa da permissão "
                "**Gerenciar Servidor**.",
                ephemeral=True
            )

            return

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
        row=1
    )
    async def fechar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="🎫 Painel fechado.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# CONFIGURAÇÃO
# ============================================================

class ConfigTicketView(
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

    async def interaction_check(
        self,
        interaction
    ):

        if interaction.user.id != self.autor.id:

            await interaction.response.send_message(
                "❌ Apenas quem abriu este painel "
                "pode configurá-lo.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # LOGS
    # ========================================================

    @discord.ui.button(
        label="Canal de Logs",
        emoji="📁",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def logs(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "📁 Selecione o canal de logs:",
            view=ConfigLogsView(
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

        await interaction.response.send_message(
            "🗂️ Selecione a categoria:",
            view=ConfigCategoriaView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # STAFF
    # ========================================================

    @discord.ui.button(
        label="Staff",
        emoji="👥",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def staff(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "👥 Selecione o cargo da staff:",
            view=ConfigStaffView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # MENSAGEM
    # ========================================================

    @discord.ui.button(
        label="Mensagem",
        emoji="📝",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def mensagem(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            PainelModal(
                self.cog,
                interaction.guild
            )
        )

    # ========================================================
    # CONFIGURAÇÃO
    # ========================================================

    @discord.ui.button(
        label="Ver Configuração",
        emoji="⚙️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def ver_config(
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
            "📢 Selecione o canal:",
            view=PublicarPainelView(
                self.cog
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
            content="⚙️ Configuração fechada.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# SELECT DE LOGS
# ============================================================

class ConfigLogsView(
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
            ConfigLogsSelect(
                cog
            )
        )


class ConfigLogsSelect(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Escolha o canal de logs...",
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

        selecionado = self.values[0]

        canal = interaction.guild.get_channel(
            selecionado.id
        )

        if canal is None:

            await interaction.response.send_message(
                "❌ Canal não encontrado.",
                ephemeral=True
            )

            return

        if not isinstance(
            canal,
            discord.TextChannel
        ):

            await interaction.response.send_message(
                "❌ Selecione um canal de texto.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        config[
            "canal_logs_id"
        ] = canal.id

        self.cog.salvar_config()

        await interaction.response.send_message(
            f"✅ Logs configurados em {canal.mention}.",
            ephemeral=True
        )


# ============================================================
# SELECT DE CATEGORIA
# ============================================================

class ConfigCategoriaView(
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
            ConfigCategoriaSelect(
                cog
            )
        )


class ConfigCategoriaSelect(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Escolha a categoria...",
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

        selecionado = self.values[0]

        categoria = interaction.guild.get_channel(
            selecionado.id
        )

        if categoria is None:

            await interaction.response.send_message(
                "❌ Categoria não encontrada.",
                ephemeral=True
            )

            return

        if not isinstance(
            categoria,
            discord.CategoryChannel
        ):

            await interaction.response.send_message(
                "❌ Selecione uma categoria válida.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        config[
            "categoria_id"
        ] = categoria.id

        self.cog.salvar_config()

        await interaction.response.send_message(
            f"✅ Tickets serão criados em "
            f"**{categoria.name}**.",
            ephemeral=True
        )


# ============================================================
# SELECT DE STAFF
# ============================================================

class ConfigStaffView(
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
            ConfigStaffSelect(
                cog
            )
        )


class ConfigStaffSelect(
    discord.ui.RoleSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Escolha o cargo da staff...",
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
                "❌ @everyone não pode ser staff.",
                ephemeral=True
            )

            return

        config = self.cog.obter_config(
            interaction.guild
        )

        config[
            "cargo_staff_id"
        ] = cargo.id

        self.cog.salvar_config()

        await interaction.response.send_message(
            f"✅ Cargo da staff definido como "
            f"{cargo.mention}.",
            ephemeral=True
        )


# ============================================================
# PUBLICAÇÃO DO PAINEL
# ============================================================

class PublicarPainelView(
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
            PublicarPainelSelect(
                cog
            )
        )


class PublicarPainelSelect(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        cog
    ):

        self.cog = cog

        super().__init__(
            placeholder="Escolha o canal do painel...",
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

        selecionado = self.values[0]

        canal = interaction.guild.get_channel(
            selecionado.id
        )

        if canal is None:

            await interaction.response.send_message(
                "❌ Canal não encontrado.",
                ephemeral=True
            )

            return

        if not isinstance(
            canal,
            discord.TextChannel
        ):

            await interaction.response.send_message(
                "❌ Selecione um canal de texto.",
                ephemeral=True
            )

            return

        sucesso = await self.cog.publicar_painel(
            interaction.guild,
            canal
        )

        if sucesso:

            await interaction.response.send_message(
                f"✅ Painel publicado em "
                f"{canal.mention}.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Não foi possível publicar o painel.",
                ephemeral=True
            )


# ============================================================
# MODAL DO PAINEL
# ============================================================

class PainelModal(
    discord.ui.Modal
):

    def __init__(
        self,
        cog,
        guild
    ):

        super().__init__(
            title="📝 Configurar Painel"
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
                "🎫 ROYALT • CENTRAL DE ATENDIMENTO"
            ),
            max_length=256,
            required=True
        )

        self.descricao = discord.ui.TextInput(
            label="Descrição",
            default=config.get(
                "painel_descricao",
                "Precisa de ajuda?"
            ),
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True
        )

        self.banner = discord.ui.TextInput(
            label="URL do Banner",
            default=config.get(
                "painel_banner",
                BANNER_TICKET
            ),
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

        config[
            "painel_titulo"
        ] = self.titulo.value

        config[
            "painel_descricao"
        ] = self.descricao.value

        config[
            "painel_banner"
        ] = self.banner.value.strip()

        self.cog.salvar_config()

        await interaction.response.send_message(
            "✅ Painel atualizado com sucesso!",
            ephemeral=True
        )


# ============================================================
# COG TICKETS
# ============================================================

class Tickets(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.tickets = carregar_json(
            ARQUIVO_TICKETS,
            {}
        )

        self.config = carregar_json(
            ARQUIVO_CONFIG,
            {}
        )

        self._views_restauradas = False

    # ========================================================
    # SALVAR
    # ========================================================

    def salvar_tickets(
        self
    ):

        salvar_json(
            ARQUIVO_TICKETS,
            self.tickets
        )

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

        if guild_id not in self.config:

            self.config[
                guild_id
            ] = configuracao_padrao()

        config = self.config[
            guild_id
        ]

        padrao = configuracao_padrao()

        for chave, valor in padrao.items():

            config.setdefault(
                chave,
                valor
            )

        return config

    # ========================================================
    # TICKET PELO CANAL
    # ========================================================

    def obter_ticket_por_canal(
        self,
        canal_id
    ):

        for ticket in self.tickets.values():

            if int(
                ticket.get(
                    "canal",
                    0
                )
            ) == int(canal_id):

                return ticket

        return None

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
    # LOG
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

        return guild.get_channel(
            int(canal_id)
        )

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
            text="Royalt Ticket Logging System"
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                f"[TICKETS] Sem permissão para "
                f"enviar logs em {guild.name}."
            )

        except discord.HTTPException as erro:

            print(
                f"[TICKETS] Erro enviando log: {erro}"
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

        embed = discord.Embed(
            title="⚙️ ROYALT • CONFIGURAÇÃO DE TICKETS",
            description=(
                "Configuração completa do sistema de atendimento."
            ),
            color=COR_TICKET
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
            name="👥 Staff",
            value=(
                staff.mention
                if staff
                else "❌ Não configurada"
            ),
            inline=False
        )

        embed.add_field(
            name="📁 Logs",
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
            name="🔢 Tickets criados",
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
            text="Royalt Ticket System"
        )

        return embed

    # ========================================================
    # EMBED DO TICKET
    # ========================================================

    def criar_embed_ticket(
        self,
        ticket
    ):

        status = ticket.get(
            "status",
            "aberto"
        )

        status_map = {

            "aberto": (
                "🟢 Aberto",
                COR_TICKET
            ),

            "em_atendimento": (
                "🟡 Em atendimento",
                COR_AVISO
            ),

            "atendido": (
                "✅ Atendido",
                COR_SUCESSO
            ),

            "arquivado": (
                "📦 Arquivado",
                COR_AZUL
            ),

            "fechado": (
                "🔒 Fechado",
                COR_ERRO
            )
        }

        status_texto, cor = status_map.get(
            status,
            (
                "🟢 Aberto",
                COR_TICKET
            )
        )

        responsavel = ticket.get(
            "responsavel"
        )

        atendente = (
            f"<@{responsavel}>"
            if responsavel
            else "Ninguém assumiu"
        )

        embed = discord.Embed(
            title="🎫 ROYALT • TICKET",
            description=(
                "## Atendimento\n\n"

                f"👤 **Autor:** "
                f"<@{ticket['autor']}>\n\n"

                f"📂 **Categoria:** "
                f"**{ticket['categoria'].title()}**\n\n"

                f"📊 **Status:** "
                f"{status_texto}\n\n"

                f"👨‍💼 **Atendente:** "
                f"{atendente}\n\n"

                f"🆔 **Ticket:** "
                f"`#{ticket['id']}`\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "Utilize os botões abaixo para "
                "administrar este atendimento."
            ),
            color=cor
        )

        banner = ticket.get(
            "banner",
            BANNER_TICKET
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.set_footer(
            text="Royalt Ticket System"
        )

        return embed

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
        # PAINEL
        # ----------------------------------------------------

        try:

            self.bot.add_view(
                PainelTicketView(
                    self
                )
            )

        except Exception as erro:

            print(
                f"[TICKETS] Erro restaurando painel: {erro}"
            )

        # ----------------------------------------------------
        # TICKETS
        # ----------------------------------------------------

        for ticket_id, ticket in self.tickets.items():

            if ticket.get(
                "fechado",
                False
            ):

                continue

            try:

                self.bot.add_view(
                    TicketView(
                        self,
                        ticket_id
                    )
                )

            except Exception as erro:

                print(
                    f"[TICKETS] Erro restaurando ticket "
                    f"{ticket_id}: {erro}"
                )

    # ========================================================
    # PUBLICAR PAINEL
    # ========================================================

    async def publicar_painel(
        self,
        guild,
        canal
    ):

        config = self.obter_config(
            guild
        )

        embed = discord.Embed(
            title=config.get(
                "painel_titulo"
            ),
            description=config.get(
                "painel_descricao"
            ),
            color=COR_TICKET
        )

        banner = config.get(
            "painel_banner",
            BANNER_TICKET
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.set_footer(
            text="Royalt Ticket System"
        )

        try:

            mensagem = await canal.send(
                embed=embed,
                view=PainelTicketView(
                    self
                )
            )

        except discord.Forbidden:

            return False

        except discord.HTTPException as erro:

            print(
                f"[TICKETS] Erro ao publicar painel: {erro}"
            )

            return False

        config[
            "painel_canal_id"
        ] = canal.id

        config[
            "painel_mensagem_id"
        ] = mensagem.id

        self.salvar_config()

        await self.enviar_log(
            guild,
            "Painel publicado",
            (
                f"📢 **Canal:** {canal.mention}\n\n"
                f"🆔 **Mensagem:** `{mensagem.id}`"
            ),
            "📢",
            COR_SUCESSO
        )

        return True

    # ========================================================
    # CRIAR TICKET
    # ========================================================

    async def criar_ticket(
        self,
        interaction,
        categoria
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Tickets só podem ser criados em servidores.",
                ephemeral=True
            )

            return

        await interaction.response.defer(
            ephemeral=True
        )

        config = self.obter_config(
            guild
        )

        # ----------------------------------------------------
        # TICKET EXISTENTE
        # ----------------------------------------------------

        for ticket in self.tickets.values():

            if (
                int(
                    ticket.get(
                        "guild",
                        0
                    )
                ) == guild.id

                and int(
                    ticket.get(
                        "autor",
                        0
                    )
                ) == interaction.user.id

                and not ticket.get(
                    "fechado",
                    False
                )
            ):

                canal_existente = guild.get_channel(
                    int(
                        ticket["canal"]
                    )
                )

                if canal_existente:

                    await interaction.followup.send(
                        "📂 Você já possui um ticket aberto:\n"
                        f"{canal_existente.mention}",
                        ephemeral=True
                    )

                    return

        # ----------------------------------------------------
        # CATEGORIA
        # ----------------------------------------------------

        categoria_canal = None

        if config.get(
            "categoria_id"
        ):

            categoria_canal = guild.get_channel(
                int(
                    config[
                        "categoria_id"
                    ]
                )
            )

        # ----------------------------------------------------
        # STAFF
        # ----------------------------------------------------

        cargo_staff = None

        if config.get(
            "cargo_staff_id"
        ):

            cargo_staff = guild.get_role(
                int(
                    config[
                        "cargo_staff_id"
                    ]
                )
            )

        # ----------------------------------------------------
        # CONTADOR
        # ----------------------------------------------------

        config[
            "contador"
        ] += 1

        numero = config[
            "contador"
        ]

        self.salvar_config()

        ticket_id = str(
            numero
        ).zfill(4)

        nome_usuario = limpar_nome(
            interaction.user.name
        )

        nome_canal = (
            f"🎫・ticket-{nome_usuario}-{ticket_id}"
        )

        # ----------------------------------------------------
        # PERMISSÕES
        # ----------------------------------------------------

        overwrites = {

            guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

            interaction.user:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )
        }

        if cargo_staff:

            overwrites[
                cargo_staff
            ] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
                attach_files=True,
                embed_links=True
            )

        # ----------------------------------------------------
        # CRIAR CANAL
        # ----------------------------------------------------

        try:

            canal = await guild.create_text_channel(
                name=nome_canal,
                overwrites=overwrites,
                category=categoria_canal,
                reason="Royalt Ticket System"
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ Não tenho permissão para criar canais.",
                ephemeral=True
            )

            return

        except discord.HTTPException as erro:

            print(
                f"[TICKETS] Erro criando canal: {erro}"
            )

            await interaction.followup.send(
                "❌ Não consegui criar o ticket.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # DADOS
        # ----------------------------------------------------

        ticket = {

            "id": ticket_id,

            "guild": guild.id,

            "canal": canal.id,

            "autor": interaction.user.id,

            "categoria": categoria,

            "responsavel": None,

            "status": "aberto",

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
                BANNER_TICKET
            )
        }

        self.tickets[
            ticket_id
        ] = ticket

        self.salvar_tickets()

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = self.criar_embed_ticket(
            ticket
        )

        mencao_staff = ""

        if cargo_staff:

            mencao_staff = (
                f" {cargo_staff.mention}"
            )

        try:

            await canal.send(
                content=(
                    f"{interaction.user.mention}"
                    f"{mencao_staff}"
                ),
                embed=embed,
                view=TicketView(
                    self,
                    ticket_id
                )
            )

        except discord.HTTPException as erro:

            print(
                f"[TICKETS] Erro enviando embed: {erro}"
            )

            await interaction.followup.send(
                "⚠️ O canal foi criado, mas não consegui "
                "enviar a mensagem inicial.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # RESPOSTA
        # ----------------------------------------------------

        await interaction.followup.send(
            "✅ **Ticket criado com sucesso!**\n"
            f"{canal.mention}",
            ephemeral=True
        )

        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        await self.enviar_log(
            guild,
            "Ticket aberto",
            (
                f"🎫 **Ticket:** `#{ticket_id}`\n\n"

                f"👤 **Usuário:** "
                f"{interaction.user.mention}\n\n"

                f"📂 **Categoria:** "
                f"**{categoria.title()}**\n\n"

                f"📁 **Canal:** "
                f"{canal.mention}"
            ),
            "🎫",
            COR_SUCESSO
        )

    # ========================================================
    # ATUALIZAR EMBED
    # ========================================================

    async def atualizar_embed_ticket(
        self,
        canal,
        ticket_id
    ):

        ticket = self.tickets.get(
            str(ticket_id)
        )

        if ticket is None:

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
                        embed=self.criar_embed_ticket(
                            ticket
                        ),
                        view=TicketView(
                            self,
                            ticket_id
                        )
                    )

                    break

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass

    # ========================================================
    # FECHAR TICKET
    # ========================================================

    async def fechar_ticket(
        self,
        canal,
        ticket_id,
        fechador
    ):

        ticket = self.tickets.get(
            str(ticket_id)
        )

        if ticket is None:
            return

        if ticket.get(
            "fechado",
            False
        ):
            return

        ticket[
            "fechado"
        ] = True

        ticket[
            "status"
        ] = "fechado"

        ticket[
            "fechado_em"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        self.salvar_tickets()

        # ====================================================
        # TRANSCRIÇÃO
        # ====================================================

        linhas = []

        try:

            async for mensagem in canal.history(
                limit=None,
                oldest_first=True
            ):

                data = mensagem.created_at.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )

                conteudo = (
                    mensagem.content
                    if mensagem.content
                    else "[Sem texto]"
                )

                if mensagem.embeds:

                    conteudo += (
                        f" [Embeds: "
                        f"{len(mensagem.embeds)}]"
                    )

                if mensagem.attachments:

                    anexos = ", ".join(
                        anexo.filename
                        for anexo in mensagem.attachments
                    )

                    conteudo += (
                        f" [Anexos: {anexos}]"
                    )

                linhas.append(
                    f"[{data}] "
                    f"{mensagem.author} "
                    f"({mensagem.author.id}): "
                    f"{conteudo}"
                )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            linhas.append(
                "[Não foi possível obter todo o histórico.]"
            )

        texto = "\n".join(
            linhas
        )

        arquivo = discord.File(
            io.BytesIO(
                texto.encode(
                    "utf-8"
                )
            ),
            filename=(
                f"ticket-{ticket_id}.txt"
            )
        )

        # ====================================================
        # LOG
        # ====================================================

        await self.enviar_log(
            canal.guild,
            "Ticket finalizado",
            (
                f"🎫 **Ticket:** `#{ticket_id}`\n\n"

                f"👤 **Autor:** "
                f"<@{ticket['autor']}>\n\n"

                f"📂 **Categoria:** "
                f"**{ticket['categoria'].title()}**\n\n"

                f"🔒 **Finalizado por:** "
                f"{fechador.mention}"
            ),
            "🔒",
            COR_ERRO
        )

        # ====================================================
        # TRANSCRIÇÃO
        # ====================================================

        canal_logs = self.obter_canal_logs(
            canal.guild
        )

        if canal_logs:

            try:

                await canal_logs.send(
                    content=(
                        f"📄 **Transcrição do "
                        f"ticket #{ticket_id}**"
                    ),
                    file=arquivo
                )

            except (
                discord.Forbidden,
                discord.HTTPException
            ):

                pass

        # ====================================================
        # AVISO NO TICKET
        # ====================================================

        try:

            await canal.send(
                embed=discord.Embed(
                    title="🔒 TICKET FINALIZADO",
                    description=(
                        "Este atendimento foi encerrado.\n\n"
                        "📄 A transcrição foi enviada "
                        "para os logs.\n\n"
                        "🗑️ O canal será removido em "
                        "alguns segundos."
                    ),
                    color=COR_ERRO
                )
            )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass

        # ====================================================
        # APAGAR CANAL
        # ====================================================

        try:

            await canal.delete(
                reason=(
                    f"Royalt • Ticket #{ticket_id} finalizado"
                )
            )

        except discord.Forbidden:

            print(
                f"[TICKETS] Sem permissão para apagar "
                f"{canal.name}."
            )

        except discord.HTTPException as erro:

            print(
                f"[TICKETS] Erro apagando canal: {erro}"
            )

    # ========================================================
    # COMANDO !TICKET
    # ========================================================

    @commands.command(
        name="ticket"
    )
    async def ticket_comando(
        self,
        ctx,
        acao: str = None
    ):

        # ====================================================
        # !TICKET
        # ====================================================

        if acao is None:

            embed = discord.Embed(
                title="🎫 ROYALT • SISTEMA DE TICKETS",
                description=(
                    "## Central de Atendimento\n\n"

                    "Use os botões abaixo para "
                    "acessar o sistema.\n\n"

                    "🎫 **Painel de Tickets**\n"
                    "Visualiza o painel utilizado pelos "
                    "membros para abrir atendimento.\n\n"

                    "⚙️ **Configurar**\n"
                    "Configura staff, categoria, logs "
                    "e aparência do painel.\n\n"

                    "📋 **Ver Configuração**\n"
                    "Mostra as configurações atuais."
                ),
                color=COR_TICKET
            )

            if BANNER_TICKET:

                embed.set_image(
                    url=BANNER_TICKET
                )

            embed.set_footer(
                text=f"Royalt Ticket System • {ctx.author}"
            )

            await ctx.send(
                embed=embed,
                view=MenuPrincipalTicketView(
                    self,
                    ctx.author
                )
            )

            return

        # ====================================================
        # !TICKET PAINEL
        # ====================================================

        if acao.lower() == "painel":

            if not ctx.author.guild_permissions.manage_guild:

                await ctx.send(
                    "❌ Você precisa da permissão "
                    "**Gerenciar Servidor**."
                )

                return

            config = self.obter_config(
                ctx.guild
            )

            embed = discord.Embed(
                title=config.get(
                    "painel_titulo"
                ),
                description=config.get(
                    "painel_descricao"
                ),
                color=COR_TICKET
            )

            banner = config.get(
                "painel_banner",
                BANNER_TICKET
            )

            if banner:

                embed.set_image(
                    url=banner
                )

            embed.set_footer(
                text="Royalt Ticket System"
            )

            await ctx.send(
                embed=embed,
                view=PainelTicketView(
                    self
                )
            )

            return

        # ====================================================
        # !TICKET CONFIGURAR
        # ====================================================

        if acao.lower() == "configurar":

            if not ctx.author.guild_permissions.manage_guild:

                await ctx.send(
                    "❌ Você precisa da permissão "
                    "**Gerenciar Servidor**."
                )

                return

            await ctx.send(
                embed=self.criar_embed_config(
                    ctx.guild
                ),
                view=ConfigTicketView(
                    self,
                    ctx.author
                )
            )

            return

        await ctx.send(
            "❌ Opção inválida.\n\n"
            "Use:\n"
            "`!ticket`\n"
            "`!ticket painel`\n"
            "`!ticket configurar`"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Tickets(bot)
    )