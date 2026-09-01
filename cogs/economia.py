import asyncio
import io
import json
import math
import random
import sqlite3
import time

from datetime import datetime, timezone
from pathlib import Path

import discord

from discord.ext import commands

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# ROYALT • ECONOMIA
# ============================================================

NOME_SISTEMA = "Royalt Economy System"
VERSAO = "3.1 SQLite"


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PASTA_DATA = (
    BASE_DIR / "data"
)

PASTA_DATA.mkdir(
    parents=True,
    exist_ok=True
)

BANCO_SQLITE = (
    PASTA_DATA / "economia.db"
)

ARQUIVO_JSON_ANTIGO = (
    PASTA_DATA / "economia.json"
)


# ============================================================
# CORES
# ============================================================

CORES = {

    "dourado": discord.Color.from_rgb(
        255,
        215,
        0
    ),

    "verde": discord.Color.from_rgb(
        46,
        204,
        113
    ),

    "azul": discord.Color.from_rgb(
        52,
        152,
        219
    ),

    "roxo": discord.Color.from_rgb(
        155,
        89,
        182
    ),

    "rosa": discord.Color.from_rgb(
        255,
        105,
        180
    ),

    "laranja": discord.Color.from_rgb(
        255,
        159,
        67
    ),

    "vermelho": discord.Color.from_rgb(
        231,
        76,
        60
    ),

    "ciano": discord.Color.from_rgb(
        0,
        206,
        209
    ),

    "amarelo": discord.Color.from_rgb(
        241,
        196,
        15
    ),

    "cinza": discord.Color.from_rgb(
        149,
        165,
        166
    )
}


# ============================================================
# CONFIGURAÇÕES
# ============================================================

SALDO_INICIAL = 1000

DIARIO_MINIMO = 500
DIARIO_MAXIMO = 1200

XP_DIARIO_MINIMO = 50
XP_DIARIO_MAXIMO = 100

COOLDOWN_DIARIO = 86400
COOLDOWN_TRABALHO = 3600
COOLDOWN_DESAFIO = 900
COOLDOWN_QUIZ = 300
COOLDOWN_REACAO = 300

BLOCO_XP_BASE = 100

MAX_STREAK_DAILY = 30


# ============================================================
# TRABALHOS
# ============================================================

TRABALHOS = [

    {
        "level": 1,
        "nome": "Ajudante",
        "emoji": "🧹",
        "minimo": 150,
        "maximo": 280,
        "xp_min": 20,
        "xp_max": 35
    },

    {
        "level": 2,
        "nome": "Entregador",
        "emoji": "📦",
        "minimo": 200,
        "maximo": 350,
        "xp_min": 25,
        "xp_max": 40
    },

    {
        "level": 3,
        "nome": "Freelancer",
        "emoji": "💻",
        "minimo": 250,
        "maximo": 450,
        "xp_min": 30,
        "xp_max": 45
    },

    {
        "level": 4,
        "nome": "Designer",
        "emoji": "🎨",
        "minimo": 300,
        "maximo": 520,
        "xp_min": 35,
        "xp_max": 50
    },

    {
        "level": 5,
        "nome": "Técnico",
        "emoji": "🔧",
        "minimo": 350,
        "maximo": 600,
        "xp_min": 40,
        "xp_max": 55
    },

    {
        "level": 6,
        "nome": "Assistente",
        "emoji": "🧑‍💼",
        "minimo": 420,
        "maximo": 700,
        "xp_min": 45,
        "xp_max": 60
    },

    {
        "level": 7,
        "nome": "Analista",
        "emoji": "📊",
        "minimo": 500,
        "maximo": 820,
        "xp_min": 50,
        "xp_max": 65
    },

    {
        "level": 8,
        "nome": "Pesquisador",
        "emoji": "🧪",
        "minimo": 580,
        "maximo": 950,
        "xp_min": 55,
        "xp_max": 70
    },

    {
        "level": 9,
        "nome": "Desenvolvedor",
        "emoji": "🖥️",
        "minimo": 650,
        "maximo": 1100,
        "xp_min": 60,
        "xp_max": 75
    },

    {
        "level": 10,
        "nome": "Especialista",
        "emoji": "🧠",
        "minimo": 750,
        "maximo": 1250,
        "xp_min": 65,
        "xp_max": 80
    },

    {
        "level": 12,
        "nome": "Consultor",
        "emoji": "📋",
        "minimo": 900,
        "maximo": 1450,
        "xp_min": 70,
        "xp_max": 90
    },

    {
        "level": 15,
        "nome": "Gerente",
        "emoji": "📈",
        "minimo": 1100,
        "maximo": 1800,
        "xp_min": 80,
        "xp_max": 100
    },

    {
        "level": 20,
        "nome": "Diretor",
        "emoji": "🏢",
        "minimo": 1400,
        "maximo": 2300,
        "xp_min": 90,
        "xp_max": 115
    },

    {
        "level": 25,
        "nome": "Executivo",
        "emoji": "👔",
        "minimo": 1800,
        "maximo": 3000,
        "xp_min": 100,
        "xp_max": 130
    },

    {
        "level": 30,
        "nome": "Magnata",
        "emoji": "💎",
        "minimo": 2500,
        "maximo": 4200,
        "xp_min": 110,
        "xp_max": 145
    },

    {
        "level": 40,
        "nome": "Lenda Empresarial",
        "emoji": "👑",
        "minimo": 3500,
        "maximo": 6000,
        "xp_min": 125,
        "xp_max": 165
    },

    {
        "level": 50,
        "nome": "Titã da Economia",
        "emoji": "🌌",
        "minimo": 5000,
        "maximo": 9000,
        "xp_min": 140,
        "xp_max": 190
    }
]


# ============================================================
# TEMAS
# ============================================================

TEMAS = {

    "dourado": {
        "nome": "Dourado Imperial",
        "cor": "#FFD700",
        "emoji": "👑",
        "banner": ""
    },

    "roxo": {
        "nome": "Royalt Roxo",
        "cor": "#9B59B6",
        "emoji": "💜",
        "banner": ""
    },

    "rosa": {
        "nome": "Neon Rosa",
        "cor": "#FF69B4",
        "emoji": "🌸",
        "banner": ""
    },

    "azul": {
        "nome": "Oceano",
        "cor": "#3498DB",
        "emoji": "🌊",
        "banner": ""
    },

    "verde": {
        "nome": "Natureza",
        "cor": "#2ECC71",
        "emoji": "🌿",
        "banner": ""
    },

    "ciano": {
        "nome": "Cyber Ciano",
        "cor": "#00CED1",
        "emoji": "⚡",
        "banner": ""
    },

    "laranja": {
        "nome": "Solar",
        "cor": "#FF9F43",
        "emoji": "☀️",
        "banner": ""
    }
}


# ============================================================
# CORES ACEITAS
# ============================================================

CORES_PERFIL = {

    "dourado": "#FFD700",
    "verde": "#2ECC71",
    "azul": "#3498DB",
    "roxo": "#9B59B6",
    "rosa": "#FF69B4",
    "laranja": "#FF9F43",
    "vermelho": "#E74C3C",
    "ciano": "#00CED1"
}


# ============================================================
# DESAFIOS
# ============================================================

DESAFIOS = [

    {
        "texto": "Organize alguma coisa do seu setup.",
        "recompensa_min": 100,
        "recompensa_max": 250,
        "xp_min": 20,
        "xp_max": 40
    },

    {
        "texto": "Aprenda alguma coisa nova durante alguns minutos.",
        "recompensa_min": 120,
        "recompensa_max": 280,
        "xp_min": 25,
        "xp_max": 45
    },

    {
        "texto": "Ajude alguém da comunidade.",
        "recompensa_min": 150,
        "recompensa_max": 320,
        "xp_min": 30,
        "xp_max": 50
    },

    {
        "texto": "Conclua uma pequena tarefa que estava adiando.",
        "recompensa_min": 160,
        "recompensa_max": 350,
        "xp_min": 30,
        "xp_max": 55
    }
]


# ============================================================
# QUIZ
# ============================================================

QUIZZES = [

    {
        "pergunta": "Qual planeta é conhecido como planeta vermelho?",
        "opcoes": [
            "A) Marte",
            "B) Vênus",
            "C) Júpiter",
            "D) Saturno"
        ],
        "resposta": "a",
        "recompensa": 250,
        "xp": 40
    },

    {
        "pergunta": "Qual é o maior oceano da Terra?",
        "opcoes": [
            "A) Atlântico",
            "B) Índico",
            "C) Pacífico",
            "D) Ártico"
        ],
        "resposta": "c",
        "recompensa": 250,
        "xp": 40
    },

    {
        "pergunta": "Quanto é 9 × 9?",
        "opcoes": [
            "A) 72",
            "B) 81",
            "C) 90",
            "D) 99"
        ],
        "resposta": "b",
        "recompensa": 250,
        "xp": 40
    },

    {
        "pergunta": "Qual linguagem está sendo usada para programar o Royalt?",
        "opcoes": [
            "A) Python",
            "B) Ruby",
            "C) Java",
            "D) Lua"
        ],
        "resposta": "a",
        "recompensa": 300,
        "xp": 50
    }
]


# ============================================================
# UTILIDADES
# ============================================================

def agora_iso():

    return datetime.now(
        timezone.utc
    ).isoformat()


def formatar_moedas(
    valor
):

    return (
        f"{int(valor):,}"
        .replace(
            ",",
            "."
        )
    )


def calcular_nivel(
    xp
):

    xp = max(
        0,
        int(xp)
    )

    nivel = 1
    restante = xp

    while restante >= (
        BLOCO_XP_BASE * nivel
    ):

        restante -= (
            BLOCO_XP_BASE * nivel
        )

        nivel += 1

        if nivel >= 1000:
            break

    return (
        nivel,
        restante,
        BLOCO_XP_BASE * nivel
    )


def barra_progresso(
    atual,
    total,
    tamanho=15
):

    if total <= 0:
        return "🟩" * tamanho

    preenchido = round(
        (
            atual / total
        )
        * tamanho
    )

    preenchido = max(
        0,
        min(
            tamanho,
            preenchido
        )
    )

    return (
        "🟩" * preenchido
        +
        "⬛" * (
            tamanho
            - preenchido
        )
    )


def cor_do_hex(
    hexadecimal
):

    texto = (
        str(
            hexadecimal
            or ""
        )
        .replace(
            "#",
            ""
        )
        .strip()
    )

    if len(texto) != 6:
        return CORES["dourado"]

    try:

        return discord.Color(
            value=int(
                texto,
                16
            )
        )

    except ValueError:

        return CORES["dourado"]


def emoji_seguro(
    texto,
    padrao="💰"
):

    texto = (
        str(
            texto or ""
        )
        .strip()
    )

    return texto[:8] or padrao


# ============================================================
# BANCO
# ============================================================

class BancoEconomia:

    def __init__(
        self,
        caminho
    ):

        self.caminho = str(
            caminho
        )

        self.lock = asyncio.Lock()

        self.inicializar()

    # ========================================================
    # CONEXÃO
    # ========================================================

    def conectar(
        self
    ):

        db = sqlite3.connect(
            self.caminho,
            timeout=15
        )

        db.row_factory = sqlite3.Row

        db.execute(
            "PRAGMA journal_mode=WAL"
        )

        db.execute(
            "PRAGMA synchronous=NORMAL"
        )

        db.execute(
            "PRAGMA foreign_keys=ON"
        )

        return db

    # ========================================================
    # GARANTIR COLUNA
    # ========================================================

    def garantir_coluna(
        self,
        db,
        nome,
        definicao
    ):

        colunas = db.execute(
            "PRAGMA table_info(usuarios)"
        ).fetchall()

        existentes = {
            coluna["name"]
            for coluna in colunas
        }

        if nome in existentes:
            return

        db.execute(
            f"""
            ALTER TABLE usuarios
            ADD COLUMN {nome} {definicao}
            """
        )

    # ========================================================
    # INICIALIZAÇÃO
    # ========================================================

    def inicializar(
        self
    ):

        with self.conectar() as db:

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (

                    id INTEGER PRIMARY KEY,

                    carteira INTEGER NOT NULL DEFAULT 1000,

                    banco INTEGER NOT NULL DEFAULT 0,

                    xp INTEGER NOT NULL DEFAULT 0,

                    nivel INTEGER NOT NULL DEFAULT 1,

                    ultimo_diario TEXT,

                    ultimo_trabalho TEXT,

                    ultimo_desafio TEXT,

                    ultimo_quiz TEXT,

                    ultimo_reacao TEXT,

                    streak_diario INTEGER NOT NULL DEFAULT 0,

                    maior_streak_diario INTEGER NOT NULL DEFAULT 0,

                    total_ganho INTEGER NOT NULL DEFAULT 1000,

                    total_gasto INTEGER NOT NULL DEFAULT 0,

                    total_transferido INTEGER NOT NULL DEFAULT 0,

                    titulo TEXT NOT NULL DEFAULT 'Cidadão Royalt',

                    bio TEXT NOT NULL DEFAULT 'Ainda não defini uma bio.',

                    emoji TEXT NOT NULL DEFAULT '💰',

                    cor TEXT NOT NULL DEFAULT '#FFD700',

                    banner TEXT NOT NULL DEFAULT '',

                    tema TEXT NOT NULL DEFAULT 'dourado',

                    criado_em TEXT NOT NULL,

                    ultima_atividade TEXT NOT NULL
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS transacoes (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    usuario_id INTEGER NOT NULL,

                    tipo TEXT NOT NULL,

                    valor INTEGER NOT NULL,

                    descricao TEXT,

                    criado_em TEXT NOT NULL,

                    FOREIGN KEY(usuario_id)
                    REFERENCES usuarios(id)

                    ON DELETE CASCADE
                )
                """
            )

            db.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_transacoes_usuario

                ON transacoes(usuario_id)
                """
            )

            self.garantir_coluna(
                db,
                "ultimo_desafio",
                "TEXT"
            )

            self.garantir_coluna(
                db,
                "ultimo_quiz",
                "TEXT"
            )

            self.garantir_coluna(
                db,
                "ultimo_reacao",
                "TEXT"
            )

            self.garantir_coluna(
                db,
                "banner",
                "TEXT NOT NULL DEFAULT ''"
            )

            self.garantir_coluna(
                db,
                "tema",
                "TEXT NOT NULL DEFAULT 'dourado'"
            )

            self.garantir_coluna(
                db,
                "streak_diario",
                "INTEGER NOT NULL DEFAULT 0"
            )

            self.garantir_coluna(
                db,
                "maior_streak_diario",
                "INTEGER NOT NULL DEFAULT 0"
            )

            db.commit()

    # ========================================================
    # EXECUÇÃO ASYNC
    # ========================================================

    async def executar(
        self,
        func
    ):

        async with self.lock:

            return await asyncio.to_thread(
                func
            )

    # ========================================================
    # GARANTIR USUÁRIO
    # ========================================================

    def garantir_usuario(
        self,
        usuario_id
    ):

        uid = int(
            usuario_id
        )

        agora = agora_iso()

        with self.conectar() as db:

            db.execute(
                """
                INSERT OR IGNORE INTO usuarios (

                    id,
                    carteira,
                    banco,
                    xp,
                    nivel,
                    criado_em,
                    ultima_atividade

                )

                VALUES (

                    ?,
                    ?,
                    0,
                    0,
                    1,
                    ?,
                    ?

                )
                """,
                (
                    uid,
                    SALDO_INICIAL,
                    agora,
                    agora
                )
            )

            db.commit()

    # ========================================================
    # OBTER USUÁRIO
    # ========================================================

    def obter_usuario(
        self,
        usuario_id
    ):

        self.garantir_usuario(
            usuario_id
        )

        with self.conectar() as db:

            row = db.execute(
                """
                SELECT *
                FROM usuarios
                WHERE id = ?
                """,
                (
                    int(usuario_id),
                )
            ).fetchone()

        if row is None:
            return None

        return dict(
            row
        )

    # ========================================================
    # MIGRAÇÃO JSON
    # ========================================================

    def migrar_json_antigo(
        self
    ):

        if not ARQUIVO_JSON_ANTIGO.exists():
            return 0

        try:

            with open(
                ARQUIVO_JSON_ANTIGO,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(
                    arquivo
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            return 0

        if not isinstance(
            dados,
            dict
        ):

            return 0

        importados = 0

        with self.conectar() as db:

            for usuario_id, info in dados.items():

                if not str(
                    usuario_id
                ).isdigit():

                    continue

                if not isinstance(
                    info,
                    dict
                ):

                    continue

                try:

                    uid = int(
                        usuario_id
                    )

                    carteira = int(
                        info.get(
                            "carteira",
                            SALDO_INICIAL
                        )
                    )

                    banco = int(
                        info.get(
                            "banco",
                            0
                        )
                    )

                    xp = int(
                        info.get(
                            "xp",
                            0
                        )
                    )

                    nivel = int(
                        info.get(
                            "nivel",
                            calcular_nivel(
                                xp
                            )[0]
                        )
                    )

                    ultimo_diario = info.get(
                        "ultimo_diario"
                    )

                    ultimo_trabalho = info.get(
                        "ultimo_trabalho"
                    )

                    total_ganho = int(
                        info.get(
                            "total_ganho",
                            carteira
                        )
                    )

                    total_gasto = int(
                        info.get(
                            "total_gasto",
                            0
                        )
                    )

                    total_transferido = int(
                        info.get(
                            "total_transferido",
                            0
                        )
                    )

                    criado_em = info.get(
                        "criado_em",
                        agora_iso()
                    )

                    ultima_atividade = info.get(
                        "ultima_atividade",
                        agora_iso()
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                existe = db.execute(
                    """
                    SELECT id
                    FROM usuarios
                    WHERE id = ?
                    """,
                    (
                        uid,
                    )
                ).fetchone()

                if existe:
                    continue

                db.execute(
                    """
                    INSERT INTO usuarios (

                        id,
                        carteira,
                        banco,
                        xp,
                        nivel,
                        ultimo_diario,
                        ultimo_trabalho,
                        total_ganho,
                        total_gasto,
                        total_transferido,
                        criado_em,
                        ultima_atividade

                    )

                    VALUES (

                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?

                    )
                    """,
                    (
                        uid,
                        carteira,
                        banco,
                        xp,
                        nivel,
                        ultimo_diario,
                        ultimo_trabalho,
                        total_ganho,
                        total_gasto,
                        total_transferido,
                        criado_em,
                        ultima_atividade
                    )
                )

                importados += 1

            db.commit()

        if importados:

            print(
                "[ECONOMIA] "
                f"✅ {importados} usuário(s) "
                "migrado(s) para SQLite."
            )

        return importados

    # ========================================================
    # MOVER DINHEIRO
    # ========================================================

    async def mover_dinheiro(
        self,
        usuario_id,
        origem,
        destino,
        valor,
        tipo,
        descricao
    ):

        if origem not in {
            "carteira",
            "banco"
        }:

            return False

        if destino not in {
            "carteira",
            "banco"
        }:

            return False

        if origem == destino:
            return False

        valor = int(
            valor
        )

        if valor <= 0:
            return False

        uid = int(
            usuario_id
        )

        def operacao():

            self.garantir_usuario(
                uid
            )

            with self.conectar() as db:

                try:

                    db.execute(
                        "BEGIN IMMEDIATE"
                    )

                    row = db.execute(
                        f"""
                        SELECT {origem}
                        FROM usuarios
                        WHERE id = ?
                        """,
                        (
                            uid,
                        )
                    ).fetchone()

                    if row is None:

                        db.rollback()

                        return False

                    saldo = int(
                        row[origem]
                    )

                    if saldo < valor:

                        db.rollback()

                        return False

                    agora = agora_iso()

                    db.execute(
                        f"""
                        UPDATE usuarios

                        SET {origem} =
                            {origem} - ?,

                            {destino} =
                            {destino} + ?,

                            ultima_atividade = ?

                        WHERE id = ?
                        """,
                        (
                            valor,
                            valor,
                            agora,
                            uid
                        )
                    )

                    db.execute(
                        """
                        INSERT INTO transacoes (

                            usuario_id,
                            tipo,
                            valor,
                            descricao,
                            criado_em

                        )

                        VALUES (
                            ?, ?, ?, ?, ?
                        )
                        """,
                        (
                            uid,
                            tipo,
                            valor,
                            descricao,
                            agora
                        )
                    )

                    db.commit()

                    return True

                except Exception:

                    db.rollback()

                    raise

        return await self.executar(
            operacao
        )

    # ========================================================
    # TRANSFERÊNCIA
    # ========================================================

    async def transferir(
        self,
        origem_id,
        destino_id,
        valor
    ):

        origem_id = int(
            origem_id
        )

        destino_id = int(
            destino_id
        )

        valor = int(
            valor
        )

        if valor <= 0:
            return False

        if origem_id == destino_id:
            return False

        def operacao():

            self.garantir_usuario(
                origem_id
            )

            self.garantir_usuario(
                destino_id
            )

            with self.conectar() as db:

                try:

                    db.execute(
                        "BEGIN IMMEDIATE"
                    )

                    origem = db.execute(
                        """
                        SELECT carteira
                        FROM usuarios
                        WHERE id = ?
                        """,
                        (
                            origem_id,
                        )
                    ).fetchone()

                    if origem is None:

                        db.rollback()

                        return False

                    if int(
                        origem["carteira"]
                    ) < valor:

                        db.rollback()

                        return False

                    agora = agora_iso()

                    db.execute(
                        """
                        UPDATE usuarios

                        SET carteira =
                            carteira - ?,

                            total_gasto =
                            total_gasto + ?,

                            total_transferido =
                            total_transferido + ?,

                            ultima_atividade = ?

                        WHERE id = ?
                        """,
                        (
                            valor,
                            valor,
                            valor,
                            agora,
                            origem_id
                        )
                    )

                    db.execute(
                        """
                        UPDATE usuarios

                        SET carteira =
                            carteira + ?,

                            total_ganho =
                            total_ganho + ?,

                            ultima_atividade = ?

                        WHERE id = ?
                        """,
                        (
                            valor,
                            valor,
                            agora,
                            destino_id
                        )
                    )

                    db.execute(
                        """
                        INSERT INTO transacoes (

                            usuario_id,
                            tipo,
                            valor,
                            descricao,
                            criado_em

                        )

                        VALUES (

                            ?,
                            'transferencia_saida',
                            ?,
                            ?,
                            ?

                        )
                        """,
                        (
                            origem_id,
                            -valor,
                            f"Transferência para {destino_id}",
                            agora
                        )
                    )

                    db.execute(
                        """
                        INSERT INTO transacoes (

                            usuario_id,
                            tipo,
                            valor,
                            descricao,
                            criado_em

                        )

                        VALUES (

                            ?,
                            'transferencia_entrada',
                            ?,
                            ?,
                            ?

                        )
                        """,
                        (
                            destino_id,
                            valor,
                            f"Transferência de {origem_id}",
                            agora
                        )
                    )

                    db.commit()

                    return True

                except Exception:

                    db.rollback()

                    raise

        return await self.executar(
            operacao
        )

    # ========================================================
    # DAILY
    # ========================================================

    async def receber_diario(
        self,
        usuario_id
    ):

        uid = int(
            usuario_id
        )

        def operacao():

            self.garantir_usuario(
                uid
            )

            agora = datetime.now(
                timezone.utc
            )

            with self.conectar() as db:

                try:

                    db.execute(
                        "BEGIN IMMEDIATE"
                    )

                    row = db.execute(
                        """
                        SELECT

                            carteira,
                            xp,
                            nivel,
                            ultimo_diario,
                            streak_diario,
                            maior_streak_diario

                        FROM usuarios

                        WHERE id = ?
                        """,
                        (
                            uid,
                        )
                    ).fetchone()

                    if row is None:

                        db.rollback()

                        return {
                            "sucesso": False
                        }

                    ultima = row[
                        "ultimo_diario"
                    ]

                    streak = int(
                        row[
                            "streak_diario"
                        ]
                    )

                    if ultima:

                        try:

                            ultima_dt = (
                                datetime.fromisoformat(
                                    ultima
                                )
                            )

                            segundos = (
                                agora
                                - ultima_dt
                            ).total_seconds()

                        except (
                            ValueError,
                            TypeError
                        ):

                            segundos = (
                                COOLDOWN_DIARIO + 1
                            )

                        if segundos < (
                            COOLDOWN_DIARIO
                        ):

                            db.rollback()

                            return {
                                "sucesso": False,
                                "restante": int(
                                    COOLDOWN_DIARIO
                                    - segundos
                                )
                            }

                        if segundos <= (
                            COOLDOWN_DIARIO * 2
                        ):

                            streak += 1

                        else:

                            streak = 1

                    else:

                        streak = 1

                    streak = min(
                        streak,
                        MAX_STREAK_DAILY
                    )

                    base = random.randint(
                        DIARIO_MINIMO,
                        DIARIO_MAXIMO
                    )

                    bonus = min(
                        streak * 50,
                        1500
                    )

                    valor = (
                        base
                        + bonus
                    )

                    xp = random.randint(
                        XP_DIARIO_MINIMO,
                        XP_DIARIO_MAXIMO
                    )

                    xp_antigo = int(
                        row["xp"]
                    )

                    nivel_antigo = int(
                        row["nivel"]
                    )

                    novo_xp = (
                        xp_antigo
                        + xp
                    )

                    nivel_novo = (
                        calcular_nivel(
                            novo_xp
                        )[0]
                    )

                    agora_texto = (
                        agora.isoformat()
                    )

                    db.execute(
                        """
                        UPDATE usuarios

                        SET carteira =
                            carteira + ?,

                            xp =
                            xp + ?,

                            nivel = ?,

                            ultimo_diario = ?,

                            streak_diario = ?,

                            maior_streak_diario =
                            MAX(
                                maior_streak_diario,
                                ?
                            ),

                            total_ganho =
                            total_ganho + ?,

                            ultima_atividade = ?

                        WHERE id = ?
                        """,
                        (
                            valor,
                            xp,
                            nivel_novo,
                            agora_texto,
                            streak,
                            streak,
                            valor,
                            agora_texto,
                            uid
                        )
                    )

                    db.execute(
                        """
                        INSERT INTO transacoes (

                            usuario_id,
                            tipo,
                            valor,
                            descricao,
                            criado_em

                        )

                        VALUES (

                            ?,
                            'diario',
                            ?,
                            ?,
                            ?

                        )
                        """,
                        (
                            uid,
                            valor,
                            f"Daily • Streak {streak}",
                            agora_texto
                        )
                    )

                    db.commit()

                    return {

                        "sucesso": True,

                        "valor": valor,

                        "base": base,

                        "bonus": bonus,

                        "xp": xp,

                        "streak": streak,

                        "nivel_antes":
                            nivel_antigo,

                        "nivel_depois":
                            nivel_novo
                    }

                except Exception:

                    db.rollback()

                    raise

        return await self.executar(
            operacao
        )

    # ========================================================
    # TRABALHO
    # ========================================================

    async def registrar_trabalho(
        self,
        usuario_id,
        valor,
        xp,
        nome_trabalho
    ):

        uid = int(
            usuario_id
        )

        valor = int(
            valor
        )

        xp = int(
            xp
        )

        def operacao():

            self.garantir_usuario(
                uid
            )

            with self.conectar() as db:

                try:

                    db.execute(
                        "BEGIN IMMEDIATE"
                    )

                    row = db.execute(
                        """
                        SELECT
                            xp,
                            nivel

                        FROM usuarios

                        WHERE id = ?
                        """,
                        (
                            uid,
                        )
                    ).fetchone()

                    if row is None:

                        db.rollback()

                        return None

                    nivel_antigo = int(
                        row["nivel"]
                    )

                    novo_xp = (
                        int(
                            row["xp"]
                        )
                        + xp
                    )

                    nivel_novo = (
                        calcular_nivel(
                            novo_xp
                        )[0]
                    )

                    agora = agora_iso()

                    db.execute(
                        """
                        UPDATE usuarios

                        SET carteira =
                            carteira + ?,

                            xp =
                            xp + ?,

                            nivel = ?,

                            ultimo_trabalho = ?,

                            total_ganho =
                            total_ganho + ?,

                            ultima_atividade = ?

                        WHERE id = ?
                        """,
                        (
                            valor,
                            xp,
                            nivel_novo,
                            agora,
                            valor,
                            agora,
                            uid
                        )
                    )

                    db.execute(
                        """
                        INSERT INTO transacoes (

                            usuario_id,
                            tipo,
                            valor,
                            descricao,
                            criado_em

                        )

                        VALUES (

                            ?,
                            'trabalho',
                            ?,
                            ?,
                            ?

                        )
                        """,
                        (
                            uid,
                            valor,
                            nome_trabalho,
                            agora
                        )
                    )

                    db.commit()

                    return {

                        "nivel_antes":
                            nivel_antigo,

                        "nivel_depois":
                            nivel_novo
                    }

                except Exception:

                    db.rollback()

                    raise

        return await self.executar(
            operacao
        )

    # ========================================================
    # RECOMPENSA
    # ========================================================

    async def registrar_recompensa(
        self,
        usuario_id,
        valor,
        xp,
        tipo,
        descricao
    ):

        uid = int(
            usuario_id
        )

        valor = int(
            valor
        )

        xp = int(
            xp
        )

        if valor < 0 or xp < 0:
            return None

        def operacao():

            self.garantir_usuario(
                uid
            )

            with self.conectar() as db:

                try:

                    db.execute(
                        "BEGIN IMMEDIATE"
                    )

                    row = db.execute(
                        """
                        SELECT xp, nivel
                        FROM usuarios
                        WHERE id = ?
                        """,
                        (
                            uid,
                        )
                    ).fetchone()

                    if row is None:

                        db.rollback()

                        return None

                    nivel_antes = int(
                        row["nivel"]
                    )

                    novo_xp = (
                        int(
                            row["xp"]
                        )
                        + xp
                    )

                    nivel_depois = (
                        calcular_nivel(
                            novo_xp
                        )[0]
                    )

                    agora = agora_iso()

                    db.execute(
                        """
                        UPDATE usuarios

                        SET carteira =
                            carteira + ?,

                            xp =
                            xp + ?,

                            nivel = ?,

                            total_ganho =
                            total_ganho + ?,

                            ultima_atividade = ?

                        WHERE id = ?
                        """,
                        (
                            valor,
                            xp,
                            nivel_depois,
                            valor,
                            agora,
                            uid
                        )
                    )

                    db.execute(
                        """
                        INSERT INTO transacoes (

                            usuario_id,
                            tipo,
                            valor,
                            descricao,
                            criado_em

                        )

                        VALUES (
                            ?, ?, ?, ?, ?
                        )
                        """,
                        (
                            uid,
                            tipo,
                            valor,
                            descricao,
                            agora
                        )
                    )

                    db.commit()

                    return {

                        "nivel_antes":
                            nivel_antes,

                        "nivel_depois":
                            nivel_depois
                    }

                except Exception:

                    db.rollback()

                    raise

        return await self.executar(
            operacao
        )

    # ========================================================
    # COOLDOWNS
    # ========================================================

    async def salvar_cooldown(
        self,
        usuario_id,
        campo
    ):

        permitidos = {

            "ultimo_desafio",
            "ultimo_quiz",
            "ultimo_reacao"
        }

        if campo not in permitidos:
            return

        uid = int(
            usuario_id
        )

        def operacao():

            self.garantir_usuario(
                uid
            )

            agora = agora_iso()

            with self.conectar() as db:

                db.execute(
                    f"""
                    UPDATE usuarios

                    SET {campo} = ?,
                        ultima_atividade = ?

                    WHERE id = ?
                    """,
                    (
                        agora,
                        agora,
                        uid
                    )
                )

                db.commit()

        await self.executar(
            operacao
        )

    # ========================================================
    # PERSONALIZAÇÃO
    # ========================================================

    async def atualizar_perfil(
        self,
        usuario_id,
        titulo,
        bio,
        emoji,
        cor,
        banner
    ):

        uid = int(
            usuario_id
        )

        def operacao():

            self.garantir_usuario(
                uid
            )

            with self.conectar() as db:

                db.execute(
                    """
                    UPDATE usuarios

                    SET titulo = ?,

                        bio = ?,

                        emoji = ?,

                        cor = ?,

                        banner = ?,

                        tema = 'personalizado',

                        ultima_atividade = ?

                    WHERE id = ?
                    """,
                    (
                        titulo,
                        bio,
                        emoji,
                        cor,
                        banner,
                        agora_iso(),
                        uid
                    )
                )

                db.commit()

        await self.executar(
            operacao
        )

    # ========================================================
    # TEMA
    # ========================================================

    async def definir_tema(
        self,
        usuario_id,
        tema
    ):

        if tema not in TEMAS:
            return False

        config = TEMAS[
            tema
        ]

        def operacao():

            self.garantir_usuario(
                usuario_id
            )

            with self.conectar() as db:

                db.execute(
                    """
                    UPDATE usuarios

                    SET tema = ?,

                        cor = ?,

                        emoji = ?,

                        banner = ?,

                        ultima_atividade = ?

                    WHERE id = ?
                    """,
                    (
                        tema,
                        config["cor"],
                        config["emoji"],
                        config["banner"],
                        agora_iso(),
                        int(usuario_id)
                    )
                )

                db.commit()

                return True

        return await self.executar(
            operacao
        )


# ============================================================
# FUNÇÃO PARA RESPONDER CONTEXT / INTERACTION
# ============================================================

async def responder(
    origem,
    *,
    content=None,
    embed=None,
    view=None,
    ephemeral=False,
    file=None
):
    """
    Responde de forma compatível com:

        commands.Context
        discord.Interaction

    Isso evita o erro:
        Context has no attribute user

    e também evita:
        InteractionResponded
    """

    if isinstance(
        origem,
        discord.Interaction
    ):

        if origem.response.is_done():

            return await origem.followup.send(
                content=content,
                embed=embed,
                view=view,
                ephemeral=ephemeral,
                file=file
            )

        return await origem.response.send_message(
            content=content,
            embed=embed,
            view=view,
            ephemeral=ephemeral,
            file=file
        )

    return await origem.send(
        content=content,
        embed=embed,
        view=view,
        file=file
    )


# ============================================================
# PERSONALIZAÇÃO
# ============================================================

class PersonalizarPerfilModal(
    discord.ui.Modal,
    title="🎨 Personalizar Perfil"
):

    titulo = discord.ui.TextInput(
        label="Título",
        placeholder="Ex.: Magnata do Royalt",
        max_length=40,
        required=True
    )

    bio = discord.ui.TextInput(
        label="Bio",
        placeholder="Escreva algo sobre você...",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=True
    )

    emoji = discord.ui.TextInput(
        label="Emoji",
        placeholder="Ex.: 💎",
        max_length=8,
        required=True
    )

    cor = discord.ui.TextInput(
        label="Cor",
        placeholder="dourado, roxo, rosa, azul...",
        max_length=20,
        required=True
    )

    banner = discord.ui.TextInput(
        label="Banner",
        placeholder="https://...",
        max_length=500,
        required=False
    )

    def __init__(
        self,
        cog
    ):

        super().__init__()

        self.cog = cog

    async def on_submit(
        self,
        interaction
    ):

        cor_nome = (
            self.cor.value
            .strip()
            .lower()
        )

        cor = (
            CORES_PERFIL.get(
                cor_nome
            )
        )

        if cor is None:

            await responder(
                interaction,
                embed=discord.Embed(
                    title="❌ COR INVÁLIDA",
                    description=(
                        "Use uma destas cores:\n\n"
                        +
                        "\n".join(
                            f"• {nome}"
                            for nome in CORES_PERFIL
                        )
                    ),
                    color=CORES["vermelho"]
                ),
                ephemeral=True
            )

            return

        banner = (
            self.banner.value
            .strip()
        )

        if banner:

            if not (
                banner.startswith("http://")
                or
                banner.startswith("https://")
            ):

                await responder(
                    interaction,
                    content=(
                        "❌ O banner precisa ser "
                        "uma URL HTTP ou HTTPS."
                    ),
                    ephemeral=True
                )

                return

        titulo = (
            self.titulo.value.strip()
            or
            "Cidadão Royalt"
        )

        bio = (
            self.bio.value.strip()
            or
            "Ainda não defini uma bio."
        )

        emoji = emoji_seguro(
            self.emoji.value,
            "💰"
        )

        await self.cog.banco.atualizar_perfil(
            interaction.user.id,
            titulo,
            bio,
            emoji,
            cor,
            banner
        )

        await responder(
            interaction,
            embed=discord.Embed(
                title="✅ PERFIL ATUALIZADO",
                description=(
                    "Sua personalização foi salva "
                    "com sucesso! 🎨"
                ),
                color=cor_do_hex(
                    cor
                )
            ),
            ephemeral=True
        )


# ============================================================
# VIEW TEMAS
# ============================================================

class TemasView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        usuario_id
    ):

        super().__init__(
            timeout=180
        )

        self.cog = cog

        self.usuario_id = int(
            usuario_id
        )

        self.montar_botoes()

    async def interaction_check(
        self,
        interaction
    ):

        if (
            interaction.user.id
            != self.usuario_id
        ):

            await responder(
                interaction,
                content=(
                    "❌ Você não pode alterar "
                    "o tema de outra pessoa."
                ),
                ephemeral=True
            )

            return False

        return True

    def montar_botoes(
        self
    ):

        for indice, (
            chave,
            tema
        ) in enumerate(
            TEMAS.items()
        ):

            botao = discord.ui.Button(
                label=tema["nome"],
                emoji=tema["emoji"],
                style=discord.ButtonStyle.primary,
                row=min(
                    indice // 2,
                    4
                )
            )

            async def callback(
                interaction,
                chave=chave
            ):

                sucesso = (
                    await self.cog.banco.definir_tema(
                        interaction.user.id,
                        chave
                    )
                )

                if not sucesso:

                    await responder(
                        interaction,
                        content=(
                            "❌ Não foi possível aplicar "
                            "o tema."
                        ),
                        ephemeral=True
                    )

                    return

                await responder(
                    interaction,
                    embed=discord.Embed(
                        title="✅ TEMA APLICADO",
                        description=(
                            f"O tema "
                            f"**{TEMAS[chave]['nome']}** "
                            "foi aplicado ao seu perfil."
                        ),
                        color=cor_do_hex(
                            TEMAS[chave]["cor"]
                        )
                    ),
                    ephemeral=True
                )

            botao.callback = callback

            self.add_item(
                botao
            )


# ============================================================
# VIEW DO PERFIL
# ============================================================

class EconomiaPerfilView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        usuario_id
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog

        self.usuario_id = int(
            usuario_id
        )

    async def interaction_check(
        self,
        interaction
    ):

        if (
            interaction.user.id
            !=
            self.usuario_id
        ):

            await responder(
                interaction,
                content=(
                    "❌ Este painel pertence "
                    "a outra pessoa."
                ),
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # ATUALIZAR
    # ========================================================

    @discord.ui.button(
        label="Atualizar",
        emoji="🔄",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def atualizar(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_perfil(
                interaction.user
            ),
            view=self
        )

    # ========================================================
    # PERSONALIZAR
    # ========================================================

    @discord.ui.button(
        label="Personalizar",
        emoji="🎨",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def personalizar(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            PersonalizarPerfilModal(
                self.cog
            )
        )

    # ========================================================
    # DAILY
    # ========================================================

    @discord.ui.button(
        label="Daily",
        emoji="🎁",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def daily(
        self,
        interaction,
        button
    ):

        await self.cog.executar_daily(
            interaction
        )

    # ========================================================
    # TRABALHAR
    # ========================================================

    @discord.ui.button(
        label="Trabalhar",
        emoji="💼",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def trabalhar(
        self,
        interaction,
        button
    ):

        await self.cog.executar_trabalho(
            interaction
        )

    # ========================================================
    # TEMAS
    # ========================================================

    @discord.ui.button(
        label="Temas",
        emoji="🖼️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def temas(
        self,
        interaction,
        button
    ):

        await responder(
            interaction,
            embed=self.cog.criar_embed_temas(),
            view=TemasView(
                self.cog,
                interaction.user.id
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
            content="💰 Painel fechado.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# RANKING VISUAL
# ============================================================

async def gerar_banner_ranking(
    membros_ranking,
    pagina,
    total_paginas,
    usuario_destaque_id=None
):

    largura = 1600
    altura = 900

    imagem = Image.new(
        "RGB",
        (
            largura,
            altura
        ),
        (18, 18, 28)
    )

    draw = ImageDraw.Draw(
        imagem
    )

    # ========================================================
    # FONTES
    # ========================================================

    def carregar_fonte(
        tamanho
    ):

        caminhos = [

            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]

        for caminho in caminhos:

            try:

                return ImageFont.truetype(
                    caminho,
                    tamanho
                )

            except OSError:
                pass

        return ImageFont.load_default()

    fonte_titulo = carregar_fonte(
        60
    )

    fonte_nome = carregar_fonte(
        36
    )

    fonte_info = carregar_fonte(
        25
    )

    fonte_posicao = carregar_fonte(
        38
    )

    fonte_pequena = carregar_fonte(
        22
    )

    # ========================================================
    # CABEÇALHO
    # ========================================================

    draw.text(
        (
            60,
            45
        ),
        "ROYALT • RANKING ECONÔMICO",
        font=fonte_titulo,
        fill=(255, 215, 0)
    )

    draw.text(
        (
            62,
            125
        ),
        f"Página {pagina}/{total_paginas}",
        font=fonte_info,
        fill=(180, 180, 190)
    )

    draw.line(
        (
            50,
            185,
            largura - 50,
            185
        ),
        fill=(255, 215, 0),
        width=4
    )

    # ========================================================
    # LINHAS
    # ========================================================

    altura_linha = 125
    inicio_y = 215

    for indice, item in enumerate(
        membros_ranking
    ):

        posicao = item[
            "posicao"
        ]

        membro = item[
            "membro"
        ]

        patrimonio = int(
            item["patrimonio"]
        )

        y = (
            inicio_y
            +
            indice * altura_linha
        )

        destaque = (
            usuario_destaque_id is not None
            and
            membro.id == usuario_destaque_id
        )

        # ----------------------------------------------------
        # Fundo
        # ----------------------------------------------------

        if destaque:

            fundo = (
                70,
                60,
                20
            )

        elif posicao <= 3:

            fundo = (
                48,
                48,
                62
            )

        else:

            fundo = (
                30,
                30,
                43
            )

        draw.rounded_rectangle(
            (
                45,
                y,
                largura - 45,
                y + 105
            ),
            radius=20,
            fill=fundo
        )

        # ----------------------------------------------------
        # Destaque
        # ----------------------------------------------------

        if destaque:

            draw.rounded_rectangle(
                (
                    45,
                    y,
                    largura - 45,
                    y + 105
                ),
                radius=20,
                outline=(255, 215, 0),
                width=4
            )

        # ----------------------------------------------------
        # Posição
        # ----------------------------------------------------

        if posicao == 1:

            texto_posicao = "🥇"

        elif posicao == 2:

            texto_posicao = "🥈"

        elif posicao == 3:

            texto_posicao = "🥉"

        else:

            texto_posicao = f"#{posicao}"

        draw.text(
            (
                72,
                y + 31
            ),
            texto_posicao,
            font=fonte_posicao,
            fill=(255, 255, 255)
        )

        # ----------------------------------------------------
        # Avatar
        # ----------------------------------------------------

        try:

            avatar_bytes = await (
                membro.display_avatar.read()
            )

            avatar = Image.open(
                io.BytesIO(
                    avatar_bytes
                )
            ).convert(
                "RGBA"
            )

            avatar = avatar.resize(
                (
                    80,
                    80
                )
            )

            mascara = Image.new(
                "L",
                (
                    80,
                    80
                ),
                0
            )

            mascara_draw = ImageDraw.Draw(
                mascara
            )

            mascara_draw.ellipse(
                (
                    0,
                    0,
                    80,
                    80
                ),
                fill=255
            )

            avatar_final = Image.new(
                "RGBA",
                (
                    80,
                    80
                ),
                (0, 0, 0, 0)
            )

            avatar_final.paste(
                avatar,
                (
                    0,
                    0
                ),
                mascara
            )

            imagem.paste(
                avatar_final,
                (
                    185,
                    y + 12
                ),
                avatar_final
            )

        except Exception:

            draw.ellipse(
                (
                    185,
                    y + 12,
                    265,
                    y + 92
                ),
                fill=(80, 80, 95)
            )

        # ----------------------------------------------------
        # Nome
        # ----------------------------------------------------

        nome = (
            membro.display_name
            or
            membro.name
            or
            "Usuário"
        )

        if len(nome) > 27:

            nome = (
                nome[:24]
                + "..."
            )

        draw.text(
            (
                300,
                y + 18
            ),
            nome,
            font=fonte_nome,
            fill=(255, 255, 255)
        )

        # ----------------------------------------------------
        # Patrimônio
        # ----------------------------------------------------

        draw.text(
            (
                300,
                y + 67
            ),
            (
                f"{formatar_moedas(patrimonio)} RC"
            ),
            font=fonte_info,
            fill=(255, 215, 0)
        )

        # ----------------------------------------------------
        # VOCÊ
        # ----------------------------------------------------

        if destaque:

            draw.text(
                (
                    1100,
                    y + 38
                ),
                "VOCÊ",
                font=fonte_pequena,
                fill=(255, 215, 0)
            )

        # ----------------------------------------------------
        # POSIÇÃO DIREITA
        # ----------------------------------------------------

        draw.text(
            (
                1370,
                y + 34
            ),
            f"#{posicao}",
            font=fonte_posicao,
            fill=(180, 180, 190)
        )

    # ========================================================
    # RODAPÉ
    # ========================================================

    draw.line(
        (
            50,
            altura - 95,
            largura - 50,
            altura - 95
        ),
        fill=(60, 60, 80),
        width=2
    )

    draw.text(
        (
            60,
            altura - 70
        ),
        "Royalt Economy System",
        font=fonte_pequena,
        fill=(160, 160, 175)
    )

    draw.text(
        (
            largura - 360,
            altura - 70
        ),
        f"{pagina}/{total_paginas}",
        font=fonte_pequena,
        fill=(255, 215, 0)
    )

    # ========================================================
    # EXPORTAR
    # ========================================================

    buffer = io.BytesIO()

    imagem.save(
        buffer,
        format="PNG"
    )

    buffer.seek(
        0
    )

    return buffer


# ============================================================
# VIEW DO RANKING
# ============================================================

class RankingEconomiaView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        autor_id,
        ranking,
        pagina=1,
        por_pagina=5
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog

        self.autor_id = int(
            autor_id
        )

        self.ranking = ranking

        self.pagina = int(
            pagina
        )

        self.por_pagina = int(
            por_pagina
        )

        self.total_paginas = max(
            1,
            math.ceil(
                len(ranking)
                /
                self.por_pagina
            )
        )

        self.atualizar_botoes()

    # ========================================================
    # SEGURANÇA
    # ========================================================

    async def interaction_check(
        self,
        interaction
    ):

        if (
            interaction.user.id
            != self.autor_id
        ):

            await responder(
                interaction,
                content=(
                    "❌ Apenas quem abriu "
                    "este ranking pode navegar."
                ),
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # BOTÕES
    # ========================================================

    def atualizar_botoes(
        self
    ):

        self.anterior.disabled = (
            self.pagina <= 1
        )

        self.proximo.disabled = (
            self.pagina >= self.total_paginas
        )

    # ========================================================
    # PAGINA
    # ========================================================

    def itens_pagina(
        self
    ):

        inicio = (
            (
                self.pagina
                - 1
            )
            *
            self.por_pagina
        )

        fim = (
            inicio
            +
            self.por_pagina
        )

        return self.ranking[
            inicio:fim
        ]

    # ========================================================
    # GERAR
    # ========================================================

    async def gerar_pagina(
        self
    ):

        itens = (
            self.itens_pagina()
        )

        inicio = (
            (
                self.pagina
                - 1
            )
            *
            self.por_pagina
        )

        membros = []

        for indice, item in enumerate(
            itens,
            start=inicio + 1
        ):

            membro = item[
                "membro"
            ]

            if membro is None:
                continue

            membros.append(
                {
                    "posicao": indice,

                    "membro": membro,

                    "patrimonio": int(
                        item["patrimonio"]
                    )
                }
            )

        imagem = (
            await gerar_banner_ranking(
                membros,
                self.pagina,
                self.total_paginas,
                self.autor_id
            )
        )

        arquivo = discord.File(
            imagem,
            filename="ranking_economia.png"
        )

        embed = discord.Embed(
            title="🏆 ROYALT • RANKING ECONÔMICO",
            description=(
                f"Página **{self.pagina}/{self.total_paginas}**\n\n"
                "💰 Maiores patrimônios do servidor.\n"
                "👑 Seu perfil é destacado quando aparece."
            ),
            color=CORES["dourado"]
        )

        embed.set_image(
            url="attachment://ranking_economia.png"
        )

        embed.set_footer(
            text="◀️ Anterior • ▶️ Próxima"
        )

        return (
            embed,
            arquivo
        )

    # ========================================================
    # ANTERIOR
    # ========================================================

    @discord.ui.button(
        label="Anterior",
        emoji="◀️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def anterior(
        self,
        interaction,
        button
    ):

        if self.pagina <= 1:
            return

        self.pagina -= 1

        self.atualizar_botoes()

        embed, arquivo = (
            await self.gerar_pagina()
        )

        await interaction.response.edit_message(
            embed=embed,
            attachments=[
                arquivo
            ],
            view=self
        )

    # ========================================================
    # PAGINA ATUAL
    # ========================================================

    @discord.ui.button(
        label="Página",
        emoji="📖",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def pagina_atual(
        self,
        interaction,
        button
    ):

        await responder(
            interaction,
            content=(
                f"📖 Você está na página "
                f"**{self.pagina}/{self.total_paginas}**."
            ),
            ephemeral=True
        )

    # ========================================================
    # PRÓXIMA
    # ========================================================

    @discord.ui.button(
        label="Próxima",
        emoji="▶️",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def proximo(
        self,
        interaction,
        button
    ):

        if self.pagina >= self.total_paginas:
            return

        self.pagina += 1

        self.atualizar_botoes()

        embed, arquivo = (
            await self.gerar_pagina()
        )

        await interaction.response.edit_message(
            embed=embed,
            attachments=[
                arquivo
            ],
            view=self
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
            content="🏆 Ranking fechado.",
            embed=None,
            attachments=[],
            view=None
        )

        self.stop()


# ============================================================
# COG ECONOMIA
# ============================================================

class Economia(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.banco = BancoEconomia(
            BANCO_SQLITE
        )

        self.banco.migrar_json_antigo()

    # ========================================================
    # TRABALHOS
    # ========================================================

    def trabalhos_desbloqueados(
        self,
        nivel
    ):

        return [
            trabalho
            for trabalho in TRABALHOS
            if trabalho["level"] <= int(
                nivel
            )
        ]

    # ========================================================
    # MELHOR TRABALHO
    # ========================================================

    def trabalho_maximo(
        self,
        nivel
    ):

        trabalhos = (
            self.trabalhos_desbloqueados(
                nivel
            )
        )

        if not trabalhos:
            return TRABALHOS[0]

        return max(
            trabalhos,
            key=lambda item:
            item["level"]
        )

    # ========================================================
    # TEMPO
    # ========================================================

    def formatar_tempo(
        self,
        segundos
    ):

        segundos = max(
            0,
            int(segundos)
        )

        horas, resto = divmod(
            segundos,
            3600
        )

        minutos, segundos = divmod(
            resto,
            60
        )

        partes = []

        if horas:
            partes.append(
                f"{horas}h"
            )

        if minutos:
            partes.append(
                f"{minutos}min"
            )

        if segundos and not horas:
            partes.append(
                f"{segundos}s"
            )

        return (
            " ".join(partes)
            if partes
            else "agora"
        )

    # ========================================================
    # COOLDOWN
    # ========================================================

    def segundos_cooldown(
        self,
        data,
        cooldown
    ):

        if not data:
            return 0

        try:

            ultima = datetime.fromisoformat(
                data
            )

            passado = (
                datetime.now(
                    timezone.utc
                )
                - ultima
            ).total_seconds()

            return max(
                0,
                int(
                    cooldown
                    - passado
                )
            )

        except (
            ValueError,
            TypeError
        ):

            return 0

    # ========================================================
    # PERFIL
    # ========================================================

    def criar_embed_perfil(
        self,
        membro
    ):

        usuario = (
            self.banco.obter_usuario(
                membro.id
            )
        )

        if usuario is None:

            return discord.Embed(
                title="❌ ERRO",
                description=(
                    "Não foi possível carregar "
                    "o perfil."
                ),
                color=CORES["vermelho"]
            )

        nivel, xp_atual, xp_proximo = (
            calcular_nivel(
                usuario["xp"]
            )
        )

        carteira = int(
            usuario["carteira"]
        )

        banco = int(
            usuario["banco"]
        )

        patrimonio = (
            carteira
            + banco
        )

        trabalho = (
            self.trabalho_maximo(
                nivel
            )
        )

        cor = cor_do_hex(
            usuario.get(
                "cor",
                "#FFD700"
            )
        )

        tema_nome = (
            usuario.get(
                "tema",
                "dourado"
            )
        )

        tema = TEMAS.get(
            tema_nome
        )

        embed = discord.Embed(

            title=(
                f"{emoji_seguro(usuario.get('emoji'), '💰')} "
                f"{usuario.get('titulo', 'Cidadão Royalt')}"
            ),

            description=(

                f"## {membro.display_name}\n\n"

                f"💬 **{usuario.get('bio', '')}**\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                f"💳 **Carteira**\n"
                f"**{formatar_moedas(carteira)} RC**\n\n"

                f"🏦 **Banco**\n"
                f"**{formatar_moedas(banco)} RC**\n\n"

                f"💎 **Patrimônio**\n"
                f"**{formatar_moedas(patrimonio)} RC**"
            ),

            color=cor
        )

        embed.add_field(
            name="⭐ Nível",
            value=f"**{nivel}**",
            inline=True
        )

        embed.add_field(
            name="✨ XP",
            value=(
                f"**{xp_atual}/{xp_proximo}**\n"
                f"{barra_progresso(xp_atual, xp_proximo)}"
            ),
            inline=True
        )

        embed.add_field(
            name="🔥 Daily",
            value=(
                f"**{usuario['streak_diario']} dias**\n"
                f"Recorde: "
                f"**{usuario['maior_streak_diario']}**"
            ),
            inline=True
        )

        embed.add_field(
            name="💼 Profissão",
            value=(
                f"{trabalho['emoji']} "
                f"**{trabalho['nome']}**\n"
                f"⭐ Nível "
                f"{trabalho['level']}"
            ),
            inline=True
        )

        embed.add_field(
            name="💰 Salário",
            value=(
                f"**{formatar_moedas(trabalho['minimo'])}"
                f"–"
                f"{formatar_moedas(trabalho['maximo'])} RC**"
            ),
            inline=True
        )

        embed.add_field(
            name="🖼️ Tema",
            value=(
                tema["nome"]
                if tema
                else "Personalizado"
            ),
            inline=True
        )

        embed.add_field(
            name="📈 Total ganho",
            value=(
                f"**{formatar_moedas(usuario['total_ganho'])} RC**"
            ),
            inline=True
        )

        embed.add_field(
            name="💸 Total gasto",
            value=(
                f"**{formatar_moedas(usuario['total_gasto'])} RC**"
            ),
            inline=True
        )

        embed.add_field(
            name="🤝 Transferido",
            value=(
                f"**{formatar_moedas(usuario['total_transferido'])} RC**"
            ),
            inline=True
        )

        banner = (
            usuario.get(
                "banner",
                ""
            )
            or
            (
                tema["banner"]
                if tema
                else ""
            )
        )

        if banner:

            embed.set_image(
                url=banner
            )

        embed.set_thumbnail(
            url=membro.display_avatar.url
        )

        embed.set_footer(
            text=(
                f"{NOME_SISTEMA} • "
                f"v{VERSAO}"
            )
        )

        return embed

    # ========================================================
    # TEMAS
    # ========================================================

    def criar_embed_temas(
        self
    ):

        embed = discord.Embed(
            title="🖼️ ROYALT • TEMAS",
            description=(
                "Escolha um tema para "
                "personalizar o perfil."
            ),
            color=CORES["roxo"]
        )

        for chave, tema in TEMAS.items():

            embed.add_field(
                name=(
                    f"{tema['emoji']} "
                    f"{tema['nome']}"
                ),
                value=(
                    f"🎨 `{chave}`\n"
                    f"🔹 `{tema['cor']}`"
                ),
                inline=True
            )

        return embed

    # ========================================================
    # DAILY
    # ========================================================

    async def executar_daily(
        self,
        origem
    ):

        membro = (
            origem.user
            if isinstance(
                origem,
                discord.Interaction
            )
            else
            origem.author
        )

        resultado = (
            await self.banco.receber_diario(
                membro.id
            )
        )

        if not resultado.get(
            "sucesso"
        ):

            restante = resultado.get(
                "restante",
                0
            )

            embed = discord.Embed(
                title="⏳ DAILY EM COOLDOWN",
                description=(
                    f"{membro.mention}, "
                    "você já coletou sua recompensa.\n\n"
                    f"⏰ Volte em "
                    f"**{self.formatar_tempo(restante)}**."
                ),
                color=CORES["amarelo"]
            )

            await responder(
                origem,
                embed=embed,
                ephemeral=isinstance(
                    origem,
                    discord.Interaction
                )
            )

            return

        nivel_texto = ""

        if (
            resultado["nivel_depois"]
            >
            resultado["nivel_antes"]
        ):

            nivel_texto = (
                f"\n\n🎉 **VOCÊ SUBIU PARA "
                f"O NÍVEL "
                f"{resultado['nivel_depois']}!**"
            )

        embed = discord.Embed(
            title="🎁 DAILY RECEBIDA",
            description=(
                f"{membro.mention}, "
                "o cofre diário foi aberto! 🪙\n\n"

                f"💰 Base: "
                f"**+{formatar_moedas(resultado['base'])} RC**\n"

                f"🔥 Bônus do streak: "
                f"**+{formatar_moedas(resultado['bonus'])} RC**\n\n"

                f"🪙 **Total:** "
                f"**+{formatar_moedas(resultado['valor'])} RC**\n\n"

                f"✨ XP: "
                f"**+{resultado['xp']} XP**\n"

                f"🔥 Sequência: "
                f"**{resultado['streak']} dias**"

                f"{nivel_texto}"
            ),
            color=CORES["dourado"]
        )

        await responder(
            origem,
            embed=embed,
            ephemeral=isinstance(
                origem,
                discord.Interaction
            )
        )

    # ========================================================
    # TRABALHO
    # ========================================================

    async def executar_trabalho(
        self,
        origem
    ):

        membro = (
            origem.user
            if isinstance(
                origem,
                discord.Interaction
            )
            else
            origem.author
        )

        usuario = (
            self.banco.obter_usuario(
                membro.id
            )
        )

        if usuario is None:
            return

        restante = (
            self.segundos_cooldown(
                usuario.get(
                    "ultimo_trabalho"
                ),
                COOLDOWN_TRABALHO
            )
        )

        if restante > 0:

            embed = discord.Embed(
                title="⏳ TRABALHO EM COOLDOWN",
                description=(
                    f"{membro.mention}, "
                    "você precisa descansar.\n\n"
                    f"⏰ Próximo trabalho em "
                    f"**{self.formatar_tempo(restante)}**."
                ),
                color=CORES["amarelo"]
            )

            await responder(
                origem,
                embed=embed,
                ephemeral=isinstance(
                    origem,
                    discord.Interaction
                )
            )

            return

        nivel = int(
            usuario["nivel"]
        )

        trabalhos = (
            self.trabalhos_desbloqueados(
                nivel
            )
        )

        if not trabalhos:

            await responder(
                origem,
                content=(
                    "❌ Você ainda não desbloqueou nenhum trabalho."
                ),
                ephemeral=isinstance(
                    origem,
                    discord.Interaction
                )
            )

            return

        trabalho = random.choice(
            trabalhos
        )

        valor = random.randint(
            trabalho["minimo"],
            trabalho["maximo"]
        )

        xp = random.randint(
            trabalho["xp_min"],
            trabalho["xp_max"]
        )

        resultado = (
            await self.banco.registrar_trabalho(
                membro.id,
                valor,
                xp,
                (
                    f"{trabalho['emoji']} "
                    f"{trabalho['nome']}"
                )
            )
        )

        if resultado is None:
            return

        nivel_texto = ""

        if (
            resultado["nivel_depois"]
            >
            resultado["nivel_antes"]
        ):

            nivel_texto = (
                f"\n\n🎉 **NÍVEL "
                f"{resultado['nivel_depois']} "
                f"DESBLOQUEADO!**"
            )

        embed = discord.Embed(
            title=(
                f"{trabalho['emoji']} "
                "TRABALHO CONCLUÍDO"
            ),
            description=(
                f"{membro.mention}, "
                f"você trabalhou como "
                f"**{trabalho['nome']}**!\n\n"

                f"💰 Salário: "
                f"**+{formatar_moedas(valor)} RC**\n"

                f"✨ XP: "
                f"**+{xp} XP**"

                f"{nivel_texto}"
            ),
            color=CORES["verde"]
        )

        await responder(
            origem,
            embed=embed,
            ephemeral=isinstance(
                origem,
                discord.Interaction
            )
        )

    # ========================================================
    # !SALDO
    # ========================================================

    @commands.command(
        name="saldo",
        aliases=[
            "bal",
            "balance"
        ],
        description=(
            "Mostra seu perfil econômico."
        )
    )
    @commands.guild_only()
    async def saldo(
        self,
        ctx,
        membro: discord.Member = None
    ):

        membro = (
            membro
            or
            ctx.author
        )

        self.banco.garantir_usuario(
            membro.id
        )

        await ctx.send(
            embed=self.criar_embed_perfil(
                membro
            ),
            view=EconomiaPerfilView(
                self,
                membro.id
            )
        )

    # ========================================================
    # !ECONOMIA
    # ========================================================

    @commands.command(
        name="economia",
        aliases=[
            "econ"
        ],
        description=(
            "Abre seu painel econômico."
        )
    )
    @commands.guild_only()
    async def economia(
        self,
        ctx
    ):

        await ctx.invoke(
            self.saldo
        )

    # ========================================================
    # !ECONOMIAPERFIL
    # ========================================================

    @commands.command(
        name="economiaperfil",
        aliases=[
            "perfilfinanceiro"
        ],
        description=(
            "Abre seu perfil econômico."
        )
    )
    @commands.guild_only()
    async def economiaperfil(
        self,
        ctx
    ):

        await ctx.invoke(
            self.saldo
        )

    # ========================================================
    # !DIARIO
    # ========================================================

    @commands.command(
        name="diario",
        aliases=[
            "daily"
        ],
        description=(
            "Recebe sua recompensa diária."
        )
    )
    @commands.guild_only()
    async def diario(
        self,
        ctx
    ):

        await self.executar_daily(
            ctx
        )

    # ========================================================
    # !TRABALHAR
    # ========================================================

    @commands.command(
        name="trabalhar",
        aliases=[
            "work"
        ],
        description=(
            "Trabalha para ganhar moedas e XP."
        )
    )
    @commands.guild_only()
    async def trabalhar(
        self,
        ctx
    ):

        await self.executar_trabalho(
            ctx
        )

    # ========================================================
    # !TRABALHOS
    # ========================================================

    @commands.command(
        name="trabalhos",
        aliases=[
            "jobs"
        ],
        description=(
            "Mostra os trabalhos disponíveis."
        )
    )
    @commands.guild_only()
    async def trabalhos(
        self,
        ctx
    ):

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        nivel = int(
            usuario["nivel"]
        )

        embed = discord.Embed(
            title="💼 ROYALT • TRABALHOS",
            description=(
                f"Seu nível atual: **{nivel}**\n\n"
                "✅ = desbloqueado\n"
                "🔒 = bloqueado"
            ),
            color=CORES["azul"]
        )

        for trabalho in TRABALHOS:

            desbloqueado = (
                nivel
                >=
                trabalho["level"]
            )

            embed.add_field(
                name=(
                    f"{'✅' if desbloqueado else '🔒'} "
                    f"{trabalho['emoji']} "
                    f"{trabalho['nome']}"
                ),
                value=(
                    f"⭐ Nível **{trabalho['level']}**\n"
                    f"💰 **"
                    f"{formatar_moedas(trabalho['minimo'])}"
                    f"–"
                    f"{formatar_moedas(trabalho['maximo'])}"
                    f" RC**\n"
                    f"✨ XP **"
                    f"{trabalho['xp_min']}"
                    f"–"
                    f"{trabalho['xp_max']}"
                    f"**"
                ),
                inline=False
            )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # !DEPOSITAR
    # ========================================================

    @commands.command(
        name="depositar",
        aliases=[
            "dep",
            "deposit"
        ],
        description=(
            "Deposita moedas no banco."
        )
    )
    @commands.guild_only()
    async def depositar(
        self,
        ctx,
        valor: str
    ):

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        if valor.lower() in (
            "tudo",
            "all",
            "max"
        ):

            quantidade = int(
                usuario["carteira"]
            )

        else:

            try:

                quantidade = int(
                    valor
                )

            except ValueError:

                await ctx.send(
                    "❌ Informe uma quantidade válida."
                )

                return

        if quantidade <= 0:

            await ctx.send(
                "❌ O valor precisa ser maior que zero."
            )

            return

        sucesso = await self.banco.mover_dinheiro(
            ctx.author.id,
            "carteira",
            "banco",
            quantidade,
            "deposito",
            f"Depósito de {quantidade} RC"
        )

        if not sucesso:

            await ctx.send(
                embed=discord.Embed(
                    title="❌ DEPÓSITO RECUSADO",
                    description=(
                        "Você não possui "
                        "esse valor na carteira."
                    ),
                    color=CORES["vermelho"]
                )
            )

            return

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        await ctx.send(
            embed=discord.Embed(
                title="🏦 DEPÓSITO REALIZADO",
                description=(
                    f"💳 Carteira: "
                    f"**{formatar_moedas(usuario['carteira'])} RC**\n"
                    f"🏦 Banco: "
                    f"**{formatar_moedas(usuario['banco'])} RC**"
                ),
                color=CORES["azul"]
            )
        )

    # ========================================================
    # !SACAR
    # ========================================================

    @commands.command(
        name="sacar",
        aliases=[
            "withdraw"
        ],
        description=(
            "Saca moedas do banco."
        )
    )
    @commands.guild_only()
    async def sacar(
        self,
        ctx,
        valor: str
    ):

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        if valor.lower() in (
            "tudo",
            "all",
            "max"
        ):

            quantidade = int(
                usuario["banco"]
            )

        else:

            try:

                quantidade = int(
                    valor
                )

            except ValueError:

                await ctx.send(
                    "❌ Informe uma quantidade válida."
                )

                return

        if quantidade <= 0:

            await ctx.send(
                "❌ O valor precisa ser maior que zero."
            )

            return

        sucesso = await self.banco.mover_dinheiro(
            ctx.author.id,
            "banco",
            "carteira",
            quantidade,
            "saque",
            f"Saque de {quantidade} RC"
        )

        if not sucesso:

            await ctx.send(
                embed=discord.Embed(
                    title="❌ SAQUE RECUSADO",
                    description=(
                        "Você não possui "
                        "esse valor no banco."
                    ),
                    color=CORES["vermelho"]
                )
            )

            return

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        await ctx.send(
            embed=discord.Embed(
                title="💳 SAQUE REALIZADO",
                description=(
                    f"💳 Carteira: "
                    f"**{formatar_moedas(usuario['carteira'])} RC**\n"
                    f"🏦 Banco: "
                    f"**{formatar_moedas(usuario['banco'])} RC**"
                ),
                color=CORES["verde"]
            )
        )

    # ========================================================
    # !PAGAR
    # ========================================================

    @commands.command(
        name="pagar",
        aliases=[
            "pay",
            "transferir"
        ],
        description=(
            "Transfere moedas para outro membro."
        )
    )
    @commands.guild_only()
    async def pagar(
        self,
        ctx,
        membro: discord.Member,
        valor: int
    ):

        if membro.bot:

            await ctx.send(
                "❌ Bots não participam da economia."
            )

            return

        if membro.id == ctx.author.id:

            await ctx.send(
                "❌ Você não pode pagar a si mesmo."
            )

            return

        if valor <= 0:

            await ctx.send(
                "❌ O valor precisa ser maior que zero."
            )

            return

        sucesso = await self.banco.transferir(
            ctx.author.id,
            membro.id,
            valor
        )

        if not sucesso:

            await ctx.send(
                embed=discord.Embed(
                    title="❌ TRANSFERÊNCIA RECUSADA",
                    description=(
                        "Você não possui "
                        "saldo suficiente na carteira."
                    ),
                    color=CORES["vermelho"]
                )
            )

            return

        await ctx.send(
            embed=discord.Embed(
                title="💸 TRANSFERÊNCIA REALIZADA",
                description=(
                    f"{ctx.author.mention} enviou "
                    f"**{formatar_moedas(valor)} RC** "
                    f"para {membro.mention}."
                ),
                color=CORES["verde"]
            )
        )

    # ========================================================
    # !TEMAS
    # ========================================================

    @commands.command(
        name="temas",
        aliases=[
            "perfiltemas"
        ],
        description=(
            "Mostra os temas do perfil."
        )
    )
    @commands.guild_only()
    async def temas(
        self,
        ctx
    ):

        await ctx.send(
            embed=self.criar_embed_temas(),
            view=TemasView(
                self,
                ctx.author.id
            )
        )

    # ========================================================
    # !ECONOMIATOP
    # ========================================================

    @commands.command(
        name="economiatop",
        aliases=[
            "moneytop",
            "riqueza",
            "ranking"
        ],
        description=(
            "Mostra o ranking econômico visual."
        )
    )
    @commands.guild_only()
    async def economiatop(
        self,
        ctx
    ):

        def buscar():

            with self.banco.conectar() as db:

                rows = db.execute(
                    """
                    SELECT

                        id,

                        carteira,

                        banco,

                        (carteira + banco)
                        AS patrimonio

                    FROM usuarios

                    ORDER BY patrimonio DESC

                    LIMIT 100
                    """
                ).fetchall()

                return [
                    dict(
                        row
                    )
                    for row in rows
                ]

        dados = await self.banco.executar(
            buscar
        )

        ranking = []

        for item in dados:

            membro = (
                ctx.guild.get_member(
                    int(
                        item["id"]
                    )
                )
            )

            if membro is None:
                continue

            if membro.bot:
                continue

            ranking.append(
                {
                    "membro": membro,
                    "patrimonio": int(
                        item["patrimonio"]
                    )
                }
            )

        if not ranking:

            await ctx.send(
                embed=discord.Embed(
                    title="📭 RANKING VAZIO",
                    description=(
                        "Ainda não existem "
                        "usuários registrados."
                    ),
                    color=CORES["cinza"]
                )
            )

            return

        view = RankingEconomiaView(
            self,
            ctx.author.id,
            ranking,
            pagina=1,
            por_pagina=5
        )

        embed, arquivo = (
            await view.gerar_pagina()
        )

        await ctx.send(
            embed=embed,
            file=arquivo,
            view=view
        )

    # ========================================================
    # !ECONOMIARANK
    # ========================================================

    @commands.command(
        name="economiarank",
        description=(
            "Mostra sua posição no ranking econômico."
        )
    )
    @commands.guild_only()
    async def economiarank(
        self,
        ctx
    ):

        def buscar():

            with self.banco.conectar() as db:

                return db.execute(
                    """
                    SELECT

                        id,

                        carteira + banco
                        AS patrimonio

                    FROM usuarios

                    ORDER BY patrimonio DESC
                    """
                ).fetchall()

        dados = await self.banco.executar(
            buscar
        )

        posicao = None
        patrimonio = 0

        for indice, item in enumerate(
            dados,
            start=1
        ):

            if (
                int(
                    item["id"]
                )
                ==
                ctx.author.id
            ):

                posicao = indice

                patrimonio = int(
                    item["patrimonio"]
                )

                break

        if posicao is None:

            await ctx.send(
                "📭 Você ainda não possui posição no ranking."
            )

            return

        await ctx.send(
            embed=discord.Embed(
                title="🏆 SUA POSIÇÃO",
                description=(
                    f"{ctx.author.mention}\n\n"
                    f"🏆 **Posição:** #{posicao}\n"
                    f"💎 **Patrimônio:** "
                    f"{formatar_moedas(patrimonio)} RC"
                ),
                color=CORES["dourado"]
            )
        )

    # ========================================================
    # !DESAFIO
    # ========================================================

    @commands.command(
        name="desafio",
        aliases=[
            "challenge"
        ],
        description=(
            "Recebe um desafio recreativo."
        )
    )
    @commands.guild_only()
    async def desafio(
        self,
        ctx
    ):

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        restante = self.segundos_cooldown(
            usuario.get(
                "ultimo_desafio"
            ),
            COOLDOWN_DESAFIO
        )

        if restante > 0:

            await ctx.send(
                embed=discord.Embed(
                    title="⏳ DESAFIO EM COOLDOWN",
                    description=(
                        f"🎯 Próximo desafio em "
                        f"**{self.formatar_tempo(restante)}**."
                    ),
                    color=CORES["amarelo"]
                )
            )

            return

        desafio = random.choice(
            DESAFIOS
        )

        valor = random.randint(
            desafio["recompensa_min"],
            desafio["recompensa_max"]
        )

        xp = random.randint(
            desafio["xp_min"],
            desafio["xp_max"]
        )

        resultado = (
            await self.banco.registrar_recompensa(
                ctx.author.id,
                valor,
                xp,
                "desafio",
                "Desafio recreativo"
            )
        )

        await self.banco.salvar_cooldown(
            ctx.author.id,
            "ultimo_desafio"
        )

        nivel_texto = ""

        if (
            resultado
            and
            resultado["nivel_depois"]
            >
            resultado["nivel_antes"]
        ):

            nivel_texto = (
                f"\n🎉 Nível "
                f"{resultado['nivel_depois']} desbloqueado!"
            )

        await ctx.send(
            embed=discord.Embed(
                title="🎯 NOVO DESAFIO",
                description=(
                    f"{ctx.author.mention}\n\n"
                    f"🧩 **Missão:**\n"
                    f"{desafio['texto']}\n\n"
                    f"💰 Recompensa: "
                    f"**+{formatar_moedas(valor)} RC**\n"
                    f"✨ XP: "
                    f"**+{xp}**"
                    f"{nivel_texto}"
                ),
                color=CORES["azul"]
            )
        )

    # ========================================================
    # !QUIZ
    # ========================================================

    @commands.command(
        name="quiz",
        description=(
            "Responde um quiz para ganhar moedas e XP."
        )
    )
    @commands.guild_only()
    async def quiz(
        self,
        ctx
    ):

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        restante = self.segundos_cooldown(
            usuario.get(
                "ultimo_quiz"
            ),
            COOLDOWN_QUIZ
        )

        if restante > 0:

            await ctx.send(
                embed=discord.Embed(
                    title="⏳ QUIZ EM COOLDOWN",
                    description=(
                        f"🧠 Próximo quiz em "
                        f"**{self.formatar_tempo(restante)}**."
                    ),
                    color=CORES["amarelo"]
                )
            )

            return

        pergunta = random.choice(
            QUIZZES
        )

        await ctx.send(
            embed=discord.Embed(
                title="🧠 ROYALT • QUIZ",
                description=(
                    f"## {pergunta['pergunta']}\n\n"
                    +
                    "\n".join(
                        pergunta["opcoes"]
                    )
                    +
                    "\n\n"
                    "Responda com A, B, C ou D "
                    "em até **20 segundos**."
                ),
                color=CORES["ciano"]
            )
        )

        def verificar(
            mensagem
        ):

            return (
                mensagem.author.id
                ==
                ctx.author.id
                and
                mensagem.channel.id
                ==
                ctx.channel.id
                and
                mensagem.content.lower().strip()
                in {
                    "a",
                    "b",
                    "c",
                    "d"
                }
            )

        try:

            resposta = (
                await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=verificar
                )
            )

        except asyncio.TimeoutError:

            await self.banco.salvar_cooldown(
                ctx.author.id,
                "ultimo_quiz"
            )

            await ctx.send(
                "⏰ Tempo esgotado!"
            )

            return

        await self.banco.salvar_cooldown(
            ctx.author.id,
            "ultimo_quiz"
        )

        if (
            resposta.content.lower().strip()
            ==
            pergunta["resposta"]
        ):

            resultado = (
                await self.banco.registrar_recompensa(
                    ctx.author.id,
                    pergunta["recompensa"],
                    pergunta["xp"],
                    "quiz",
                    "Resposta correta"
                )
            )

            nivel_texto = ""

            if (
                resultado
                and
                resultado["nivel_depois"]
                >
                resultado["nivel_antes"]
            ):

                nivel_texto = (
                    f"\n🎉 Nível "
                    f"{resultado['nivel_depois']} "
                    "desbloqueado!"
                )

            await ctx.send(
                embed=discord.Embed(
                    title="✅ RESPOSTA CORRETA!",
                    description=(
                        f"{ctx.author.mention}\n\n"
                        f"💰 +"
                        f"{formatar_moedas(pergunta['recompensa'])}"
                        f" RC\n"
                        f"✨ +"
                        f"{pergunta['xp']}"
                        f" XP"
                        f"{nivel_texto}"
                    ),
                    color=CORES["verde"]
                )
            )

        else:

            await ctx.send(
                embed=discord.Embed(
                    title="❌ RESPOSTA INCORRETA",
                    description=(
                        f"A resposta correta era "
                        f"**{pergunta['resposta'].upper()}**."
                    ),
                    color=CORES["vermelho"]
                )
            )

    # ========================================================
    # !REACAO
    # ========================================================

    @commands.command(
        name="reacao",
        aliases=[
            "reflexo"
        ],
        description=(
            "Testa sua velocidade de reação."
        )
    )
    @commands.guild_only()
    async def reacao(
        self,
        ctx
    ):

        usuario = (
            self.banco.obter_usuario(
                ctx.author.id
            )
        )

        restante = self.segundos_cooldown(
            usuario.get(
                "ultimo_reacao"
            ),
            COOLDOWN_REACAO
        )

        if restante > 0:

            await ctx.send(
                embed=discord.Embed(
                    title="⏳ TESTE EM COOLDOWN",
                    description=(
                        f"⚡ Próximo teste em "
                        f"**{self.formatar_tempo(restante)}**."
                    ),
                    color=CORES["amarelo"]
                )
            )

            return

        mensagem = await ctx.send(
            embed=discord.Embed(
                title="⚡ TESTE DE REAÇÃO",
                description=(
                    "Prepare-se...\n\n"
                    "👀 Não responda ainda."
                ),
                color=CORES["azul"]
            )
        )

        await asyncio.sleep(
            random.uniform(
                2,
                5
            )
        )

        inicio = time.perf_counter()

        await mensagem.edit(
            embed=discord.Embed(
                title="⚡ AGORA!",
                description=(
                    "🔥 **RESPONDA `VAI`!**"
                ),
                color=CORES["vermelho"]
            )
        )

        def verificar(
            resposta
        ):

            return (
                resposta.author.id
                ==
                ctx.author.id
                and
                resposta.channel.id
                ==
                ctx.channel.id
                and
                resposta.content.lower().strip()
                ==
                "vai"
            )

        try:

            await self.bot.wait_for(
                "message",
                timeout=5,
                check=verificar
            )

            tempo_resposta = (
                time.perf_counter()
                - inicio
            )

            if tempo_resposta < 0.45:

                valor = 450
                xp = 60
                categoria = "🚀 Lendário"

            elif tempo_resposta < 0.75:

                valor = 350
                xp = 50
                categoria = "⚡ Muito rápido"

            elif tempo_resposta < 1.20:

                valor = 250
                xp = 40
                categoria = "🔥 Rápido"

            else:

                valor = 150
                xp = 25
                categoria = "🙂 Normal"

            resultado = (
                await self.banco.registrar_recompensa(
                    ctx.author.id,
                    valor,
                    xp,
                    "reacao",
                    "Teste de reação"
                )
            )

            await self.banco.salvar_cooldown(
                ctx.author.id,
                "ultimo_reacao"
            )

            nivel_texto = ""

            if (
                resultado
                and
                resultado["nivel_depois"]
                >
                resultado["nivel_antes"]
            ):

                nivel_texto = (
                    f"\n🎉 Nível "
                    f"{resultado['nivel_depois']} "
                    "desbloqueado!"
                )

            await ctx.send(
                embed=discord.Embed(
                    title="⚡ RESULTADO",
                    description=(
                        f"{categoria}\n\n"
                        f"⏱️ Tempo: "
                        f"**{tempo_resposta:.3f}s**\n\n"
                        f"💰 +"
                        f"{formatar_moedas(valor)}"
                        f" RC\n"
                        f"✨ +"
                        f"{xp} XP"
                        f"{nivel_texto}"
                    ),
                    color=CORES["verde"]
                )
            )

        except asyncio.TimeoutError:

            await self.banco.salvar_cooldown(
                ctx.author.id,
                "ultimo_reacao"
            )

            await ctx.send(
                embed=discord.Embed(
                    title="💥 TARDE DEMAIS!",
                    description=(
                        "Você demorou para reagir. 😂"
                    ),
                    color=CORES["vermelho"]
                )
            )

    # ========================================================
    # !ECONOMIAINFO
    # ========================================================

    @commands.command(
        name="economiainfo",
        aliases=[
            "economystats"
        ],
        description=(
            "Mostra estatísticas gerais da economia."
        )
    )
    @commands.guild_only()
    async def economiainfo(
        self,
        ctx
    ):

        def buscar():

            with self.banco.conectar() as db:

                usuarios = db.execute(
                    """
                    SELECT

                        COUNT(*) AS total,

                        COALESCE(
                            SUM(carteira),
                            0
                        ) AS carteira,

                        COALESCE(
                            SUM(banco),
                            0
                        ) AS banco,

                        COALESCE(
                            SUM(carteira + banco),
                            0
                        ) AS patrimonio

                    FROM usuarios
                    """
                ).fetchone()

                transacoes = db.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM transacoes
                    """
                ).fetchone()

                return (
                    dict(usuarios),
                    dict(transacoes)
                )

        usuarios, transacoes = (
            await self.banco.executar(
                buscar
            )
        )

        embed = discord.Embed(
            title="📊 ROYALT • ECONOMIA",
            description=(
                "Estatísticas gerais do sistema."
            ),
            color=CORES["roxo"]
        )

        embed.add_field(
            name="👥 Usuários",
            value=(
                f"**{usuarios['total']}**"
            ),
            inline=True
        )

        embed.add_field(
            name="💳 Carteiras",
            value=(
                f"**{formatar_moedas(usuarios['carteira'])} RC**"
            ),
            inline=True
        )

        embed.add_field(
            name="🏦 Bancos",
            value=(
                f"**{formatar_moedas(usuarios['banco'])} RC**"
            ),
            inline=True
        )

        embed.add_field(
            name="💎 Patrimônio total",
            value=(
                f"**{formatar_moedas(usuarios['patrimonio'])} RC**"
            ),
            inline=False
        )

        embed.add_field(
            name="🧾 Transações",
            value=(
                f"**{transacoes['total']}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🗃️ Banco",
            value="SQLite",
            inline=True
        )

        embed.add_field(
            name="⚙️ Versão",
            value=VERSAO,
            inline=True
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Economia(
            bot
        )
    )