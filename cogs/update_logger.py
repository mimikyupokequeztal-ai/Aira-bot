"""
============================================================
ROYALT • UPDATE LOGGER 2.0
============================================================

Responsável por:

- detectar automaticamente comandos novos/alterados/removidos;
- guardar snapshots em SQLite;
- criar histórico público em linguagem humana;
- guardar histórico privado/técnico para desenvolvimento;
- migrar o antigo help_registry.json, quando existir;
- permitir consultar o histórico público e o privado;
- publicar automaticamente no canal definido pelo !admin;
- utilizar uma configuração diferente para cada servidor.

O canal de atualização é definido pelo:

    !admin configurar_canal update_logger #canal

A configuração fica em:

    data/admin_config.json

O histórico fica em:

    data/update_history.sqlite3

============================================================
"""

from __future__ import annotations

import json
import os
import sqlite3

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

import discord

from discord.ext import commands


# ============================================================
# IDENTIDADE
# ============================================================

NOME_SISTEMA = "Royalt Update System"
VERSAO_SISTEMA = "2.0"

VERSAO_BOT = os.getenv(
    "ROYALT_VERSION",
    "0.7.45"
)


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_DATA = BASE_DIR / "data"

PASTA_DATA.mkdir(
    parents=True,
    exist_ok=True
)

DB_PATH = Path(
    os.getenv(
        "ROYALT_UPDATE_DB",
        str(PASTA_DATA / "update_history.sqlite3")
    )
)

LEGACY_JSON = PASTA_DATA / "help_registry.json"

# Configuração criada pelo admin.py
ADMIN_CONFIG_FILE = PASTA_DATA / "admin_config.json"


# ============================================================
# CORES
# ============================================================

COR_ROXA = discord.Color.from_rgb(
    128,
    0,
    255
)

COR_AZUL = discord.Color.from_rgb(
    52,
    152,
    219
)

COR_VERDE = discord.Color.from_rgb(
    46,
    204,
    113
)

COR_VERMELHO = discord.Color.from_rgb(
    231,
    76,
    60
)

COR_LARANJA = discord.Color.from_rgb(
    255,
    159,
    67
)

COR_AMARELO = discord.Color.from_rgb(
    241,
    196,
    15
)

COR_ROSA = discord.Color.from_rgb(
    255,
    105,
    180
)

COR_CINZA = discord.Color.from_rgb(
    149,
    165,
    166
)


# ============================================================
# CATEGORIAS
# ============================================================

CONFIG_CATEGORIAS = {

    "moderacao": {
        "nome": "MODERAÇÃO",
        "emoji": "🛡️",
        "cor": COR_VERMELHO
    },

    "warns": {
        "nome": "ADVERTÊNCIAS",
        "emoji": "⚠️",
        "cor": COR_LARANJA
    },

    "seguranca": {
        "nome": "SEGURANÇA",
        "emoji": "🔐",
        "cor": COR_VERMELHO
    },

    "sorteios": {
        "nome": "SORTEIOS",
        "emoji": "🎁",
        "cor": COR_VERDE
    },

    "tickets": {
        "nome": "TICKETS",
        "emoji": "🎫",
        "cor": COR_AZUL
    },

    "desabafos": {
        "nome": "DESABAFOS",
        "emoji": "🫂",
        "cor": COR_ROXA
    },

    "economia": {
        "nome": "ECONOMIA",
        "emoji": "💰",
        "cor": COR_AMARELO
    },

    "ship": {
        "nome": "SHIPS",
        "emoji": "💘",
        "cor": COR_ROSA
    },

    "pokemon": {
        "nome": "POKÉMON",
        "emoji": "🐾",
        "cor": COR_VERDE
    },

    "updates": {
        "nome": "ATUALIZAÇÕES",
        "emoji": "🛠️",
        "cor": COR_VERDE
    },

    "utilidades": {
        "nome": "UTILIDADES",
        "emoji": "⚙️",
        "cor": COR_AZUL
    },

    "outros": {
        "nome": "OUTROS",
        "emoji": "📦",
        "cor": COR_CINZA
    },
}


# ============================================================
# EMOJIS DOS COMANDOS
# ============================================================

PALAVRAS_EMOJIS = {

    "ban": "🔨",
    "unban": "🔓",
    "kick": "👢",
    "timeout": "⏳",
    "unmute": "🔊",

    "warn": "⚠️",
    "warns": "📋",
    "unwarn": "✅",

    "clear": "🧹",
    "lock": "🔒",
    "unlock": "🔓",
    "slowmode": "🐌",

    "antiraid": "🛡️",
    "security": "🔐",

    "sorteio": "🎁",
    "criar": "✨",
    "encerrar": "🛑",
    "reroll": "🎲",

    "log": "📁",
    "ticket": "🎫",
    "desabafo": "🫂",

    "ship": "💘",
    "shipperfil": "💌",
    "shiptop": "🏆",

    "economia": "💰",
    "saldo": "💳",
    "diario": "🎁",
    "daily": "🎁",
    "trabalhar": "💼",
    "work": "💼",
    "depositar": "🏦",
    "sacar": "💳",
    "pagar": "💸",

    "desafio": "🎯",
    "quiz": "🧠",
    "reacao": "⚡",
    "temas": "🖼️",

    "pokemon": "🐾",
    "poke": "🐾",
    "starter": "🌟",
    "inicial": "🌟",
    "capturar": "🎯",
    "catch": "🎯",
    "pokelista": "🎒",
    "pokemons": "🎒",
    "time": "🎒",
    "pokeinfo": "🔎",
    "pinfo": "🔎",
    "pokedex": "📚",
    "dex": "📚",
    "explorar": "🥾",
    "explore": "🥾",
    "poketop": "🏆",
    "pokemonrank": "🏆",
    "rankpokemon": "🏆",

    "update": "🛠️",
    "updates": "🛠️",
    "changelog": "📖",
    "historico": "📜",
    "updatecanal": "📢",

    "ajuda": "📖",
    "comandos": "📚",
}


# ============================================================
# UTILITÁRIOS
# ============================================================

def descobrir_emoji(
    comando,
    categoria
):
    nome = comando.name.lower()

    if nome in PALAVRAS_EMOJIS:
        return PALAVRAS_EMOJIS[nome]

    for palavra, emoji in PALAVRAS_EMOJIS.items():

        if palavra in nome:
            return emoji

    return CONFIG_CATEGORIAS.get(
        categoria,
        CONFIG_CATEGORIAS["outros"]
    )["emoji"]


def descobrir_categoria(
    comando
):
    nome = comando.name.lower()

    cog = getattr(
        comando,
        "cog",
        None
    )

    if cog is not None:

        nome_cog = (
            cog.__class__.__name__.lower()
        )

        regras = [

            (
                ("sorteio", "giveaway"),
                "sorteios"
            ),

            (
                ("ticket",),
                "tickets"
            ),

            (
                ("desabaf",),
                "desabafos"
            ),

            (
                ("economia", "economy"),
                "economia"
            ),

            (
                ("ship",),
                "ship"
            ),

            (
                ("pokemon", "pokémon"),
                "pokemon"
            ),

            (
                ("update", "changelog"),
                "updates"
            ),

            (
                ("segur", "security", "antiraid"),
                "seguranca"
            ),

            (
                ("warn", "advert"),
                "warns"
            ),

            (
                ("moder", "mod"),
                "moderacao"
            ),

            (
                ("help", "util"),
                "utilidades"
            ),
        ]

        for palavras, categoria in regras:

            if any(
                palavra in nome_cog
                for palavra in palavras
            ):
                return categoria

    grupos = {

        "sorteios": (
            "sorteio",
            "giveaway"
        ),

        "tickets": (
            "ticket",
            "tickets"
        ),

        "desabafos": (
            "desabafo",
            "desabafos"
        ),

        "economia": (
            "economia",
            "saldo",
            "diario",
            "daily",
            "trabalhar",
            "work",
            "depositar",
            "sacar",
            "pagar",
            "economiatop",
            "economiarank",
            "economiainfo",
            "desafio",
            "quiz",
            "reacao",
            "temas",
        ),

        "ship": (
            "ship",
        ),

        "pokemon": (
            "pokemon",
            "pokémon",
            "poke",
            "starter",
            "inicial",
            "capturar",
            "catch",
            "pokelista",
            "pokemons",
            "pokedex",
            "dex",
            "explorar",
            "explore",
            "poketop",
        ),

        "warns": (
            "warn",
            "unwarn",
            "advert"
        ),

        "seguranca": (
            "antiraid",
            "security",
            "seguranca",
            "segurança"
        ),

        "moderacao": (
            "ban",
            "unban",
            "kick",
            "timeout",
            "unmute",
            "clear",
            "lock",
            "unlock",
            "slowmode",
        ),

        "updates": (
            "updates",
            "atualizacoes",
            "atualizações",
            "changelog",
            "historico",
            "updatecanal",
        ),

        "utilidades": (
            "ajuda",
            "comandos"
        ),
    }

    for categoria, palavras in grupos.items():

        if any(
            palavra in nome
            for palavra in palavras
        ):
            return categoria

    return "outros"


def nome_comando_completo(
    comando
):
    try:

        nome = comando.qualified_name

        if nome:
            return nome

    except AttributeError:
        pass

    parent = getattr(
        comando,
        "parent",
        None
    )

    if parent is not None:

        return (
            f"{parent.name} "
            f"{comando.name}"
        )

    return comando.name


def obter_assinatura(
    comando
):
    return (
        getattr(
            comando,
            "signature",
            ""
        )
        or ""
    )


def obter_aliases(
    comando
):
    aliases = getattr(
        comando,
        "aliases",
        None
    )

    return list(
        aliases or []
    )


def _agora():
    return datetime.now(
        timezone.utc
    )


def _data_bonita(
    iso
):
    try:

        data = datetime.fromisoformat(
            iso
        )

        return data.astimezone().strftime(
            "%d/%m/%Y às %H:%M"
        )

    except Exception:
        return iso or ""


# ============================================================
# CONFIGURAÇÃO DO CANAL PELO ADMIN
# ============================================================

def carregar_admin_config():
    """
    Lê o data/admin_config.json criado pelo admin.py.
    """

    if not ADMIN_CONFIG_FILE.exists():
        return {
            "guilds": {}
        }

    try:

        with ADMIN_CONFIG_FILE.open(
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

        return dados

    except Exception as erro:

        print(
            "[UPDATE LOGGER] "
            f"Erro lendo admin_config.json: {erro}"
        )

        return {
            "guilds": {}
        }


def obter_canal_configurado(
    guild_id: int
):
    """
    Retorna o ID do canal de Update Logger
    configurado para o servidor.

    Estrutura esperada:

    {
        "guilds": {
            "123456789": {
                "update_logger": 987654321
            }
        }
    }
    """

    config = carregar_admin_config()

    guilds = config.get(
        "guilds",
        {}
    )

    guild_config = guilds.get(
        str(guild_id),
        {}
    )

    if not isinstance(
        guild_config,
        dict
    ):
        return None

    canal_id = guild_config.get(
        "update_logger"
    )

    if not canal_id:
        return None

    try:
        return int(canal_id)

    except (
        TypeError,
        ValueError
    ):
        return None


# ============================================================
# BANCO
# ============================================================

class UpdateLogger:

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.db = None

        self._inicializado = False


    # ========================================================
    # CONEXÃO
    # ========================================================

    def conectar(
        self
    ):

        if self.db is None:

            self.db = sqlite3.connect(
                DB_PATH,
                timeout=15,
                check_same_thread=False,
            )

            self.db.row_factory = sqlite3.Row

            self.db.execute(
                "PRAGMA journal_mode=WAL"
            )

            self.db.execute(
                "PRAGMA foreign_keys=ON"
            )

            self._criar_tabelas()

            self._migrar_json_antigo()

            self._inicializado = True

        return self.db


    # ========================================================
    # TABELAS
    # ========================================================

    def _criar_tabelas(
        self
    ):

        db = self.db

        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS command_snapshots (

                command_name TEXT PRIMARY KEY,

                description TEXT NOT NULL,

                signature TEXT NOT NULL,

                aliases_json TEXT NOT NULL,

                category TEXT NOT NULL,

                captured_at TEXT NOT NULL
            );


            CREATE TABLE IF NOT EXISTS public_updates (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                version TEXT NOT NULL,

                title TEXT NOT NULL,

                summary TEXT NOT NULL,

                date TEXT NOT NULL,

                items_json TEXT NOT NULL,

                source TEXT NOT NULL DEFAULT 'automatico'
            );


            CREATE TABLE IF NOT EXISTS developer_updates (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                version TEXT NOT NULL,

                title TEXT NOT NULL,

                date TEXT NOT NULL,

                payload_json TEXT NOT NULL,

                source TEXT NOT NULL DEFAULT 'automatico'
            );


            CREATE INDEX IF NOT EXISTS idx_public_updates_date

                ON public_updates(id DESC);


            CREATE INDEX IF NOT EXISTS idx_developer_updates_date

                ON developer_updates(id DESC);
            """
        )

        db.commit()


    # ========================================================
    # MIGRAÇÃO ANTIGA
    # ========================================================

    def _migrar_json_antigo(
        self
    ):

        db = self.db

        existe = db.execute(
            """
            SELECT 1
            FROM command_snapshots
            LIMIT 1
            """
        ).fetchone()

        if existe:
            return

        if not LEGACY_JSON.exists():
            return

        try:

            with LEGACY_JSON.open(
                "r",
                encoding="utf-8"
            ) as f:

                dados = json.load(f)

            comandos = dados.get(
                "comandos",
                {}
            )

            agora = _agora().isoformat()

            for nome, item in comandos.items():

                db.execute(
                    """
                    INSERT OR IGNORE INTO command_snapshots

                    (
                        command_name,
                        description,
                        signature,
                        aliases_json,
                        category,
                        captured_at
                    )

                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome,

                        item.get(
                            "descricao",
                            "Sem descrição disponível."
                        ),

                        item.get(
                            "assinatura",
                            ""
                        ),

                        json.dumps(
                            item.get(
                                "aliases",
                                []
                            ),
                            ensure_ascii=False
                        ),

                        item.get(
                            "categoria",
                            "outros"
                        ),

                        agora,
                    ),
                )

            db.commit()

        except (
            OSError,
            json.JSONDecodeError,
            sqlite3.Error
        ) as erro:

            print(
                "[UPDATE LOGGER] "
                f"Migração ignorada: {erro}"
            )


    # ========================================================
    # COLETA DE COMANDOS
    # ========================================================

    def obter_comandos(
        self
    ):

        comandos = []

        vistos = set()


        # ----------------------------------------------------
        # COMANDOS DE PREFIXO
        # ----------------------------------------------------

        for comando in self.bot.walk_commands():

            if getattr(
                comando,
                "hidden",
                False
            ):
                continue

            nome = nome_comando_completo(
                comando
            )

            if nome in vistos:
                continue

            vistos.add(
                nome
            )

            comandos.append(
                comando
            )


        # ----------------------------------------------------
        # SLASH COMMANDS
        # ----------------------------------------------------

        try:

            for comando in self.bot.tree.walk_commands():

                nome = nome_comando_completo(
                    comando
                )

                if nome in vistos:
                    continue

                vistos.add(
                    nome
                )

                comandos.append(
                    comando
                )

        except Exception:
            pass


        return sorted(
            comandos,
            key=lambda c:
                nome_comando_completo(c).lower()
        )


    # ========================================================
    # SNAPSHOT ATUAL
    # ========================================================

    def snapshot_atual(
        self
    ):

        snapshot = {}

        for comando in self.obter_comandos():

            nome = nome_comando_completo(
                comando
            )

            categoria = descobrir_categoria(
                comando
            )

            snapshot[nome] = {

                "nome": nome,

                "descricao": (
                    getattr(
                        comando,
                        "description",
                        None
                    )
                    or "Sem descrição disponível."
                ),

                "assinatura": obter_assinatura(
                    comando
                ),

                "aliases": obter_aliases(
                    comando
                ),

                "categoria": categoria,
            }

        return snapshot


    # ========================================================
    # SNAPSHOT DO BANCO
    # ========================================================

    def _snapshot_banco(
        self
    ):

        rows = self.conectar().execute(
            """
            SELECT

                command_name,
                description,
                signature,
                aliases_json,
                category

            FROM command_snapshots
            """
        ).fetchall()

        resultado = {}

        for row in rows:

            try:

                aliases = json.loads(
                    row["aliases_json"]
                )

            except Exception:

                aliases = []


            resultado[
                row["command_name"]
            ] = {

                "nome": row["command_name"],

                "descricao": row["description"],

                "assinatura": row["signature"],

                "aliases": aliases,

                "categoria": row["category"],
            }

        return resultado


    # ========================================================
    # VERIFICAR + PUBLICAR
    # ========================================================

    async def verificar_comandos_e_publicar(
        self
    ):

        resultado = self.verificar_comandos()

        total = (
            len(resultado["novos"])
            + len(resultado["alterados"])
            + len(resultado["removidos"])
        )

        if total == 0:
            return resultado


        # ----------------------------------------------------
        # PUBLICAR EM CADA SERVIDOR
        # ----------------------------------------------------

        for guild in self.bot.guilds:

            canal_id = obter_canal_configurado(
                guild.id
            )

            if not canal_id:
                continue

            try:

                canal = guild.get_channel(
                    canal_id
                )

                if canal is None:

                    try:

                        canal = await self.bot.fetch_channel(
                            canal_id
                        )

                    except Exception:

                        canal = None


                if canal is None:
                    continue


                await canal.send(
                    embed=self.embed_historico_publico(
                        limite=1
                    )
                )

            except Exception as erro:

                print(
                    "[UPDATE LOGGER] "
                    f"Não foi possível publicar "
                    f"no servidor {guild.id}: {erro}"
                )


        return resultado


    # ========================================================
    # DETECÇÃO
    # ========================================================

    def verificar_comandos(
        self
    ):

        db = self.conectar()

        antigos = self._snapshot_banco()

        atuais = self.snapshot_atual()


        novos = [

            nome

            for nome in atuais

            if nome not in antigos
        ]


        removidos = [

            nome

            for nome in antigos

            if nome not in atuais
        ]


        alterados = []


        campos = (
            "descricao",
            "assinatura",
            "aliases",
            "categoria"
        )


        for nome in (
            atuais.keys()
            & antigos.keys()
        ):

            if any(
                atuais[nome].get(campo)
                !=
                antigos[nome].get(campo)

                for campo in campos
            ):

                alterados.append(
                    nome
                )


        agora = _agora().isoformat()


        with db:

            db.execute(
                """
                DELETE FROM command_snapshots
                """
            )


            for nome, item in atuais.items():

                db.execute(
                    """
                    INSERT INTO command_snapshots

                    (
                        command_name,
                        description,
                        signature,
                        aliases_json,
                        category,
                        captured_at
                    )

                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome,

                        item["descricao"],

                        item["assinatura"],

                        json.dumps(
                            item["aliases"],
                            ensure_ascii=False
                        ),

                        item["categoria"],

                        agora,
                    ),
                )


        if (
            novos
            or alterados
            or removidos
        ):

            self._registrar_deteccao_automatica(
                novos,
                alterados,
                removidos
            )


        return {

            "novos": novos,

            "alterados": alterados,

            "removidos": removidos,
        }


    # ========================================================
    # REGISTRO AUTOMÁTICO
    # ========================================================

    def _registrar_deteccao_automatica(
        self,
        novos,
        alterados,
        removidos
    ):

        agora = _agora()

        versao = VERSAO_BOT

        itens = []


        for nome in novos:

            categoria = CONFIG_CATEGORIAS.get(

                descobrir_categoria_por_nome(
                    nome
                ),

                CONFIG_CATEGORIAS["outros"]
            )


            itens.append({

                "tipo": "novo",

                "texto":
                    f"Novo comando disponível: {nome}.",

                "comando": nome,

                "categoria":
                    categoria["nome"],
            })


        for nome in alterados:

            itens.append({

                "tipo": "melhoria",

                "texto":
                    f"O comando {nome} recebeu uma atualização.",

                "comando": nome,
            })


        for nome in removidos:

            itens.append({

                "tipo": "removido",

                "texto":
                    f"O comando {nome} foi removido.",

                "comando": nome,
            })


        if not itens:
            return


        titulo = (
            "Atualização de comandos"
        )

        resumo = self._resumo_humano(
            novos,
            alterados,
            removidos
        )


        self._inserir_publico(

            version=versao,

            title=titulo,

            summary=resumo,

            items=itens,

            source="automatico",

            date=agora.isoformat()
        )


        payload = {

            "novos": [
                self._detalhe_comando(
                    n,
                    "novo"
                )
                for n in novos
            ],

            "alterados": [
                self._detalhe_comando(
                    n,
                    "alterado"
                )
                for n in alterados
            ],

            "removidos": [
                self._detalhe_comando(
                    n,
                    "removido"
                )
                for n in removidos
            ],
        }


        self._inserir_dev(

            version=versao,

            title=titulo,

            payload=payload,

            source="automatico",

            date=agora.isoformat()
        )


    # ========================================================
    # DETALHE
    # ========================================================

    def _detalhe_comando(
        self,
        nome,
        tipo
    ):

        snapshot = self.snapshot_atual()

        item = snapshot.get(
            nome
        )


        if item is None:

            item = self._snapshot_banco().get(
                nome,
                {
                    "nome": nome
                }
            )


        return {

            "tipo": tipo,

            **item,
        }


    # ========================================================
    # RESUMO
    # ========================================================

    @staticmethod
    def _resumo_humano(
        novos,
        alterados,
        removidos
    ):

        partes = []


        if novos:

            partes.append(
                f"{len(novos)} novo"
                f"{'s' if len(novos) != 1 else ''}"
            )


        if alterados:

            partes.append(
                f"{len(alterados)} atualização"
                f"{'ões' if len(alterados) != 1 else ''}"
            )


        if removidos:

            partes.append(
                f"{len(removidos)} remoção"
                f"{'ões' if len(removidos) != 1 else ''}"
            )


        return (
            " • ".join(partes)
            + " nos comandos do Royalt."
        )


    # ========================================================
    # BANCO • PÚBLICO
    # ========================================================

    def _inserir_publico(
        self,
        version,
        title,
        summary,
        items,
        source,
        date
    ):

        with self.conectar():

            self.db.execute(
                """
                INSERT INTO public_updates

                (
                    version,
                    title,
                    summary,
                    date,
                    items_json,
                    source
                )

                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    version,

                    title,

                    summary,

                    date,

                    json.dumps(
                        items,
                        ensure_ascii=False
                    ),

                    source,
                ),
            )


    # ========================================================
    # BANCO • DEV
    # ========================================================

    def _inserir_dev(
        self,
        version,
        title,
        payload,
        source,
        date
    ):

        with self.conectar():

            self.db.execute(
                """
                INSERT INTO developer_updates

                (
                    version,
                    title,
                    date,
                    payload_json,
                    source
                )

                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    version,

                    title,

                    date,

                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        indent=2
                    ),

                    source,
                ),
            )


    # ========================================================
    # REGISTRAR MANUALMENTE
    # ========================================================

    def registrar_atualizacao(
        self,
        versao: str,
        titulo: str,
        resumo: str,
        itens: Iterable[
            dict[str, Any]
        ],
        detalhes_dev: Optional[
            dict[str, Any]
        ] = None
    ):

        date = _agora().isoformat()

        itens = list(itens)


        self._inserir_publico(

            version=versao,

            title=titulo,

            summary=resumo,

            items=itens,

            source="manual",

            date=date
        )


        self._inserir_dev(

            version=versao,

            title=titulo,

            payload=(
                detalhes_dev
                or
                {
                    "itens": itens
                }
            ),

            source="manual",

            date=date
        )


    # ========================================================
    # HISTÓRICO PÚBLICO
    # ========================================================

    def historico_publico(
        self,
        limite=8
    ):

        rows = self.conectar().execute(
            """
            SELECT

                version,
                title,
                summary,
                date,
                items_json,
                source

            FROM public_updates

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                max(
                    1,
                    min(
                        int(limite),
                        25
                    )
                ),
            )
        ).fetchall()


        resultado = []


        for row in rows:

            try:

                itens = json.loads(
                    row["items_json"]
                )

            except Exception:

                itens = []


            resultado.append({

                "versao":
                    row["version"],

                "titulo":
                    row["title"],

                "resumo":
                    row["summary"],

                "data":
                    _data_bonita(
                        row["date"]
                    ),

                "itens":
                    itens,

                "source":
                    row["source"],
            })


        return resultado


    # ========================================================
    # HISTÓRICO DEV
    # ========================================================

    def historico_dev(
        self,
        limite=10
    ):

        rows = self.conectar().execute(
            """
            SELECT

                version,
                title,
                date,
                payload_json,
                source

            FROM developer_updates

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                max(
                    1,
                    min(
                        int(limite),
                        25
                    )
                ),
            )
        ).fetchall()


        resultado = []


        for row in rows:

            try:

                payload = json.loads(
                    row["payload_json"]
                )

            except Exception:

                payload = {}


            resultado.append({

                "versao":
                    row["version"],

                "titulo":
                    row["title"],

                "data":
                    _data_bonita(
                        row["date"]
                    ),

                "payload":
                    payload,

                "source":
                    row["source"],
            })


        return resultado


    # ========================================================
    # ÚLTIMA ATUALIZAÇÃO
    # ========================================================

    def ultima_atualizacao(
        self
    ):

        historico = self.historico_publico(
            1
        )

        return (
            historico[0]
            if historico
            else None
        )


    # ========================================================
    # EMBED DEV
    # ========================================================

    def embed_historico_dev(
        self,
        limite=5
    ):

        embed = discord.Embed(

            title=
                "🧪 ROYALT • HISTÓRICO DE DESENVOLVIMENTO",

            description=(
                "Área privada para acompanhamento técnico. "
                "Não é exibida na Central de Ajuda pública."
            ),

            color=COR_ROSA,

            timestamp=_agora()
        )


        registros = self.historico_dev(
            limite
        )


        if not registros:

            embed.add_field(

                name="📭 Vazio",

                value=
                    "Nenhum registro técnico encontrado.",

                inline=False
            )

            return embed


        for registro in registros:

            payload = json.dumps(

                registro["payload"],

                ensure_ascii=False,

                indent=2
            )


            if len(payload) > 900:

                payload = (
                    payload[:897]
                    + "..."
                )


            embed.add_field(

                name=(
                    f"🧪 {registro['versao']} • "
                    f"{registro['titulo']}"
                ),

                value=(
                    f"🗓️ {registro['data']}\n"
                    f"```json\n"
                    f"{payload}\n"
                    f"```"
                ),

                inline=False
            )


        embed.set_footer(

            text=(
                f"{NOME_SISTEMA} • "
                f"privado • "
                f"v{VERSAO_SISTEMA}"
            )
        )


        return embed


    # ========================================================
    # EMBED PÚBLICO
    # ========================================================

    def embed_historico_publico(
        self,
        limite=8
    ):

        embed = discord.Embed(

            title=
                "🛠️ ROYALT • HISTÓRICO DE ATUALIZAÇÕES",

            description=(
                "Mudanças do Royalt explicadas de forma simples, "
                "sem detalhes de código."
            ),

            color=COR_VERDE,

            timestamp=_agora()
        )


        registros = self.historico_publico(
            limite
        )


        if not registros:

            embed.add_field(

                name="📭 Nenhuma atualização",

                value=
                    "O histórico público ainda está vazio.",

                inline=False
            )

            return embed


        for registro in registros:

            linhas = [

                f"**{registro['resumo']}**",

                f"🗓️ {registro['data']}",
            ]


            for item in registro["itens"][:8]:

                emoji = {

                    "novo": "🆕",

                    "melhoria": "✨",

                    "correcao": "🛠️",

                    "removido": "🗑️",

                    "seguranca": "🛡️",

                }.get(

                    item.get(
                        "tipo"
                    ),

                    "•"
                )


                linhas.append(

                    f"{emoji} "
                    f"{item.get(
                        'texto',
                        'Mudança registrada.'
                    )}"
                )


            valor = "\n".join(
                linhas
            )


            if len(valor) > 1000:

                valor = (
                    valor[:997]
                    + "…"
                )


            embed.add_field(

                name=(
                    f"🚀 {registro['versao']} • "
                    f"{registro['titulo']}"
                ),

                value=valor,

                inline=False
            )


        embed.set_footer(

            text=(
                f"{NOME_SISTEMA} • "
                f"público • "
                f"v{VERSAO_SISTEMA}"
            )
        )


        return embed


# ============================================================
# CATEGORIA FALLBACK
# ============================================================

def descobrir_categoria_por_nome(
    nome
):

    nome = (
        nome or ""
    ).lower()


    if any(
        p in nome
        for p in (
            "pokemon",
            "poke",
            "starter",
            "pokedex",
            "poketop"
        )
    ):
        return "pokemon"


    if "ship" in nome:
        return "ship"


    if any(
        p in nome
        for p in (
            "saldo",
            "economia",
            "trabalhar",
            "pagar"
        )
    ):
        return "economia"


    if "ticket" in nome:
        return "tickets"


    if any(
        p in nome
        for p in (
            "warn",
            "advert"
        )
    ):
        return "warns"


    if any(
        p in nome
        for p in (
            "ban",
            "kick",
            "timeout",
            "clear"
        )
    ):
        return "moderacao"


    return "outros"


# ============================================================
# COG PRIVADO
# ============================================================

class UpdateHistory(
    commands.Cog
):

    """
    Comandos internos.

    Somente owners do bot podem consultar
    o histórico técnico.
    """

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.logger = UpdateLogger(
            bot
        )


    def _eh_owner(
        self,
        user_id
    ):

        owner_ids = getattr(
            self.bot,
            "owner_ids",
            set()
        ) or set()


        if getattr(
            self.bot,
            "owner_id",
            None
        ):

            owner_ids = (
                set(owner_ids)
                |
                {
                    self.bot.owner_id
                }
            )


        return user_id in owner_ids


    @commands.command(
        name="royaltdevlog",
        hidden=True,
        description=
            "Histórico técnico privado para desenvolvedores."
    )
    async def royaltdevlog(
        self,
        ctx
    ):

        if not self._eh_owner(
            ctx.author.id
        ):

            await ctx.send(
                "🔒 Este histórico é reservado à equipe de desenvolvimento."
            )

            return


        await ctx.send(

            embed=
                self.logger.embed_historico_dev()
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot: commands.Bot
):

    # Inicializa o banco.
    logger = UpdateLogger(
        bot
    )

    logger.conectar()


    # Adiciona o histórico privado.
    await bot.add_cog(
        UpdateHistory(
            bot
        )
    )


    print(
        "✅ Update Logger carregado."
    )