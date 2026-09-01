import json
import os
import time

from datetime import datetime

import discord
from discord.ext import commands, tasks


# ============================================================
# AIRA • CONFIGURAÇÕES
# ============================================================

OWNER_ID = 1527022875444379751

AIRA_VERSION = "0.7.94"

STATUS_FILE = "status.json"

TIME_FORMAT = "%d/%m/%Y %H:%M"


# ============================================================
# STATUS PADRÃO
# ============================================================

DEFAULT_STATUS = {
    "version": AIRA_VERSION,

    "channel_id": None,

    "maintenance": {
        "enabled": False,
        "scheduled": False,
        "date": None,
        "time": None,
        "reason": None,
        "services": []
    },

    "offline_commands": [],

    "maintenance_commands": []
}


# ============================================================
# FUNÇÕES DO ARQUIVO
# ============================================================

def load_status():

    if not os.path.exists(STATUS_FILE):

        save_status(DEFAULT_STATUS)

        return DEFAULT_STATUS.copy()

    try:

        with open(
            STATUS_FILE,
            "r",
            encoding="utf-8"
        ) as arquivo:

            data = json.load(arquivo)

        # Garante que campos novos existam
        for chave, valor in DEFAULT_STATUS.items():

            if chave not in data:

                data[chave] = valor

        # Garante campos da manutenção
        for chave, valor in DEFAULT_STATUS["maintenance"].items():

            if chave not in data["maintenance"]:

                data["maintenance"][chave] = valor

        return data

    except Exception as erro:

        print(
            f"❌ [BOT STATUS] Erro ao carregar status.json: {erro}"
        )

        return DEFAULT_STATUS.copy()


def save_status(data):

    try:

        with open(
            STATUS_FILE,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                data,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    except Exception as erro:

        print(
            f"❌ [BOT STATUS] Erro ao salvar status.json: {erro}"
        )


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def format_list(items):

    if not items:

        return "```Nenhum```"

    return "\n".join(
        f"• `{item}`"
        for item in items
    )


def format_uptime(seconds):

    seconds = int(seconds)

    dias, resto = divmod(seconds, 86400)

    horas, resto = divmod(resto, 3600)

    minutos, segundos = divmod(resto, 60)

    partes = []

    if dias:
        partes.append(f"{dias}d")

    if horas:
        partes.append(f"{horas}h")

    if minutos:
        partes.append(f"{minutos}m")

    partes.append(f"{segundos}s")

    return " ".join(partes)


# ============================================================
# MODAL • VERSÃO
# ============================================================

class VersionModal(discord.ui.Modal):

    def __init__(self, cog):

        super().__init__(
            title="🔖 Alterar versão da Aira"
        )

        self.cog = cog

        self.version = discord.ui.TextInput(
            label="Nova versão",
            placeholder="Ex: 0.7.95",
            default=self.cog.status["version"],
            required=True,
            max_length=20
        )

        self.add_item(self.version)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Você não possui permissão para isso.",
                ephemeral=True
            )

            return

        nova_versao = self.version.value.strip()

        self.cog.status["version"] = nova_versao

        self.cog.save()

        await interaction.response.send_message(
            f"✅ Versão da Aira alterada para **v{nova_versao}**.",
            ephemeral=True
        )


# ============================================================
# MODAL • MANUTENÇÃO
# ============================================================

class MaintenanceModal(discord.ui.Modal):

    def __init__(self, cog):

        super().__init__(
            title="🔧 Programar manutenção"
        )

        self.cog = cog

        self.data = discord.ui.TextInput(
            label="Data",
            placeholder="Ex: 05/09/2026",
            required=True,
            max_length=10
        )

        self.horario = discord.ui.TextInput(
            label="Horário",
            placeholder="Ex: 02:00",
            required=True,
            max_length=5
        )

        self.motivo = discord.ui.TextInput(
            label="Motivo",
            placeholder="Ex: Atualização para v0.7.95",
            required=True,
            max_length=500
        )

        self.sistemas = discord.ui.TextInput(
            label="Sistemas afetados",
            placeholder="Ex: Música, Economia, Perfil",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )

        self.add_item(self.data)
        self.add_item(self.horario)
        self.add_item(self.motivo)
        self.add_item(self.sistemas)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Você não possui permissão para isso.",
                ephemeral=True
            )

            return

        data_text = self.data.value.strip()

        horario_text = self.horario.value.strip()

        # ----------------------------------------------------
        # VALIDAR DATA
        # ----------------------------------------------------

        try:

            datetime.strptime(
                f"{data_text} {horario_text}",
                TIME_FORMAT
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Data ou horário inválido.\n\n"
                "Use:\n"
                "`DD/MM/AAAA`\n"
                "`HH:MM`",
                ephemeral=True
            )

            return

        sistemas = [
            item.strip()
            for item in self.sistemas.value.split(",")
            if item.strip()
        ]

        self.cog.status["maintenance"] = {

            "enabled": False,

            "scheduled": True,

            "date": data_text,

            "time": horario_text,

            "reason": self.motivo.value.strip(),

            "services": sistemas
        }

        self.cog.save()

        await interaction.response.send_message(
            "✅ **Manutenção programada!**\n\n"
            f"📅 Data: `{data_text}`\n"
            f"🕐 Horário: `{horario_text}`\n"
            f"📝 Motivo: {self.motivo.value.strip()}",
            ephemeral=True
        )

        await self.cog.send_maintenance_notice(
            "scheduled"
        )


# ============================================================
# MODAL • COMANDOS
# ============================================================

class CommandsModal(discord.ui.Modal):

    def __init__(self, cog, tipo):

        if tipo == "offline":

            titulo = "🔴 Comandos offline"

        else:

            titulo = "🛠️ Comandos em manutenção"

        super().__init__(
            title=titulo
        )

        self.cog = cog

        self.tipo = tipo

        if tipo == "offline":

            atuais = self.cog.status["offline_commands"]

        else:

            atuais = self.cog.status["maintenance_commands"]

        self.comandos = discord.ui.TextInput(
            label="Comandos",
            placeholder="Ex: musica, perfil, economia",
            default=", ".join(atuais),
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000
        )

        self.add_item(self.comandos)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Você não possui permissão para isso.",
                ephemeral=True
            )

            return

        lista = [
            item.strip()
            for item in self.comandos.value.split(",")
            if item.strip()
        ]

        if self.tipo == "offline":

            self.cog.status["offline_commands"] = lista

        else:

            self.cog.status["maintenance_commands"] = lista

        self.cog.save()

        await interaction.response.send_message(
            "✅ Lista atualizada com sucesso.",
            ephemeral=True
        )


# ============================================================
# SELETOR DE CANAL
# ============================================================

class StatusChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(self, cog):

        self.cog = cog

        super().__init__(
            placeholder="📢 Selecione o canal de avisos...",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Você não possui permissão para isso.",
                ephemeral=True
            )

            return

        canal = self.values[0]

        self.cog.status["channel_id"] = canal.id

        self.cog.save()

        await interaction.response.send_message(
            f"✅ Canal de avisos definido como {canal.mention}.",
            ephemeral=True
        )


class ChannelSelectView(
    discord.ui.View
):

    def __init__(self, cog):

        super().__init__(
            timeout=120
        )

        self.add_item(
            StatusChannelSelect(cog)
        )


# ============================================================
# PAINEL ADMINISTRATIVO
# ============================================================

class StatusAdminView(
    discord.ui.View
):

    def __init__(self, cog):

        super().__init__(
            timeout=600
        )

        self.cog = cog

    # ========================================================
    # MANUTENÇÃO
    # ========================================================

    @discord.ui.button(
        label="Programar manutenção",
        emoji="🔧",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def maintenance(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            MaintenanceModal(self.cog)
        )

    # ========================================================
    # CANCELAR
    # ========================================================

    @discord.ui.button(
        label="Cancelar manutenção",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def cancel(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        self.cog.status["maintenance"] = {

            "enabled": False,

            "scheduled": False,

            "date": None,

            "time": None,

            "reason": None,

            "services": []
        }

        self.cog.save()

        await interaction.response.send_message(
            "✅ Manutenção cancelada.",
            ephemeral=True
        )

    # ========================================================
    # VERSÃO
    # ========================================================

    @discord.ui.button(
        label="Alterar versão",
        emoji="🔖",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def version(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            VersionModal(self.cog)
        )

    # ========================================================
    # OFFLINE
    # ========================================================

    @discord.ui.button(
        label="Comandos offline",
        emoji="🔴",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def offline(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            CommandsModal(
                self.cog,
                "offline"
            )
        )

    # ========================================================
    # MANUTENÇÃO DE COMANDOS
    # ========================================================

    @discord.ui.button(
        label="Comandos em manutenção",
        emoji="🛠️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def maintenance_commands(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            CommandsModal(
                self.cog,
                "maintenance"
            )
        )

    # ========================================================
    # CANAL
    # ========================================================

    @discord.ui.button(
        label="Definir canal",
        emoji="📢",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def channel(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "📢 **Escolha o canal para os avisos da Aira:**",
            view=ChannelSelectView(
                self.cog
            ),
            ephemeral=True
        )

    # ========================================================
    # ATUALIZAR
    # ========================================================

    @discord.ui.button(
        label="Atualizar painel",
        emoji="🔄",
        style=discord.ButtonStyle.primary,
        row=2
    )
    async def refresh(
        self,
        interaction,
        button
    ):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Acesso negado.",
                ephemeral=True
            )

            return

        embed = self.cog.create_admin_embed()

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ============================================================
# COG
# ============================================================

class BotStatus(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.status = load_status()

        self.start_time = time.time()

        self.maintenance_checker.start()

        print(
            "   💠 Sistema de Bot Status iniciado."
        )

    # ========================================================
    # SALVAR
    # ========================================================

    def save(self):

        save_status(
            self.status
        )

    # ========================================================
    # CANAL
    # ========================================================

    def get_channel(self):

        channel_id = self.status.get(
            "channel_id"
        )

        if not channel_id:

            return None

        return self.bot.get_channel(
            int(channel_id)
        )

    # ========================================================
    # EMBED STATUS
    # ========================================================

    def create_status_embed(self):

        maintenance = self.status["maintenance"]

        ping = round(
            self.bot.latency * 1000
        )

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        if maintenance["enabled"]:

            estado = "🟠 **EM MANUTENÇÃO**"

            cor = discord.Color.orange()

        elif maintenance["scheduled"]:

            estado = "🔵 **MANUTENÇÃO AGENDADA**"

            cor = discord.Color.blue()

        else:

            estado = "🟢 **ONLINE**"

            cor = discord.Color.green()

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(

            title="💠 AIRA • STATUS",

            description=(
                "╭────────────────────────────────╮\n"
                "          **CENTRAL DE STATUS**\n"
                "╰────────────────────────────────╯\n\n"

                "Acompanhe em tempo real o estado "
                "dos sistemas da **Aira**.\n\n"

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),

            color=cor,

            timestamp=datetime.now()
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        embed.add_field(
            name="📡 Estado",
            value=estado,
            inline=True
        )

        embed.add_field(
            name="🔖 Versão",
            value=f"`v{self.status['version']}`",
            inline=True
        )

        embed.add_field(
            name="⏱️ Uptime",
            value=(
                f"`{format_uptime(time.time() - self.start_time)}`"
            ),
            inline=True
        )

        # ----------------------------------------------------
        # REDE
        # ----------------------------------------------------

        embed.add_field(
            name="🏓 Ping",
            value=f"`{ping} ms`",
            inline=True
        )

        embed.add_field(
            name="⚡ Latência",
            value=f"`{ping} ms`",
            inline=True
        )

        embed.add_field(
            name="🌐 Servidores",
            value=f"`{len(self.bot.guilds)}`",
            inline=True
        )

        # ----------------------------------------------------
        # COMANDOS
        # ----------------------------------------------------

        embed.add_field(
            name="🔴 Comandos offline",
            value=format_list(
                self.status["offline_commands"]
            ),
            inline=False
        )

        embed.add_field(
            name="🛠️ Comandos em manutenção",
            value=format_list(
                self.status["maintenance_commands"]
            ),
            inline=False
        )

        # ----------------------------------------------------
        # MANUTENÇÃO
        # ----------------------------------------------------

        if maintenance["enabled"]:

            texto = (
                "🟠 **A Aira está em manutenção.**\n\n"

                f"📅 **Data:** `{maintenance['date']}`\n"

                f"🕐 **Horário:** `{maintenance['time']}`\n"

                f"📝 **Motivo:** "
                f"{maintenance['reason'] or 'Não informado'}\n\n"

                "🔧 **Sistemas afetados:**\n"

                f"{format_list(maintenance['services'])}"
            )

        elif maintenance["scheduled"]:

            texto = (
                "🔵 **Manutenção programada.**\n\n"

                f"📅 **Data:** `{maintenance['date']}`\n"

                f"🕐 **Horário:** `{maintenance['time']}`\n"

                f"📝 **Motivo:** "
                f"{maintenance['reason'] or 'Não informado'}\n\n"

                "🔧 **Sistemas afetados:**\n"

                f"{format_list(maintenance['services'])}"
            )

        else:

            texto = (
                "🟢 **Nenhuma manutenção programada.**\n\n"
                "Todos os sistemas estão funcionando "
                "normalmente."
            )

        embed.add_field(
            name="🔧 Manutenção",
            value=texto,
            inline=False
        )

        # ----------------------------------------------------
        # CANAL
        # ----------------------------------------------------

        canal = self.get_channel()

        embed.add_field(
            name="📢 Canal de avisos",
            value=(
                canal.mention
                if canal
                else "`Não configurado`"
            ),
            inline=True
        )

        # ----------------------------------------------------
        # USUÁRIOS
        # ----------------------------------------------------

        total_users = sum(
            guild.member_count or 0
            for guild in self.bot.guilds
        )

        embed.add_field(
            name="👥 Usuários",
            value=f"`{total_users:,}`".replace(",", "."),
            inline=True
        )

        # ----------------------------------------------------
        # RODAPÉ
        # ----------------------------------------------------

        embed.set_footer(
            text=(
                f"Aira • Sistema de Status • "
                f"v{self.status['version']}"
            )
        )

        return embed

    # ========================================================
    # EMBED ADMIN
    # ========================================================

    def create_admin_embed(self):

        maintenance = self.status["maintenance"]

        if maintenance["enabled"]:

            estado = "🟠 Em manutenção"

        elif maintenance["scheduled"]:

            estado = "🔵 Agendada"

        else:

            estado = "🟢 Online"

        canal = self.get_channel()

        embed = discord.Embed(

            title="👑 AIRA • PAINEL ADMINISTRATIVO",

            description=(
                "Central privada de gerenciamento "
                "dos sistemas da Aira.\n\n"

                "Use os controles abaixo para configurar "
                "o status, manutenção, versão e avisos."
            ),

            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🔖 Versão",
            value=f"`v{self.status['version']}`",
            inline=True
        )

        embed.add_field(
            name="📡 Estado",
            value=estado,
            inline=True
        )

        embed.add_field(
            name="📢 Canal",
            value=(
                canal.mention
                if canal
                else "`Não configurado`"
            ),
            inline=True
        )

        embed.add_field(
            name="🔴 Offline",
            value=(
                f"`{len(self.status['offline_commands'])}`"
            ),
            inline=True
        )

        embed.add_field(
            name="🛠️ Manutenção",
            value=(
                f"`{len(self.status['maintenance_commands'])}`"
            ),
            inline=True
        )

        embed.add_field(
            name="🔧 Agendamento",
            value=(
                "🟢 Ativo"
                if maintenance["scheduled"]
                else "⚪ Nenhum"
            ),
            inline=True
        )

        embed.set_footer(
            text=(
                "Aira • Painel exclusivo "
                "do administrador"
            )
        )

        return embed

    # ========================================================
    # AVISO
    # ========================================================

    async def send_maintenance_notice(
        self,
        tipo
    ):

        canal = self.get_channel()

        if canal is None:

            print(
                "⚠️ [BOT STATUS] Canal de avisos "
                "não configurado."
            )

            return

        maintenance = self.status["maintenance"]

        # ----------------------------------------------------
        # AGENDAMENTO
        # ----------------------------------------------------

        if tipo == "scheduled":

            embed = discord.Embed(

                title="📅 AIRA • MANUTENÇÃO AGENDADA",

                description=(
                    "Uma manutenção da **Aira** "
                    "foi programada."
                ),

                color=discord.Color.blue(),

                timestamp=datetime.now()
            )

            embed.add_field(
                name="📅 Data",
                value=maintenance["date"],
                inline=True
            )

            embed.add_field(
                name="🕐 Horário",
                value=maintenance["time"],
                inline=True
            )

            embed.add_field(
                name="📝 Motivo",
                value=maintenance["reason"],
                inline=False
            )

            embed.add_field(
                name="🔧 Sistemas afetados",
                value=format_list(
                    maintenance["services"]
                ),
                inline=False
            )

        # ----------------------------------------------------
        # INÍCIO
        # ----------------------------------------------------

        else:

            embed = discord.Embed(

                title="🟠 AIRA • MANUTENÇÃO INICIADA",

                description=(
                    "A **Aira** entrou em manutenção.\n\n"

                    "Alguns comandos podem ficar "
                    "temporariamente indisponíveis."
                ),

                color=discord.Color.orange(),

                timestamp=datetime.now()
            )

            embed.add_field(
                name="📝 Motivo",
                value=(
                    maintenance["reason"]
                    or "Não informado"
                ),
                inline=False
            )

            embed.add_field(
                name="🔧 Sistemas afetados",
                value=format_list(
                    maintenance["services"]
                ),
                inline=False
            )

        embed.set_footer(
            text=f"Aira • v{self.status['version']}"
        )

        try:

            await canal.send(
                embed=embed
            )

            print(
                f"📢 [BOT STATUS] Aviso enviado para #{canal.name}"
            )

        except discord.Forbidden:

            print(
                "❌ [BOT STATUS] Aira não possui "
                "permissão para enviar mensagens no canal."
            )

        except Exception as erro:

            print(
                f"❌ [BOT STATUS] Erro ao enviar aviso: {erro}"
            )

    # ========================================================
    # VERIFICADOR DE MANUTENÇÃO
    # ========================================================

    @tasks.loop(seconds=30)
    async def maintenance_checker(self):

        maintenance = self.status["maintenance"]

        if not maintenance["scheduled"]:

            return

        if maintenance["enabled"]:

            return

        data = maintenance.get("date")

        horario = maintenance.get("time")

        if not data or not horario:

            return

        try:

            momento = datetime.strptime(
                f"{data} {horario}",
                TIME_FORMAT
            )

        except ValueError:

            return

        agora = datetime.now()

        if agora >= momento:

            self.status["maintenance"]["enabled"] = True

            self.status["maintenance"]["scheduled"] = False

            self.save()

            print(
                "🟠 [BOT STATUS] "
                "Aira entrou automaticamente "
                "em manutenção."
            )

            await self.send_maintenance_notice(
                "started"
            )

    @maintenance_checker.before_loop
    async def before_maintenance_checker(self):

        await self.bot.wait_until_ready()

    # ========================================================
    # !status
    # ========================================================

    @commands.command(
        name="status"
    )
    async def status_command(
        self,
        ctx
    ):

        embed = self.create_status_embed()

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # !status-admin
    # ========================================================

    @commands.command(
        name="status-admin"
    )
    async def status_admin_command(
        self,
        ctx
    ):

        if ctx.author.id != OWNER_ID:

            await ctx.send(
                "❌ **Acesso negado.**\n\n"
                "Este painel é exclusivo "
                "do administrador da Aira.",
                delete_after=5
            )

            return

        embed = self.create_admin_embed()

        await ctx.send(
            embed=embed,
            view=StatusAdminView(self)
        )

    # ========================================================
    # LIMPEZA
    # ========================================================

    def cog_unload(self):

        self.maintenance_checker.cancel()


# ============================================================
# SETUP DA COG
# ============================================================

async def setup(bot):

    await bot.add_cog(
        BotStatus(bot)
    )
