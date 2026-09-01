"""
ROYALT • UPDATE SYSTEM 4.1

Responsabilidades:
- Monitorar os Cogs do Royalt.
- Detectar comandos novos, alterados e removidos.
- Detectar arquivos novos, alterados e removidos.
- Gerar changelog público em linguagem de usuário.
- Manter histórico técnico para desenvolvimento.
- Persistir histórico em SQLite.
- Criar snapshot automático.
- Fazer verificação automática quando o bot estiver pronto.
- Preservar compatibilidade com:
    !updates
    /updates
    !historico
    !ultimoupdate
    !updatecanal
    !updateteste

IMPORTANTE:
O main.py carrega este arquivo como "cogs.updates".
Não é necessário criar outro updates.py.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands, tasks


# ============================================================
# CONFIGURAÇÃO
# ============================================================

NOME_SISTEMA = "Royalt Update System"
VERSAO_SISTEMA = "4.1"

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_DATA = BASE_DIR / "data"
PASTA_COGS = BASE_DIR / "cogs"

PASTA_DATA.mkdir(parents=True, exist_ok=True)
PASTA_COGS.mkdir(parents=True, exist_ok=True)

DB_PATH = PASTA_DATA / "royalt_updates.sqlite3"
LEGACY_STATE = PASTA_DATA / "updates_state.json"
SNAPSHOT_PATH = PASTA_DATA / "updates_snapshot.json"

# ============================================================
# AMBIENTE
# ============================================================

AUTO_DETECTAR = (
    os.getenv("ROYALT_UPDATE_AUTO", "1").strip().lower()
    in {"1", "true", "yes", "on"}
)

CANAL_PUBLICO_ENV = os.getenv(
    "UPDATE_PUBLIC_CHANNEL_ID",
    "0",
)

CANAL_DEV_ENV = os.getenv(
    "UPDATE_DEV_CHANNEL_ID",
    "0",
)

# IDs de desenvolvedores opcionais.
#
# Pode colocar no .env:
#
# ROYALT_DEVELOPER_IDS=123456789,987654321
#
# Se não estiver configurado, o sistema usa os owners do bot
# para comandos técnicos privados.
DEVELOPER_IDS_ENV = os.getenv(
    "ROYALT_DEVELOPER_IDS",
    "",
)


def ler_id_env(valor: str) -> int | None:
    try:
        numero = int(valor)
        return numero if numero > 0 else None
    except (TypeError, ValueError):
        return None


CANAL_PUBLICO_ID = ler_id_env(CANAL_PUBLICO_ENV)
CANAL_DEV_ID = ler_id_env(CANAL_DEV_ENV)


def ler_ids_env(valor: str) -> set[int]:
    resultado = set()

    for item in str(valor).split(","):
        item = item.strip()

        if not item:
            continue

        try:
            numero = int(item)

            if numero > 0:
                resultado.add(numero)

        except ValueError:
            continue

    return resultado


DEVELOPER_IDS = ler_ids_env(DEVELOPER_IDS_ENV)


# ============================================================
# CORES
# ============================================================

COR_VERDE = discord.Color.from_rgb(
    46,
    204,
    113,
)

COR_AZUL = discord.Color.from_rgb(
    52,
    152,
    219,
)

COR_ROXA = discord.Color.from_rgb(
    128,
    0,
    255,
)

COR_AMARELO = discord.Color.from_rgb(
    241,
    196,
    15,
)

COR_VERMELHO = discord.Color.from_rgb(
    231,
    76,
    60,
)

COR_CINZA = discord.Color.from_rgb(
    149,
    165,
    166,
)


# ============================================================
# HELPERS
# ============================================================

def agora() -> datetime:
    return datetime.now(timezone.utc)


def agora_iso() -> str:
    return agora().isoformat()


def data_discord(valor: str) -> str:
    try:
        data = datetime.fromisoformat(valor)

        return f"<t:{int(data.timestamp())}:F>"

    except (
        ValueError,
        TypeError,
    ):
        return "Data desconhecida"


def nome_arquivo_seguro(nome: str) -> str:
    return str(nome).replace("\\", "/").split("/")[-1]


# ============================================================
# BANCO DE DADOS
# ============================================================

def conectar():
    db = sqlite3.connect(
        DB_PATH,
        timeout=15,
    )

    db.row_factory = sqlite3.Row

    return db


def inicializar_banco():
    with conectar() as db:

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS atualizacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero INTEGER NOT NULL,
                versao_anterior TEXT NOT NULL,
                versao TEXT NOT NULL,
                momento TEXT NOT NULL,
                resumo_publico TEXT NOT NULL,
                detalhes_json TEXT NOT NULL,
                publico INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT
            )
            """
        )

        db.commit()


def proximo_numero() -> int:
    with conectar() as db:

        row = db.execute(
            """
            SELECT COALESCE(MAX(numero), 0) + 1 AS numero
            FROM atualizacoes
            """
        ).fetchone()

        return int(row["numero"])


def salvar_update(
    numero: int,
    versao_anterior: str,
    versao: str,
    resumo_publico: str,
    detalhes: dict[str, Any],
):
    with conectar() as db:

        db.execute(
            """
            INSERT INTO atualizacoes (
                numero,
                versao_anterior,
                versao,
                momento,
                resumo_publico,
                detalhes_json,
                publico
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                int(numero),
                versao_anterior,
                versao,
                agora_iso(),
                resumo_publico,
                json.dumps(
                    detalhes,
                    ensure_ascii=False,
                ),
            ),
        )

        db.commit()


def obter_historico_publico(limite: int = 10):
    limite = max(
        1,
        min(int(limite), 25),
    )

    with conectar() as db:

        return db.execute(
            """
            SELECT *
            FROM atualizacoes
            WHERE publico = 1
            ORDER BY numero DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()


def obter_configuracao(
    chave: str,
) -> str | None:

    with conectar() as db:

        row = db.execute(
            """
            SELECT valor
            FROM configuracoes
            WHERE chave = ?
            """,
            (chave,),
        ).fetchone()

    if row is None:
        return None

    return row["valor"]


def salvar_configuracao(
    chave: str,
    valor: str,
):
    with conectar() as db:

        db.execute(
            """
            INSERT INTO configuracoes (
                chave,
                valor
            )
            VALUES (?, ?)
            ON CONFLICT(chave)
            DO UPDATE SET valor = excluded.valor
            """,
            (
                chave,
                valor,
            ),
        )

        db.commit()


# ============================================================
# SNAPSHOT — ARQUIVOS
# ============================================================

def hash_arquivo(
    caminho: Path,
) -> str | None:

    try:

        sha = hashlib.sha256()

        with caminho.open(
            "rb",
        ) as arquivo:

            while True:

                bloco = arquivo.read(
                    65536,
                )

                if not bloco:
                    break

                sha.update(bloco)

        return sha.hexdigest()

    except (
        OSError,
        PermissionError,
    ):
        return None


def texto_arquivo(
    caminho: Path,
) -> str:

    try:

        return caminho.read_text(
            encoding="utf-8",
        )

    except (
        OSError,
        UnicodeDecodeError,
    ):
        return ""


# ============================================================
# AST
# ============================================================

def obter_nome_decorador(
    decorator: ast.AST,
) -> str:

    """
    Retorna o nome do decorator.

    Exemplos:

        @commands.command
        -> commands.command

        @commands.command(...)
        -> commands.command

        @command
        -> command
    """

    alvo = decorator

    if isinstance(
        decorator,
        ast.Call,
    ):
        alvo = decorator.func

    if isinstance(
        alvo,
        ast.Attribute,
    ):

        partes = []

        atual = alvo

        while isinstance(
            atual,
            ast.Attribute,
        ):

            partes.append(
                atual.attr,
            )

            atual = atual.value

        if isinstance(
            atual,
            ast.Name,
        ):

            partes.append(
                atual.id,
            )

        return ".".join(
            reversed(partes),
        )

    if isinstance(
        alvo,
        ast.Name,
    ):

        return alvo.id

    return ""


def string_ast(
    no: ast.AST,
) -> str | None:

    if isinstance(
        no,
        ast.Constant,
    ) and isinstance(
        no.value,
        str,
    ):

        return no.value

    return None


def lista_strings_ast(
    no: ast.AST,
) -> list[str]:

    resultado = []

    if not isinstance(
        no,
        (
            ast.List,
            ast.Tuple,
            ast.Set,
        ),
    ):
        return resultado

    for elemento in no.elts:

        valor = string_ast(
            elemento,
        )

        if valor:
            resultado.append(
                valor,
            )

    return sorted(
        set(resultado),
    )


def analisar_codigo(
    texto: str,
) -> dict[str, Any]:

    resultado = {
        "comandos": {},
        "funcoes": {},
        "classes": {},
    }

    if not texto.strip():
        return resultado

    try:

        arvore = ast.parse(
            texto,
        )

    except SyntaxError:

        return resultado

    decoradores_comando = {
        "commands.command",
        "commands.hybrid_command",
        "commands.group",
        "commands.hybrid_group",
        "command",
        "hybrid_command",
        "group",
        "hybrid_group",
    }

    for no in ast.walk(arvore):

        # ----------------------------------------------------
        # CLASSES
        # ----------------------------------------------------

        if isinstance(
            no,
            ast.ClassDef,
        ):

            resultado["classes"][no.name] = {
                "linha": no.lineno,
                "fim": getattr(
                    no,
                    "end_lineno",
                    no.lineno,
                ),
            }

        # ----------------------------------------------------
        # FUNÇÕES
        # ----------------------------------------------------

        if not isinstance(
            no,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        resultado["funcoes"][no.name] = {
            "linha": no.lineno,
            "fim": getattr(
                no,
                "end_lineno",
                no.lineno,
            ),
        }

        # ----------------------------------------------------
        # DECORADORES
        # ----------------------------------------------------

        for decorator in no.decorator_list:

            # IMPORTANTE:
            #
            # Não fazer:
            #
            # nome_decorador = nome_decorador(...)
            #
            # Isso causa UnboundLocalError.
            #
            nome_do_decorador = obter_nome_decorador(
                decorator,
            )

            if nome_do_decorador not in decoradores_comando:
                continue

            nome = no.name
            descricao = ""
            aliases = []

            if isinstance(
                decorator,
                ast.Call,
            ):

                for keyword in decorator.keywords:

                    if keyword.arg == "name":

                        valor = string_ast(
                            keyword.value,
                        )

                        if valor:
                            nome = valor

                    elif keyword.arg == "description":

                        valor = string_ast(
                            keyword.value,
                        )

                        if valor:
                            descricao = valor

                    elif keyword.arg == "aliases":

                        aliases.extend(
                            lista_strings_ast(
                                keyword.value,
                            )
                        )

            resultado["comandos"][no.name] = {
                "nome": nome,
                "descricao": descricao,
                "aliases": sorted(
                    set(aliases),
                ),
                "funcao": no.name,
                "linha": no.lineno,
                "decorador": nome_do_decorador,
            }

            break

    return resultado


# ============================================================
# CRIAÇÃO DO SNAPSHOT
# ============================================================

def criar_snapshot():
    snapshot = {}

    try:
        arquivos = sorted(
            PASTA_COGS.glob("*.py"),
        )
    except OSError:
        arquivos = []

    for caminho in arquivos:

        if caminho.name in {
            "__init__.py",
            "updates.py",
            "update_logger.py",
        }:
            continue

        texto = texto_arquivo(
            caminho,
        )

        if not texto:
            continue

        assinatura = hash_arquivo(
            caminho,
        )

        if not assinatura:
            continue

        snapshot[caminho.name] = {
            "hash": assinatura,
            "analise": analisar_codigo(
                texto,
            ),
        }

    return snapshot


def carregar_snapshot():

    if not SNAPSHOT_PATH.exists():
        return {}

    try:

        dados = json.loads(
            SNAPSHOT_PATH.read_text(
                encoding="utf-8",
            )
        )

        if isinstance(
            dados,
            dict,
        ):
            return dados

    except (
        OSError,
        json.JSONDecodeError,
    ):
        pass

    return {}


def salvar_snapshot(
    snapshot: dict[str, Any],
):

    temporario = SNAPSHOT_PATH.with_suffix(
        ".tmp",
    )

    try:

        temporario.write_text(
            json.dumps(
                snapshot,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporario.replace(
            SNAPSHOT_PATH,
        )

    except OSError as erro:

        print(
            "[UPDATES] Erro salvando snapshot: "
            f"{erro}"
        )

        try:

            if temporario.exists():
                temporario.unlink()

        except OSError:
            pass


# ============================================================
# COMPARAÇÃO
# ============================================================

def comparar_maps(
    antigo,
    atual,
):

    antigo = antigo or {}
    atual = atual or {}

    adicionados = sorted(
        set(atual) - set(antigo),
    )

    removidos = sorted(
        set(antigo) - set(atual),
    )

    alterados = sorted(
        nome
        for nome in (
            set(antigo) & set(atual)
        )
        if antigo[nome] != atual[nome]
    )

    return (
        adicionados,
        removidos,
        alterados,
    )


def extrair_comandos(
    snapshot,
):

    comandos = {}

    for arquivo, dados in (
        snapshot or {}
    ).items():

        analise = dados.get(
            "analise",
            {},
        )

        for _, comando in (
            analise.get(
                "comandos",
                {},
            ).items()
        ):

            nome = (
                comando.get("nome")
                or comando.get("funcao")
            )

            if not nome:
                continue

            comandos[nome] = {
                **comando,
                "arquivo": arquivo,
            }

    return comandos


def comparar_snapshots(
    antigo,
    atual,
):

    antigo = antigo or {}
    atual = atual or {}

    # --------------------------------------------------------
    # ARQUIVOS
    # --------------------------------------------------------

    arquivos_novos = sorted(
        set(atual) - set(antigo),
    )

    arquivos_removidos = sorted(
        set(antigo) - set(atual),
    )

    arquivos_alterados = sorted(
        nome
        for nome in (
            set(antigo) & set(atual)
        )
        if antigo[nome].get("hash")
        != atual[nome].get("hash")
    )

    # --------------------------------------------------------
    # COMANDOS
    # --------------------------------------------------------

    comandos_antigos = extrair_comandos(
        antigo,
    )

    comandos_atuais = extrair_comandos(
        atual,
    )

    comandos_novos = sorted(
        set(comandos_atuais)
        - set(comandos_antigos)
    )

    comandos_removidos = sorted(
        set(comandos_antigos)
        - set(comandos_atuais)
    )

    comandos_alterados = sorted(
        nome
        for nome in (
            set(comandos_antigos)
            & set(comandos_atuais)
        )
        if comandos_antigos[nome]
        != comandos_atuais[nome]
    )

    return {
        "arquivos_novos": arquivos_novos,
        "arquivos_removidos": arquivos_removidos,
        "arquivos_alterados": arquivos_alterados,
        "comandos_novos": comandos_novos,
        "comandos_removidos": comandos_removidos,
        "comandos_alterados": comandos_alterados,
    }


# ============================================================
# VERSÃO
# ============================================================

def interpretar_versao(
    texto,
):

    try:

        limpo = (
            str(texto)
            .replace("v", "")
            .replace("V", "")
            .replace("beta", "")
            .replace("Beta", "")
            .strip()
        )

        partes = limpo.split(".")

        major = int(partes[0])
        minor = int(partes[1])
        patch = int(partes[2])

        return (
            major,
            minor,
            patch,
        )

    except (
        ValueError,
        TypeError,
        IndexError,
    ):

        return (
            0,
            7,
            0,
        )


def proxima_versao(
    versao,
):

    major, minor, patch = interpretar_versao(
        versao,
    )

    patch += 1

    return f"{major}.{minor}.{patch}"


def versao_atual():

    with conectar() as db:

        row = db.execute(
            """
            SELECT versao
            FROM atualizacoes
            ORDER BY numero DESC
            LIMIT 1
            """
        ).fetchone()

        if row and row["versao"]:
            return row["versao"]

    # --------------------------------------------------------
    # Compatibilidade com estado antigo
    # --------------------------------------------------------

    if LEGACY_STATE.exists():

        try:

            dados = json.loads(
                LEGACY_STATE.read_text(
                    encoding="utf-8",
                )
            )

            valor = dados.get(
                "versao",
            )

            if valor:
                return str(valor)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            pass

    return "0.7.0"


# ============================================================
# TEXTO PÚBLICO
# ============================================================

def nome_amigavel(
    nome,
):

    mapa = {
        "pokemon": "Pokémon",
        "economia": "Economia",
        "moderation": "Moderação",
        "moderacao": "Moderação",
        "antiraid": "Segurança",
        "tickets": "Tickets",
        "sorteios": "Sorteios",
        "desabafos": "Desabafos",
        "ship": "Ships",
        "help": "Central de Ajuda",
        "logs": "Logs",
        "updates": "Atualizações",
    }

    limpo = (
        str(nome)
        .lower()
        .replace(".py", "")
    )

    return mapa.get(
        limpo,
        str(nome)
        .replace(".py", "")
        .replace("_", " ")
        .title(),
    )


def resumo_publico(
    mudancas,
):

    partes = []

    if mudancas["comandos_novos"]:

        partes.append(
            "✨ **"
            f"{len(mudancas['comandos_novos'])}"
            " novo(s) recurso(s)**"
        )

    if mudancas["comandos_alterados"]:

        partes.append(
            "🔧 **"
            f"{len(mudancas['comandos_alterados'])}"
            " recurso(s) aprimorado(s)**"
        )

    if mudancas["comandos_removidos"]:

        partes.append(
            "🗑️ **"
            f"{len(mudancas['comandos_removidos'])}"
            " recurso(s) removido(s)**"
        )

    if mudancas["arquivos_novos"]:

        partes.append(
            "📦 **"
            f"{len(mudancas['arquivos_novos'])}"
            " sistema(s) adicionado(s)**"
        )

    if mudancas["arquivos_removidos"]:

        partes.append(
            "🗑️ **"
            f"{len(mudancas['arquivos_removidos'])}"
            " sistema(s) removido(s)**"
        )

    if not partes:

        partes.append(
            "🔧 **Melhorias internas de "
            "estabilidade e manutenção.**"
        )

    return " • ".join(
        partes,
    )


def criar_descricao_usuario(
    mudancas,
):

    blocos = []

    novos = mudancas[
        "comandos_novos"
    ][:12]

    alterados = mudancas[
        "comandos_alterados"
    ][:12]

    removidos = mudancas[
        "comandos_removidos"
    ][:12]

    if novos:

        linhas = [
            "✨ **NOVO**",
            "Novos recursos foram adicionados "
            "ao Royalt.",
        ]

        linhas.extend(
            f"• `{item}`"
            for item in novos
        )

        blocos.append(
            "\n".join(linhas),
        )

    if alterados:

        linhas = [
            "🔧 **MELHORIAS**",
            "Recursos existentes receberam "
            "ajustes e melhorias.",
        ]

        linhas.extend(
            f"• `{item}`"
            for item in alterados
        )

        blocos.append(
            "\n".join(linhas),
        )

    if removidos:

        linhas = [
            "🗑️ **ALTERAÇÕES**",
            "Alguns recursos foram removidos "
            "ou substituídos.",
        ]

        linhas.extend(
            f"• `{item}`"
            for item in removidos
        )

        blocos.append(
            "\n".join(linhas),
        )

    if not blocos:

        blocos.append(
            "✨ **Melhorias gerais**\n"
            "O Royalt recebeu ajustes de "
            "estabilidade e manutenção."
        )

    return "\n\n".join(
        blocos,
    )


# ============================================================
# EMBED PÚBLICO
# ============================================================

def embed_publico(
    registro,
):

    mudancas = registro[
        "mudancas"
    ]

    try:

        timestamp = datetime.fromisoformat(
            registro["data"],
        )

    except (
        ValueError,
        TypeError,
    ):

        timestamp = agora()

    embed = discord.Embed(
        title=(
            "🛠️ ROYALT • "
            f"ATUALIZAÇÃO #{registro['numero']}"
        ),
        description=(
            f"## 🚀 Royalt `{registro['versao']}`\n\n"
            f"📦 **Anterior:** "
            f"`{registro['versao_anterior']}`\n"
            f"🚀 **Atual:** "
            f"`{registro['versao']}`\n"
            f"📅 {data_discord(registro['data'])}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{criar_descricao_usuario(mudancas)}\n\n"
            "📌 **Resumo**\n"
            f"{registro['resumo_publico']}"
        ),
        color=COR_VERDE,
        timestamp=timestamp,
    )

    sistemas = sorted(
        set(
            mudancas[
                "arquivos_novos"
            ]
        )
        | set(
            mudancas[
                "arquivos_alterados"
            ]
        )
        | set(
            mudancas[
                "arquivos_removidos"
            ]
        )
    )

    if sistemas:

        nomes = ", ".join(
            nome_amigavel(
                item,
            )
            for item in sistemas[:8]
        )

        embed.add_field(
            name="📂 Áreas envolvidas",
            value=nomes[:1024],
            inline=False,
        )

    embed.set_footer(
        text=(
            f"{NOME_SISTEMA} • "
            "Histórico público"
        ),
    )

    return embed


# ============================================================
# EMBED DEV
# ============================================================

def embed_dev(
    registro,
):

    mudancas = registro[
        "mudancas"
    ]

    try:

        timestamp = datetime.fromisoformat(
            registro["data"],
        )

    except (
        ValueError,
        TypeError,
    ):

        timestamp = agora()

    embed = discord.Embed(
        title=(
            "🔒 ROYALT • "
            f"DEVLOG #{registro['numero']}"
        ),
        description=(
            f"**Royalt {registro['versao']}**\n"
            f"`{registro['versao_anterior']}` "
            f"→ `{registro['versao']}`\n"
            f"{data_discord(registro['data'])}"
        ),
        color=COR_ROXA,
        timestamp=timestamp,
    )

    if mudancas["arquivos_novos"]:

        embed.add_field(
            name="📁 Arquivos novos",
            value="\n".join(
                f"`{x}`"
                for x in mudancas[
                    "arquivos_novos"
                ][:15]
            )[:1024],
            inline=False,
        )

    if mudancas["arquivos_alterados"]:

        embed.add_field(
            name="🔧 Arquivos alterados",
            value="\n".join(
                f"`{x}`"
                for x in mudancas[
                    "arquivos_alterados"
                ][:15]
            )[:1024],
            inline=False,
        )

    if mudancas["arquivos_removidos"]:

        embed.add_field(
            name="🗑️ Arquivos removidos",
            value="\n".join(
                f"`{x}`"
                for x in mudancas[
                    "arquivos_removidos"
                ][:15]
            )[:1024],
            inline=False,
        )

    if mudancas["comandos_novos"]:

        embed.add_field(
            name="🆕 Comandos novos",
            value="\n".join(
                f"`{x}`"
                for x in mudancas[
                    "comandos_novos"
                ][:20]
            )[:1024],
            inline=False,
        )

    if mudancas["comandos_alterados"]:

        embed.add_field(
            name="🔄 Comandos alterados",
            value="\n".join(
                f"`{x}`"
                for x in mudancas[
                    "comandos_alterados"
                ][:20]
            )[:1024],
            inline=False,
        )

    if mudancas["comandos_removidos"]:

        embed.add_field(
            name="🗑️ Comandos removidos",
            value="\n".join(
                f"`{x}`"
                for x in mudancas[
                    "comandos_removidos"
                ][:20]
            )[:1024],
            inline=False,
        )

    embed.add_field(
        name="📊 Resumo técnico",
        value=(
            "Arquivos novos: "
            f"**{len(mudancas['arquivos_novos'])}**\n"
            "Arquivos alterados: "
            f"**{len(mudancas['arquivos_alterados'])}**\n"
            "Arquivos removidos: "
            f"**{len(mudancas['arquivos_removidos'])}**\n"
            "Comandos novos: "
            f"**{len(mudancas['comandos_novos'])}**\n"
            "Comandos alterados: "
            f"**{len(mudancas['comandos_alterados'])}**\n"
            "Comandos removidos: "
            f"**{len(mudancas['comandos_removidos'])}**"
        ),
        inline=False,
    )

    embed.set_footer(
        text=(
            f"{NOME_SISTEMA} • "
            "Histórico privado de desenvolvimento"
        ),
    )

    return embed


# ============================================================
# HISTÓRICO
# ============================================================

class HistoricoSelect(
    discord.ui.Select,
):

    def __init__(
        self,
        updates_cog,
        registros,
    ):

        self.updates_cog = updates_cog

        options = []

        for registro in registros[:25]:

            label = (
                f"#{registro['numero']} • "
                f"Royalt {registro['versao']}"
            )[:100]

            descricao = (
                registro[
                    "resumo_publico"
                ][:100]
            )

            options.append(
                discord.SelectOption(
                    label=label,
                    description=descricao,
                    value=str(
                        registro["numero"],
                    ),
                    emoji="🛠️",
                )
            )

        super().__init__(
            placeholder=(
                "Escolha uma atualização..."
            ),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(
        self,
        interaction: discord.Interaction,
    ):

        numero = int(
            self.values[0],
        )

        registro = (
            self.updates_cog
            .buscar_registro(
                numero,
            )
        )

        if registro is None:

            await interaction.response.send_message(
                "❌ Esta atualização não foi encontrada.",
                ephemeral=True,
            )

            return

        await interaction.response.edit_message(
            embed=embed_publico(
                registro,
            ),
            view=HistoricoView(
                self.updates_cog,
                interaction.user,
                self.updates_cog.historico_publico(),
            ),
        )


class HistoricoView(
    discord.ui.View,
):

    def __init__(
        self,
        updates_cog,
        autor,
        registros,
    ):

        super().__init__(
            timeout=300,
        )

        self.updates_cog = updates_cog
        self.autor_id = autor.id

        self.add_item(
            HistoricoSelect(
                updates_cog,
                registros,
            )
        )

    async def interaction_check(
        self,
        interaction,
    ):

        if interaction.user.id != self.autor_id:

            await interaction.response.send_message(
                "🔒 Este painel foi aberto por outra pessoa.",
                ephemeral=True,
            )

            return False

        return True


# ============================================================
# COG
# ============================================================

class Updates(
    commands.Cog,
):

    def __init__(
        self,
        bot,
    ):

        self.bot = bot

        inicializar_banco()

        self._verificacao_executada = False

        # A tarefa espera o bot ficar pronto antes
        # de analisar os Cogs.
        self._verificar_inicial.start()

    def cog_unload(
        self,
    ):

        if self._verificar_inicial.is_running():
            self._verificar_inicial.cancel()

    # ========================================================
    # VERIFICAÇÃO AUTOMÁTICA
    # ========================================================

    @tasks.loop(
        count=1,
    )
    async def _verificar_inicial(
        self,
    ):

        await self.bot.wait_until_ready()

        if self._verificacao_executada:
            return

        self._verificacao_executada = True

        if not AUTO_DETECTAR:

            print(
                "[UPDATES] "
                "Detecção automática desativada."
            )

            return

        # Pequena margem para garantir que os outros
        # Cogs já tenham sido carregados.
        await asyncio.sleep(2)

        try:

            print(
                "[UPDATES] "
                "Verificando alterações..."
            )

            snapshot_antigo = carregar_snapshot()
            snapshot_atual = criar_snapshot()

            # ------------------------------------------------
            # PRIMEIRA EXECUÇÃO
            # ------------------------------------------------

            if not snapshot_antigo:

                salvar_snapshot(
                    snapshot_atual,
                )

                print(
                    "[UPDATES] "
                    "Snapshot inicial criado."
                )

                return

            # ------------------------------------------------
            # COMPARAÇÃO
            # ------------------------------------------------

            mudancas = comparar_snapshots(
                snapshot_antigo,
                snapshot_atual,
            )

            # O snapshot é atualizado mesmo quando
            # não houve alterações.
            salvar_snapshot(
                snapshot_atual,
            )

            houve = any(
                mudancas[chave]
                for chave in (
                    "arquivos_novos",
                    "arquivos_removidos",
                    "arquivos_alterados",
                    "comandos_novos",
                    "comandos_removidos",
                    "comandos_alterados",
                )
            )

            if not houve:

                print(
                    "[UPDATES] "
                    "Nenhuma alteração detectada."
                )

                return

            # ------------------------------------------------
            # CRIA NOVA VERSÃO
            # ------------------------------------------------

            versao_anterior = versao_atual()

            nova_versao = proxima_versao(
                versao_anterior,
            )

            numero = proximo_numero()

            momento = agora_iso()

            registro = {
                "numero": numero,
                "versao_anterior": versao_anterior,
                "versao": nova_versao,
                "data": momento,
                "resumo_publico": resumo_publico(
                    mudancas,
                ),
                "mudancas": mudancas,
            }

            # ------------------------------------------------
            # SALVA SQLITE
            # ------------------------------------------------

            salvar_update(
                numero=numero,
                versao_anterior=versao_anterior,
                versao=nova_versao,
                resumo_publico=registro[
                    "resumo_publico"
                ],
                detalhes=mudancas,
            )

            print(
                "[UPDATES] "
                f"#{numero} • "
                f"{versao_anterior} → "
                f"{nova_versao}"
            )

            # ------------------------------------------------
            # ENVIA LOG PÚBLICO
            # ------------------------------------------------

            await self.enviar_publico(
                registro,
            )

            # ------------------------------------------------
            # ENVIA LOG DEV
            # ------------------------------------------------

            await self.enviar_dev(
                registro,
            )

        except Exception as erro:

            print(
                "[UPDATES] Erro verificando atualização: "
                f"{type(erro).__name__}: {erro}"
            )

    # ========================================================
    # CONSULTAS
    # ========================================================

    def historico_publico(
        self,
    ):

        registros = []

        for row in obter_historico_publico(
            25,
        ):

            try:

                detalhes = json.loads(
                    row["detalhes_json"],
                )

            except (
                TypeError,
                json.JSONDecodeError,
            ):

                detalhes = {}

            registros.append(
                {
                    "numero": row["numero"],
                    "versao_anterior": row[
                        "versao_anterior"
                    ],
                    "versao": row["versao"],
                    "data": row["momento"],
                    "resumo_publico": row[
                        "resumo_publico"
                    ],
                    "mudancas": detalhes,
                }
            )

        return registros

    def buscar_registro(
        self,
        numero,
    ):

        with conectar() as db:

            row = db.execute(
                """
                SELECT *
                FROM atualizacoes
                WHERE numero = ?
                """,
                (
                    int(numero),
                ),
            ).fetchone()

        if row is None:
            return None

        try:

            detalhes = json.loads(
                row["detalhes_json"],
            )

        except (
            TypeError,
            json.JSONDecodeError,
        ):

            detalhes = {}

        return {
            "numero": row["numero"],
            "versao_anterior": row[
                "versao_anterior"
            ],
            "versao": row["versao"],
            "data": row["momento"],
            "resumo_publico": row[
                "resumo_publico"
            ],
            "mudancas": detalhes,
        }

    # ========================================================
    # PERMISSÕES DEV
    # ========================================================

    def eh_desenvolvedor(
        self,
        user_id: int,
    ) -> bool:

        # IDs definidos explicitamente no .env
        if user_id in DEVELOPER_IDS:
            return True

        # Owners do bot
        owner_ids = set(
            getattr(
                self.bot,
                "owner_ids",
                set(),
            )
            or set()
        )

        owner_id = getattr(
            self.bot,
            "owner_id",
            None,
        )

        if owner_id:
            owner_ids.add(
                owner_id,
            )

        return user_id in owner_ids

    # ========================================================
    # CANAIS
    # ========================================================

    def _canal_configurado(
        self,
        guild,
        canal_id,
    ):

        if canal_id is None:
            return None

        canal = guild.get_channel(
            canal_id,
        )

        if isinstance(
            canal,
            discord.TextChannel,
        ):
            return canal

        return None

    def _canal_publico_da_guild(
        self,
        guild,
    ):

        # 1. Configuração específica do servidor
        valor = obter_configuracao(
            f"public_channel:{guild.id}",
        )

        canal_id = ler_id_env(
            valor or "",
        )

        canal = self._canal_configurado(
            guild,
            canal_id,
        )

        if canal:
            return canal

        # 2. Variável global
        return self._canal_configurado(
            guild,
            CANAL_PUBLICO_ID,
        )

    async def enviar_publico(
        self,
        registro,
    ):

        embed = embed_publico(
            registro,
        )

        enviados = set()

        for guild in self.bot.guilds:

            canal = self._canal_publico_da_guild(
                guild,
            )

            if canal is None:
                continue

            # Evita mandar duas vezes para o mesmo canal.
            if canal.id in enviados:
                continue

            enviados.add(
                canal.id,
            )

            try:

                await canal.send(
                    embed=embed,
                )

                print(
                    "[UPDATES] "
                    f"Update público enviado "
                    f"para #{canal.name} "
                    f"({guild.name})."
                )

            except (
                discord.HTTPException,
                discord.Forbidden,
            ) as erro:

                print(
                    "[UPDATES] Falha no canal público "
                    f"{guild.name}: {erro}"
                )

    async def enviar_dev(
        self,
        registro,
    ):

        if not CANAL_DEV_ID:
            return

        embed = embed_dev(
            registro,
        )

        enviados = set()

        for guild in self.bot.guilds:

            canal = self._canal_configurado(
                guild,
                CANAL_DEV_ID,
            )

            if canal is None:
                continue

            if canal.id in enviados:
                continue

            enviados.add(
                canal.id,
            )

            try:

                await canal.send(
                    embed=embed,
                )

                print(
                    "[UPDATES] "
                    f"Devlog enviado para #{canal.name} "
                    f"({guild.name})."
                )

            except (
                discord.HTTPException,
                discord.Forbidden,
            ) as erro:

                print(
                    "[UPDATES] Falha no canal DEV "
                    f"{guild.name}: {erro}"
                )

    # ========================================================
    # !UPDATES
    # ========================================================

    @commands.command(
        name="updates",
        aliases=[
            "atualizacoes",
            "atualizações",
            "changelog",
        ],
        description=(
            "Mostra as últimas atualizações "
            "do Royalt."
        ),
    )
    async def updates_comando(
        self,
        ctx,
    ):

        registros = self.historico_publico()

        if not registros:

            embed = discord.Embed(
                title="📭 ROYALT • ATUALIZAÇÕES",
                description=(
                    "O histórico público ainda está vazio."
                ),
                color=COR_CINZA,
            )

            await ctx.send(
                embed=embed,
            )

            return

        ultimo = registros[0]

        embed = discord.Embed(
            title="🛠️ ROYALT • ATUALIZAÇÕES",
            description=(
                "Acompanhe as novidades, melhorias "
                "e correções do Royalt.\n\n"
                f"🚀 **Versão atual:** "
                f"`{ultimo['versao']}`\n"
                f"📚 **Atualizações registradas:** "
                f"`{len(registros)}`\n\n"
                "Use o menu abaixo para consultar "
                "uma atualização."
            ),
            color=COR_VERDE,
        )

        embed.add_field(
            name=(
                "✨ Última atualização "
                f"#{ultimo['numero']}"
            ),
            value=(
                f"`{ultimo['versao_anterior']}` "
                f"→ `{ultimo['versao']}`\n\n"
                f"{ultimo['resumo_publico']}\n"
                f"📅 {data_discord(ultimo['data'])}"
            ),
            inline=False,
        )

        embed.set_footer(
            text=(
                f"{NOME_SISTEMA} • "
                "Histórico público"
            ),
        )

        await ctx.send(
            embed=embed,
            view=HistoricoView(
                self,
                ctx.author,
                registros,
            ),
        )

    # ========================================================
    # /UPDATES
    # ========================================================

    @app_commands.command(
        name="updates",
        description=(
            "Mostra as últimas atualizações "
            "do Royalt."
        ),
    )
    async def updates_slash(
        self,
        interaction: discord.Interaction,
    ):

        registros = self.historico_publico()

        if not registros:

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="📭 ROYALT • ATUALIZAÇÕES",
                    description=(
                        "O histórico público ainda está vazio."
                    ),
                    color=COR_CINZA,
                )
            )

            return

        ultimo = registros[0]

        embed = discord.Embed(
            title="🛠️ ROYALT • ATUALIZAÇÕES",
            description=(
                "Acompanhe a evolução do Royalt.\n\n"
                f"🚀 **Versão atual:** "
                f"`{ultimo['versao']}`\n"
                "📚 Escolha uma atualização "
                "no menu abaixo."
            ),
            color=COR_VERDE,
        )

        embed.add_field(
            name=(
                "✨ Última atualização "
                f"#{ultimo['numero']}"
            ),
            value=(
                f"`{ultimo['versao_anterior']}` "
                f"→ `{ultimo['versao']}`\n"
                f"{ultimo['resumo_publico']}\n"
                f"📅 {data_discord(ultimo['data'])}"
            ),
            inline=False,
        )

        embed.set_footer(
            text=(
                f"{NOME_SISTEMA} • "
                "Histórico público"
            ),
        )

        await interaction.response.send_message(
            embed=embed,
            view=HistoricoView(
                self,
                interaction.user,
                registros,
            ),
        )

    # ========================================================
    # !HISTORICO
    # ========================================================

    @commands.command(
        name="historico",
        aliases=[
            "updatehistorico",
            "updateshistorico",
        ],
        description=(
            "Mostra o histórico público "
            "de atualizações."
        ),
    )
    async def historico(
        self,
        ctx,
    ):

        registros = self.historico_publico()

        if not registros:

            await ctx.send(
                embed=discord.Embed(
                    title="📭 HISTÓRICO VAZIO",
                    description=(
                        "Nenhuma atualização pública "
                        "foi registrada."
                    ),
                    color=COR_CINZA,
                )
            )

            return

        embed = discord.Embed(
            title="📚 ROYALT • HISTÓRICO PÚBLICO",
            description=(
                "Selecione uma atualização para "
                "visualizar as novidades daquela versão."
            ),
            color=COR_AZUL,
        )

        await ctx.send(
            embed=embed,
            view=HistoricoView(
                self,
                ctx.author,
                registros,
            ),
        )

    # ========================================================
    # !ULTIMOUPDATE
    # ========================================================

    @commands.command(
        name="ultimoupdate",
        aliases=[
            "ultimo_update",
            "lastupdate",
        ],
        description=(
            "Mostra a última atualização "
            "do Royalt."
        ),
    )
    async def ultimoupdate(
        self,
        ctx,
    ):

        registros = self.historico_publico()

        if not registros:

            await ctx.send(
                "📭 Nenhuma atualização registrada.",
            )

            return

        await ctx.send(
            embed=embed_publico(
                registros[0],
            )
        )

    # ========================================================
    # !UPDATECANAL
    # ========================================================

    @commands.command(
        name="updatecanal",
        description=(
            "Define o canal público "
            "dos updates."
        ),
    )
    @commands.guild_only()
    @commands.has_permissions(
        manage_guild=True,
    )
    async def updatecanal(
        self,
        ctx,
        canal: discord.TextChannel,
    ):

        salvar_configuracao(
            f"public_channel:{ctx.guild.id}",
            str(canal.id),
        )

        await ctx.send(
            embed=discord.Embed(
                title=(
                    "📢 ROYALT • "
                    "CANAL DE UPDATES"
                ),
                description=(
                    "✅ Canal configurado com sucesso.\n\n"
                    f"📁 **Canal:** {canal.mention}\n\n"
                    "Novas atualizações públicas "
                    "serão enviadas aqui."
                ),
                color=COR_VERDE,
            )
        )

    # ========================================================
    # !UPDATETESTE
    # ========================================================

    @commands.command(
        name="updateteste",
        aliases=[
            "testupdate",
        ],
        description=(
            "Envia um teste visual "
            "do sistema de updates."
        ),
    )
    @commands.guild_only()
    @commands.has_permissions(
        manage_guild=True,
    )
    async def update_teste(
        self,
        ctx,
    ):

        embed = discord.Embed(
            title=(
                "🛠️ ROYALT • "
                "ATUALIZAÇÃO DE TESTE"
            ),
            description=(
                "## 🚀 Royalt Update System\n\n"
                "Este é um teste do formato "
                "público de atualizações.\n\n"
                "✨ **NOVO**\n"
                "Um novo recurso foi disponibilizado.\n\n"
                "🔧 **MELHORIAS**\n"
                "A experiência geral recebeu melhorias.\n\n"
                "🐛 **CORREÇÕES**\n"
                "Problemas encontrados foram corrigidos.\n\n"
                "📌 O teste não cria uma nova "
                "versão no histórico."
            ),
            color=COR_AMARELO,
            timestamp=agora(),
        )

        embed.set_footer(
            text=(
                f"{NOME_SISTEMA} • "
                "Teste"
            ),
        )

        await ctx.send(
            embed=embed,
        )

    # ========================================================
    # !DEVUPDATE
    #
    # Histórico técnico.
    #
    # SOMENTE:
    # - owners do bot
    # - IDs definidos em ROYALT_DEVELOPER_IDS
    # ========================================================

    @commands.command(
        name="devupdate",
        aliases=[
            "devupdates",
            "updatedev",
            "devlog",
        ],
        hidden=True,
        description=(
            "Mostra o histórico técnico "
            "privado do Royalt."
        ),
    )
    async def devupdate(
        self,
        ctx,
    ):

        if not self.eh_desenvolvedor(
            ctx.author.id,
        ):

            await ctx.send(
                "🔒 Você não possui acesso "
                "ao histórico técnico.",
                delete_after=8,
            )

            return

        registros = self.historico_publico()

        if not registros:

            await ctx.send(
                embed=discord.Embed(
                    title=(
                        "🔒 ROYALT • DEVLOG"
                    ),
                    description=(
                        "Nenhum update técnico "
                        "foi registrado ainda."
                    ),
                    color=COR_ROXA,
                )
            )

            return

        # Mostra até 5 atualizações.
        for registro in registros[:5]:

            await ctx.send(
                embed=embed_dev(
                    registro,
                )
            )

    # ========================================================
    # ERROS DE PERMISSÃO
    # ========================================================

    @updatecanal.error
    async def updatecanal_error(
        self,
        ctx,
        erro,
    ):

        if isinstance(
            erro,
            commands.MissingPermissions,
        ):

            await ctx.send(
                "🔒 Você precisa da permissão "
                "**Gerenciar Servidor** para "
                "configurar o canal de updates.",
                delete_after=8,
            )

            return

        if isinstance(
            erro,
            commands.BadArgument,
        ):

            await ctx.send(
                "❌ Não consegui encontrar esse canal.",
                delete_after=8,
            )

            return

        print(
            "[UPDATES] Erro em !updatecanal: "
            f"{type(erro).__name__}: {erro}"
        )

    @update_teste.error
    async def update_teste_error(
        self,
        ctx,
        erro,
    ):

        if isinstance(
            erro,
            commands.MissingPermissions,
        ):

            await ctx.send(
                "🔒 Você precisa da permissão "
                "**Gerenciar Servidor** para "
                "usar este teste.",
                delete_after=8,
            )

            return

        print(
            "[UPDATES] Erro em !updateteste: "
            f"{type(erro).__name__}: {erro}"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot,
):

    inicializar_banco()

    await bot.add_cog(
        Updates(bot),
    )

    print(
        "[UPDATES] "
        f"{NOME_SISTEMA} v{VERSAO_SISTEMA} "
        "carregado com sucesso."
    )