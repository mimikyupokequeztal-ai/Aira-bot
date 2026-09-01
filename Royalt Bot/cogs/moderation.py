import discord
from discord.ext import commands

from datetime import timedelta, datetime, timezone
from pathlib import Path
import json


# ============================================================
# CONFIGURAÇÕES
# ============================================================

NOME_CANAL_LOGS = "📁・logs"

PASTA_DATA = Path("data")
ARQUIVO_WARNS = PASTA_DATA / "warns.json"


# ============================================================
# CORES
# ============================================================

COR_BAN = discord.Color.red()
COR_KICK = discord.Color.orange()
COR_TIMEOUT = discord.Color.gold()
COR_WARN = discord.Color.yellow()
COR_WARNS = discord.Color.purple()
COR_CLEAR = discord.Color.blue()
COR_LOCK = discord.Color.red()
COR_UNLOCK = discord.Color.green()
COR_SLOWMODE = discord.Color.blurple()
COR_UNBAN = discord.Color.green()


# ============================================================
# BANNERS
# ============================================================

BANNER_BAN = "https://cdn.discordapp.com/attachments/1527325771650171028/1543418584544444457/Gemini_Generated_Image_xhh93ixhh93ixhh9.jpg?ex=6a94cc11&is=6a937a91&hm=e9166dbe5ec6c9e9db5afcea32bc8f7d7e451d815c6eee24c79eaabdf66ec186&"

BANNER_KICK = "https://cdn.discordapp.com/attachments/1527325771650171028/1543421703516979291/Gemini_Generated_Image_r2fu77r2fu77r2fu.jpg?ex=6a94cef9&is=6a937d79&hm=8d7de56d6891dbed27d52bccb1221d4239fc00ddb6678d2bad655e9a7bdaeab7&"

BANNER_TIMEOUT = "https://cdn.discordapp.com/attachments/1527325771650171028/1543421749885018202/Gemini_Generated_Image_mih21xmih21xmih2.jpg?ex=6a94cf04&is=6a937d84&hm=c9ab56e6d7019c370ba19ee1474c72ce3cf4ec8bbe09a1b12d1ec5ef7084b22c&"

BANNER_WARN = "https://cdn.discordapp.com/attachments/1527325771650171028/1543419020881952870/Gemini_Generated_Image_46osb446osb446os.jpg?ex=6a94cc79&is=6a937af9&hm=2cf36eff42868f7e6652d917e902f132a4416b045ec8a32e6740a51714787c91&"

BANNER_WARNS = "https://cdn.discordapp.com/attachments/1527325771650171028/1543419020881952870/Gemini_Generated_Image_46osb446osb446os.jpg?ex=6a94cc79&is=6a937af9&hm=2cf36eff42868f7e6652d917e902f132a4416b045ec8a32e6740a51714787c91&"

BANNER_CLEAR = ""

BANNER_LOCK = "https://cdn.discordapp.com/attachments/1527325771650171028/1543421884069187684/Gemini_Generated_Image_ctluo5ctluo5ctlu.jpg?ex=6a94cf24&is=6a937da4&hm=030908c02c2b0947e8d56cb019028e8eeaef149c934543b414fc460cf2e95eb4&"

BANNER_UNLOCK = ""

BANNER_SLOWMODE = ""

BANNER_UNBAN = "https://cdn.discordapp.com/attachments/1527325771650171028/1543421726812278895/Gemini_Generated_Image_52ctw952ctw952ct.jpg?ex=6a94ceff&is=6a937d7f&hm=3f048287d1d8570ebcc5ef77611fbe1631da17f3aedd86f6e66f92b086e6a983&"


# ============================================================
# GARANTIR PASTA DE DADOS
# ============================================================

PASTA_DATA.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# VIEW DE CONFIRMAÇÃO
# ============================================================

class ConfirmacaoView(discord.ui.View):

    def __init__(self, autor):

        super().__init__(
            timeout=30
        )

        self.autor = autor
        self.confirmado = None

    # ========================================================
    # VERIFICAR USUÁRIO
    # ========================================================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.autor.id:

            await interaction.response.send_message(
                "❌ Apenas o moderador que iniciou esta ação "
                "pode utilizar estes botões.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # BOTÃO SIM
    # ========================================================

    @discord.ui.button(
        label="Sim",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def sim(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.confirmado = True

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="✅ **Ação confirmada. Executando...**",
            view=self
        )

        self.stop()

    # ========================================================
    # BOTÃO NÃO
    # ========================================================

    @discord.ui.button(
        label="Não",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def nao(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.confirmado = False

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content="❌ **Ação cancelada.**",
            view=self
        )

        self.stop()


# ============================================================
# COG MODERATION
# ============================================================

class Moderation(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.warns = {}

        self.carregar_warns()

    # ========================================================
    # CARREGAR WARNS
    # ========================================================

    def carregar_warns(self):

        if not ARQUIVO_WARNS.exists():

            self.warns = {}

            self.salvar_warns()

            return

        try:

            with open(
                ARQUIVO_WARNS,
                "r",
                encoding="utf-8"
            ) as arquivo:

                self.warns = json.load(arquivo)

        except (
            json.JSONDecodeError,
            OSError
        ):

            print(
                "[WARNS] Não foi possível carregar "
                "o arquivo de warns."
            )

            self.warns = {}

    # ========================================================
    # SALVAR WARNS
    # ========================================================

    def salvar_warns(self):

        try:

            with open(
                ARQUIVO_WARNS,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    self.warns,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError as erro:

            print(
                f"[WARNS] Erro ao salvar warns: {erro}"
            )

    # ========================================================
    # OBTER WARNS
    # ========================================================

    def obter_warns(
        self,
        guild_id,
        user_id
    ):

        guild_id = str(guild_id)
        user_id = str(user_id)

        if guild_id not in self.warns:

            self.warns[guild_id] = {}

        if user_id not in self.warns[guild_id]:

            self.warns[guild_id][user_id] = []

        return self.warns[guild_id][user_id]

    # ========================================================
    # APLICAR BANNER
    # ========================================================

    def aplicar_banner(
        self,
        embed,
        banner
    ):

        if banner:

            embed.set_image(
                url=banner
            )

        return embed

    # ========================================================
    # EMBED PADRÃO
    # ========================================================

    def criar_embed(
        self,
        titulo,
        membro,
        moderador,
        motivo,
        emoji,
        cor,
        banner=""
    ):

        embed = discord.Embed(
            title=f"{emoji} {titulo}",
            color=cor,
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="👤 Usuário",
            value=(
                f"{membro.mention}\n"
                f"`{membro}`\n"
                f"🆔 `{membro.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🛡️ Moderador",
            value=(
                f"{moderador.mention}\n"
                f"`{moderador}`\n"
                f"🆔 `{moderador.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )

        embed.set_footer(
            text="Royalt Moderation"
        )

        self.aplicar_banner(
            embed,
            banner
        )

        return embed

    # ========================================================
    # ENVIAR LOG
    # ========================================================

    async def enviar_log(
        self,
        guild,
        titulo,
        descricao,
        emoji="📜",
        cor=discord.Color.dark_gray(),
        banner=""
    ):

        if guild is None:
            return

        canal = discord.utils.get(
            guild.text_channels,
            name=NOME_CANAL_LOGS
        )

        if canal is None:

            print(
                f"[LOGS] Canal {NOME_CANAL_LOGS} "
                f"não encontrado em {guild.name}."
            )

            return

        embed = discord.Embed(
            title=f"{emoji} {titulo}",
            description=descricao,
            color=cor,
            timestamp=datetime.now(timezone.utc)
        )

        embed.set_footer(
            text="Royalt Logging System"
        )

        self.aplicar_banner(
            embed,
            banner
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                f"[LOGS] Royalt não possui permissão "
                f"para enviar mensagens em {guild.name}."
            )

        except discord.HTTPException as erro:

            print(
                f"[LOGS] Erro ao enviar log: {erro}"
            )

    # ========================================================
    # CONFIRMAÇÃO GENÉRICA
    # ========================================================

    async def pedir_confirmacao(
        self,
        ctx,
        titulo,
        descricao,
        cor,
        banner=""
    ):

        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=cor,
            timestamp=datetime.now(timezone.utc)
        )

        if banner:
            embed.set_image(
                url=banner
            )

        embed.set_footer(
            text="Royalt Moderation • Confirmação"
        )

        view = ConfirmacaoView(
            ctx.author
        )

        mensagem = await ctx.send(
            embed=embed,
            view=view
        )

        await view.wait()

        if view.confirmado is None:

            for item in view.children:
                item.disabled = True

            await mensagem.edit(
                content="⌛ **A confirmação expirou. Ação cancelada.**",
                view=view
            )

            return False

        if view.confirmado is False:

            return False

        return True

    # ========================================================
    # BAN
    # ========================================================

    @commands.hybrid_command(
        name="ban",
        description="Bane um usuário do servidor."
    )
    @commands.has_permissions(
        ban_members=True
    )
    @commands.bot_has_permissions(
        ban_members=True
    )
    async def ban(
        self,
        ctx,
        membro: discord.Member,
        *,
        motivo: str = "Nenhum motivo informado"
    ):

        confirmado = await self.pedir_confirmacao(
            ctx,
            "🔨 CONFIRMAR BANIMENTO",
            (
                f"Você realmente deseja banir "
                f"{membro.mention}?\n\n"
                f"👤 **Usuário:** `{membro}`\n"
                f"🆔 **ID:** `{membro.id}`\n"
                f"📝 **Motivo:** {motivo}\n\n"
                "⚠️ Essa ação removerá o usuário do servidor."
            ),
            COR_BAN,
            BANNER_BAN
        )

        if not confirmado:
            return

        try:

            await membro.ban(
                reason=motivo
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para banir esse usuário."
            )

            return

        embed = self.criar_embed(
            "USUÁRIO BANIDO",
            membro,
            ctx.author,
            motivo,
            "🔨",
            COR_BAN,
            BANNER_BAN
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Usuário banido",
            (
                f"👤 **Usuário:** {membro}\n"
                f"🆔 **ID:** `{membro.id}`\n\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{ctx.author.id}`\n\n"
                f"📝 **Motivo:** {motivo}"
            ),
            "🔨",
            COR_BAN,
            BANNER_BAN
        )

    # ========================================================
    # UNBAN
    # ========================================================

    @commands.hybrid_command(
        name="unban",
        description="Remove o banimento de um usuário."
    )
    @commands.has_permissions(
        ban_members=True
    )
    @commands.bot_has_permissions(
        ban_members=True
    )
    async def unban(
        self,
        ctx,
        usuario: discord.User,
        *,
        motivo: str = "Nenhum motivo informado"
    ):

        confirmado = await self.pedir_confirmacao(
            ctx,
            "🔓 CONFIRMAR UNBAN",
            (
                f"Você realmente deseja remover o banimento de "
                f"**{usuario}**?\n\n"
                f"👤 **Usuário:** `{usuario}`\n"
                f"🆔 **ID:** `{usuario.id}`\n"
                f"📝 **Motivo:** {motivo}"
            ),
            COR_UNBAN,
            BANNER_UNBAN
        )

        if not confirmado:
            return

        try:

            await ctx.guild.unban(
                usuario,
                reason=motivo
            )

        except discord.NotFound:

            await ctx.send(
                "❌ Esse usuário não está banido ou não foi encontrado na lista de banidos."
            )

            return

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para remover banimentos."
            )

            return

        embed = discord.Embed(
            title="🔓 BANIMENTO REMOVIDO",
            description=(
                f"👤 **Usuário:** `{usuario}`\n"
                f"🆔 **ID:** `{usuario.id}`\n\n"
                f"🛡️ **Moderador:** {ctx.author.mention}\n"
                f"📝 **Motivo:** {motivo}"
            ),
            color=COR_UNBAN,
            timestamp=datetime.now(timezone.utc)
        )

        self.aplicar_banner(
            embed,
            BANNER_UNBAN
        )

        embed.set_footer(
            text="Royalt Moderation"
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Banimento removido",
            (
                f"👤 **Usuário:** {usuario}\n"
                f"🆔 **ID:** `{usuario.id}`\n\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{ctx.author.id}`\n\n"
                f"📝 **Motivo:** {motivo}"
            ),
            "🔓",
            COR_UNBAN,
            BANNER_UNBAN
        )

    # ========================================================
    # KICK
    # ========================================================

    @commands.hybrid_command(
        name="kick",
        description="Expulsa um usuário do servidor."
    )
    @commands.has_permissions(
        kick_members=True
    )
    @commands.bot_has_permissions(
        kick_members=True
    )
    async def kick(
        self,
        ctx,
        membro: discord.Member,
        *,
        motivo: str = "Nenhum motivo informado"
    ):

        confirmado = await self.pedir_confirmacao(
            ctx,
            "👢 CONFIRMAR EXPULSÃO",
            (
                f"Você realmente deseja expulsar "
                f"{membro.mention}?\n\n"
                f"👤 **Usuário:** `{membro}`\n"
                f"🆔 **ID:** `{membro.id}`\n"
                f"📝 **Motivo:** {motivo}"
            ),
            COR_KICK,
            BANNER_KICK
        )

        if not confirmado:
            return

        try:

            await membro.kick(
                reason=motivo
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para expulsar esse usuário."
            )

            return

        embed = self.criar_embed(
            "USUÁRIO EXPULSO",
            membro,
            ctx.author,
            motivo,
            "👢",
            COR_KICK,
            BANNER_KICK
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Usuário expulso",
            (
                f"👤 **Usuário:** {membro}\n"
                f"🆔 **ID:** `{membro.id}`\n\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{ctx.author.id}`\n\n"
                f"📝 **Motivo:** {motivo}"
            ),
            "👢",
            COR_KICK,
            BANNER_KICK
        )

    # ========================================================
    # TIMEOUT / MUTE
    # ========================================================

    @commands.hybrid_command(
        name="timeout",
        description="Coloca um usuário em timeout/mute."
    )
    @commands.has_permissions(
        moderate_members=True
    )
    @commands.bot_has_permissions(
        moderate_members=True
    )
    async def timeout(
        self,
        ctx,
        membro: discord.Member,
        minutos: int,
        *,
        motivo: str = "Nenhum motivo informado"
    ):

        if minutos <= 0:

            await ctx.send(
                "❌ O tempo precisa ser maior que 0 minutos."
            )

            return

        duracao = timedelta(
            minutes=minutos
        )

        try:

            await membro.timeout(
                duracao,
                reason=motivo
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para aplicar timeout nesse usuário."
            )

            return

        embed = self.criar_embed(
            "TIMEOUT / MUTE APLICADO",
            membro,
            ctx.author,
            motivo,
            "⏳",
            COR_TIMEOUT,
            BANNER_TIMEOUT
        )

        embed.add_field(
            name="⏱️ Duração",
            value=f"**{minutos} minutos**",
            inline=False
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Timeout / Mute aplicado",
            (
                f"👤 **Usuário:** {membro}\n"
                f"🆔 **ID:** `{membro.id}`\n\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{ctx.author.id}`\n\n"
                f"⏱️ **Duração:** {minutos} minutos\n"
                f"📝 **Motivo:** {motivo}"
            ),
            "⏳",
            COR_TIMEOUT,
            BANNER_TIMEOUT
        )

    # ========================================================
    # UNMUTE
    # ========================================================

    @commands.hybrid_command(
        name="unmute",
        description="Remove o timeout de um usuário."
    )
    @commands.has_permissions(
        moderate_members=True
    )
    @commands.bot_has_permissions(
        moderate_members=True
    )
    async def unmute(
        self,
        ctx,
        membro: discord.Member,
        *,
        motivo: str = "Nenhum motivo informado"
    ):

        try:

            await membro.timeout(
                None,
                reason=motivo
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para remover o timeout."
            )

            return

        embed = self.criar_embed(
            "TIMEOUT REMOVIDO",
            membro,
            ctx.author,
            motivo,
            "🔊",
            COR_UNLOCK,
            BANNER_UNLOCK
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Timeout removido",
            (
                f"👤 **Usuário:** {membro}\n"
                f"🆔 **ID:** `{membro.id}`\n\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{ctx.author.id}`\n\n"
                f"📝 **Motivo:** {motivo}"
            ),
            "🔊",
            COR_UNLOCK,
            BANNER_UNLOCK
        )

    # ========================================================
    # WARN
    # ========================================================

    @commands.hybrid_command(
        name="warn",
        description="Adverte um usuário."
    )
    @commands.has_permissions(
        moderate_members=True
    )
    async def warn(
        self,
        ctx,
        membro: discord.Member,
        *,
        motivo: str = "Nenhum motivo informado"
    ):

        lista_warns = self.obter_warns(
            ctx.guild.id,
            membro.id
        )

        agora = datetime.now(
            timezone.utc
        )

        lista_warns.append(
            {
                "motivo": motivo,
                "moderador": ctx.author.id,
                "moderador_nome": str(ctx.author),
                "data": agora.isoformat()
            }
        )

        self.salvar_warns()

        quantidade = len(
            lista_warns
        )

        embed = self.criar_embed(
            "ADVERTÊNCIA APLICADA",
            membro,
            ctx.author,
            motivo,
            "⚠️",
            COR_WARN,
            BANNER_WARN
        )

        embed.add_field(
            name="📊 Total de avisos",
            value=f"**{quantidade}**",
            inline=False
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Advertência aplicada",
            (
                f"👤 **Usuário:** {membro.mention}\n"
                f"🆔 **ID:** `{membro.id}`\n\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🆔 **ID:** `{ctx.author.id}`\n\n"
                f"📝 **Motivo:** {motivo}\n\n"
                f"📊 **Total de avisos:** "
                f"**{quantidade}**"
            ),
            "⚠️",
            COR_WARN,
            BANNER_WARN
        )

    # ========================================================
    # VER WARNS
    # ========================================================

    @commands.hybrid_command(
        name="warns",
        description="Mostra os avisos de um usuário."
    )
    @commands.has_permissions(
        moderate_members=True
    )
    async def warns(
        self,
        ctx,
        membro: discord.Member
    ):

        lista_warns = self.obter_warns(
            ctx.guild.id,
            membro.id
        )

        quantidade = len(
            lista_warns
        )

        embed = discord.Embed(
            title="📋 HISTÓRICO DE ADVERTÊNCIAS",
            description=(
                f"👤 **Usuário:** "
                f"{membro.mention}\n"
                f"🆔 **ID:** `{membro.id}`\n"
                f"📊 **Total:** "
                f"**{quantidade} aviso(s)**"
            ),
            color=COR_WARNS,
            timestamp=datetime.now(timezone.utc)
        )

        if quantidade == 0:

            embed.add_field(
                name="📭 Histórico",
                value=(
                    "Este usuário não possui "
                    "advertências registradas."
                ),
                inline=False
            )

        else:

            ultimos = lista_warns[-10:]

            linhas = []

            inicio = (
                quantidade
                - len(ultimos)
                + 1
            )

            for numero, warn_data in enumerate(
                ultimos,
                start=inicio
            ):

                data_texto = warn_data.get(
                    "data",
                    "Data desconhecida"
                )

                try:

                    data = datetime.fromisoformat(
                        data_texto
                    )

                    timestamp = int(
                        data.timestamp()
                    )

                    data_formatada = (
                        f"<t:{timestamp}:f>"
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    data_formatada = data_texto

                linhas.append(
                    f"**#{numero}** • "
                    f"{data_formatada}\n"
                    f"📝 {warn_data.get('motivo', 'Sem motivo')}\n"
                    f"🛡️ <@{warn_data.get('moderador', '0')}>"
                )

            texto = "\n\n".join(
                linhas
            )

            embed.add_field(
                name="⚠️ Últimos avisos",
                value=texto,
                inline=False
            )

        embed.set_footer(
            text="Royalt Moderation • Warn System"
        )

        self.aplicar_banner(
            embed,
            BANNER_WARNS
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # CLEAR
    # ========================================================

    @commands.hybrid_command(
        name="clear",
        description="Apaga mensagens do canal."
    )
    @commands.has_permissions(
        manage_messages=True
    )
    @commands.bot_has_permissions(
        manage_messages=True
    )
    async def clear(
        self,
        ctx,
        quantidade: int
    ):

        if quantidade <= 0:

            await ctx.send(
                "❌ A quantidade precisa ser maior que 0."
            )

            return

        mensagens = await ctx.channel.purge(
            limit=quantidade + 1
        )

        apagadas = max(
            len(mensagens) - 1,
            0
        )

        embed = discord.Embed(
            title="🧹 MENSAGENS APAGADAS",
            description=(
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"📍 **Canal:** "
                f"{ctx.channel.mention}\n"
                f"🧹 **Quantidade:** "
                f"**{apagadas}**"
            ),
            color=COR_CLEAR,
            timestamp=datetime.now(timezone.utc)
        )

        embed.set_footer(
            text="Royalt Moderation"
        )

        self.aplicar_banner(
            embed,
            BANNER_CLEAR
        )

        await ctx.send(
            embed=embed,
            delete_after=5
        )

        await self.enviar_log(
            ctx.guild,
            "Mensagens apagadas",
            (
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"📍 **Canal:** "
                f"{ctx.channel.mention}\n"
                f"🧹 **Quantidade:** "
                f"**{apagadas}**"
            ),
            "🧹",
            COR_CLEAR,
            BANNER_CLEAR
        )

    # ========================================================
    # LOCK
    # ========================================================

    @commands.hybrid_command(
        name="lock",
        description="Bloqueia o canal para membros."
    )
    @commands.has_permissions(
        manage_channels=True
    )
    @commands.bot_has_permissions(
        manage_channels=True
    )
    async def lock(
        self,
        ctx
    ):

        canal = ctx.channel

        await canal.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )

        embed = discord.Embed(
            title="🔒 CANAL BLOQUEADO",
            description=(
                f"📍 **Canal:** "
                f"{canal.mention}\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}"
            ),
            color=COR_LOCK,
            timestamp=datetime.now(timezone.utc)
        )

        embed.set_footer(
            text="Royalt Moderation"
        )

        self.aplicar_banner(
            embed,
            BANNER_LOCK
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Canal bloqueado",
            (
                f"📍 **Canal:** "
                f"{canal.mention}\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}"
            ),
            "🔒",
            COR_LOCK,
            BANNER_LOCK
        )

    # ========================================================
    # UNLOCK
    # ========================================================

    @commands.hybrid_command(
        name="unlock",
        description="Desbloqueia o canal."
    )
    @commands.has_permissions(
        manage_channels=True
    )
    @commands.bot_has_permissions(
        manage_channels=True
    )
    async def unlock(
        self,
        ctx
    ):

        canal = ctx.channel

        await canal.set_permissions(
            ctx.guild.default_role,
            send_messages=None
        )

        embed = discord.Embed(
            title="🔓 CANAL DESBLOQUEADO",
            description=(
                f"📍 **Canal:** "
                f"{canal.mention}\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}"
            ),
            color=COR_UNLOCK,
            timestamp=datetime.now(timezone.utc)
        )

        embed.set_footer(
            text="Royalt Moderation"
        )

        self.aplicar_banner(
            embed,
            BANNER_UNLOCK
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Canal desbloqueado",
            (
                f"📍 **Canal:** "
                f"{canal.mention}\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}"
            ),
            "🔓",
            COR_UNLOCK,
            BANNER_UNLOCK
        )

    # ========================================================
    # SLOWMODE
    # ========================================================

    @commands.hybrid_command(
        name="slowmode",
        description="Define o slowmode do canal."
    )
    @commands.has_permissions(
        manage_channels=True
    )
    @commands.bot_has_permissions(
        manage_channels=True
    )
    async def slowmode(
        self,
        ctx,
        segundos: int
    ):

        if segundos < 0:

            await ctx.send(
                "❌ O valor não pode ser negativo."
            )

            return

        try:

            await ctx.channel.edit(
                slowmode_delay=segundos
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ Não tenho permissão para alterar o slowmode."
            )

            return

        embed = discord.Embed(
            title="🐌 SLOWMODE ALTERADO",
            description=(
                f"📍 **Canal:** "
                f"{ctx.channel.mention}\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🐌 **Tempo:** "
                f"**{segundos} segundos**"
            ),
            color=COR_SLOWMODE,
            timestamp=datetime.now(timezone.utc)
        )

        embed.set_footer(
            text="Royalt Moderation"
        )

        self.aplicar_banner(
            embed,
            BANNER_SLOWMODE
        )

        await ctx.send(
            embed=embed
        )

        await self.enviar_log(
            ctx.guild,
            "Slowmode alterado",
            (
                f"📍 **Canal:** "
                f"{ctx.channel.mention}\n"
                f"🛡️ **Moderador:** "
                f"{ctx.author.mention}\n"
                f"🐌 **Tempo:** "
                f"**{segundos} segundos**"
            ),
            "🐌",
            COR_SLOWMODE,
            BANNER_SLOWMODE
        )


# ============================================================
# CARREGAMENTO DA COG
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Moderation(bot)
    )