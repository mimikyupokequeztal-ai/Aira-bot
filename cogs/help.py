"""
ROYALT • HELP SYSTEM 4.0
Central de ajuda moderna com menus Select, histórico público e integração
com o sistema de atualizações.

Substitui o antigo help.py.

Requisitos:
- discord.py 2.x
- update_logger.py na mesma pasta/cog directory
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import asyncio

import discord
from discord.ext import commands

try:
    from .update_logger import (
        UpdateLogger,
        CONFIG_CATEGORIAS,
        descobrir_categoria,
        descobrir_emoji,
        nome_comando_completo,
        obter_assinatura,
        obter_aliases,
    )
except ImportError:
    from update_logger import (
        UpdateLogger,
        CONFIG_CATEGORIAS,
        descobrir_categoria,
        descobrir_emoji,
        nome_comando_completo,
        obter_assinatura,
        obter_aliases,
    )


VERSAO_HELP = "4.0"
NOME_SISTEMA = "Royalt • Central de Ajuda"

BANNER_HELP = (
    "https://cdn.discordapp.com/attachments/"
    "1527325771650171028/1543332063812391073/"
    "ChatGPT_Image_29_de_ago._de_2026_15_50_32.png"
    "?ex=6a947b7d&is=6a9329fd&hm="
    "4641b04e3566d13a0ae8f5769cf6a10cd148537bc9ea4f2ef15f963f15ac44ba"
)

COR_ROXA = discord.Color.from_rgb(128, 0, 255)
COR_AZUL = discord.Color.from_rgb(52, 152, 219)
COR_VERDE = discord.Color.from_rgb(46, 204, 113)
COR_VERMELHO = discord.Color.from_rgb(231, 76, 60)
COR_LARANJA = discord.Color.from_rgb(255, 159, 67)
COR_AMARELO = discord.Color.from_rgb(241, 196, 15)
COR_CINZA = discord.Color.from_rgb(149, 165, 166)


def _agora():
    return datetime.now(timezone.utc)


class HelpSelect(discord.ui.Select):
    """Menu principal do Help. Nada de uma parede de botões."""

    def __init__(self, view: "HelpView"):
        self.help_view = view

        options = [
            discord.SelectOption(
                label="Início",
                value="inicio",
                emoji="🏠",
                description="Visão geral da Central de Ajuda",
            ),
            discord.SelectOption(
                label="Comandos",
                value="comandos",
                emoji="📚",
                description="Escolha uma categoria de comandos",
            ),
            discord.SelectOption(
                label="Atualizações",
                value="updates",
                emoji="🛠️",
                description="Histórico público das mudanças",
            ),
            discord.SelectOption(
                label="Como funciona",
                value="como",
                emoji="💡",
                description="Entenda a Central e o histórico",
            ),
            discord.SelectOption(
                label="Fechar",
                value="fechar",
                emoji="✖️",
                description="Fechar esta Central de Ajuda",
            ),
        ]

        super().__init__(
            placeholder="📖 Navegue pela Central de Ajuda...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await self.help_view.validar_usuario(interaction):
            return

        valor = self.values[0]

        if valor == "inicio":
            embed = self.help_view.pagina_inicial()
            await interaction.response.edit_message(embed=embed, view=self.help_view)
            return

        if valor == "comandos":
            embed = self.help_view.pagina_categorias()
            self.help_view.rebuild()
            await interaction.response.edit_message(embed=embed, view=self.help_view)
            return

        if valor == "updates":
            embed = self.help_view.pagina_updates()
            await interaction.response.edit_message(embed=embed, view=self.help_view)
            return

        if valor == "como":
            embed = self.help_view.pagina_como_funciona()
            await interaction.response.edit_message(embed=embed, view=self.help_view)
            return

        await interaction.response.edit_message(
            content="📖 Central de Ajuda fechada.",
            embed=None,
            view=None,
        )
        self.help_view.stop()


class CategoriaSelect(discord.ui.Select):
    def __init__(self, view: "HelpView"):
        self.help_view = view
        categorias = view.categorias_existentes()

        options = []
        for categoria in categorias[:25]:
            config = CONFIG_CATEGORIAS.get(
                categoria, CONFIG_CATEGORIAS["outros"]
            )
            quantidade = len(view.comandos_categoria(categoria))
            options.append(
                discord.SelectOption(
                    label=config["nome"].title()[:100],
                    value=categoria,
                    emoji=config["emoji"],
                    description=f"{quantidade} comando(s) disponível(is)",
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="Nenhuma categoria",
                    value="outros",
                    emoji="📦",
                    description="Nenhum comando encontrado",
                )
            )

        super().__init__(
            placeholder="📚 Escolha uma categoria...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await self.help_view.validar_usuario(interaction):
            return

        categoria = self.values[0]
        self.help_view.categoria_atual = categoria
        await interaction.response.edit_message(
            embed=self.help_view.pagina_categoria(categoria),
            view=self.help_view,
        )


class UpdateSelect(discord.ui.Select):
    def __init__(self, view: "HelpView"):
        self.help_view = view
        options = [
            discord.SelectOption(
                label="Última atualização",
                value="latest",
                emoji="🆕",
                description="O que mudou recentemente",
            ),
            discord.SelectOption(
                label="Histórico público",
                value="history",
                emoji="📜",
                description="Consulte as últimas versões publicadas",
            ),
            discord.SelectOption(
                label="Como ler os updates",
                value="about",
                emoji="💡",
                description="Entenda o formato dos registros",
            ),
        ]
        super().__init__(
            placeholder="🛠️ Escolha uma seção de atualizações...",
            min_values=1,
            max_values=1,
            options=options,
            row=2,
        )

    async def callback(self, interaction: discord.Interaction):
        if not await self.help_view.validar_usuario(interaction):
            return

        valor = self.values[0]
        if valor == "latest":
            embed = self.help_view.pagina_updates(latest_only=True)
        elif valor == "history":
            embed = self.help_view.pagina_updates()
        else:
            embed = self.help_view.pagina_update_info()

        await interaction.response.edit_message(
            embed=embed,
            view=self.help_view,
        )


class HelpView(discord.ui.View):
    def __init__(self, bot, autor, update_logger: UpdateLogger):
        super().__init__(timeout=900)
        self.bot = bot
        self.autor = autor
        self.update_logger = update_logger
        self.categoria_atual: Optional[str] = None
        self.rebuild()

    async def validar_usuario(self, interaction):
        if interaction.user.id != self.autor.id:
            await interaction.response.send_message(
                "🔒 Esta Central foi aberta por outra pessoa.",
                ephemeral=True,
            )
            return False
        return True

    def rebuild(self):
        self.clear_items()
        self.add_item(HelpSelect(self))

        if self.categoria_atual:
            self.add_item(CategoriaSelect(self))
        else:
            # Mesmo sem categoria, deixa o seletor de categoria disponível.
            self.add_item(CategoriaSelect(self))

        self.add_item(UpdateSelect(self))

    def obter_comandos(self):
        comandos = []
        vistos = set()

        for comando in self.bot.walk_commands():
            if getattr(comando, "hidden", False):
                continue

            nome = nome_comando_completo(comando)
            if nome in vistos:
                continue

            vistos.add(nome)
            comandos.append(comando)

        return sorted(comandos, key=lambda c: nome_comando_completo(c).lower())

    def comandos_categoria(self, categoria):
        return [
            comando
            for comando in self.obter_comandos()
            if descobrir_categoria(comando) == categoria
        ]

    def categorias_existentes(self):
        encontradas = {
            descobrir_categoria(comando)
            for comando in self.obter_comandos()
        }

        ordem = [
            "moderacao",
            "warns",
            "seguranca",
            "sorteios",
            "tickets",
            "desabafos",
            "economia",
            "ship",
            "pokemon",
            "updates",
            "utilidades",
            "outros",
        ]
        return [categoria for categoria in ordem if categoria in encontradas]

    def base_embed(self, titulo, descricao, cor=COR_ROXA):
        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=cor,
            timestamp=_agora(),
        )

        if BANNER_HELP:
            embed.set_thumbnail(url=BANNER_HELP)

        embed.set_footer(
            text=f"{NOME_SISTEMA} • v{VERSAO_HELP} • {self.autor.display_name}"
        )
        return embed

    def pagina_inicial(self):
        comandos = self.obter_comandos()
        categorias = self.categorias_existentes()
        ultimo = self.update_logger.ultima_atualizacao()

        descricao = (
            "Uma central simples para encontrar comandos, entender sistemas "
            "e acompanhar as mudanças do Royalt.\n\n"
            "Use os menus abaixo para navegar — sem uma sequência enorme de botões."
        )

        embed = self.base_embed(
            "👑 ROYALT • CENTRAL DE AJUDA",
            descricao,
            COR_ROXA,
        )

        embed.add_field(
            name="📚 Comandos",
            value=f"`{len(comandos)}` comandos carregados",
            inline=True,
        )
        embed.add_field(
            name="🗂️ Categorias",
            value=f"`{len(categorias)}` áreas disponíveis",
            inline=True,
        )
        embed.add_field(
            name="🛠️ Atualizações",
            value=(
                f"`{ultimo['versao']}`"
                if ultimo
                else "Nenhuma publicada"
            ),
            inline=True,
        )

        if ultimo:
            resumo = ultimo.get("resumo", "Atualização do Royalt.")
            embed.add_field(
                name="✨ Última mudança",
                value=f"**{ultimo['versao']}** • {resumo}",
                inline=False,
            )

        embed.add_field(
            name="💡 Dica",
            value=(
                "Abra **Comandos** para escolher uma categoria ou "
                "vá em **Atualizações** para consultar o histórico."
            ),
            inline=False,
        )
        return embed

    def pagina_categorias(self):
        embed = self.base_embed(
            "📚 ROYALT • CATEGORIAS",
            "Selecione uma categoria no menu para ver os comandos disponíveis.",
            COR_AZUL,
        )

        for categoria in self.categorias_existentes():
            config = CONFIG_CATEGORIAS.get(
                categoria, CONFIG_CATEGORIAS["outros"]
            )
            quantidade = len(self.comandos_categoria(categoria))
            embed.add_field(
                name=f"{config['emoji']} {config['nome'].title()}",
                value=f"`{quantidade}` comando(s)",
                inline=True,
            )
        return embed

    def pagina_categoria(self, categoria):
        config = CONFIG_CATEGORIAS.get(
            categoria, CONFIG_CATEGORIAS["outros"]
        )
        comandos = self.comandos_categoria(categoria)

        embed = self.base_embed(
            f"{config['emoji']} ROYALT • {config['nome']}",
            f"**{len(comandos)}** comando(s) nesta categoria.",
            config["cor"],
        )

        if not comandos:
            embed.add_field(
                name="📭 Vazio",
                value="Nenhum comando disponível nesta categoria.",
                inline=False,
            )
            return embed

        # Uma categoria grande é dividida em campos menores para não virar
        # uma parede de texto. O Discord limita embeds a 25 fields.
        for comando in comandos[:20]:
            nome = nome_comando_completo(comando)
            descricao = (
                getattr(comando, "description", None)
                or "Sem descrição disponível."
            )
            assinatura = obter_assinatura(comando)
            aliases = obter_aliases(comando)
            emoji = descobrir_emoji(comando, categoria)

            uso = f"`!{nome}"
            if assinatura:
                uso += f" {assinatura}"
            uso += "`"

            valor = f"{descricao}\n\n📝 **Uso:** {uso}"
            if aliases:
                valor += "\n🔁 **Aliases:** " + ", ".join(
                    f"`{a}`" for a in aliases[:8]
                )

            if len(valor) > 1024:
                valor = valor[:1000] + "…"

            embed.add_field(
                name=f"{emoji} {nome}",
                value=valor,
                inline=False,
            )

        restantes = len(comandos) - min(len(comandos), 20)
        if restantes:
            embed.add_field(
                name="📦 Mais comandos",
                value=f"`{restantes}` comando(s) não exibido(s) nesta página.",
                inline=False,
            )

        return embed

    def pagina_updates(self, latest_only=False):
        registros = self.update_logger.historico_publico(
            limite=1 if latest_only else 8
        )

        embed = self.base_embed(
            "🛠️ ROYALT • ATUALIZAÇÕES",
            "Histórico público das mudanças do bot, escrito para usuários — não para programadores.",
            COR_VERDE,
        )

        if not registros:
            embed.add_field(
                name="📭 Nenhuma atualização registrada",
                value="O histórico público ainda está vazio.",
                inline=False,
            )
            return embed

        for registro in registros:
            versao = registro.get("versao", "?")
            titulo = registro.get("titulo", "Atualização")
            resumo = registro.get("resumo", "Mudanças gerais.")
            data = registro.get("data", "")
            itens = registro.get("itens", [])

            linhas = [f"**{resumo}**"]
            if data:
                linhas.append(f"🗓️ {data}")

            if itens:
                linhas.append("")
                for item in itens[:8]:
                    tipo = item.get("tipo", "mudanca")
                    texto = item.get("texto", "Alteração.")
                    emoji = {
                        "novo": "🆕",
                        "melhoria": "✨",
                        "correcao": "🛠️",
                        "removido": "🗑️",
                        "seguranca": "🛡️",
                    }.get(tipo, "•")
                    linhas.append(f"{emoji} {texto}")

            valor = "\n".join(linhas)
            if len(valor) > 1000:
                valor = valor[:997] + "…"

            embed.add_field(
                name=f"🚀 {versao} • {titulo}",
                value=valor,
                inline=False,
            )

        embed.add_field(
            name="📜 Histórico",
            value="Use o menu **Atualizações → Histórico público** para consultar as versões publicadas.",
            inline=False,
        )
        return embed

    def pagina_update_info(self):
        return self.base_embed(
            "💡 COMO LER OS UPDATES",
            (
                "O histórico público mostra as mudanças de forma humana e objetiva.\n\n"
                "🆕 **Novo** — algo que passou a existir.\n"
                "✨ **Melhoria** — algo que já existia e ficou melhor.\n"
                "🛠️ **Correção** — um problema foi corrigido.\n"
                "🗑️ **Removido** — algo deixou de existir.\n"
                "🛡️ **Segurança** — mudança relacionada à proteção do servidor/bot.\n\n"
                "Informações técnicas e internas ficam no histórico privado de desenvolvimento."
            ),
            COR_AZUL,
        )

    def pagina_como_funciona(self):
        return self.base_embed(
            "💡 ROYALT • COMO FUNCIONA",
            (
                "**Central de Ajuda**\n"
                "Os comandos carregados pelo bot são detectados automaticamente "
                "e organizados por categoria.\n\n"
                "**Histórico público**\n"
                "Mostra novidades em linguagem normal, sem códigos internos.\n\n"
                "**Histórico privado**\n"
                "Guarda detalhes técnicos para a equipe de desenvolvimento.\n\n"
                "Use os menus para navegar. A Central não depende de uma fileira "
                "de botões e pode crescer junto com o bot."
            ),
            COR_AZUL,
        )


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_logger = UpdateLogger(bot)
        self._update_task = bot.loop.create_task(self._verificar_updates_ao_iniciar())

    async def _verificar_updates_ao_iniciar(self):
        try:
            await self.bot.wait_until_ready()
            resultado = await self.update_logger.verificar_comandos_e_publicar()
            total = (
                len(resultado["novos"])
                + len(resultado["alterados"])
                + len(resultado["removidos"])
            )
            if total:
                print(
                    "[HELP] Atualizações detectadas: "
                    f"{len(resultado['novos'])} novos, "
                    f"{len(resultado['alterados'])} alterados, "
                    f"{len(resultado['removidos'])} removidos."
                )
        except asyncio.CancelledError:
            raise
        except Exception as erro:
            print(f"[HELP] Erro ao verificar atualizações: {erro}")

    def cog_unload(self):
        if self._update_task and not self._update_task.done():
            self._update_task.cancel()

    @commands.hybrid_command(
        name="ajuda",
        aliases=["comandos"],
        description="Abre a Central de Ajuda do Royalt.",
    )
    async def ajuda(self, ctx):
        view = HelpView(self.bot, ctx.author, self.update_logger)
        await ctx.send(embed=view.pagina_inicial(), view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))

    # Publica os hybrid commands como slash commands.
    # Se o main.py já faz o sync da árvore, este sync pode ser removido
    # para evitar sincronização duplicada.
    try:
        await bot.tree.sync()
        print("[HELP] Slash commands sincronizados.")
    except Exception as erro:
        print(f"[HELP] Erro ao sincronizar slash commands: {erro}")
