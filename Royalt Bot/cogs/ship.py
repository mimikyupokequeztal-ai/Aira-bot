import asyncio
import json
import random
import re

from datetime import datetime, timezone
from pathlib import Path

import discord

from discord.ext import commands


# ============================================================
# IDENTIDADE
# ============================================================

NOME_SISTEMA = "Royalt Ship System"
VERSAO_SISTEMA = "2.1"


# ============================================================
# CORES
# ============================================================

COR_ROSA = discord.Color.from_rgb(
    255,
    105,
    180
)

COR_ROXO = discord.Color.from_rgb(
    155,
    89,
    182
)

COR_VERMELHO = discord.Color.from_rgb(
    255,
    71,
    87
)

COR_LARANJA = discord.Color.from_rgb(
    255,
    159,
    67
)

COR_AMARELO = discord.Color.from_rgb(
    255,
    214,
    10
)

COR_VERDE = discord.Color.from_rgb(
    46,
    204,
    113
)

COR_AZUL = discord.Color.from_rgb(
    52,
    152,
    219
)

COR_NEUTRA = discord.Color.from_rgb(
    149,
    165,
    166
)

COR_AVISO = discord.Color.from_rgb(
    241,
    196,
    15
)

COR_ERRO = discord.Color.from_rgb(
    231,
    76,
    60
)


# ============================================================
# EMOJIS
# ============================================================

EMOJIS = {

    "ship": "💘",
    "coracao": "💗",
    "amor": "💞",
    "fogo": "🔥",
    "trofeu": "🏆",
    "estrela": "⭐",
    "diamante": "💎",
    "coroa": "👑",
    "dados": "🎲",
    "medalha": "🏅",
    "perfil": "💌",
    "conquista": "🎖️",
    "bloqueado": "🔒",
    "desbloqueado": "✅",
    "novo": "🆕",
    "fechar": "❌",
    "refresh": "🔄",
    "aleatorio": "🎯",
    "estatisticas": "📊",
    "fantasma": "👻",
    "magia": "✨"
}


# ============================================================
# ARQUIVO
# ============================================================

PASTA_DATA = Path(
    "data"
)

ARQUIVO_SHIPS = (
    PASTA_DATA / "ships.json"
)

PASTA_DATA.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONQUISTAS
# ============================================================

CONQUISTAS = {

    "primeiro_ship": {
        "nome": "Primeiro Ship",
        "descricao": "Realize seu primeiro ship.",
        "emoji": "💞",
        "pontos": 5
    },

    "10_ships": {
        "nome": "Shipador Iniciante",
        "descricao": "Realize 10 ships diferentes.",
        "emoji": "🎯",
        "pontos": 10
    },

    "25_ships": {
        "nome": "Shipador Experiente",
        "descricao": "Realize 25 ships diferentes.",
        "emoji": "🔥",
        "pontos": 15
    },

    "50_ships": {
        "nome": "Especialista em Ships",
        "descricao": "Realize 50 ships diferentes.",
        "emoji": "💘",
        "pontos": 25
    },

    "100_ships": {
        "nome": "Lenda dos Ships",
        "descricao": "Realize 100 ships diferentes.",
        "emoji": "👑",
        "pontos": 50
    },

    "primeiro_100": {
        "nome": "Destino Absoluto",
        "descricao": "Encontre uma compatibilidade de 100%.",
        "emoji": "💯",
        "pontos": 30
    },

    "5_altos": {
        "nome": "Sensor de Química",
        "descricao": "Encontre 5 ships com 80% ou mais.",
        "emoji": "🔥",
        "pontos": 20
    },

    "10_altos": {
        "nome": "Detector de Química",
        "descricao": "Encontre 10 ships com 80% ou mais.",
        "emoji": "💞",
        "pontos": 30
    },

    "25_altos": {
        "nome": "Ímã de Ships",
        "descricao": "Encontre 25 ships com 80% ou mais.",
        "emoji": "🧲",
        "pontos": 50
    },

    "5_duplas": {
        "nome": "Explorador",
        "descricao": "Conheça 5 duplas diferentes.",
        "emoji": "🗺️",
        "pontos": 10
    },

    "10_duplas": {
        "nome": "Explorador Avançado",
        "descricao": "Conheça 10 duplas diferentes.",
        "emoji": "🧭",
        "pontos": 20
    },

    "25_duplas": {
        "nome": "Caçador de Ships",
        "descricao": "Conheça 25 duplas diferentes.",
        "emoji": "🎯",
        "pontos": 40
    },

    "ship_90": {
        "nome": "Quase Perfeito",
        "descricao": "Encontre um ship de 90% ou mais.",
        "emoji": "💎",
        "pontos": 20
    },

    "ship_95": {
        "nome": "Ship Épico",
        "descricao": "Encontre um ship de 95% ou mais.",
        "emoji": "✨",
        "pontos": 30
    },

    "ship_baixo": {
        "nome": "Caos do Algoritmo",
        "descricao": "Encontre um ship de 10% ou menos.",
        "emoji": "💀",
        "pontos": 15
    }
}


# ============================================================
# DADOS PADRÃO
# ============================================================

def dados_padrao():

    return {

        "ships": {},

        "usuarios": {},

        "estatisticas": {

            "total_ships": 0,

            "ships_100": 0,

            "maior_ship": 0,

            "dupla_maior_ship": None,

            "ultimo_ship": None
        }
    }


# ============================================================
# JSON
# ============================================================

def carregar_dados():

    if not ARQUIVO_SHIPS.exists():

        return dados_padrao()

    try:

        with open(
            ARQUIVO_SHIPS,
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

            return dados_padrao()

        padrao = dados_padrao()

        for chave, valor in padrao.items():

            if chave not in dados:

                dados[chave] = valor

        if not isinstance(
            dados.get("ships"),
            dict
        ):

            dados["ships"] = {}

        if not isinstance(
            dados.get("usuarios"),
            dict
        ):

            dados["usuarios"] = {}

        if not isinstance(
            dados.get("estatisticas"),
            dict
        ):

            dados["estatisticas"] = (
                padrao["estatisticas"].copy()
            )

        return dados

    except (
        json.JSONDecodeError,
        OSError
    ) as erro:

        print(
            f"[SHIP] Erro carregando dados: {erro}"
        )

        return dados_padrao()


def salvar_dados(
    dados
):

    arquivo_temporario = (
        ARQUIVO_SHIPS.with_suffix(
            ".tmp"
        )
    )

    try:

        with open(
            arquivo_temporario,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        arquivo_temporario.replace(
            ARQUIVO_SHIPS
        )

    except OSError as erro:

        print(
            f"[SHIP] Erro salvando dados: {erro}"
        )

        try:

            if arquivo_temporario.exists():

                arquivo_temporario.unlink()

        except OSError:

            pass


# ============================================================
# UTILIDADES
# ============================================================

def chave_dupla(
    id1,
    id2
):

    ids = sorted(
        [
            int(id1),
            int(id2)
        ]
    )

    return (
        f"{ids[0]}:{ids[1]}"
    )


def nome_ship(
    pessoa1,
    pessoa2
):

    nome1 = (
        pessoa1.display_name.strip()
    )

    nome2 = (
        pessoa2.display_name.strip()
    )

    nome1 = re.sub(
        r"[^a-zA-ZÀ-ÿ0-9]",
        "",
        nome1
    )

    nome2 = re.sub(
        r"[^a-zA-ZÀ-ÿ0-9]",
        "",
        nome2
    )

    if not nome1 or not nome2:

        return "Royalt Ship"

    metade1 = max(
        1,
        len(nome1) // 2
    )

    metade2 = max(
        1,
        len(nome2) // 2
    )

    resultado = (
        nome1[:metade1]
        + nome2[-metade2:]
    )

    if len(resultado) < 3:

        resultado = (
            nome1[:2]
            + nome2[:2]
        )

    return resultado[:32]


def barra_compatibilidade(
    porcentagem,
    tamanho=20
):

    porcentagem = max(
        0,
        min(
            100,
            int(porcentagem)
        )
    )

    preenchido = round(
        porcentagem
        / 100
        * tamanho
    )

    vazio = (
        tamanho
        - preenchido
    )

    return (
        "💗" * preenchido
        + "🖤" * vazio
    )


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar(
    porcentagem
):

    if porcentagem <= 10:

        return {

            "nome": "Caos Absoluto",

            "emoji": "💀",

            "cor": COR_NEUTRA,

            "texto": (
                "O algoritmo analisou tudo e "
                "entrou em estado de emergência."
            ),

            "fala": (
                "💀 O Royalt desligou o computador "
                "por alguns segundos para processar isso."
            )
        }

    if porcentagem <= 25:

        return {

            "nome": "Quase Nada",

            "emoji": "🥶",

            "cor": COR_AZUL,

            "texto": (
                "A química resolveu passar longe."
            ),

            "fala": (
                "🥶 O algoritmo procurou uma faísca. "
                "Ela aparentemente estava de folga."
            )
        }

    if porcentagem <= 40:

        return {

            "nome": "Curiosidade",

            "emoji": "👀",

            "cor": COR_AZUL,

            "texto": (
                "Existe material suficiente "
                "para levantar suspeitas."
            ),

            "fala": (
                "👀 O Royalt não está afirmando nada... "
                "mas ficou bastante curioso."
            )
        }

    if porcentagem <= 55:

        return {

            "nome": "Possível",

            "emoji": "🙂",

            "cor": COR_AMARELO,

            "texto": (
                "O algoritmo detectou alguma possibilidade."
            ),

            "fala": (
                "🙂 Talvez exista alguma coisa "
                "escondida nessa matemática."
            )
        }

    if porcentagem <= 70:

        return {

            "nome": "Química",

            "emoji": "💞",

            "cor": COR_LARANJA,

            "texto": (
                "A pontuação começou a ficar interessante."
            ),

            "fala": (
                "💞 O Royalt olhou os dados duas vezes "
                "e soltou um: 'hmm... interessante'."
            )
        }

    if porcentagem <= 85:

        return {

            "nome": "Ship Forte",

            "emoji": "🔥",

            "cor": COR_ROSA,

            "texto": (
                "O algoritmo encontrou bastante química."
            ),

            "fala": (
                "🔥 O sensor de ship começou a apitar."
            )
        }

    if porcentagem <= 95:

        return {

            "nome": "Ship Épico",

            "emoji": "💘",

            "cor": COR_VERMELHO,

            "texto": (
                "A pontuação ficou perigosamente alta."
            ),

            "fala": (
                "💘 O Royalt tentou manter a neutralidade. "
                "Falhou miseravelmente."
            )
        }

    return {

        "nome": "Lenda do Servidor",

        "emoji": "💍",

        "cor": COR_ROXO,

        "texto": (
            "O algoritmo entrou em território lendário."
        ),

        "fala": (
            "💍 O algoritmo pediu para registrar "
            "esse momento nos arquivos históricos."
        )
    }


# ============================================================
# COG
# ============================================================

class Ship(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.dados = carregar_dados()

        self.lock = asyncio.Lock()

    # ========================================================
    # SALVAR
    # ========================================================

    async def salvar(
        self
    ):

        async with self.lock:

            salvar_dados(
                self.dados
            )

    # ========================================================
    # REGISTRAR USUÁRIO
    # ========================================================

    def registrar_usuario(
        self,
        usuario_id
    ):

        usuario_id = str(
            usuario_id
        )

        usuarios = self.dados[
            "usuarios"
        ]

        if usuario_id not in usuarios:

            usuarios[
                usuario_id
            ] = {

                "ships_realizados": 0,

                "ships_altos": 0,

                "maior_compatibilidade": 0,

                "duplas_diferentes": 0,

                "ships_100": 0,

                "pontos_conquistas": 0,

                "conquistas": [],

                "duplas": []
            }

        usuario = usuarios[
            usuario_id
        ]

        usuario.setdefault(
            "ships_realizados",
            0
        )

        usuario.setdefault(
            "ships_altos",
            0
        )

        usuario.setdefault(
            "maior_compatibilidade",
            0
        )

        usuario.setdefault(
            "duplas_diferentes",
            0
        )

        usuario.setdefault(
            "ships_100",
            0
        )

        usuario.setdefault(
            "pontos_conquistas",
            0
        )

        usuario.setdefault(
            "conquistas",
            []
        )

        usuario.setdefault(
            "duplas",
            []
        )

        return usuario

    # ========================================================
    # ESCOLHER MEMBRO
    # ========================================================

    def escolher_membro_aleatorio(
        self,
        guild,
        ignorar_id
    ):

        membros = [

            membro

            for membro in guild.members

            if (
                not membro.bot
                and membro.id != ignorar_id
            )
        ]

        if not membros:

            return None

        return random.choice(
            membros
        )

    # ========================================================
    # VERIFICAR CONQUISTAS
    # ========================================================

    def verificar_conquistas(
        self,
        usuario_id
    ):

        usuario = self.registrar_usuario(
            usuario_id
        )

        total = int(
            usuario.get(
                "ships_realizados",
                0
            )
        )

        altos = int(
            usuario.get(
                "ships_altos",
                0
            )
        )

        duplas = int(
            usuario.get(
                "duplas_diferentes",
                0
            )
        )

        maior = int(
            usuario.get(
                "maior_compatibilidade",
                0
            )
        )

        ships_100 = int(
            usuario.get(
                "ships_100",
                0
            )
        )

        regras = {

            "primeiro_ship":
                total >= 1,

            "10_ships":
                total >= 10,

            "25_ships":
                total >= 25,

            "50_ships":
                total >= 50,

            "100_ships":
                total >= 100,

            "primeiro_100":
                ships_100 >= 1,

            "5_altos":
                altos >= 5,

            "10_altos":
                altos >= 10,

            "25_altos":
                altos >= 25,

            "5_duplas":
                duplas >= 5,

            "10_duplas":
                duplas >= 10,

            "25_duplas":
                duplas >= 25,

            "ship_90":
                maior >= 90,

            "ship_95":
                maior >= 95,

            "ship_baixo":
                any(
                    int(
                        resultado.get(
                            "porcentagem",
                            100
                        )
                    ) <= 10
                    for chave in usuario.get(
                        "duplas",
                        []
                    )
                    if chave in self.dados["ships"]
                    for resultado in [
                        self.dados["ships"][chave]
                    ]
                )
        }

        conquistas_atuais = set(
            usuario.get(
                "conquistas",
                []
            )
        )

        novas = []

        for conquista_id, liberada in (
            regras.items()
        ):

            if not liberada:

                continue

            if conquista_id in conquistas_atuais:

                continue

            conquista = CONQUISTAS.get(
                conquista_id
            )

            if conquista is None:

                continue

            usuario[
                "conquistas"
            ].append(
                conquista_id
            )

            usuario[
                "pontos_conquistas"
            ] += int(
                conquista[
                    "pontos"
                ]
            )

            novas.append(
                conquista_id
            )

        return novas

    # ========================================================
    # CRIAR / OBTER SHIP
    # ========================================================

    def obter_ou_criar_ship(
        self,
        pessoa1,
        pessoa2
    ):

        chave = chave_dupla(
            pessoa1.id,
            pessoa2.id
        )

        existente = self.dados[
            "ships"
        ].get(
            chave
        )

        if existente:

            existente.setdefault(
                "vezes",
                1
            )

            existente[
                "vezes"
            ] += 1

            existente[
                "ultima_consulta"
            ] = datetime.now(
                timezone.utc
            ).isoformat()

            salvar_dados(
                self.dados
            )

            return (
                existente,
                []
            )

        porcentagem = random.randint(
            0,
            100
        )

        agora = datetime.now(
            timezone.utc
        ).isoformat()

        resultado = {

            "id1": pessoa1.id,

            "id2": pessoa2.id,

            "porcentagem": porcentagem,

            "porcentagem_anterior": None,

            "maior_porcentagem": porcentagem,

            "nome_ship": nome_ship(
                pessoa1,
                pessoa2
            ),

            "vezes": 1,

            "recalculado": 0,

            "criado_em": agora,

            "ultima_consulta": agora
        }

        self.dados[
            "ships"
        ][
            chave
        ] = resultado

        usuario1 = self.registrar_usuario(
            pessoa1.id
        )

        usuario2 = self.registrar_usuario(
            pessoa2.id
        )

        for usuario in (
            usuario1,
            usuario2
        ):

            usuario[
                "ships_realizados"
            ] += 1

            if porcentagem >= 80:

                usuario[
                    "ships_altos"
                ] += 1

            usuario[
                "maior_compatibilidade"
            ] = max(
                usuario[
                    "maior_compatibilidade"
                ],
                porcentagem
            )

            if porcentagem == 100:

                usuario[
                    "ships_100"
                ] += 1

            if chave not in usuario[
                "duplas"
            ]:

                usuario[
                    "duplas"
                ].append(
                    chave
                )

                usuario[
                    "duplas_diferentes"
                ] += 1

        estatisticas = self.dados[
            "estatisticas"
        ]

        estatisticas[
            "total_ships"
        ] += 1

        if porcentagem == 100:

            estatisticas[
                "ships_100"
            ] += 1

        if porcentagem > int(
            estatisticas.get(
                "maior_ship",
                0
            )
        ):

            estatisticas[
                "maior_ship"
            ] = porcentagem

            estatisticas[
                "dupla_maior_ship"
            ] = [
                pessoa1.id,
                pessoa2.id
            ]

        estatisticas[
            "ultimo_ship"
        ] = {

            "id1": pessoa1.id,

            "id2": pessoa2.id,

            "porcentagem": porcentagem,

            "data": agora
        }

        novas1 = self.verificar_conquistas(
            pessoa1.id
        )

        novas2 = self.verificar_conquistas(
            pessoa2.id
        )

        salvar_dados(
            self.dados
        )

        return (
            resultado,
            {
                str(pessoa1.id): novas1,
                str(pessoa2.id): novas2
            }
        )

    # ========================================================
    # REFAZER SHIP
    # ========================================================

    def refazer_ship(
        self,
        pessoa1,
        pessoa2
    ):

        chave = chave_dupla(
            pessoa1.id,
            pessoa2.id
        )

        existente = self.dados[
            "ships"
        ].get(
            chave
        )

        if existente is None:

            return self.obter_ou_criar_ship(
                pessoa1,
                pessoa2
            )

        porcentagem_antiga = int(
            existente.get(
                "porcentagem",
                0
            )
        )

        nova_porcentagem = random.randint(
            0,
            100
        )

        # Evita repetir imediatamente o mesmo número.
        if nova_porcentagem == porcentagem_antiga:

            nova_porcentagem = (
                (nova_porcentagem + 37)
                % 101
            )

        agora = datetime.now(
            timezone.utc
        ).isoformat()

        existente[
            "porcentagem_anterior"
        ] = porcentagem_antiga

        existente[
            "porcentagem"
        ] = nova_porcentagem

        existente[
            "maior_porcentagem"
        ] = max(
            int(
                existente.get(
                    "maior_porcentagem",
                    porcentagem_antiga
                )
            ),
            nova_porcentagem
        )

        existente[
            "vezes"
        ] = int(
            existente.get(
                "vezes",
                1
            )
        ) + 1

        existente[
            "recalculado"
        ] = int(
            existente.get(
                "recalculado",
                0
            )
        ) + 1

        existente[
            "ultima_consulta"
        ] = agora

        # ----------------------------------------------------
        # Atualiza estatísticas do usuário,
        # mas NÃO adiciona uma nova dupla.
        # ----------------------------------------------------

        for usuario_id in (
            pessoa1.id,
            pessoa2.id
        ):

            usuario = self.registrar_usuario(
                usuario_id
            )

            usuario[
                "maior_compatibilidade"
            ] = max(
                usuario[
                    "maior_compatibilidade"
                ],
                nova_porcentagem
            )

            if nova_porcentagem >= 80:

                usuario[
                    "ships_altos"
                ] += 1

            if nova_porcentagem == 100:

                usuario[
                    "ships_100"
                ] += 1

        estatisticas = self.dados[
            "estatisticas"
        ]

        if nova_porcentagem == 100:

            estatisticas[
                "ships_100"
            ] += 1

        if nova_porcentagem > int(
            estatisticas.get(
                "maior_ship",
                0
            )
        ):

            estatisticas[
                "maior_ship"
            ] = nova_porcentagem

            estatisticas[
                "dupla_maior_ship"
            ] = [
                pessoa1.id,
                pessoa2.id
            ]

        estatisticas[
            "ultimo_ship"
        ] = {

            "id1": pessoa1.id,

            "id2": pessoa2.id,

            "porcentagem": nova_porcentagem,

            "data": agora
        }

        novas1 = self.verificar_conquistas(
            pessoa1.id
        )

        novas2 = self.verificar_conquistas(
            pessoa2.id
        )

        salvar_dados(
            self.dados
        )

        return (
            existente,
            {
                str(pessoa1.id): novas1,
                str(pessoa2.id): novas2
            }
        )

    # ========================================================
    # EMBED SHIP
    # ========================================================

    def criar_embed_ship(
        self,
        pessoa1,
        pessoa2,
        resultado
    ):

        porcentagem = int(
            resultado.get(
                "porcentagem",
                0
            )
        )

        anterior = resultado.get(
            "porcentagem_anterior"
        )

        categoria = classificar(
            porcentagem
        )

        barra = barra_compatibilidade(
            porcentagem
        )

        nome = resultado.get(
            "nome_ship"
        )

        if not nome:

            nome = nome_ship(
                pessoa1,
                pessoa2
            )

        vezes = int(
            resultado.get(
                "vezes",
                1
            )
        )

        recalculado = int(
            resultado.get(
                "recalculado",
                0
            )
        )

        # ----------------------------------------------------
        # Variação
        # ----------------------------------------------------

        if anterior is None:

            variacao = (
                "🆕 Primeiro cálculo desta dupla."
            )

        else:

            diferenca = (
                porcentagem
                - int(anterior)
            )

            if diferenca > 0:

                variacao = (
                    f"📈 O ship subiu "
                    f"**+{diferenca}%** "
                    f"desde o cálculo anterior."
                )

            elif diferenca < 0:

                variacao = (
                    f"📉 O ship caiu "
                    f"**{diferenca}%** "
                    f"desde o cálculo anterior."
                )

            else:

                variacao = (
                    "➡️ O resultado permaneceu igual."
                )

        embed = discord.Embed(
            title=(
                f"{EMOJIS['ship']} "
                f"ROYALT • SHIP"
            ),
            description=(
                "## 💞 Dupla analisada\n\n"

                f"{pessoa1.mention} "
                f"**×** "
                f"{pessoa2.mention}\n\n"

                f"### {categoria['emoji']} "
                f"{categoria['nome']}\n\n"

                f"**Compatibilidade divertida:** "
                f"**{porcentagem}%**\n\n"

                f"{barra}\n\n"

                f"💍 **Nome do Ship:** "
                f"`{nome}`\n\n"

                f"{categoria['texto']}\n"

                f"{categoria['fala']}\n\n"

                f"{variacao}\n\n"

                f"🔄 **Consultas:** "
                f"**{vezes}**\n"

                f"🎲 **Recálculos:** "
                f"**{recalculado}x**\n\n"

                "🎲 *Resultado recreativo. "
                "Não representa sentimentos reais.*"
            ),
            color=categoria[
                "cor"
            ]
        )

        embed.add_field(
            name="👤 Pessoa 1",
            value=(
                f"{pessoa1.mention}\n"
                f"`{pessoa1.display_name[:40]}`"
            ),
            inline=True
        )

        embed.add_field(
            name="👤 Pessoa 2",
            value=(
                f"{pessoa2.mention}\n"
                f"`{pessoa2.display_name[:40]}`"
            ),
            inline=True
        )

        embed.add_field(
            name="📊 Resultado",
            value=(
                f"**{porcentagem}%**"
            ),
            inline=True
        )

        if anterior is not None:

            embed.add_field(
                name="📈 Resultado anterior",
                value=(
                    f"**{int(anterior)}%**"
                ),
                inline=True
            )

        recorde_dupla = int(
            resultado.get(
                "maior_porcentagem",
                porcentagem
            )
        )

        embed.add_field(
            name="🏆 Recorde da dupla",
            value=(
                f"**{recorde_dupla}%**"
            ),
            inline=True
        )

        embed.set_thumbnail(
            url=pessoa1.display_avatar.url
        )

        embed.set_footer(
            text=(
                f"{NOME_SISTEMA} "
                f"• v{VERSAO_SISTEMA}"
            )
        )

        return embed

    # ========================================================
    # EMBED CONQUISTAS
    # ========================================================

    def criar_embed_conquistas(
        self,
        membro
    ):

        usuario = self.registrar_usuario(
            membro.id
        )

        desbloqueadas = set(
            usuario.get(
                "conquistas",
                []
            )
        )

        pontos = int(
            usuario.get(
                "pontos_conquistas",
                0
            )
        )

        embed = discord.Embed(
            title=(
                f"🏆 CONQUISTAS • "
                f"{membro.display_name}"
            ),
            description=(
                f"Progresso de conquistas de "
                f"**{membro.display_name}**.\n\n"

                f"💎 **Pontos:** "
                f"**{pontos}**\n"

                f"🏆 **Desbloqueadas:** "
                f"**{len(desbloqueadas)}/"
                f"{len(CONQUISTAS)}**"
            ),
            color=COR_ROSA
        )

        for conquista_id, conquista in (
            CONQUISTAS.items()
        ):

            if conquista_id in desbloqueadas:

                estado = (
                    f"✅ **Desbloqueada**\n"
                    f"💎 {conquista['pontos']} pontos"
                )

            else:

                estado = (
                    "🔒 **Bloqueada**"
                )

            embed.add_field(
                name=(
                    f"{conquista['emoji']} "
                    f"{conquista['nome']}"
                ),
                value=(
                    f"{conquista['descricao']}\n"
                    f"{estado}"
                ),
                inline=False
            )

        embed.set_thumbnail(
            url=membro.display_avatar.url
        )

        embed.set_footer(
            text=NOME_SISTEMA
        )

        return embed

    # ========================================================
    # ANUNCIAR CONQUISTAS
    # ========================================================

    async def anunciar_conquistas(
        self,
        ctx,
        ids
    ):

        if not ids:

            return

        linhas = []

        for conquista_id in ids:

            conquista = CONQUISTAS.get(
                conquista_id
            )

            if conquista is None:

                continue

            linhas.append(
                (
                    f"{conquista['emoji']} "
                    f"**{conquista['nome']}**\n"
                    f"{conquista['descricao']}\n"
                    f"💎 **+{conquista['pontos']} pontos**"
                )
            )

        if not linhas:

            return

        embed = discord.Embed(
            title="🎉 NOVA CONQUISTA!",
            description=(
                f"{ctx.author.mention}, "
                "você acabou de desbloquear:"
            ),
            color=COR_AMARELO
        )

        embed.add_field(
            name="🏆 Desbloqueios",
            value="\n\n".join(
                linhas
            ),
            inline=False
        )

        await ctx.send(
            embed=embed,
            delete_after=15
        )

    # ========================================================
    # !SHIP
    # ========================================================

    @commands.command(
        name="ship",
        description=(
            "Calcula uma compatibilidade recreativa."
        )
    )
    @commands.guild_only()
    @commands.cooldown(
        3,
        10,
        commands.BucketType.user
    )
    async def ship(
        self,
        ctx,
        pessoa1: discord.Member = None,
        pessoa2: discord.Member = None
    ):

        pessoa1 = (
            pessoa1
            or ctx.author
        )

        if pessoa2 is None:

            pessoa2 = (
                self.escolher_membro_aleatorio(
                    ctx.guild,
                    pessoa1.id
                )
            )

            if pessoa2 is None:

                await ctx.send(
                    embed=discord.Embed(
                        title="❌ SHIP IMPOSSÍVEL",
                        description=(
                            "Não encontrei outra "
                            "pessoa disponível."
                        ),
                        color=COR_ERRO
                    )
                )

                return

        if pessoa1.bot or pessoa2.bot:

            await ctx.send(
                embed=discord.Embed(
                    title="🤖 SHIP BLOQUEADO",
                    description=(
                        "O sistema é voltado "
                        "para membros humanos."
                    ),
                    color=COR_AVISO
                )
            )

            return

        if pessoa1.id == pessoa2.id:

            await ctx.send(
                embed=discord.Embed(
                    title="💅 SHIP SOLO",
                    description=(
                        f"{pessoa1.mention}\n\n"

                        "💗 **100% de autoestima**\n\n"

                        "O algoritmo decidiu que "
                        "você combina perfeitamente "
                        "com você mesmo."
                    ),
                    color=COR_ROSA
                )
            )

            return

        resultado, novas = (
            self.obter_ou_criar_ship(
                pessoa1,
                pessoa2
            )
        )

        embed = self.criar_embed_ship(
            pessoa1,
            pessoa2,
            resultado
        )

        view = ShipView(
            self,
            pessoa1,
            pessoa2,
            ctx.author.id
        )

        await ctx.send(
            embed=embed,
            view=view
        )

        novas_autor = novas.get(
            str(
                ctx.author.id
            ),
            []
        )

        await self.anunciar_conquistas(
            ctx,
            novas_autor
        )

    # ========================================================
    # !SHIPPERFIL
    # ========================================================

    @commands.command(
        name="shipperfil",
        description=(
            "Mostra as estatísticas de um membro."
        )
    )
    @commands.guild_only()
    async def shipperfil(
        self,
        ctx,
        membro: discord.Member = None
    ):

        membro = (
            membro
            or ctx.author
        )

        usuario = self.registrar_usuario(
            membro.id
        )

        maior = int(
            usuario.get(
                "maior_compatibilidade",
                0
            )
        )

        categoria = classificar(
            maior
        )

        pontos = int(
            usuario.get(
                "pontos_conquistas",
                0
            )
        )

        conquistas = len(
            usuario.get(
                "conquistas",
                []
            )
        )

        embed = discord.Embed(
            title=(
                f"💘 SHIP PERFIL • "
                f"{membro.display_name}"
            ),
            description=(
                f"Perfil recreativo de "
                f"**{membro.display_name}**."
            ),
            color=categoria[
                "cor"
            ]
        )

        embed.set_thumbnail(
            url=membro.display_avatar.url
        )

        embed.add_field(
            name="💞 Ships diferentes",
            value=(
                f"**{usuario.get('ships_realizados', 0)}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🔥 Ships ≥ 80%",
            value=(
                f"**{usuario.get('ships_altos', 0)}**"
            ),
            inline=True
        )

        embed.add_field(
            name="💗 Maior compatibilidade",
            value=(
                f"**{maior}%**"
            ),
            inline=True
        )

        embed.add_field(
            name="🏆 Conquistas",
            value=(
                f"**{conquistas}/"
                f"{len(CONQUISTAS)}**"
            ),
            inline=True
        )

        embed.add_field(
            name="💎 Pontos",
            value=(
                f"**{pontos}**"
            ),
            inline=True
        )

        embed.add_field(
            name="👑 Título",
            value=(
                f"{categoria['emoji']} "
                f"{categoria['nome']}"
            ),
            inline=True
        )

        embed.set_footer(
            text=NOME_SISTEMA
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # !SHIPCONQUISTAS
    # ========================================================

    @commands.command(
        name="shipconquistas",
        aliases=[
            "shipachievements"
        ],
        description=(
            "Mostra as conquistas de um membro."
        )
    )
    @commands.guild_only()
    async def shipconquistas(
        self,
        ctx,
        membro: discord.Member = None
    ):

        membro = (
            membro
            or ctx.author
        )

        await ctx.send(
            embed=self.criar_embed_conquistas(
                membro
            )
        )

    # ========================================================
    # !SHIPTOP
    # ========================================================

    @commands.command(
        name="shiptop",
        aliases=[
            "shipranking"
        ],
        description=(
            "Mostra os maiores ships."
        )
    )
    @commands.guild_only()
    async def shiptop(
        self,
        ctx
    ):

        ranking = []

        for resultado in self.dados[
            "ships"
        ].values():

            try:

                porcentagem = int(
                    resultado[
                        "porcentagem"
                    ]
                )

                id1 = int(
                    resultado[
                        "id1"
                    ]
                )

                id2 = int(
                    resultado[
                        "id2"
                    ]
                )

            except (
                KeyError,
                TypeError,
                ValueError
            ):

                continue

            ranking.append(
                (
                    porcentagem,
                    id1,
                    id2,
                    resultado
                )
            )

        ranking.sort(
            key=lambda item: item[0],
            reverse=True
        )

        ranking = ranking[:10]

        embed = discord.Embed(
            title="🏆 ROYALT • TOP SHIPS",
            description=(
                "Os maiores ships registrados."
            ),
            color=COR_ROSA
        )

        if not ranking:

            embed.add_field(
                name="📭 Sem resultados",
                value=(
                    "Ainda não existem ships."
                ),
                inline=False
            )

        else:

            medalhas = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            for indice, (
                porcentagem,
                id1,
                id2,
                resultado
            ) in enumerate(
                ranking,
                start=1
            ):

                membro1 = (
                    ctx.guild.get_member(
                        id1
                    )
                )

                membro2 = (
                    ctx.guild.get_member(
                        id2
                    )
                )

                nome1 = (
                    membro1.display_name
                    if membro1
                    else f"Usuário {id1}"
                )

                nome2 = (
                    membro2.display_name
                    if membro2
                    else f"Usuário {id2}"
                )

                medalha = (
                    medalhas.get(
                        indice,
                        f"`#{indice}`"
                    )
                )

                categoria = classificar(
                    porcentagem
                )

                embed.add_field(
                    name=(
                        f"{medalha} "
                        f"{categoria['emoji']} "
                        f"{nome1} × {nome2}"
                    ),
                    value=(
                        f"💗 **{porcentagem}%**\n"
                        f"💍 `{resultado.get('nome_ship', 'Ship')}`"
                    ),
                    inline=False
                )

        embed.set_footer(
            text=NOME_SISTEMA
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # !SHIPCONQUISTATOP
    # ========================================================

    @commands.command(
        name="shipconquistranking",
        aliases=[
            "shipconquistatop",
            "shiprank"
        ],
        description=(
            "Mostra o ranking de conquistas."
        )
    )
    @commands.guild_only()
    async def shipconquistranking(
        self,
        ctx
    ):

        ranking = []

        for usuario_id, usuario in (
            self.dados[
                "usuarios"
            ].items()
        ):

            pontos = int(
                usuario.get(
                    "pontos_conquistas",
                    0
                )
            )

            quantidade = len(
                usuario.get(
                    "conquistas",
                    []
                )
            )

            if pontos <= 0:

                continue

            ranking.append(
                (
                    pontos,
                    quantidade,
                    int(usuario_id)
                )
            )

        ranking.sort(
            key=lambda item: (
                item[0],
                item[1]
            ),
            reverse=True
        )

        ranking = ranking[:10]

        embed = discord.Embed(
            title=(
                "🏆 ROYALT • "
                "RANKING DE CONQUISTAS"
            ),
            description=(
                "Os maiores colecionadores "
                "de conquistas."
            ),
            color=COR_AMARELO
        )

        if not ranking:

            embed.add_field(
                name="📭 Ranking vazio",
                value=(
                    "Ninguém desbloqueou "
                    "conquistas ainda."
                ),
                inline=False
            )

        else:

            medalhas = {

                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            for indice, (
                pontos,
                quantidade,
                usuario_id
            ) in enumerate(
                ranking,
                start=1
            ):

                membro = (
                    ctx.guild.get_member(
                        usuario_id
                    )
                )

                if membro:

                    nome = (
                        membro.display_name
                    )

                else:

                    nome = (
                        f"Usuário {usuario_id}"
                    )

                medalha = (
                    medalhas.get(
                        indice,
                        f"`#{indice}`"
                    )
                )

                embed.add_field(
                    name=(
                        f"{medalha} "
                        f"{nome}"
                    ),
                    value=(
                        f"💎 **{pontos} pontos**\n"
                        f"🏆 **{quantidade} conquistas**"
                    ),
                    inline=False
                )

        embed.set_footer(
            text=NOME_SISTEMA
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # !SHIPINFO
    # ========================================================

    @commands.command(
        name="shipinfo",
        aliases=[
            "shipstats"
        ],
        description=(
            "Mostra as estatísticas gerais."
        )
    )
    @commands.guild_only()
    async def shipinfo(
        self,
        ctx
    ):

        estatisticas = self.dados[
            "estatisticas"
        ]

        total = int(
            estatisticas.get(
                "total_ships",
                0
            )
        )

        ships100 = int(
            estatisticas.get(
                "ships_100",
                0
            )
        )

        recorde = int(
            estatisticas.get(
                "maior_ship",
                0
            )
        )

        dupla_id = estatisticas.get(
            "dupla_maior_ship"
        )

        dupla = "Nenhuma"

        if (
            isinstance(
                dupla_id,
                list
            )
            and len(dupla_id) == 2
        ):

            membro1 = (
                ctx.guild.get_member(
                    int(
                        dupla_id[0]
                    )
                )
            )

            membro2 = (
                ctx.guild.get_member(
                    int(
                        dupla_id[1]
                    )
                )
            )

            nome1 = (
                membro1.display_name
                if membro1
                else "Usuário"
            )

            nome2 = (
                membro2.display_name
                if membro2
                else "Usuário"
            )

            dupla = (
                f"{nome1} × {nome2}"
            )

        embed = discord.Embed(
            title="📊 ROYALT • SHIP SYSTEM",
            description=(
                "Estatísticas globais "
                "do sistema."
            ),
            color=COR_ROXO
        )

        embed.add_field(
            name="💞 Ships registrados",
            value=f"**{total}**",
            inline=True
        )

        embed.add_field(
            name="💯 Ships de 100%",
            value=f"**{ships100}**",
            inline=True
        )

        embed.add_field(
            name="🔥 Recorde",
            value=f"**{recorde}%**",
            inline=True
        )

        embed.add_field(
            name="🏆 Maior dupla",
            value=dupla,
            inline=False
        )

        embed.add_field(
            name="🎖️ Conquistas",
            value=f"**{len(CONQUISTAS)}**",
            inline=True
        )

        embed.add_field(
            name="💎 Sistema de pontos",
            value="Ativo",
            inline=True
        )

        embed.set_footer(
            text=(
                f"{NOME_SISTEMA} "
                f"• v{VERSAO_SISTEMA}"
            )
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# VIEW DO SHIP
# ============================================================

class ShipView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        pessoa1,
        pessoa2,
        autor_id
    ):

        super().__init__(
            timeout=180
        )

        self.cog = cog

        self.pessoa1 = pessoa1

        self.pessoa2 = pessoa2

        self.autor_id = autor_id

    # ========================================================
    # CHECK
    # ========================================================

    async def interaction_check(
        self,
        interaction
    ):

        if (
            interaction.user.id
            != self.autor_id
        ):

            await interaction.response.send_message(
                "❌ Apenas quem executou "
                "o comando pode usar "
                "estes botões.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # NOVO SHIP
    # ========================================================

    @discord.ui.button(
        label="Novo Ship",
        emoji="💘",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def novo_ship(
        self,
        interaction,
        button
    ):

        membro = (
            self.cog.escolher_membro_aleatorio(
                interaction.guild,
                self.autor_id
            )
        )

        if membro is None:

            await interaction.response.send_message(
                "❌ Não encontrei outra pessoa disponível.",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🎲 ROYALT • NOVA DUPLA",
                description=(
                    "🎯 O algoritmo escolheu uma "
                    "nova combinação...\n\n"

                    "💫 Preparando os dados...\n"
                    "💗 Calculando compatibilidade..."
                ),
                color=COR_ROSA
            ),
            view=None
        )

        await asyncio.sleep(
            0.8
        )

        resultado, novas = (
            self.cog.obter_ou_criar_ship(
                interaction.user,
                membro
            )
        )

        embed = (
            self.cog.criar_embed_ship(
                interaction.user,
                membro,
                resultado
            )
        )

        await interaction.edit_original_response(
            embed=embed,
            view=ShipView(
                self.cog,
                interaction.user,
                membro,
                interaction.user.id
            )
        )

        novas_autor = novas.get(
            str(
                interaction.user.id
            ),
            []
        )

        if novas_autor:

            linhas = []

            for conquista_id in novas_autor:

                conquista = (
                    CONQUISTAS.get(
                        conquista_id
                    )
                )

                if conquista:

                    linhas.append(
                        (
                            f"{conquista['emoji']} "
                            f"**{conquista['nome']}** "
                            f"+{conquista['pontos']} 💎"
                        )
                    )

            if linhas:

                await interaction.followup.send(
                    embed=discord.Embed(
                        title="🏆 NOVA CONQUISTA!",
                        description="\n".join(
                            linhas
                        ),
                        color=COR_AMARELO
                    ),
                    ephemeral=True
                )

    # ========================================================
    # REFAZER SHIP
    # ========================================================

    @discord.ui.button(
        label="Refazer Ship",
        emoji="🔄",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def refazer(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="🔄 ROYALT • RECALCULANDO",
                description=(
                    "🎲 Os dados estão girando...\n\n"

                    "🧠 Revisando a matemática...\n"
                    "💗 recalculando a compatibilidade...\n"
                    "✨ procurando um novo resultado..."
                ),
                color=COR_ROXO
            ),
            view=None
        )

        await asyncio.sleep(
            1.0
        )

        resultado, novas = (
            self.cog.refazer_ship(
                self.pessoa1,
                self.pessoa2
            )
        )

        embed = (
            self.cog.criar_embed_ship(
                self.pessoa1,
                self.pessoa2,
                resultado
            )
        )

        await interaction.edit_original_response(
            embed=embed,
            view=ShipView(
                self.cog,
                self.pessoa1,
                self.pessoa2,
                self.autor_id
            )
        )

        novas_autor = novas.get(
            str(
                interaction.user.id
            ),
            []
        )

        if novas_autor:

            linhas = []

            for conquista_id in novas_autor:

                conquista = (
                    CONQUISTAS.get(
                        conquista_id
                    )
                )

                if conquista:

                    linhas.append(
                        (
                            f"{conquista['emoji']} "
                            f"**{conquista['nome']}** "
                            f"+{conquista['pontos']} 💎"
                        )
                    )

            if linhas:

                await interaction.followup.send(
                    embed=discord.Embed(
                        title="🏆 NOVA CONQUISTA!",
                        description="\n".join(
                            linhas
                        ),
                        color=COR_AMARELO
                    ),
                    ephemeral=True
                )

    # ========================================================
    # CONQUISTAS
    # ========================================================

    @discord.ui.button(
        label="Conquistas",
        emoji="🏆",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def conquistas(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            embed=(
                self.cog.criar_embed_conquistas(
                    interaction.user
                )
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
            content="💘 Resultado fechado.",
            embed=None,
            view=None
        )

        self.stop()


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Ship(
            bot
        )
    )