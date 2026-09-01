import asyncio
import html
import json
import re
import time

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Optional

import aiohttp
import discord

from discord.ext import commands


# ============================================================
# IDENTIDADE
# ============================================================

NOME_SISTEMA = "Royalt Research System"


# ============================================================
# CORES
# ============================================================

COR_PESQUISA = discord.Color.blurple()
COR_SUCESSO = discord.Color.green()
COR_AVISO = discord.Color.orange()
COR_ERRO = discord.Color.red()


# ============================================================
# ENDPOINTS
# ============================================================

DUCKDUCKGO_HTML = (
    "https://html.duckduckgo.com/html/"
)

WIKIPEDIA_PT = (
    "https://pt.wikipedia.org/w/api.php"
)

WIKIPEDIA_EN = (
    "https://en.wikipedia.org/w/api.php"
)


# ============================================================
# PERFORMANCE
# ============================================================

TIMEOUT_DUCKDUCKGO = 6.0

TIMEOUT_WIKIPEDIA = 5.0

MAX_RESULTADOS_DDG = 8

MAX_RESULTADOS_WIKI = 4

MAX_RESULTADOS_FINAIS = 10

MAX_BOTOES_FONTES = 5

CACHE_TTL = 45


# ============================================================
# HTTP
# ============================================================

class ClienteHTTP:

    def __init__(
        self
    ):

        self.session: Optional[
            aiohttp.ClientSession
        ] = None

        self.lock = asyncio.Lock()

    # ========================================================
    # INICIAR
    # ========================================================

    async def iniciar(
        self
    ):

        if (
            self.session is not None
            and not self.session.closed
        ):

            return

        async with self.lock:

            if (
                self.session is not None
                and not self.session.closed
            ):

                return

            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/150.0 Safari/537.36 "
                        "RoyaltResearch/5.0"
                    ),
                    "Accept": (
                        "text/html,"
                        "application/xhtml+xml,"
                        "application/json;q=0.9,"
                        "*/*;q=0.8"
                    ),
                    "Accept-Language": (
                        "pt-BR,pt;q=0.9,en;q=0.7"
                    )
                }
            )

    # ========================================================
    # FECHAR
    # ========================================================

    async def fechar(
        self
    ):

        if self.session is not None:

            if not self.session.closed:

                await self.session.close()

            self.session = None

    # ========================================================
    # GET TEXTO
    # ========================================================

    async def get_text(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        timeout: float = 6.0
    ):

        await self.iniciar()

        if self.session is None:

            return None

        try:

            async with self.session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(
                    total=timeout
                ),
                allow_redirects=True
            ) as resposta:

                if resposta.status != 200:

                    return None

                return await resposta.text(
                    encoding="utf-8",
                    errors="ignore"
                )

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError
        ):

            return None


# ============================================================
# RESULTADO
# ============================================================

@dataclass
class ResultadoPesquisa:

    titulo: str

    descricao: str

    url: str

    fonte: str

    pontuacao: float = 0.0

    dominio: str = ""


# ============================================================
# PARSER DUCKDUCKGO
# ============================================================

class DuckParser(
    HTMLParser
):

    def __init__(
        self
    ):

        super().__init__(
            convert_charrefs=True
        )

        self.resultados = []

        self.ativo = False

        self.em_titulo = False

        self.em_descricao = False

        self.url = ""

        self.titulo = ""

        self.descricao = ""

    # ========================================================
    # START TAG
    # ========================================================

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        atributos = dict(
            attrs
        )

        classe = atributos.get(
            "class",
            ""
        )

        classes = classe.split()

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        if (
            tag == "div"
            and "result" in classes
            and "results_links" in classes
        ):

            self.ativo = True

            self.url = ""

            self.titulo = ""

            self.descricao = ""

            return

        if not self.ativo:

            return

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        if (
            tag == "a"
            and "result__a" in classes
        ):

            self.em_titulo = True

            href = atributos.get(
                "href",
                ""
            )

            self.url = (
                html.unescape(
                    href
                ).strip()
            )

        # ----------------------------------------------------
        # DESCRIÇÃO
        # ----------------------------------------------------

        if (
            tag == "a"
            and "result__snippet" in classes
        ):

            self.em_descricao = True

        if (
            tag == "div"
            and "result__snippet" in classes
        ):

            self.em_descricao = True

    # ========================================================
    # END TAG
    # ========================================================

    def handle_endtag(
        self,
        tag
    ):

        if tag == "a":

            self.em_titulo = False

        if tag in (
            "div",
            "a"
        ):

            if (
                self.titulo.strip()
                and self.url.strip()
                and len(
                    self.titulo.strip()
                ) > 3
            ):

                self.resultados.append(
                    {
                        "titulo": (
                            self.titulo.strip()
                        ),
                        "descricao": (
                            self.descricao.strip()
                        ),
                        "url": (
                            self.url.strip()
                        )
                    }
                )

                self.ativo = False

                self.titulo = ""

                self.descricao = ""

                self.url = ""

    # ========================================================
    # DATA
    # ========================================================

    def handle_data(
        self,
        data
    ):

        if not self.ativo:

            return

        texto = data.strip()

        if not texto:

            return

        if self.em_titulo:

            self.titulo += (
                " " + texto
            )

        elif self.em_descricao:

            self.descricao += (
                " " + texto
            )


# ============================================================
# MOTOR
# ============================================================

class MotorPesquisa:

    def __init__(
        self
    ):

        self.http = ClienteHTTP()

        self.cache = {}

        self.cache_lock = asyncio.Lock()

    # ========================================================
    # FECHAR
    # ========================================================

    async def fechar(
        self
    ):

        await self.http.fechar()

    # ========================================================
    # NORMALIZAR
    # ========================================================

    @staticmethod
    def normalizar(
        texto: str
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            texto
        ).strip()

    # ========================================================
    # URL
    # ========================================================

    @staticmethod
    def normalizar_url(
        url: str
    ) -> str:

        url = (
            url
            .strip()
            .lower()
        )

        url = re.sub(
            r"^https?://",
            "",
            url
        )

        return url.rstrip("/")

    # ========================================================
    # DOMÍNIO
    # ========================================================

    @staticmethod
    def dominio(
        url: str
    ) -> str:

        url = re.sub(
            r"^https?://",
            "",
            url.lower()
        )

        return (
            url
            .split("/")[0]
            .split("?")[0]
        )

    # ========================================================
    # DUCKDUCKGO
    # ========================================================

    async def buscar_duckduckgo(
        self,
        consulta: str
    ):

        inicio = time.monotonic()

        pagina = await self.http.get_text(
            DUCKDUCKGO_HTML,
            params={
                "q": consulta,
                "kl": "br-pt",
                "kp": "1"
            },
            timeout=TIMEOUT_DUCKDUCKGO
        )

        tempo = (
            time.monotonic()
            - inicio
        )

        if not pagina:

            return [], tempo

        parser = DuckParser()

        try:

            parser.feed(
                pagina
            )

        except Exception:

            return [], tempo

        resultados = []

        for item in parser.resultados:

            titulo = self.normalizar(
                item["titulo"]
            )

            descricao = self.normalizar(
                item["descricao"]
            )

            url = item["url"].strip()

            if not titulo or not url:

                continue

            # ------------------------------------------------
            # Algumas páginas podem retornar redirecionamento.
            # Só usamos links HTTP(S).
            # ------------------------------------------------

            if not (
                url.startswith(
                    "http://"
                )
                or url.startswith(
                    "https://"
                )
            ):

                continue

            if len(
                descricao
            ) > 1000:

                descricao = (
                    descricao[:1000]
                    + "..."
                )

            resultados.append(
                ResultadoPesquisa(
                    titulo=titulo,
                    descricao=(
                        descricao
                        or "Sem descrição disponível."
                    ),
                    url=url,
                    fonte="DuckDuckGo",
                    dominio=self.dominio(
                        url
                    )
                )
            )

            if (
                len(resultados)
                >= MAX_RESULTADOS_DDG
            ):

                break

        return resultados, tempo

    # ========================================================
    # WIKIPEDIA
    # ========================================================

    async def buscar_wikipedia(
        self,
        consulta: str,
        idioma: str
    ):

        endpoint = (
            WIKIPEDIA_PT
            if idioma == "pt"
            else WIKIPEDIA_EN
        )

        inicio = time.monotonic()

        pagina = await self.http.get_text(
            endpoint,
            params={
                "action": "query",
                "format": "json",

                # Pesquisa da wiki.
                "list": "search",

                "srsearch": consulta,

                "srlimit": MAX_RESULTADOS_WIKI,

                "srprop": "snippet"
            },
            timeout=TIMEOUT_WIKIPEDIA
        )

        tempo = (
            time.monotonic()
            - inicio
        )

        if not pagina:

            return [], tempo

        try:

            dados = json.loads(
                pagina
            )

        except json.JSONDecodeError:

            return [], tempo

        itens = (
            dados
            .get(
                "query",
                {}
            )
            .get(
                "search",
                []
            )
        )

        resultados = []

        dominio = (
            "https://pt.wikipedia.org/wiki/"
            if idioma == "pt"
            else "https://en.wikipedia.org/wiki/"
        )

        for item in itens:

            titulo = str(
                item.get(
                    "title",
                    ""
                )
            ).strip()

            snippet = str(
                item.get(
                    "snippet",
                    ""
                )
            ).strip()

            if not titulo:

                continue

            # Remover HTML do snippet.
            snippet = re.sub(
                r"<[^>]+>",
                "",
                snippet
            )

            snippet = (
                html.unescape(
                    snippet
                )
            )

            pagina_url = (
                dominio
                + titulo.replace(
                    " ",
                    "_"
                )
            )

            resultados.append(
                ResultadoPesquisa(
                    titulo=titulo,
                    descricao=(
                        snippet
                        or "Sem resumo disponível."
                    ),
                    url=pagina_url,
                    fonte=(
                        "Wikipedia PT"
                        if idioma == "pt"
                        else "Wikipedia EN"
                    ),
                    dominio=(
                        "pt.wikipedia.org"
                        if idioma == "pt"
                        else "en.wikipedia.org"
                    )
                )
            )

        return resultados, tempo

    # ========================================================
    # PESQUISA PARALELA
    # ========================================================

    async def pesquisar_fontes(
        self,
        consulta
    ):

        tarefas = [

            asyncio.create_task(
                self.buscar_duckduckgo(
                    consulta
                )
            ),

            asyncio.create_task(
                self.buscar_wikipedia(
                    consulta,
                    "pt"
                )
            ),

            asyncio.create_task(
                self.buscar_wikipedia(
                    consulta,
                    "en"
                )
            )
        ]

        respostas = await asyncio.gather(
            *tarefas,
            return_exceptions=True
        )

        resultados = []

        tempos = []

        nomes = (
            "DuckDuckGo",
            "Wikipedia PT",
            "Wikipedia EN"
        )

        for indice, resposta in enumerate(
            respostas
        ):

            nome = nomes[
                indice
            ]

            if isinstance(
                resposta,
                Exception
            ):

                tempos.append(
                    {
                        "fonte": nome,
                        "funcionou": False,
                        "tempo": 0.0
                    }
                )

                continue

            grupo, tempo = resposta

            tempos.append(
                {
                    "fonte": nome,
                    "funcionou": bool(
                        grupo
                    ),
                    "tempo": tempo
                }
            )

            if isinstance(
                grupo,
                list
            ):

                resultados.extend(
                    grupo
                )

        return resultados, tempos

    # ========================================================
    # RANKING
    # ========================================================

    def pontuar(
        self,
        resultado,
        consulta
    ):

        consulta_lower = (
            consulta.lower()
        )

        titulo = (
            resultado.titulo.lower()
        )

        descricao = (
            resultado.descricao.lower()
        )

        pontos = 0.0

        # ----------------------------------------------------
        # Correspondência total
        # ----------------------------------------------------

        if consulta_lower in titulo:

            pontos += 7

        # ----------------------------------------------------
        # Termos
        # ----------------------------------------------------

        termos = [
            termo
            for termo in re.findall(
                r"\w+",
                consulta_lower,
                flags=re.UNICODE
            )
            if len(termo) >= 3
        ]

        for termo in termos:

            if termo in titulo:

                pontos += 2

            elif termo in descricao:

                pontos += 0.5

        # ----------------------------------------------------
        # Fontes de referência
        # ----------------------------------------------------

        fontes_prioritarias = (
            "gov.br",
            "who.int",
            "unicef.org",
            "nih.gov",
            "ncbi.nlm.nih.gov",
            "scielo.br",
            "scielo.org",
            "nature.com"
        )

        if any(
            dominio in resultado.dominio
            for dominio in fontes_prioritarias
        ):

            pontos += 3

        # ----------------------------------------------------
        # Wikipedia
        # ----------------------------------------------------

        if "wikipedia" in (
            resultado.fonte.lower()
        ):

            pontos += 1

        # ----------------------------------------------------
        # HTTPS
        # ----------------------------------------------------

        if resultado.url.startswith(
            "https://"
        ):

            pontos += 0.25

        resultado.pontuacao = pontos

        return resultado

    # ========================================================
    # DEDUPLICAÇÃO
    # ========================================================

    def deduplicar(
        self,
        resultados
    ):

        urls = set()

        titulos = set()

        finais = []

        for resultado in resultados:

            url = self.normalizar_url(
                resultado.url
            )

            titulo = self.normalizar(
                resultado.titulo
            ).lower()

            if url in urls:

                continue

            if titulo in titulos:

                continue

            urls.add(
                url
            )

            titulos.add(
                titulo
            )

            finais.append(
                resultado
            )

        return finais

    # ========================================================
    # CACHE
    # ========================================================

    async def obter_cache(
        self,
        consulta
    ):

        agora = time.monotonic()

        async with self.cache_lock:

            item = self.cache.get(
                consulta
            )

            if item is None:

                return None

            timestamp, resultados = item

            if (
                agora - timestamp
                > CACHE_TTL
            ):

                self.cache.pop(
                    consulta,
                    None
                )

                return None

            return list(
                resultados
            )

    async def salvar_cache(
        self,
        consulta,
        resultados
    ):

        async with self.cache_lock:

            self.cache[
                consulta
            ] = (
                time.monotonic(),
                list(
                    resultados
                )
            )

    # ========================================================
    # PESQUISA PRINCIPAL
    # ========================================================

    async def pesquisar(
        self,
        consulta
    ):

        consulta = self.normalizar(
            consulta
        )

        if not consulta:

            return [], []

        # ----------------------------------------------------
        # CACHE
        # ----------------------------------------------------

        cache = await self.obter_cache(
            consulta.lower()
        )

        if cache is not None:

            return (
                cache,
                []
            )

        # ----------------------------------------------------
        # FONTES
        # ----------------------------------------------------

        resultados, tempos = (
            await self.pesquisar_fontes(
                consulta
            )
        )

        # ----------------------------------------------------
        # DEDUPLICAR
        # ----------------------------------------------------

        resultados = self.deduplicar(
            resultados
        )

        # ----------------------------------------------------
        # RANKING
        # ----------------------------------------------------

        for resultado in resultados:

            self.pontuar(
                resultado,
                consulta
            )

        resultados.sort(
            key=lambda item:
            item.pontuacao,
            reverse=True
        )

        resultados = resultados[
            :MAX_RESULTADOS_FINAIS
        ]

        # ----------------------------------------------------
        # CACHE
        # ----------------------------------------------------

        if resultados:

            await self.salvar_cache(
                consulta.lower(),
                resultados
            )

        return (
            resultados,
            tempos
        )


# ============================================================
# BOTÕES
# ============================================================

class PesquisaView(
    discord.ui.View
):

    def __init__(
        self,
        resultados
    ):

        super().__init__(
            timeout=180
        )

        for indice, resultado in enumerate(
            resultados[:MAX_BOTOES_FONTES],
            start=1
        ):

            self.add_item(
                discord.ui.Button(
                    label=f"Fonte {indice}",
                    emoji="🔗",
                    style=discord.ButtonStyle.link,
                    url=resultado.url
                )
            )


# ============================================================
# COG
# ============================================================

class DesabafosPesquisa(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.motor = MotorPesquisa()

    # ========================================================
    # UNLOAD
    # ========================================================

    def cog_unload(
        self
    ):

        try:

            asyncio.create_task(
                self.motor.fechar()
            )

        except RuntimeError:

            pass

    # ========================================================
    # PESQUISA INTERNA
    # ========================================================

    async def pesquisar(
        self,
        consulta
    ):

        return await self.motor.pesquisar(
            consulta
        )

    # ========================================================
    # EMBED FINAL
    # ========================================================

    def criar_embed_resultados(
        self,
        consulta,
        resultados,
        tempos,
        tempo_total
    ):

        if not resultados:

            embed = discord.Embed(
                title="🔎 ROYALT • PESQUISA",
                description=(
                    "Não encontrei resultados "
                    "suficientes para esta pesquisa."
                ),
                color=COR_AVISO
            )

            fontes_ok = sum(
                1
                for item in tempos
                if item["funcionou"]
            )

            embed.add_field(
                name="🌐 Fontes",
                value=(
                    f"**{fontes_ok}/3** responderam."
                ),
                inline=True
            )

            embed.add_field(
                name="⏱️ Tempo",
                value=(
                    f"**{tempo_total:.2f}s**"
                ),
                inline=True
            )

            embed.set_footer(
                text=NOME_SISTEMA
            )

            return embed

        embed = discord.Embed(
            title="🔎 ROYALT • PESQUISA",
            description=(
                f"Resultados para:\n"
                f"**{consulta}**"
            ),
            color=COR_PESQUISA
        )

        for indice, resultado in enumerate(
            resultados,
            start=1
        ):

            descricao = resultado.descricao

            if len(
                descricao
            ) > 650:

                descricao = (
                    descricao[:650]
                    + "..."
                )

            embed.add_field(
                name=(
                    f"{indice}. "
                    f"{resultado.titulo[:180]}"
                ),
                value=(
                    f"{descricao}\n\n"
                    f"🌐 **Fonte:** "
                    f"{resultado.fonte}\n"
                    f"🔗 [Abrir fonte]({resultado.url})"
                ),
                inline=False
            )

        fontes_ok = sum(
            1
            for item in tempos
            if item["funcionou"]
        )

        embed.add_field(
            name="⚡ Pesquisa",
            value=(
                f"⏱️ **{tempo_total:.2f}s**\n"
                f"🌐 **{fontes_ok}/3** fontes responderam\n"
                f"📚 **{len(resultados)}** resultados"
            ),
            inline=False
        )

        embed.set_footer(
            text=NOME_SISTEMA
        )

        return embed

    # ========================================================
    # !PESQUISAR
    # ========================================================

    @commands.command(
        name="pesquisar",
        aliases=[
            "pesquisa",
            "buscar"
        ],
        description=(
            "Pesquisa informações públicas "
            "na internet."
        )
    )
    @commands.cooldown(
        3,
        20,
        commands.BucketType.user
    )
    async def pesquisar_comando(
        self,
        ctx,
        *,
        consulta: str
    ):

        consulta = self.motor.normalizar(
            consulta
        )

        if not consulta:

            await ctx.send(
                "❌ Digite o que deseja pesquisar."
            )

            return

        mensagem = await ctx.send(
            embed=discord.Embed(
                title="🔎 PESQUISANDO...",
                description=(
                    f"Consulta:\n"
                    f"**{consulta}**\n\n"
                    "🌐 Consultando DuckDuckGo "
                    "e Wikipedia em paralelo.\n\n"
                    "⏱️ **Tempo:** `0.0s`"
                ),
                color=COR_PESQUISA
            )
        )

        inicio = time.monotonic()

        # ----------------------------------------------------
        # Atualizador do cronômetro
        # ----------------------------------------------------

        pesquisa_concluida = False

        async def atualizar_tempo():

            while not pesquisa_concluida:

                tempo_atual = (
                    time.monotonic()
                    - inicio
                )

                try:

                    embed_status = discord.Embed(
                        title="🔎 PESQUISANDO...",
                        description=(
                            f"Consulta:\n"
                            f"**{consulta}**\n\n"

                            "🌐 Consultando fontes "
                            "simultaneamente.\n\n"

                            f"⏱️ **Tempo:** "
                            f"`{tempo_atual:.1f}s`\n\n"

                            "⚡ A pesquisa continua..."
                        ),
                        color=COR_PESQUISA
                    )

                    await mensagem.edit(
                        embed=embed_status
                    )

                except (
                    discord.HTTPException
                ):

                    pass

                await asyncio.sleep(
                    0.8
                )

        tarefa_tempo = asyncio.create_task(
            atualizar_tempo()
        )

        try:

            resultados, tempos = (
                await self.motor.pesquisar(
                    consulta
                )
            )

        finally:

            pesquisa_concluida = True

            tarefa_tempo.cancel()

            try:

                await tarefa_tempo

            except asyncio.CancelledError:

                pass

        tempo_total = (
            time.monotonic()
            - inicio
        )

        embed = self.criar_embed_resultados(
            consulta,
            resultados,
            tempos,
            tempo_total
        )

        view = None

        if resultados:

            view = PesquisaView(
                resultados
            )

        await mensagem.edit(
            embed=embed,
            view=view
        )

    # ========================================================
    # STATUS
    # ========================================================

    @commands.command(
        name="pesquisastatus",
        description=(
            "Mostra o estado dos sistemas de pesquisa."
        )
    )
    async def pesquisastatus(
        self,
        ctx
    ):

        mensagem = await ctx.send(
            embed=discord.Embed(
                title="🌐 ROYALT • RESEARCH SYSTEM",
                description=(
                    "Verificando os mecanismos "
                    "de pesquisa..."
                ),
                color=COR_PESQUISA
            )
        )

        inicio = time.monotonic()

        tarefas = [

            asyncio.create_task(
                self.motor.buscar_duckduckgo(
                    "teste"
                )
            ),

            asyncio.create_task(
                self.motor.buscar_wikipedia(
                    "teste",
                    "pt"
                )
            ),

            asyncio.create_task(
                self.motor.buscar_wikipedia(
                    "teste",
                    "en"
                )
            )
        ]

        respostas = await asyncio.gather(
            *tarefas,
            return_exceptions=True
        )

        tempo_total = (
            time.monotonic()
            - inicio
        )

        nomes = (
            "🦆 DuckDuckGo",
            "📚 Wikipedia PT",
            "📚 Wikipedia EN"
        )

        embed = discord.Embed(
            title="🌐 ROYALT • RESEARCH SYSTEM",
            description=(
                "Status atual dos mecanismos."
            ),
            color=COR_SUCESSO
        )

        for indice, resposta in enumerate(
            respostas
        ):

            nome = nomes[
                indice
            ]

            if isinstance(
                resposta,
                Exception
            ):

                embed.add_field(
                    name=nome,
                    value="🔴 Erro",
                    inline=False
                )

                continue

            resultados, tempo = resposta

            if resultados:

                estado = "🟢 Online"

            else:

                estado = "🔴 Indisponível"

            embed.add_field(
                name=nome,
                value=(
                    f"{estado}\n"
                    f"⚡ **{tempo:.2f}s**"
                ),
                inline=False
            )

        embed.add_field(
            name="⏱️ Teste total",
            value=(
                f"**{tempo_total:.2f}s**"
            ),
            inline=False
        )

        embed.set_footer(
            text=NOME_SISTEMA
        )

        await mensagem.edit(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        DesabafosPesquisa(
            bot
        )
    )