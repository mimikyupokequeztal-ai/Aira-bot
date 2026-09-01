import asyncio
import json
import random
import sqlite3

from datetime import datetime, timezone
from pathlib import Path

import aiohttp
import discord
from discord import app_commands

from discord.ext import commands, tasks


# ============================================================
# ROYALT • POKÉMON SYSTEM
# ============================================================

NOME_SISTEMA = "Royalt Pokémon System"
VERSAO = "2.3v"

DONO_ROYALT_ID = 1527022875444379751


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

BANCO_POKEMON = (
    PASTA_DATA / "pokemon.db"
)


# ============================================================
# API
# ============================================================

POKEAPI = (
    "https://pokeapi.co/api/v2"
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

POKECOINS_INICIAL = 500
POKEBALL_INICIAL = 10

LIMITE_EQUIPE = 6

TEMPO_ENCONTRO = 20

COOLDOWN_EXPLORAR = 30
COOLDOWN_BATALHA = 60

# EVENTOS DE EXPLORAÇÃO / PvE
# Após as primeiras 3 explorações, o combate surge 1 ou 2 explorações depois.
# Depois de cada combate, uma nova meta de 4 ou 5 explorações é sorteada.
EXPLORACOES_PVE_MIN = 4
EXPLORACOES_PVE_MAX = 5

# ECONOMIA
COOLDOWN_DAILY = 86400
RECOMPENSA_DAILY_MIN = 300
RECOMPENSA_DAILY_MAX = 600
POKECAIXA_BONUS_POR_STREAK = 50
POKECAIXA_BONUS_MAX = 500
POKECAIXA_BONUS_SEMANA = 500
RECOMPENSA_EXPLORAR_MIN = 10
RECOMPENSA_EXPLORAR_MAX = 30
RECOMPENSA_CAPTURA = {
    "comum": (50, 80),
    "incomum": (70, 110),
    "raro": (100, 160),
    "epico": (150, 230),
    "lendario": (250, 400)
}
BONUS_SHINY = 250
RECOMPENSA_BATALHA_VITORIA = (120, 220)
RECOMPENSA_BATALHA_DERROTA = (25, 60)

XP_POR_NIVEL = 100


# ============================================================
# CORES
# ============================================================

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

COR_VERMELHO = discord.Color.from_rgb(
    231,
    76,
    60
)

COR_AMARELO = discord.Color.from_rgb(
    241,
    196,
    15
)

COR_ROXO = discord.Color.from_rgb(
    155,
    89,
    182
)

COR_ROSA = discord.Color.from_rgb(
    255,
    105,
    180
)

COR_LARANJA = discord.Color.from_rgb(
    255,
    159,
    67
)

COR_CIANO = discord.Color.from_rgb(
    0,
    206,
    209
)

COR_CINZA = discord.Color.from_rgb(
    149,
    165,
    166
)


# ============================================================
# STARTERS
# ============================================================

STARTERS = {

    "bulbasaur": {
        "id": 1, "nome": "Bulbasaur", "emoji": "🌱", "regiao": "kanto"
    },
    "charmander": {
        "id": 4, "nome": "Charmander", "emoji": "🔥", "regiao": "kanto"
    },
    "squirtle": {
        "id": 7, "nome": "Squirtle", "emoji": "💧", "regiao": "kanto"
    }
}

# Um trio oficial de iniciais por geração/região.
STARTERS_POR_REGIAO = {
    "kanto": [
        {"id": 1, "nome": "Bulbasaur", "emoji": "🌱"},
        {"id": 4, "nome": "Charmander", "emoji": "🔥"},
        {"id": 7, "nome": "Squirtle", "emoji": "💧"},
    ],
    "johto": [
        {"id": 152, "nome": "Chikorita", "emoji": "🌿"},
        {"id": 155, "nome": "Cyndaquil", "emoji": "🔥"},
        {"id": 158, "nome": "Totodile", "emoji": "💧"},
    ],
    "hoenn": [
        {"id": 252, "nome": "Treecko", "emoji": "🌿"},
        {"id": 255, "nome": "Torchic", "emoji": "🔥"},
        {"id": 258, "nome": "Mudkip", "emoji": "💧"},
    ],
    "sinnoh": [
        {"id": 387, "nome": "Turtwig", "emoji": "🌿"},
        {"id": 390, "nome": "Chimchar", "emoji": "🔥"},
        {"id": 393, "nome": "Piplup", "emoji": "💧"},
    ],
    "unova": [
        {"id": 495, "nome": "Snivy", "emoji": "🌿"},
        {"id": 498, "nome": "Tepig", "emoji": "🔥"},
        {"id": 501, "nome": "Oshawott", "emoji": "💧"},
    ],
    "kalos": [
        {"id": 650, "nome": "Chespin", "emoji": "🌿"},
        {"id": 653, "nome": "Fennekin", "emoji": "🔥"},
        {"id": 656, "nome": "Froakie", "emoji": "💧"},
    ],
    "alola": [
        {"id": 722, "nome": "Rowlet", "emoji": "🌿"},
        {"id": 725, "nome": "Litten", "emoji": "🔥"},
        {"id": 728, "nome": "Popplio", "emoji": "💧"},
    ],
    "galar": [
        {"id": 810, "nome": "Grookey", "emoji": "🌿"},
        {"id": 813, "nome": "Scorbunny", "emoji": "🔥"},
        {"id": 816, "nome": "Sobble", "emoji": "💧"},
    ],
    "paldea": [
        {"id": 906, "nome": "Sprigatito", "emoji": "🌿"},
        {"id": 909, "nome": "Fuecoco", "emoji": "🔥"},
        {"id": 912, "nome": "Quaxly", "emoji": "💧"},
    ],
}


# ============================================================
# REGIÕES
# ============================================================

REGIOES = {

    "kanto": {"nome": "Kanto", "emoji": "🌿", "min_id": 1, "max_id": 151},
    "johto": {"nome": "Johto", "emoji": "🌸", "min_id": 152, "max_id": 251},
    "hoenn": {"nome": "Hoenn", "emoji": "🏝️", "min_id": 252, "max_id": 386},
    "sinnoh": {"nome": "Sinnoh", "emoji": "⛰️", "min_id": 387, "max_id": 493},
    "unova": {"nome": "Unova", "emoji": "🏙️", "min_id": 494, "max_id": 649},
    "kalos": {"nome": "Kalos", "emoji": "🗼", "min_id": 650, "max_id": 721},
    "alola": {"nome": "Alola", "emoji": "🌺", "min_id": 722, "max_id": 809},
    "galar": {"nome": "Galar", "emoji": "⚔️", "min_id": 810, "max_id": 905},
    "paldea": {"nome": "Paldea", "emoji": "🏫", "min_id": 906, "max_id": 1025},
}

# A cada 15 níveis uma nova região fica disponível.
NIVEIS_REGIAO = {
    regiao: (indice + 1) * 15
    for indice, regiao in enumerate(REGIOES)
}

# Conteúdo especial da Pokédex Royalt.
# Estes registros são regras próprias do servidor e podem ser ampliados
# sem alterar o navegador dos 1025 Pokémon.
POKEDEX_ESPECIAIS = {
    "conquistas": [
        {"pokemon_id": 133, "nome": "Eevee", "regra": "Sylveon pode exigir a conquista Mestre dos Golpes."},
        {"pokemon_id": 236, "nome": "Tyrogue", "regra": "As três evoluções podem exigir conquistas diferentes de batalha/evolução."},
        {"pokemon_id": 447, "nome": "Riolu", "regra": "Lucario pode exigir a conquista Treinador de Campo."},
        {"pokemon_id": 458, "nome": "Mantyke", "regra": "Registro reservado para requisitos especiais do servidor."},
    ],
    "ginasios": [
        {"pokemon_id": 150, "nome": "Mewtwo", "regra": "Disponível somente em conteúdo especial de ginásio/evento."},
        {"pokemon_id": 249, "nome": "Lugia", "regra": "Disponível em conteúdo especial de Johto."},
        {"pokemon_id": 250, "nome": "Ho-Oh", "regra": "Disponível em conteúdo especial de Johto."},
        {"pokemon_id": 384, "nome": "Rayquaza", "regra": "Disponível em conteúdo especial de Hoenn."},
        {"pokemon_id": 487, "nome": "Giratina", "regra": "Disponível em conteúdo especial de Sinnoh."},
        {"pokemon_id": 643, "nome": "Reshiram", "regra": "Disponível em conteúdo especial de Unova."},
        {"pokemon_id": 644, "nome": "Zekrom", "regra": "Disponível em conteúdo especial de Unova."},
        {"pokemon_id": 716, "nome": "Xerneas", "regra": "Disponível em conteúdo especial de Kalos."},
        {"pokemon_id": 717, "nome": "Yveltal", "regra": "Disponível em conteúdo especial de Kalos."},
        {"pokemon_id": 800, "nome": "Necrozma", "regra": "Disponível em conteúdo especial de Alola."},
        {"pokemon_id": 888, "nome": "Zacian", "regra": "Disponível em conteúdo especial de Galar."},
        {"pokemon_id": 889, "nome": "Zamazenta", "regra": "Disponível em conteúdo especial de Galar."},
        {"pokemon_id": 1007, "nome": "Koraidon", "regra": "Disponível em conteúdo especial de Paldea."},
        {"pokemon_id": 1008, "nome": "Miraidon", "regra": "Disponível em conteúdo especial de Paldea."},
    ],
}


# ============================================================
# GINÁSIOS / INSÍGNIAS / ELITE 4
# ============================================================
# Alola e Galar recebem uma Liga adaptada no mesmo formato das
# demais regiões para manter a progressão uniforme do Royalt.
GINASIOS = {
    "kanto": {
        "nome": 'Kanto',
        "emoji": '🌿',
        "ginasios": [
            {"numero": 1, "lider": 'Brock', "insignia": 'Boulder', "pokemon": [95, 111, 76]},
            {"numero": 2, "lider": 'Misty', "insignia": 'Cascade', "pokemon": [120, 121, 55]},
            {"numero": 3, "lider": 'Lt. Surge', "insignia": 'Thunder', "pokemon": [26, 101, 125]},
            {"numero": 4, "lider": 'Erika', "insignia": 'Rainbow', "pokemon": [45, 71, 114]},
            {"numero": 5, "lider": 'Koga', "insignia": 'Soul', "pokemon": [110, 89, 49]},
            {"numero": 6, "lider": 'Sabrina', "insignia": 'Marsh', "pokemon": [65, 122, 124]},
            {"numero": 7, "lider": 'Blaine', "insignia": 'Volcano', "pokemon": [59, 78, 126]},
            {"numero": 8, "lider": 'Giovanni', "insignia": 'Earth', "pokemon": [111, 31, 51]},
        ],
        "elite4": ['Lorelei', 'Bruno', 'Agatha', 'Lance'],
    },
    "johto": {
        "nome": 'Johto',
        "emoji": '🌸',
        "ginasios": [
            {"numero": 1, "lider": 'Falkner', "insignia": 'Zephyr', "pokemon": [17, 18, 22]},
            {"numero": 2, "lider": 'Bugsy', "insignia": 'Hive', "pokemon": [12, 123, 127]},
            {"numero": 3, "lider": 'Whitney', "insignia": 'Plain', "pokemon": [241, 36, 241]},
            {"numero": 4, "lider": 'Morty', "insignia": 'Fog', "pokemon": [94, 93, 200]},
            {"numero": 5, "lider": 'Chuck', "insignia": 'Storm', "pokemon": [67, 57, 237]},
            {"numero": 6, "lider": 'Jasmine', "insignia": 'Mineral', "pokemon": [208, 212, 82]},
            {"numero": 7, "lider": 'Pryce', "insignia": 'Glacier', "pokemon": [124, 221, 87]},
            {"numero": 8, "lider": 'Clair', "insignia": 'Rising', "pokemon": [230, 130, 149]},
        ],
        "elite4": ['Will', 'Koga', 'Bruno', 'Karen'],
    },
    "hoenn": {
        "nome": 'Hoenn',
        "emoji": '🏝️',
        "ginasios": [
            {"numero": 1, "lider": 'Roxanne', "insignia": 'Stone', "pokemon": [74, 299, 185]},
            {"numero": 2, "lider": 'Brawly', "insignia": 'Knuckle', "pokemon": [296, 297, 307]},
            {"numero": 3, "lider": 'Wattson', "insignia": 'Dynamo', "pokemon": [100, 82, 310]},
            {"numero": 4, "lider": 'Flannery', "insignia": 'Heat', "pokemon": [218, 324, 323]},
            {"numero": 5, "lider": 'Norman', "insignia": 'Balance', "pokemon": [327, 288, 289]},
            {"numero": 6, "lider": 'Winona', "insignia": 'Feather', "pokemon": [333, 357, 279]},
            {"numero": 7, "lider": 'Tate & Liza', "insignia": 'Mind', "pokemon": [344, 337, 338]},
            {"numero": 8, "lider": 'Wallace', "insignia": 'Rain', "pokemon": [370, 340, 350]},
        ],
        "elite4": ['Sidney', 'Phoebe', 'Glacia', 'Drake'],
    },
    "sinnoh": {
        "nome": 'Sinnoh',
        "emoji": '⛰️',
        "ginasios": [
            {"numero": 1, "lider": 'Roark', "insignia": 'Coal', "pokemon": [74, 95, 408]},
            {"numero": 2, "lider": 'Gardenia', "insignia": 'Forest', "pokemon": [407, 315, 388]},
            {"numero": 3, "lider": 'Maylene', "insignia": 'Cobble', "pokemon": [67, 308, 448]},
            {"numero": 4, "lider": 'Crasher Wake', "insignia": 'Fen', "pokemon": [130, 340, 195]},
            {"numero": 5, "lider": 'Fantina', "insignia": 'Relic', "pokemon": [426, 429, 442]},
            {"numero": 6, "lider": 'Byron', "insignia": 'Mine', "pokemon": [208, 305, 411]},
            {"numero": 7, "lider": 'Candice', "insignia": 'Icicle', "pokemon": [460, 478, 471]},
            {"numero": 8, "lider": 'Volkner', "insignia": 'Beacon', "pokemon": [405, 466, 462]},
        ],
        "elite4": ['Aaron', 'Bertha', 'Flint', 'Lucian'],
    },
    "unova": {
        "nome": 'Unova',
        "emoji": '🏙️',
        "ginasios": [
            {"numero": 1, "lider": 'Cilan', "insignia": 'Trio', "pokemon": [511, 512, 513]},
            {"numero": 2, "lider": 'Lenora', "insignia": 'Basic', "pokemon": [505, 507, 518]},
            {"numero": 3, "lider": 'Burgh', "insignia": 'Insect', "pokemon": [542, 545, 557]},
            {"numero": 4, "lider": 'Elesa', "insignia": 'Bolt', "pokemon": [587, 181, 596]},
            {"numero": 5, "lider": 'Clay', "insignia": 'Quake', "pokemon": [530, 552, 558]},
            {"numero": 6, "lider": 'Skyla', "insignia": 'Jet', "pokemon": [581, 528, 227]},
            {"numero": 7, "lider": 'Brycen', "insignia": 'Freeze', "pokemon": [614, 615, 620]},
            {"numero": 8, "lider": 'Drayden', "insignia": 'Legend', "pokemon": [621, 612, 334]},
        ],
        "elite4": ['Shauntal', 'Marshal', 'Grimsley', 'Caitlin'],
    },
    "kalos": {
        "nome": 'Kalos',
        "emoji": '🗼',
        "ginasios": [
            {"numero": 1, "lider": 'Viola', "insignia": 'Bug', "pokemon": [283, 123, 666]},
            {"numero": 2, "lider": 'Grant', "insignia": 'Cliff', "pokemon": [696, 698, 699]},
            {"numero": 3, "lider": 'Korrina', "insignia": 'Rumble', "pokemon": [701, 448, 67]},
            {"numero": 4, "lider": 'Ramos', "insignia": 'Plant', "pokemon": [188, 254, 275]},
            {"numero": 5, "lider": 'Clemont', "insignia": 'Voltage', "pokemon": [702, 695, 82]},
            {"numero": 6, "lider": 'Valerie', "insignia": 'Fairy', "pokemon": [122, 303, 700]},
            {"numero": 7, "lider": 'Olympia', "insignia": 'Psychic', "pokemon": [561, 337, 678]},
            {"numero": 8, "lider": 'Wulfric', "insignia": 'Iceberg', "pokemon": [713, 614, 362]},
        ],
        "elite4": ['Malva', 'Siebold', 'Wikstrom', 'Drasna'],
    },
    "alola": {
        "nome": 'Alola',
        "emoji": '🌺',
        "ginasios": [
            {"numero": 1, "lider": 'Hala', "insignia": 'Fighting', "pokemon": [739, 67, 297]},
            {"numero": 2, "lider": 'Olivia', "insignia": 'Rock', "pokemon": [74, 745, 248]},
            {"numero": 3, "lider": 'Nanu', "insignia": 'Dark', "pokemon": [53, 275, 630]},
            {"numero": 4, "lider": 'Hapu', "insignia": 'Ground', "pokemon": [749, 750, 623]},
            {"numero": 5, "lider": 'Mina', "insignia": 'Fairy', "pokemon": [707, 682, 700]},
            {"numero": 6, "lider": 'Acerola', "insignia": 'Ghost', "pokemon": [778, 768, 681]},
            {"numero": 7, "lider": 'Mallow', "insignia": 'Grass', "pokemon": [753, 762, 286]},
            {"numero": 8, "lider": 'Lana', "insignia": 'Water', "pokemon": [746, 594, 195]},
        ],
        "elite4": ['Molayne', 'Olivia', 'Acerola', 'Kahili'],
    },
    "galar": {
        "nome": 'Galar',
        "emoji": '⚔️',
        "ginasios": [
            {"numero": 1, "lider": 'Milo', "insignia": 'Grass', "pokemon": [829, 812, 830]},
            {"numero": 2, "lider": 'Nessa', "insignia": 'Water', "pokemon": [846, 121, 834]},
            {"numero": 3, "lider": 'Kabu', "insignia": 'Fire', "pokemon": [838, 851, 324]},
            {"numero": 4, "lider": 'Bea', "insignia": 'Fighting', "pokemon": [865, 68, 889]},
            {"numero": 5, "lider": 'Opal', "insignia": 'Fairy', "pokemon": [859, 303, 869]},
            {"numero": 6, "lider": 'Gordie', "insignia": 'Rock', "pokemon": [744, 874, 874]},
            {"numero": 7, "lider": 'Piers', "insignia": 'Dark', "pokemon": [862, 861, 560]},
            {"numero": 8, "lider": 'Raihan', "insignia": 'Dragon', "pokemon": [776, 884, 887]},
        ],
        "elite4": ['Piers', 'Melony', 'Gordie', 'Raihan'],
    },
    "paldea": {
        "nome": 'Paldea',
        "emoji": '🏫',
        "ginasios": [
            {"numero": 1, "lider": 'Katy', "insignia": 'Bug', "pokemon": [919, 917, 18]},
            {"numero": 2, "lider": 'Brassius', "insignia": 'Grass', "pokemon": [928, 951, 275]},
            {"numero": 3, "lider": 'Iono', "insignia": 'Electric', "pokemon": [1009, 94, 702]},
            {"numero": 4, "lider": 'Kofu', "insignia": 'Water', "pokemon": [120, 779, 976]},
            {"numero": 5, "lider": 'Larry', "insignia": 'Normal', "pokemon": [398, 85, 20]},
            {"numero": 6, "lider": 'Ryme', "insignia": 'Ghost', "pokemon": [1056, 426, 354]},
            {"numero": 7, "lider": 'Tulip', "insignia": 'Psychic', "pokemon": [124, 678, 475]},
            {"numero": 8, "lider": 'Grusha', "insignia": 'Ice', "pokemon": [873, 713, 460]},
        ],
        "elite4": ['Rika', 'Poppy', 'Larry', 'Hassel'],
    },
}

# Tipos de especialidade usados para apresentar os líderes.
# Os Pokémon reais e seus golpes são carregados da PokéAPI.
TIPOS_GINASIO = {
    "Brock": "rock", "Misty": "water", "Lt. Surge": "electric",
    "Erika": "grass", "Koga": "poison", "Sabrina": "psychic",
    "Blaine": "fire", "Giovanni": "ground",
    "Falkner": "flying", "Bugsy": "bug", "Whitney": "normal",
    "Morty": "ghost", "Chuck": "fighting", "Jasmine": "steel",
    "Pryce": "ice", "Clair": "dragon",
    "Roxanne": "rock", "Brawly": "fighting", "Wattson": "electric",
    "Flannery": "fire", "Norman": "normal", "Winona": "flying",
    "Tate & Liza": "psychic", "Wallace": "water",
    "Roark": "rock", "Gardenia": "grass", "Maylene": "fighting",
    "Crasher Wake": "water", "Fantina": "ghost", "Byron": "steel",
    "Candice": "ice", "Volkner": "electric",
    "Cilan": "grass", "Lenora": "normal", "Burgh": "bug",
    "Elesa": "electric", "Clay": "ground", "Skyla": "flying",
    "Brycen": "ice", "Drayden": "dragon",
    "Viola": "bug", "Grant": "rock", "Korrina": "fighting",
    "Ramos": "grass", "Clemont": "electric", "Valerie": "fairy",
    "Olympia": "psychic", "Wulfric": "ice",
    "Hala": "fighting", "Olivia": "rock", "Nanu": "dark",
    "Hapu": "ground", "Mina": "fairy", "Acerola": "ghost",
    "Mallow": "grass", "Lana": "water",
    "Milo": "grass", "Nessa": "water", "Kabu": "fire", "Bea": "fighting",
    "Opal": "fairy", "Gordie": "rock", "Piers": "dark", "Raihan": "dragon",
    "Katy": "bug", "Brassius": "grass", "Iono": "electric", "Kofu": "water",
    "Larry": "normal", "Ryme": "ghost", "Tulip": "psychic", "Grusha": "ice",
}

ELITE4_TIPOS = {
    "Lorelei": "ice", "Bruno": "fighting", "Agatha": "ghost", "Lance": "dragon",
    "Will": "psychic", "Karen": "dark",
    "Sidney": "dark", "Phoebe": "ghost", "Glacia": "ice", "Drake": "dragon",
    "Aaron": "bug", "Bertha": "ground", "Flint": "fire", "Lucian": "psychic",
    "Shauntal": "ghost", "Marshal": "fighting", "Grimsley": "dark", "Caitlin": "psychic",
    "Malva": "fire", "Siebold": "water", "Wikstrom": "steel", "Drasna": "dragon",
    "Molayne": "steel", "Olivia": "rock", "Acerola": "ghost", "Kahili": "flying",
    "Melony": "ice", "Marnie": "dark", "Bede": "psychic", "Leon": "dragon",
    "Rika": "ground", "Poppy": "steel", "Hassel": "dragon",
}
# ============================================================
# RARIDADES
# ============================================================

RARIDADES = {

    "comum": {
        "nome": "Comum",
        "emoji": "⚪",
        "peso": 60
    },

    "incomum": {
        "nome": "Incomum",
        "emoji": "🟢",
        "peso": 25
    },

    "raro": {
        "nome": "Raro",
        "emoji": "🔵",
        "peso": 10
    },

    "epico": {
        "nome": "Épico",
        "emoji": "🟣",
        "peso": 4
    },

    "lendario": {
        "nome": "Lendário",
        "emoji": "🟡",
        "peso": 1
    }
}


# ============================================================
# SISTEMA DE IV / STATUS DOS POKÉMON
# ============================================================

IV_MAX = 31
XP_POKEMON_POR_NIVEL = 100

STARTER_BASE_STATS = {
    1: {"hp": 45, "ataque": 49, "defesa": 49, "velocidade": 45},
    4: {"hp": 39, "ataque": 52, "defesa": 43, "velocidade": 65},
    7: {"hp": 44, "ataque": 48, "defesa": 65, "velocidade": 43},
}


def extrair_base_stats_pokeapi(dados):
    resultado = {
        "hp": 50,
        "ataque": 50,
        "defesa": 50,
        "velocidade": 50,
    }
    if not dados:
        return resultado

    mapa = {
        "hp": "hp",
        "attack": "ataque",
        "defense": "defesa",
        "speed": "velocidade",
    }

    for item in dados.get("stats", []):
        nome = item.get("stat", {}).get("name")
        chave = mapa.get(nome)
        if chave:
            resultado[chave] = max(1, int(item.get("base_stat", 50)))

    return resultado


def gerar_ivs():
    return {
        "iv_hp": random.randint(0, IV_MAX),
        "iv_ataque": random.randint(0, IV_MAX),
        "iv_defesa": random.randint(0, IV_MAX),
        "iv_velocidade": random.randint(0, IV_MAX),
    }


def calcular_stats_pokemon(base_stats, ivs, nivel):
    nivel = max(1, int(nivel))
    hp = int(((2 * int(base_stats["hp"]) + int(ivs["iv_hp"])) * nivel) / 100) + nivel + 10
    ataque = int(((2 * int(base_stats["ataque"]) + int(ivs["iv_ataque"])) * nivel) / 100) + 5
    defesa = int(((2 * int(base_stats["defesa"]) + int(ivs["iv_defesa"])) * nivel) / 100) + 5
    velocidade = int(((2 * int(base_stats["velocidade"]) + int(ivs["iv_velocidade"])) * nivel) / 100) + 5
    return {
        "hp": max(1, hp),
        "ataque": max(1, ataque),
        "defesa": max(1, defesa),
        "velocidade": max(1, velocidade),
    }


def calcular_nivel_pokemon(xp):
    return max(1, (max(0, int(xp)) // XP_POKEMON_POR_NIVEL) + 1)


def xp_atual_pokemon(xp):
    return max(0, int(xp)) % XP_POKEMON_POR_NIVEL


def barra_xp_pokemon(xp, tamanho=12):
    atual = xp_atual_pokemon(xp)
    preenchido = min(tamanho, int((atual / XP_POKEMON_POR_NIVEL) * tamanho))
    return "🟩" * preenchido + "⬛" * (tamanho - preenchido)



# ============================================================
# LOJA
# ============================================================

LOJA = {
    "pokeball": {
        "categoria": "jornada",
        "nome": "Poké Ball",
        "preco": 100,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png",
        "descricao": "Poké Ball básica para capturas."
    },
    "greatball": {
        "categoria": "jornada",
        "nome": "Great Ball",
        "preco": 250,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/great-ball.png",
        "descricao": "Melhora suas chances de captura."
    },
    "ultraball": {
        "categoria": "jornada",
        "nome": "Ultra Ball",
        "preco": 500,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ultra-ball.png",
        "descricao": "Uma Ball de alto desempenho."
    },
    "potion": {
        "categoria": "jornada",
        "nome": "Potion",
        "preco": 150,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/potion.png",
        "descricao": "Item de cura para Pokémon."
    },
    "super_potion": {
        "categoria": "jornada",
        "nome": "Super Potion",
        "preco": 300,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/super-potion.png",
        "descricao": "Cura mais forte para sua jornada."
    },
    "hyper_potion": {
        "categoria": "jornada",
        "nome": "Hyper Potion",
        "preco": 600,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/hyper-potion.png",
        "descricao": "Restauração poderosa de HP."
    },
    "revive": {
        "categoria": "jornada",
        "nome": "Revive",
        "preco": 900,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/revive.png",
        "descricao": "Item especial de recuperação."
    },
    "bottle_cap": {
        "categoria": "jornada",
        "nome": "Cápsula IV • Bottle Cap",
        "preco": 2500,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/bottle-cap.png",
        "descricao": "Recurso destinado ao sistema de IVs."
    },
    "fire_stone": {
        "categoria": "jornada", "nome": "Fire Stone", "preco": 1200,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/fire-stone.png",
        "descricao": "Pedra de Fogo para evoluções específicas."
    },
    "water_stone": {
        "categoria": "jornada", "nome": "Water Stone", "preco": 1200,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/water-stone.png",
        "descricao": "Pedra de Água para evoluções específicas."
    },
    "thunder_stone": {
        "categoria": "jornada", "nome": "Thunder Stone", "preco": 1200,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/thunder-stone.png",
        "descricao": "Pedra do Trovão para evoluções específicas."
    },
    "leaf_stone": {
        "categoria": "jornada", "nome": "Leaf Stone", "preco": 1200,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/leaf-stone.png",
        "descricao": "Pedra da Folha para evoluções específicas."
    },
    "moon_stone": {
        "categoria": "jornada", "nome": "Moon Stone", "preco": 1400,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/moon-stone.png",
        "descricao": "Pedra da Lua para evoluções específicas."
    },
    "sun_stone": {
        "categoria": "jornada", "nome": "Sun Stone", "preco": 1400,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/sun-stone.png",
        "descricao": "Pedra do Sol para evoluções específicas."
    },
    "shiny_stone": {
        "categoria": "jornada", "nome": "Shiny Stone", "preco": 1600,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/shiny-stone.png",
        "descricao": "Pedra Brilhante para evoluções específicas."
    },
    "dusk_stone": {
        "categoria": "jornada", "nome": "Dusk Stone", "preco": 1600,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dusk-stone.png",
        "descricao": "Pedra do Crepúsculo para evoluções específicas."
    },
    "dawn_stone": {
        "categoria": "jornada", "nome": "Dawn Stone", "preco": 1600,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dawn-stone.png",
        "descricao": "Pedra do Amanhecer para evoluções específicas."
    },
    "ice_stone": {
        "categoria": "jornada", "nome": "Ice Stone", "preco": 1600,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/ice-stone.png",
        "descricao": "Pedra de Gelo para evoluções específicas."
    },
    "link_cable": {
        "categoria": "jornada", "nome": "Link Cable", "preco": 2200,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/linking-cord.png",
        "descricao": "Item especial usado pelo Royalt para simular evoluções de troca."
    }
}


# ============================================================
# COSMÉTICOS DO PERFIL
# ============================================================

PERFIL_LOJA = {
    "banner_pikachu": {
        "tipo": "banner",
        "nome": "Banner • Pikachu",
        "preco": 750,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
        "valor": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
        "descricao": "Banner inspirado no Pikachu."
    },
    "banner_charizard": {
        "tipo": "banner",
        "nome": "Banner • Charizard",
        "preco": 1200,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png",
        "valor": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png",
        "descricao": "Banner inspirado no Charizard."
    },
    "banner_mewtwo": {
        "tipo": "banner",
        "nome": "Banner • Mewtwo",
        "preco": 1800,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png",
        "valor": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png",
        "descricao": "Banner inspirado no Mewtwo."
    },
    "fonte_classica": {
        "tipo": "fonte",
        "nome": "Fonte • Clássica",
        "preco": 500,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/town-map.png",
        "valor": "normal",
        "descricao": "Estilo clássico para sua bio."
    },
    "fonte_negrito": {
        "tipo": "fonte",
        "nome": "Fonte • Treinador",
        "preco": 800,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/letter-mail.png",
        "valor": "bold",
        "descricao": "Estilo em destaque para sua bio."
    },
    "fonte_mono": {
        "tipo": "fonte",
        "nome": "Fonte • Pokédex",
        "preco": 900,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/old-sea-map.png",
        "valor": "mono",
        "descricao": "Estilo inspirado em uma Pokédex."
    },
    "emblema_mestre": {
        "tipo": "emblema",
        "nome": "Emblema • Mestre Pokémon",
        "preco": 1500,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/champion-belt.png",
        "valor": "🏆",
        "descricao": "Emblema de Mestre Pokémon."
    },
    "emblema_raio": {
        "tipo": "emblema",
        "nome": "Emblema • Insígnia do Trovão",
        "preco": 1000,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/yellow-shard.png",
        "valor": "⚡",
        "descricao": "Emblema inspirado em energia elétrica."
    },
    "emblema_shiny": {
        "tipo": "emblema",
        "nome": "Emblema • Shiny Hunter",
        "preco": 2000,
        "imagem": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/shiny-stone.png",
        "valor": "✨",
        "descricao": "Emblema para caçadores de Shiny."
    }
}

POKEMON_AVISO = f"PokeAira: {VERSAO} • ⚠️ Ainda podem ocorrer bugs ou erros; informe ao servidor de suporte."


# ============================================================
# TIPOS
# ============================================================

TIPOS_EMOJIS = {

    "normal": "⚪",
    "fire": "🔥",
    "water": "💧",
    "electric": "⚡",
    "grass": "🌿",
    "ice": "❄️",
    "fighting": "🥊",
    "poison": "☠️",
    "ground": "🌍",
    "flying": "🪽",
    "psychic": "🔮",
    "bug": "🐛",
    "rock": "🪨",
    "ghost": "👻",
    "dragon": "🐉",
    "dark": "🌑",
    "steel": "⚙️",
    "fairy": "🧚"
}


# ============================================================
# CONQUISTAS
# ============================================================

# Recompensas reais das conquistas.
# Cada recompensa é aplicada dentro da mesma transação que registra a conquista,
# evitando pagamento duplicado mesmo se o comando/evento for disparado duas vezes.
RECOMPENSAS_CONQUISTAS = {
    "primeiro_pokemon": {"tipo": "coins", "quantidade": 250},
    "primeira_captura": {"tipo": "item", "item_id": "pokeball", "quantidade": 5},
    "cinco_pokemon": {"tipo": "coins", "quantidade": 500},
    "dez_pokemon": {"tipo": "item", "item_id": "greatball", "quantidade": 3},
    "primeira_evolucao": {"tipo": "coins", "quantidade": 750},
    "primeira_batalha": {"tipo": "coins", "quantidade": 500},
    "primeira_troca": {"tipo": "coins", "quantidade": 400},
    "shiny": {"tipo": "item", "item_id": "bottle_cap", "quantidade": 1},
    "lendario": {"tipo": "coins", "quantidade": 2500},
    "evolucao_item": {"tipo": "item", "item_id": "random_evolution_stone", "quantidade": 1},
    "cinco_evolucoes": {"tipo": "coins", "quantidade": 1500},
    "mestre_golpes": {"tipo": "xp_treinador", "quantidade": 1000},
    "quinze_pokemon": {"tipo": "coins", "quantidade": 1000},
    "vinte_e_cinco_pokemon": {"tipo": "item", "item_id": "ultraball", "quantidade": 1},
    "dez_capturas": {"tipo": "coins", "quantidade": 1000},
    "cinquenta_capturas": {"tipo": "item", "item_id": "greatball", "quantidade": 5},
    "dez_batalhas": {"tipo": "coins", "quantidade": 1500},
    "vinte_vitorias": {"tipo": "coins", "quantidade": 2000},
    "streak_sete": {"tipo": "coins", "quantidade": 1500},
    "nivel_15": {"tipo": "item", "item_id": "bottle_cap", "quantidade": 1},
    "nivel_30": {"tipo": "coins", "quantidade": 3000},
    "dex_50": {"tipo": "coins", "quantidade": 1500},
    "dex_150": {"tipo": "coins", "quantidade": 3500},
}

# Evoluções especiais próprias do Royalt. Elas são opcionais e ficam separadas
# das regras oficiais da PokéAPI. Isso permite criar progressão por conquistas
# sem quebrar a linha evolutiva oficial dos outros Pokémon.
EVOLUCOES_ESPECIAIS_ROYALT = {
    (133, 700): {"conquista": "mestre_golpes", "descricao": "Tenha a conquista 🗡️ Mestre dos Golpes."},
    (236, 237): {"conquista": "dez_batalhas", "descricao": "Desbloqueie 🥊 Treinador de Campo (10 batalhas)."},
    (236, 238): {"conquista": "vinte_vitorias", "descricao": "Desbloqueie 🏆 Vencedor (20 vitórias)."},
    (236, 239): {"conquista": "cinco_evolucoes", "descricao": "Desbloqueie 🧬 Mestre da Evolução (5 evoluções)."},
    (447, 448): {"conquista": "dez_batalhas", "descricao": "Desbloqueie 🥊 Treinador de Campo (10 batalhas)."},
}

CONQUISTAS = {
    # chave: emoji, nome, como_fazer, recompensa
    "primeiro_pokemon": ("🌟", "Primeiro Pokémon", "Escolha seu Pokémon inicial.", "🪙 +250 Pokécoins"),
    "primeira_captura": ("🎯", "Primeira Captura", "Capture seu primeiro Pokémon selvagem.", "🔴 +5 Poké Balls"),
    "cinco_pokemon": ("🎒", "Pequena Coleção", "Tenha pelo menos 5 Pokémon na coleção.", "🪙 +500 Pokécoins"),
    "dez_pokemon": ("📚", "Colecionador", "Tenha pelo menos 10 Pokémon na coleção.", "🔵 +3 Great Balls"),
    "primeira_evolucao": ("✨", "Evolução!", "Evolua seu primeiro Pokémon.", "🪙 +750 Pokécoins"),
    "primeira_batalha": ("⚔️", "Primeira Batalha", "Participe de sua primeira batalha Pokémon.", "🪙 +500 Pokécoins"),
    "primeira_troca": ("🔄", "Troca Justa", "Realize sua primeira troca com outro treinador.", "🪙 +400 Pokécoins"),
    "shiny": ("✨", "Brilho Raro", "Capture um Pokémon Shiny.", "💎 +1 Item raro"),
    "lendario": ("👑", "Encontro Lendário", "Capture um Pokémon Lendário.", "🪙 +2.500 Pokécoins"),
    "evolucao_item": ("🪨", "Evolução por Item", "Evolua um Pokémon usando pedra ou item evolutivo.", "🎁 +1 item evolutivo"),
    "cinco_evolucoes": ("🧬", "Mestre da Evolução", "Evolua pelo menos 5 Pokémon.", "🪙 +1.500 Pokécoins"),
    "mestre_golpes": ("⚔️", "Mestre dos Golpes", "Tenha um Pokémon com 4 golpes reais sincronizados.", "📈 +1.000 XP de treinador"),
    "quinze_pokemon": ("🗃️", "Caçador de Espécies", "Tenha pelo menos 15 Pokémon diferentes na coleção.", "🪙 +1.000 Pokécoins"),
    "vinte_e_cinco_pokemon": ("🏛️", "Museu Pokémon", "Tenha pelo menos 25 Pokémon na coleção.", "🟣 +1 Ultra Ball"),
    "dez_capturas": ("🎯", "Capturador Experiente", "Realize 10 capturas.", "🪙 +1.000 Pokécoins"),
    "cinquenta_capturas": ("🎖️", "Mestre da Captura", "Realize 50 capturas.", "🔵 +5 Great Balls"),
    "dez_batalhas": ("🥊", "Treinador de Campo", "Participe de 10 batalhas.", "🪙 +1.500 Pokécoins"),
    "vinte_vitorias": ("🏆", "Vencedor", "Alcance 20 vitórias em batalhas.", "🪙 +2.000 Pokécoins"),
    "streak_sete": ("🔥", "Semana Perfeita", "Mantenha uma sequência de 7 dias no PokéCaixa.", "🪙 +1.500 Pokécoins"),
    "nivel_15": ("⭐", "Treinador Veterano", "Alcance o nível 15 de treinador.", "🎁 +1 item especial"),
    "nivel_30": ("👑", "Mestre Regional", "Alcance o nível 30 de treinador.", "🪙 +3.000 Pokécoins"),
    "dex_50": ("📖", "Pesquisador", "Registre 50 espécies na Pokédex.", "🪙 +1.500 Pokécoins"),
    "dex_150": ("🔬", "Professor Pokémon", "Registre 150 espécies na Pokédex.", "🪙 +3.500 Pokécoins"),
}



# ============================================================
# UTILIDADES
# ============================================================

def agora_iso():

    return datetime.now(
        timezone.utc
    ).isoformat()


def formatar_tempo(
    segundos
):

    segundos = max(
        0,
        int(segundos)
    )

    minutos, segundos = divmod(
        segundos,
        60
    )

    horas, minutos = divmod(
        minutos,
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


def nivel_treinador(
    xp
):

    xp = max(
        0,
        int(xp)
    )

    return (
        xp // XP_POR_NIVEL
    ) + 1


def xp_atual(
    xp
):

    return (
        int(xp)
        %
        XP_POR_NIVEL
    )


def barra_xp(
    atual,
    total=100,
    tamanho=15
):

    if total <= 0:

        return "🟩" * tamanho

    preenchido = round(
        (
            atual
            /
            total
        )
        *
        tamanho
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
            -
            preenchido
        )
    )


def nome_formatado(
    nome
):

    return (
        str(nome)
        .replace(
            "-",
            " "
        )
        .title()
    )


def escolher_raridade():

    nomes = list(
        RARIDADES.keys()
    )

    pesos = [
        RARIDADES[
            nome
        ][
            "peso"
        ]

        for nome in nomes
    ]

    return random.choices(
        nomes,
        weights=pesos,
        k=1
    )[0]


def escolher_regiao():

    return random.choice(
        list(
            REGIOES.keys()
        )
    )


def obter_emoji_tipo(
    tipo
):

    return TIPOS_EMOJIS.get(
        tipo,
        "❔"
    )


# ============================================================
# BANCO SQLITE
# ============================================================

class BancoPokemon:

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
            timeout=20
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
    # ADICIONAR COLUNA
    # ========================================================

    def adicionar_coluna_se_faltar(
        self,
        db,
        tabela,
        coluna,
        definicao
    ):
        colunas = db.execute(
            f"PRAGMA table_info({tabela})"
        ).fetchall()

        existentes = {
            coluna_db["name"]
            for coluna_db in colunas
        }

        if coluna in existentes:
            return True

        try:
            db.execute(
                f"""
                ALTER TABLE {tabela}
                ADD COLUMN {coluna}
                {definicao}
                """
            )

            print(
                "[POKEMON] "
                f"🛠️ Migração aplicada: "
                f"{tabela}.{coluna}"
            )
            return True

        except sqlite3.OperationalError as erro:
            if "duplicate column name" in str(erro).lower():
                return True

            print(
                "[POKEMON] "
                f"❌ Falha migrando "
                f"{tabela}.{coluna}: {erro}"
            )
            return False

    # ========================================================
    # INICIALIZAR
    # ========================================================


    def inicializar(
        self
    ):

        with self.conectar() as db:

            # ------------------------------------------------
            # TREINADORES
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS treinadores (

                    id INTEGER PRIMARY KEY,

                    xp INTEGER NOT NULL DEFAULT 0,

                    nivel INTEGER NOT NULL DEFAULT 1,

                    pokecoins INTEGER NOT NULL DEFAULT 500,

                    pokeballs INTEGER NOT NULL DEFAULT 10,

                    greatballs INTEGER NOT NULL DEFAULT 0,

                    ultraballs INTEGER NOT NULL DEFAULT 0,

                    starter TEXT,

                    ultimo_explorar TEXT,

                    ultimo_captura TEXT,

                    ultimo_batalha TEXT,

                    ultimo_daily TEXT,

                    ultima_pokecaixa TEXT,

                    perfil_bio TEXT NOT NULL DEFAULT '',

                    perfil_banner TEXT NOT NULL DEFAULT '',

                    perfil_fonte TEXT NOT NULL DEFAULT 'normal',

                    perfil_emblema TEXT NOT NULL DEFAULT '',

                    streak_pokecaixa INTEGER NOT NULL DEFAULT 0,

                    capturas INTEGER NOT NULL DEFAULT 0,

                    batalhas INTEGER NOT NULL DEFAULT 0,

                    vitorias INTEGER NOT NULL DEFAULT 0,

                    trocas INTEGER NOT NULL DEFAULT 0,
                    exploracoes INTEGER NOT NULL DEFAULT 0,
                    proxima_batalha_pve INTEGER NOT NULL DEFAULT 5,
                    batalha_pve_pendente INTEGER NOT NULL DEFAULT 0,

                    criado_em TEXT NOT NULL,

                    ultima_atividade TEXT NOT NULL
                )
                """
            )

            # ------------------------------------------------
            # POKÉMON
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS pokemon (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    treinador_id INTEGER NOT NULL,

                    pokemon_id INTEGER NOT NULL,

                    nome TEXT NOT NULL,

                    apelido TEXT,

                    nivel INTEGER NOT NULL DEFAULT 5,

                    xp INTEGER NOT NULL DEFAULT 0,

                    raridade TEXT NOT NULL DEFAULT 'comum',

                    regiao TEXT NOT NULL DEFAULT 'kanto',

                    shiny INTEGER NOT NULL DEFAULT 0,

                    equipe INTEGER NOT NULL DEFAULT 0,

                    favorito INTEGER NOT NULL DEFAULT 0,

                    tipos TEXT NOT NULL DEFAULT '[]',

                    movimentos TEXT NOT NULL DEFAULT '[]',

                    hp INTEGER NOT NULL DEFAULT 100,

                    ataque INTEGER NOT NULL DEFAULT 50,

                    defesa INTEGER NOT NULL DEFAULT 50,

                    velocidade INTEGER NOT NULL DEFAULT 50,

                    iv_hp INTEGER NOT NULL DEFAULT 15,

                    iv_ataque INTEGER NOT NULL DEFAULT 15,

                    iv_defesa INTEGER NOT NULL DEFAULT 15,

                    iv_velocidade INTEGER NOT NULL DEFAULT 15,

                    base_hp INTEGER NOT NULL DEFAULT 50,

                    base_ataque INTEGER NOT NULL DEFAULT 50,

                    base_defesa INTEGER NOT NULL DEFAULT 50,

                    base_velocidade INTEGER NOT NULL DEFAULT 50,

                    batalhas INTEGER NOT NULL DEFAULT 0,

                    vitorias INTEGER NOT NULL DEFAULT 0,

                    evolucoes INTEGER NOT NULL DEFAULT 0,

                    capturado_em TEXT NOT NULL,

                    FOREIGN KEY(treinador_id)

                    REFERENCES treinadores(id)

                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # DEX
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS dex (

                    treinador_id INTEGER NOT NULL,

                    pokemon_id INTEGER NOT NULL,

                    nome TEXT NOT NULL,

                    encontrado_em TEXT NOT NULL,

                    PRIMARY KEY(
                        treinador_id,
                        pokemon_id
                    ),

                    FOREIGN KEY(treinador_id)

                    REFERENCES treinadores(id)

                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # CONQUISTAS
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS conquistas (

                    treinador_id INTEGER NOT NULL,

                    chave TEXT NOT NULL,

                    desbloqueada_em TEXT NOT NULL,

                    PRIMARY KEY(
                        treinador_id,
                        chave
                    ),

                    FOREIGN KEY(treinador_id)

                    REFERENCES treinadores(id)

                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # TROCAS
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS trocas (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    origem_id INTEGER NOT NULL,

                    destino_id INTEGER NOT NULL,

                    pokemon_origem INTEGER NOT NULL,

                    pokemon_destino INTEGER NOT NULL,

                    criado_em TEXT NOT NULL
                )
                """
            )

            # ------------------------------------------------
            # ITENS DE PERFIL
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS perfil_itens (

                    treinador_id INTEGER NOT NULL,

                    item_id TEXT NOT NULL,

                    comprado_em TEXT NOT NULL,

                    PRIMARY KEY(treinador_id, item_id),

                    FOREIGN KEY(treinador_id)
                    REFERENCES treinadores(id)
                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # INSÍGNIAS E PROGRESSO DA LIGA
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS insignias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    treinador_id INTEGER NOT NULL,
                    regiao TEXT NOT NULL,
                    numero INTEGER NOT NULL,
                    nome TEXT NOT NULL,
                    lider TEXT NOT NULL,
                    conquistada_em TEXT NOT NULL,
                    UNIQUE(treinador_id, regiao, numero),
                    FOREIGN KEY(treinador_id)
                    REFERENCES treinadores(id)
                    ON DELETE CASCADE
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS liga_progresso (
                    treinador_id INTEGER NOT NULL,
                    regiao TEXT NOT NULL,
                    elite_etapa INTEGER NOT NULL DEFAULT 0,
                    elite_concluida INTEGER NOT NULL DEFAULT 0,
                    atualizado_em TEXT NOT NULL,
                    PRIMARY KEY(treinador_id, regiao),
                    FOREIGN KEY(treinador_id)
                    REFERENCES treinadores(id)
                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # RECOMPENSAS DO POKÉTOP
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS poketop_recompensas (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    guild_id INTEGER NOT NULL,

                    periodo TEXT NOT NULL,

                    treinador_id INTEGER NOT NULL,

                    posicao INTEGER NOT NULL,

                    pokecoins INTEGER NOT NULL DEFAULT 0,

                    xp INTEGER NOT NULL DEFAULT 0,

                    item_id TEXT NOT NULL DEFAULT '',

                    quantidade INTEGER NOT NULL DEFAULT 0,

                    resgatado_em TEXT NOT NULL,

                    UNIQUE(guild_id, periodo, treinador_id),

                    FOREIGN KEY(treinador_id)
                    REFERENCES treinadores(id)
                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # REGISTRO DO POKÉTOP
            # ------------------------------------------------
            # O treinador só entra no ranking depois de se registrar
            # explicitamente e possuir exatamente 6 Pokémon na equipe.
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS poketop_registros (
                    guild_id INTEGER NOT NULL,
                    treinador_id INTEGER NOT NULL,
                    registrado_em TEXT NOT NULL,
                    PRIMARY KEY(guild_id, treinador_id),
                    FOREIGN KEY(treinador_id)
                    REFERENCES treinadores(id)
                    ON DELETE CASCADE
                )
                """
            )

            # ------------------------------------------------
            # ITENS DE JORNADA
            # ------------------------------------------------

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS itens_jornada (

                    treinador_id INTEGER NOT NULL,

                    item_id TEXT NOT NULL,

                    quantidade INTEGER NOT NULL DEFAULT 0,

                    atualizado_em TEXT NOT NULL,

                    PRIMARY KEY(treinador_id, item_id),

                    FOREIGN KEY(treinador_id)
                    REFERENCES treinadores(id)
                    ON DELETE CASCADE
                )
                """
            )

            # =================================================
            # MIGRAÇÃO COMPLETA DO SQLITE
            # =================================================
            # O CREATE TABLE IF NOT EXISTS NÃO atualiza tabelas
            # antigas. Esta rotina garante todas as colunas usadas
            # pela versão atual do sistema sem apagar os dados.

            # ------------------------------------------------
            # TREINADORES
            # ------------------------------------------------
            treinador_cols = {
                "xp": "INTEGER NOT NULL DEFAULT 0",
                "nivel": "INTEGER NOT NULL DEFAULT 1",
                "pokecoins": "INTEGER NOT NULL DEFAULT 500",
                "pokeballs": "INTEGER NOT NULL DEFAULT 10",
                "greatballs": "INTEGER NOT NULL DEFAULT 0",
                "ultraballs": "INTEGER NOT NULL DEFAULT 0",
                "starter": "TEXT",
                "ultimo_explorar": "TEXT",
                "ultimo_captura": "TEXT",
                "ultimo_batalha": "TEXT",
                "ultimo_daily": "TEXT",
                "ultima_pokecaixa": "TEXT",
                "perfil_bio": "TEXT NOT NULL DEFAULT ''",
                "perfil_banner": "TEXT NOT NULL DEFAULT ''",
                "perfil_fonte": "TEXT NOT NULL DEFAULT 'normal'",
                "perfil_emblema": "TEXT NOT NULL DEFAULT ''",
                "streak_pokecaixa": "INTEGER NOT NULL DEFAULT 0",
                "capturas": "INTEGER NOT NULL DEFAULT 0",
                "batalhas": "INTEGER NOT NULL DEFAULT 0",
                "vitorias": "INTEGER NOT NULL DEFAULT 0",
                "trocas": "INTEGER NOT NULL DEFAULT 0",
                "exploracoes": "INTEGER NOT NULL DEFAULT 0",
                "proxima_batalha_pve": "INTEGER NOT NULL DEFAULT 5",
                "batalha_pve_pendente": "INTEGER NOT NULL DEFAULT 0",
                "criado_em": "TEXT NOT NULL DEFAULT ''",
                "ultima_atividade": "TEXT NOT NULL DEFAULT ''",
            }

            for coluna, definicao in treinador_cols.items():
                self.adicionar_coluna_se_faltar(
                    db,
                    "treinadores",
                    coluna,
                    definicao
                )

            # ------------------------------------------------
            # POKÉMON
            # ------------------------------------------------
            pokemon_cols = {
                "treinador_id": "INTEGER",
                "pokemon_id": "INTEGER NOT NULL DEFAULT 0",
                "nome": "TEXT NOT NULL DEFAULT 'Pokémon'",
                "apelido": "TEXT",
                "nivel": "INTEGER NOT NULL DEFAULT 5",
                "xp": "INTEGER NOT NULL DEFAULT 0",
                "raridade": "TEXT NOT NULL DEFAULT 'comum'",
                "regiao": "TEXT NOT NULL DEFAULT 'kanto'",
                "shiny": "INTEGER NOT NULL DEFAULT 0",
                "equipe": "INTEGER NOT NULL DEFAULT 0",
                "favorito": "INTEGER NOT NULL DEFAULT 0",
                "tipos": "TEXT NOT NULL DEFAULT '[]'",
                "movimentos": "TEXT NOT NULL DEFAULT '[]'",
                "hp": "INTEGER NOT NULL DEFAULT 100",
                "ataque": "INTEGER NOT NULL DEFAULT 50",
                "defesa": "INTEGER NOT NULL DEFAULT 50",
                "velocidade": "INTEGER NOT NULL DEFAULT 50",
                "iv_hp": "INTEGER NOT NULL DEFAULT -1",
                "iv_ataque": "INTEGER NOT NULL DEFAULT -1",
                "iv_defesa": "INTEGER NOT NULL DEFAULT -1",
                "iv_velocidade": "INTEGER NOT NULL DEFAULT -1",
                "base_hp": "INTEGER NOT NULL DEFAULT 50",
                "base_ataque": "INTEGER NOT NULL DEFAULT 50",
                "base_defesa": "INTEGER NOT NULL DEFAULT 50",
                "base_velocidade": "INTEGER NOT NULL DEFAULT 50",
                "batalhas": "INTEGER NOT NULL DEFAULT 0",
                "vitorias": "INTEGER NOT NULL DEFAULT 0",
                "evolucoes": "INTEGER NOT NULL DEFAULT 0",
                "capturado_em": "TEXT NOT NULL DEFAULT ''",
            }

            for coluna, definicao in pokemon_cols.items():
                self.adicionar_coluna_se_faltar(
                    db,
                    "pokemon",
                    coluna,
                    definicao
                )

            # ------------------------------------------------
            # DEX
            # ------------------------------------------------
            dex_cols = {
                "treinador_id": "INTEGER",
                "pokemon_id": "INTEGER NOT NULL DEFAULT 0",
                "nome": "TEXT NOT NULL DEFAULT 'Pokémon'",
                "encontrado_em": "TEXT DEFAULT ''",
            }

            for coluna, definicao in dex_cols.items():
                self.adicionar_coluna_se_faltar(
                    db,
                    "dex",
                    coluna,
                    definicao
                )

            # ------------------------------------------------
            # CONQUISTAS
            # ------------------------------------------------
            conquista_cols = {
                "treinador_id": "INTEGER",
                "chave": "TEXT NOT NULL DEFAULT ''",
                "desbloqueada_em": "TEXT NOT NULL DEFAULT ''",
            }

            for coluna, definicao in conquista_cols.items():
                self.adicionar_coluna_se_faltar(
                    db,
                    "conquistas",
                    coluna,
                    definicao
                )

            # ------------------------------------------------
            # TROCAS
            # ------------------------------------------------
            troca_cols = {
                "origem_id": "INTEGER NOT NULL DEFAULT 0",
                "destino_id": "INTEGER NOT NULL DEFAULT 0",
                "pokemon_origem": "INTEGER NOT NULL DEFAULT 0",
                "pokemon_destino": "INTEGER NOT NULL DEFAULT 0",
                "criado_em": "TEXT NOT NULL DEFAULT ''",
            }

            for coluna, definicao in troca_cols.items():
                self.adicionar_coluna_se_faltar(
                    db,
                    "trocas",
                    coluna,
                    definicao
                )

            # ------------------------------------------------
            # CORREÇÃO DE DADOS LEGADOS
            # ------------------------------------------------
            agora = agora_iso()

            db.execute(
                """
                UPDATE treinadores
                SET nivel = 1
                WHERE nivel IS NULL OR nivel < 1
                """
            )

            db.execute(
                """
                UPDATE treinadores
                SET streak_pokecaixa = 0
                WHERE streak_pokecaixa IS NULL OR streak_pokecaixa < 0
                """
            )

            db.execute(
                """
                UPDATE treinadores
                SET criado_em = ?
                WHERE criado_em IS NULL OR criado_em = ''
                """,
                (agora,)
            )

            db.execute(
                """
                UPDATE treinadores
                SET ultima_atividade = criado_em
                WHERE ultima_atividade IS NULL OR ultima_atividade = ''
                """
            )

            db.execute(
                """
                UPDATE treinadores
                SET exploracoes = 0
                WHERE exploracoes IS NULL OR exploracoes < 0
                """
            )

            db.execute(
                """
                UPDATE treinadores
                SET proxima_batalha_pve = 5
                WHERE proxima_batalha_pve IS NULL OR proxima_batalha_pve < 1
                """
            )

            db.execute(
                """
                UPDATE treinadores
                SET batalha_pve_pendente = 0
                WHERE batalha_pve_pendente IS NULL
                """
            )

            db.execute(
                """
                UPDATE pokemon
                SET nivel = 5
                WHERE nivel IS NULL OR nivel < 1
                """
            )

            db.execute(
                """
                UPDATE pokemon
                SET xp = 0
                WHERE xp IS NULL OR xp < 0
                """
            )

            db.execute(
                """
                UPDATE pokemon
                SET capturado_em = ?
                WHERE capturado_em IS NULL OR capturado_em = ''
                """,
                (agora,)
            )

            db.execute(
                """
                UPDATE dex
                SET encontrado_em = ?
                WHERE encontrado_em IS NULL OR encontrado_em = ''
                """,
                (agora,)
            )

            # ------------------------------------------------
            # MIGRAÇÃO DOS IVs E STATUS
            # ------------------------------------------------
            rows_iv = db.execute(
                """
                SELECT id, nivel, xp, iv_hp, iv_ataque, iv_defesa,
                       iv_velocidade, base_hp, base_ataque,
                       base_defesa, base_velocidade
                FROM pokemon
                """
            ).fetchall()

            for row in rows_iv:
                nivel = max(1, int(row["nivel"] or 5))
                xp_legado = row["xp"]
                xp = (
                    max(0, int(xp_legado))
                    if xp_legado is not None and int(xp_legado) > 0
                    else max(0, (nivel - 1) * XP_POKEMON_POR_NIVEL)
                )

                ivs = {
                    "iv_hp": int(row["iv_hp"] if row["iv_hp"] is not None else -1),
                    "iv_ataque": int(row["iv_ataque"] if row["iv_ataque"] is not None else -1),
                    "iv_defesa": int(row["iv_defesa"] if row["iv_defesa"] is not None else -1),
                    "iv_velocidade": int(row["iv_velocidade"] if row["iv_velocidade"] is not None else -1),
                }

                # Só gera IV novo quando a coluna ainda está no valor inválido.
                if any(v < 0 or v > IV_MAX for v in ivs.values()):
                    ivs = gerar_ivs()
                elif (
                    all(v == 15 for v in ivs.values())
                    and int(row["base_hp"] or 50) == 50
                    and int(row["base_ataque"] or 50) == 50
                    and int(row["base_defesa"] or 50) == 50
                    and int(row["base_velocidade"] or 50) == 50
                ):
                    # Compatibilidade com a primeira versão que adicionou
                    # IVs sem dados reais: gera IVs para registros legados.
                    ivs = gerar_ivs()

                base = {
                    "hp": max(1, int(row["base_hp"] or 50)),
                    "ataque": max(1, int(row["base_ataque"] or 50)),
                    "defesa": max(1, int(row["base_defesa"] or 50)),
                    "velocidade": max(1, int(row["base_velocidade"] or 50)),
                }

                nivel_real = calcular_nivel_pokemon(xp)
                stats = calcular_stats_pokemon(base, ivs, nivel_real)

                db.execute(
                    """
                    UPDATE pokemon
                    SET xp = ?,
                        nivel = ?,
                        iv_hp = ?,
                        iv_ataque = ?,
                        iv_defesa = ?,
                        iv_velocidade = ?,
                        base_hp = ?,
                        base_ataque = ?,
                        base_defesa = ?,
                        base_velocidade = ?,
                        hp = ?,
                        ataque = ?,
                        defesa = ?,
                        velocidade = ?
                    WHERE id = ?
                    """,
                    (
                        xp,
                        nivel_real,
                        ivs["iv_hp"],
                        ivs["iv_ataque"],
                        ivs["iv_defesa"],
                        ivs["iv_velocidade"],
                        base["hp"],
                        base["ataque"],
                        base["defesa"],
                        base["velocidade"],
                        stats["hp"],
                        stats["ataque"],
                        stats["defesa"],
                        stats["velocidade"],
                        row["id"],
                    )
                )

            # ------------------------------------------------
            # ÍNDICES
            # ------------------------------------------------
            # Ajudam !equipe, !pokemon, DEX e buscas por dono.
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_pokemon_treinador "
                "ON pokemon(treinador_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_pokemon_equipe "
                "ON pokemon(treinador_id, equipe)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_pokemon_favorito "
                "ON pokemon(treinador_id, favorito)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_dex_treinador "
                "ON dex(treinador_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_conquistas_treinador "
                "ON conquistas(treinador_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_poketop_recompensas_guild_periodo "
                "ON poketop_recompensas(guild_id, periodo)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_poketop_registros_guild "
                "ON poketop_registros(guild_id, treinador_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_trocas_origem "
                "ON trocas(origem_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_trocas_destino "
                "ON trocas(destino_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_itens_jornada_treinador "
                "ON itens_jornada(treinador_id)"
            )

            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_insignias_treinador "
                "ON insignias(treinador_id, regiao, numero)"
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_liga_progresso_treinador "
                "ON liga_progresso(treinador_id, regiao)"
            )

            # Verificação final: nenhuma coluna usada pelo sistema
            # pode ficar faltando após a migração.
            tabelas_obrigatorias = {
                "treinadores": (
                    "id", "xp", "nivel", "pokecoins",
                    "pokeballs", "greatballs", "ultraballs",
                    "starter", "ultimo_explorar", "ultima_pokecaixa",
                    "perfil_bio", "perfil_banner", "perfil_fonte",
                    "perfil_emblema", "streak_pokecaixa",
                    "capturas", "batalhas", "vitorias", "trocas",
                    "exploracoes", "proxima_batalha_pve",
                    "batalha_pve_pendente",
                ),
                "pokemon": (
                    "id", "treinador_id", "pokemon_id", "nome",
                    "nivel", "xp", "raridade", "regiao", "shiny",
                    "equipe", "favorito", "tipos", "movimentos",
                    "hp", "ataque", "defesa",
                    "velocidade", "iv_hp", "iv_ataque", "iv_defesa",
                    "iv_velocidade", "base_hp", "base_ataque",
                    "base_defesa", "base_velocidade", "batalhas",
                    "vitorias", "evolucoes", "capturado_em",
                ),
                "dex": (
                    "treinador_id", "pokemon_id",
                    "nome", "encontrado_em",
                ),
                "conquistas": (
                    "treinador_id", "chave", "desbloqueada_em",
                ),
                "trocas": (
                    "id", "origem_id", "destino_id",
                    "pokemon_origem", "pokemon_destino", "criado_em",
                ),
                "perfil_itens": (
                    "treinador_id", "item_id", "comprado_em",
                ),
                "insignias": (
                    "id", "treinador_id", "regiao", "numero",
                    "nome", "lider", "conquistada_em",
                ),
                "liga_progresso": (
                    "treinador_id", "regiao", "elite_etapa",
                    "elite_concluida", "atualizado_em",
                ),
            }

            faltando = []

            for tabela, esperadas in tabelas_obrigatorias.items():
                atuais = {
                    linha["name"]
                    for linha in db.execute(
                        f"PRAGMA table_info({tabela})"
                    ).fetchall()
                }

                for coluna in esperadas:
                    if coluna not in atuais:
                        faltando.append(f"{tabela}.{coluna}")

            if faltando:
                raise RuntimeError(
                    "[POKEMON] Migração incompleta. "
                    "Colunas ausentes: "
                    + ", ".join(faltando)
                )

            db.execute("PRAGMA user_version = 13")
            db.commit()

            print(
                "[POKEMON] ✅ SQLite inicializado/migrado "
                "com sucesso (schema v13)."
            )

    # ========================================================
    # EXECUTAR ASYNC
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
    # GARANTIR TREINADOR
    # ========================================================

    def garantir_treinador(
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
                INSERT OR IGNORE INTO treinadores (

                    id,

                    xp,

                    nivel,

                    pokecoins,

                    pokeballs,

                    criado_em,

                    ultima_atividade

                )

                VALUES (

                    ?,
                    0,
                    1,
                    ?,
                    ?,
                    ?,
                    ?

                )
                """,
                (
                    uid,
                    POKECOINS_INICIAL,
                    POKEBALL_INICIAL,
                    agora,
                    agora
                )
            )

            db.commit()

    # ========================================================
    # TREINADOR
    # ========================================================

    def obter_treinador(
        self,
        usuario_id
    ):

        self.garantir_treinador(
            usuario_id
        )

        with self.conectar() as db:

            row = db.execute(
                """
                SELECT *

                FROM treinadores

                WHERE id = ?
                """,
                (
                    int(
                        usuario_id
                    ),
                )
            ).fetchone()

            return (
                dict(row)
                if row
                else None
            )

    def obter_perfil(self, usuario_id):
        """Compatibilidade do sistema de perfil com o banco SQLite atual."""
        return self.obter_treinador(usuario_id)

    def listar_itens_perfil(self, usuario_id):
        """Retorna somente os cosméticos que o treinador já comprou."""
        self.garantir_treinador(usuario_id)
        with self.conectar() as db:
            rows = db.execute(
                """
                SELECT item_id
                FROM perfil_itens
                WHERE treinador_id = ?
                ORDER BY comprado_em ASC
                """,
                (int(usuario_id),)
            ).fetchall()
            return [row["item_id"] for row in rows]

    # ========================================================
    # BALL
    # ========================================================

    async def alterar_ball(
        self,
        usuario_id,
        tipo,
        quantidade
    ):

        mapa = {

            "pokeball":
                "pokeballs",

            "greatball":
                "greatballs",

            "ultraball":
                "ultraballs"
        }

        campo = mapa.get(
            tipo
        )

        if campo is None:
            return False

        uid = int(
            usuario_id
        )

        quantidade = int(
            quantidade
        )

        def operacao():

            self.garantir_treinador(
                uid
            )

            with self.conectar() as db:

                row = db.execute(
                    f"""
                    SELECT {campo}

                    FROM treinadores

                    WHERE id = ?
                    """,
                    (
                        uid,
                    )
                ).fetchone()

                if row is None:
                    return False

                novo = (
                    int(
                        row[campo]
                    )
                    +
                    quantidade
                )

                if novo < 0:

                    return False

                db.execute(
                    f"""
                    UPDATE treinadores

                    SET {campo} = ?,

                        ultima_atividade = ?

                    WHERE id = ?
                    """,
                    (
                        novo,
                        agora_iso(),
                        uid
                    )
                )

                db.commit()

                return True

        return await self.executar(
            operacao
        )

    # ========================================================
    # POKÉCOINS
    # ========================================================

    async def alterar_pokecoins(
        self,
        usuario_id,
        quantidade
    ):

        uid = int(
            usuario_id
        )

        quantidade = int(
            quantidade
        )

        def operacao():

            self.garantir_treinador(
                uid
            )

            with self.conectar() as db:

                row = db.execute(
                    """
                    SELECT pokecoins

                    FROM treinadores

                    WHERE id = ?
                    """,
                    (
                        uid,
                    )
                ).fetchone()

                if row is None:
                    return False

                novo = (
                    int(
                        row["pokecoins"]
                    )
                    +
                    quantidade
                )

                if novo < 0:
                    return False

                db.execute(
                    """
                    UPDATE treinadores

                    SET pokecoins = ?,

                        ultima_atividade = ?

                    WHERE id = ?
                    """,
                    (
                        novo,
                        agora_iso(),
                        uid
                    )
                )

                db.commit()

                return True

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

        campos_validos = {
            "ultimo_explorar",
            "ultimo_captura",
            "ultimo_batalha"
        }

        if campo not in campos_validos:
            return False

        uid = int(usuario_id)

        def operacao():
            self.garantir_treinador(uid)
            agora = agora_iso()
            with self.conectar() as db:
                db.execute(
                    f"UPDATE treinadores SET {campo} = ?, ultima_atividade = ? WHERE id = ?",
                    (agora, agora, uid)
                )
                db.commit()
                return True

        return await self.executar(operacao)

    # ========================================================
    # POKÉCAIXA • RECOMPENSA + STREAK
    # ========================================================

    async def resgatar_pokecaixa(self, usuario_id):

        uid = int(usuario_id)

        def operacao():
            self.garantir_treinador(uid)

            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")

                row = db.execute(
                    """
                    SELECT pokecoins, ultima_pokecaixa, streak_pokecaixa
                    FROM treinadores
                    WHERE id = ?
                    """,
                    (uid,)
                ).fetchone()

                if row is None:
                    db.rollback()
                    return None

                agora = datetime.now(timezone.utc)
                hoje = agora.date()
                ultima = None

                if row["ultima_pokecaixa"]:
                    try:
                        ultima = datetime.fromisoformat(
                            row["ultima_pokecaixa"]
                        ).date()
                    except (ValueError, TypeError):
                        ultima = None

                if ultima == hoje:
                    db.rollback()
                    return {
                        "ok": False,
                        "motivo": "hoje",
                        "restante": max(1, int(
                            (agora.replace(hour=23, minute=59, second=59, microsecond=999999) - agora).total_seconds()
                        )),
                        "saldo": int(row["pokecoins"]),
                        "streak": int(row["streak_pokecaixa"] or 0)
                    }

                streak_anterior = int(row["streak_pokecaixa"] or 0)

                if ultima == hoje.fromordinal(hoje.toordinal() - 1):
                    streak = streak_anterior + 1
                else:
                    streak = 1

                recompensa = random.randint(
                    RECOMPENSA_DAILY_MIN,
                    RECOMPENSA_DAILY_MAX
                )

                bonus_streak = min(
                    max(0, streak - 1) * POKECAIXA_BONUS_POR_STREAK,
                    POKECAIXA_BONUS_MAX
                )

                bonus_semana = (
                    POKECAIXA_BONUS_SEMANA
                    if streak % 7 == 0
                    else 0
                )

                total = recompensa + bonus_streak + bonus_semana
                saldo = int(row["pokecoins"]) + total
                agora_txt = agora.isoformat()

                db.execute(
                    """
                    UPDATE treinadores
                    SET pokecoins = ?,
                        ultima_pokecaixa = ?,
                        streak_pokecaixa = ?,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (saldo, agora_txt, streak, agora_txt, uid)
                )

                db.commit()

                return {
                    "ok": True,
                    "recompensa": recompensa,
                    "bonus_streak": bonus_streak,
                    "bonus_semana": bonus_semana,
                    "total": total,
                    "saldo": saldo,
                    "streak": streak
                }

        return await self.executar(operacao)

    # ========================================================
    # XP
    # ========================================================

    async def adicionar_xp(
        self,
        usuario_id,
        quantidade
    ):

        uid = int(
            usuario_id
        )

        quantidade = int(
            quantidade
        )

        def operacao():

            self.garantir_treinador(
                uid
            )

            with self.conectar() as db:

                row = db.execute(
                    """
                    SELECT xp, nivel

                    FROM treinadores

                    WHERE id = ?
                    """,
                    (
                        uid,
                    )
                ).fetchone()

                if row is None:
                    return None

                xp_antigo = int(
                    row["xp"]
                )

                nivel_antigo = int(
                    row["nivel"]
                )

                novo_xp = (
                    xp_antigo
                    +
                    quantidade
                )

                novo_nivel = (
                    novo_xp
                    //
                    XP_POR_NIVEL
                ) + 1

                db.execute(
                    """
                    UPDATE treinadores

                    SET xp = ?,

                        nivel = ?,

                        ultima_atividade = ?

                    WHERE id = ?
                    """,
                    (
                        novo_xp,
                        novo_nivel,
                        agora_iso(),
                        uid
                    )
                )

                db.commit()

                return {

                    "nivel_antes":
                        nivel_antigo,

                    "nivel_depois":
                        novo_nivel,

                    "xp":
                        novo_xp
                }

        return await self.executar(
            operacao
        )

    # ========================================================
    # STARTER
    # ========================================================

    async def escolher_starter(
        self,
        usuario_id,
        starter
    ):
        uid = int(usuario_id)

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT starter FROM treinadores WHERE id = ?", (uid,)
                ).fetchone()
                if row is None or row["starter"]:
                    db.rollback()
                    return False

                agora = agora_iso()
                regiao = starter.get("regiao", "kanto")
                base = starter.get("base_stats") or STARTER_BASE_STATS.get(
                    int(starter["id"]),
                    {"hp": 50, "ataque": 50, "defesa": 50, "velocidade": 50}
                )
                ivs = starter.get("ivs") or gerar_ivs()
                nivel_inicial = 5
                stats = calcular_stats_pokemon(base, ivs, nivel_inicial)
                tipos = starter.get("tipos") or []
                movimentos = starter.get("movimentos") or []

                db.execute(
                    """
                    UPDATE treinadores
                    SET starter = ?, ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (starter["nome"], agora, uid)
                )

                db.execute(
                    """
                    INSERT INTO pokemon (
                        treinador_id, pokemon_id, nome, nivel, xp, raridade, regiao, equipe,
                        tipos, movimentos, hp, ataque, defesa, velocidade,
                        iv_hp, iv_ataque, iv_defesa, iv_velocidade,
                        base_hp, base_ataque, base_defesa, base_velocidade, capturado_em
                    )
                    VALUES (?, ?, ?, ?, ?, 'comum', ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid, starter["id"], starter["nome"], nivel_inicial,
                        (nivel_inicial - 1) * XP_POKEMON_POR_NIVEL, regiao,
                        json.dumps(tipos, ensure_ascii=False),
                        json.dumps(movimentos, ensure_ascii=False),
                        stats["hp"], stats["ataque"], stats["defesa"], stats["velocidade"],
                        ivs["iv_hp"], ivs["iv_ataque"], ivs["iv_defesa"], ivs["iv_velocidade"],
                        base["hp"], base["ataque"], base["defesa"], base["velocidade"], agora
                    )
                )
                db.execute(
                    "INSERT OR IGNORE INTO dex (treinador_id, pokemon_id, nome, encontrado_em) VALUES (?, ?, ?, ?)",
                    (uid, starter["id"], starter["nome"], agora)
                )
                db.commit()
                return True

        return await self.executar(operacao)

    async def comprar_item_jornada(
        self,
        usuario_id,
        item_id,
        preco,
        quantidade
    ):
        uid = int(usuario_id)
        quantidade = int(quantidade)

        if item_id not in LOJA:
            return False, "invalido"

        if quantidade <= 0:
            return False, "quantidade"

        def operacao():
            self.garantir_treinador(uid)
            custo = int(preco) * quantidade

            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")

                saldo = db.execute(
                    "SELECT pokecoins FROM treinadores WHERE id = ?",
                    (uid,)
                ).fetchone()

                if not saldo or int(saldo["pokecoins"]) < custo:
                    return False, "saldo"

                agora = agora_iso()

                db.execute(
                    """
                    UPDATE treinadores
                    SET pokecoins = pokecoins - ?,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (custo, agora, uid)
                )

                db.execute(
                    """
                    INSERT INTO itens_jornada
                    (
                        treinador_id,
                        item_id,
                        quantidade,
                        atualizado_em
                    )
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(treinador_id, item_id)
                    DO UPDATE SET
                        quantidade = quantidade + excluded.quantidade,
                        atualizado_em = excluded.atualizado_em
                    """,
                    (uid, item_id, quantidade, agora)
                )

                db.commit()
                return True, custo

        return await self.executar(operacao)

    def listar_itens_jornada(self, usuario_id):
        self.garantir_treinador(usuario_id)

        with self.conectar() as db:
            rows = db.execute(
                """
                SELECT item_id, quantidade
                FROM itens_jornada
                WHERE treinador_id = ?
                  AND quantidade > 0
                ORDER BY item_id
                """,
                (int(usuario_id),)
            ).fetchall()

            return [dict(row) for row in rows]

    async def consumir_item_jornada(self, usuario_id, item_id, quantidade=1):
        uid = int(usuario_id)
        quantidade = int(quantidade)
        if quantidade <= 0:
            return False

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT quantidade FROM itens_jornada WHERE treinador_id = ? AND item_id = ?",
                    (uid, item_id)
                ).fetchone()
                if not row or int(row["quantidade"]) < quantidade:
                    db.rollback()
                    return False
                nova = int(row["quantidade"]) - quantidade
                if nova <= 0:
                    db.execute(
                        "DELETE FROM itens_jornada WHERE treinador_id = ? AND item_id = ?",
                        (uid, item_id)
                    )
                else:
                    db.execute(
                        "UPDATE itens_jornada SET quantidade = ?, atualizado_em = ? WHERE treinador_id = ? AND item_id = ?",
                        (nova, agora_iso(), uid, item_id)
                    )
                db.commit()
                return True
        return await self.executar(operacao)

    def garantir_colunas_perfil(self):
        """
        Garante que o treinador tenha os campos usados pela
        personalização do perfil.
        """
        with self.conectar() as db:
            existentes = {
                row["name"]
                for row in db.execute(
                    "PRAGMA table_info(treinadores)"
                ).fetchall()
            }

            for coluna in ("banner", "fonte_bio", "emblema"):
                if coluna not in existentes:
                    db.execute(
                        f"ALTER TABLE treinadores ADD COLUMN {coluna} TEXT"
                    )

            db.commit()

    def possui_item_perfil(self, usuario_id, item_id):
        with self.conectar() as db:
            row = db.execute(
                """
                SELECT 1
                FROM perfil_itens
                WHERE treinador_id = ? AND item_id = ?
                """,
                (int(usuario_id), item_id)
            ).fetchone()
            return row is not None

    async def equipar_item_perfil(self, usuario_id, item_id):
        uid = int(usuario_id)

        def operacao():
            item = PERFIL_LOJA.get(item_id)
            if not item or not self.possui_item_perfil(uid, item_id):
                return False

            self.garantir_colunas_perfil()

            coluna = {
                "banner": "banner",
                "fonte": "fonte_bio",
                "emblema": "emblema",
            }.get(item["tipo"])

            if not coluna:
                return False

            with self.conectar() as db:
                db.execute(
                    f"UPDATE treinadores SET {coluna} = ? WHERE id = ?",
                    (item["valor"], uid)
                )
                db.commit()

            return True

        return await self.executar(operacao)

    async def comprar_item_perfil(self, usuario_id, item_id, preco):
        uid = int(usuario_id)
        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")
                saldo = db.execute(
                    "SELECT pokecoins FROM treinadores WHERE id = ?",
                    (uid,)
                ).fetchone()
                if not saldo or int(saldo["pokecoins"]) < int(preco):
                    return False, "saldo"
                existe = db.execute(
                    "SELECT 1 FROM perfil_itens WHERE treinador_id = ? AND item_id = ?",
                    (uid, item_id)
                ).fetchone()
                if existe:
                    return False, "possui"
                agora = agora_iso()
                db.execute(
                    "UPDATE treinadores SET pokecoins = pokecoins - ?, ultima_atividade = ? WHERE id = ?",
                    (int(preco), agora, uid)
                )
                db.execute(
                    "INSERT INTO perfil_itens (treinador_id, item_id, comprado_em) VALUES (?, ?, ?)",
                    (uid, item_id, agora)
                )
                db.commit()
                return True, "ok"
        return await self.executar(operacao)

    async def equipar_perfil(self, usuario_id, item_id):
        uid = int(usuario_id)
        def operacao():
            self.garantir_treinador(uid)
            item = PERFIL_LOJA.get(item_id)
            if not item:
                return False, "invalido"
            with self.conectar() as db:
                possui = db.execute(
                    "SELECT 1 FROM perfil_itens WHERE treinador_id = ? AND item_id = ?",
                    (uid, item_id)
                ).fetchone()
                if not possui:
                    return False, "nao_possui"
                campo = {
                    "banner": "perfil_banner",
                    "fonte": "perfil_fonte",
                    "emblema": "perfil_emblema"
                }[item["tipo"]]
                db.execute(
                    f"UPDATE treinadores SET {campo} = ?, ultima_atividade = ? WHERE id = ?",
                    (item["valor"], agora_iso(), uid)
                )
                db.commit()
                return True, "ok"
        return await self.executar(operacao)

    async def salvar_bio(self, usuario_id, bio):
        uid = int(usuario_id)
        bio = str(bio).strip()[:250]
        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                db.execute(
                    "UPDATE treinadores SET perfil_bio = ?, ultima_atividade = ? WHERE id = ?",
                    (bio, agora_iso(), uid)
                )
                db.commit()
                return True
        return await self.executar(operacao)

    # ========================================================
    # CAPTURAR
    # ========================================================

    async def capturar(
        self,
        usuario_id,
        pokemon_id,
        nome,
        nivel,
        raridade,
        regiao,
        shiny,
        ball,
        base_stats=None
    ):
        uid = int(usuario_id)
        campo = {
            "pokeball": "pokeballs",
            "greatball": "greatballs",
            "ultraball": "ultraballs"
        }.get(ball)

        if campo is None:
            return None

        base_stats = base_stats or {
            "hp": 50,
            "ataque": 50,
            "defesa": 50,
            "velocidade": 50,
        }

        def operacao():
            self.garantir_treinador(uid)

            with self.conectar() as db:
                try:
                    db.execute("BEGIN IMMEDIATE")

                    row = db.execute(
                        f"SELECT {campo} FROM treinadores WHERE id = ?",
                        (uid,)
                    ).fetchone()

                    if row is None or int(row[campo]) <= 0:
                        return None

                    agora = agora_iso()
                    nivel_inicial = max(1, int(nivel))
                    xp_inicial = (
                        (nivel_inicial - 1) * XP_POKEMON_POR_NIVEL
                        + random.randint(20, 50)
                    )
                    ivs = gerar_ivs()
                    stats = calcular_stats_pokemon(
                        base_stats,
                        ivs,
                        nivel_inicial
                    )

                    db.execute(
                        f"""
                        UPDATE treinadores
                        SET {campo} = {campo} - 1,
                            capturas = capturas + 1,
                            ultima_atividade = ?
                        WHERE id = ?
                        """,
                        (agora, uid)
                    )

                    cursor = db.execute(
                        """
                        INSERT INTO pokemon (
                            treinador_id, pokemon_id, nome, nivel, xp,
                            raridade, regiao, shiny,
                            hp, ataque, defesa, velocidade,
                            iv_hp, iv_ataque, iv_defesa, iv_velocidade,
                            base_hp, base_ataque, base_defesa, base_velocidade,
                            capturado_em
                        )
                        VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            ?
                        )
                        """,
                        (
                            uid, pokemon_id, nome, nivel_inicial, xp_inicial,
                            raridade, regiao, int(shiny),
                            stats["hp"], stats["ataque"], stats["defesa"], stats["velocidade"],
                            ivs["iv_hp"], ivs["iv_ataque"], ivs["iv_defesa"], ivs["iv_velocidade"],
                            int(base_stats["hp"]), int(base_stats["ataque"]),
                            int(base_stats["defesa"]), int(base_stats["velocidade"]),
                            agora
                        )
                    )

                    db.execute(
                        """
                        INSERT OR IGNORE INTO dex (
                            treinador_id, pokemon_id, nome, encontrado_em
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (uid, pokemon_id, nome, agora)
                    )

                    db.commit()

                    return {
                        "id": cursor.lastrowid,
                        "xp_ganho": xp_inicial,
                        "nivel": nivel_inicial,
                        "stats": stats,
                        "ivs": ivs,
                    }

                except Exception:
                    db.rollback()
                    raise

        return await self.executar(operacao)

    async def atualizar_dados_combate_pokemon(
        self,
        pokemon_db_id,
        tipos,
        movimentos
    ):
        pid = int(pokemon_db_id)

        def operacao():
            with self.conectar() as db:
                db.execute(
                    """
                    UPDATE pokemon
                    SET tipos = ?, movimentos = ?
                    WHERE id = ?
                    """,
                    (
                        json.dumps(tipos, ensure_ascii=False),
                        json.dumps(movimentos, ensure_ascii=False),
                        pid
                    )
                )
                db.commit()
                row = db.execute(
                    "SELECT * FROM pokemon WHERE id = ?",
                    (pid,)
                ).fetchone()
                return dict(row) if row else None

        return await self.executar(operacao)

    async def atualizar_stats_pokemon(
        self,
        pokemon_db_id,
        base_stats=None
    ):
        pid = int(pokemon_db_id)

        def operacao():
            with self.conectar() as db:
                row = db.execute(
                    "SELECT * FROM pokemon WHERE id = ?",
                    (pid,)
                ).fetchone()

                if row is None:
                    return None

                ivs = {
                    "iv_hp": int(row["iv_hp"] if row["iv_hp"] is not None else 15),
                    "iv_ataque": int(row["iv_ataque"] if row["iv_ataque"] is not None else 15),
                    "iv_defesa": int(row["iv_defesa"] if row["iv_defesa"] is not None else 15),
                    "iv_velocidade": int(row["iv_velocidade"] if row["iv_velocidade"] is not None else 15),
                }

                base = base_stats or {
                    "hp": int(row["base_hp"] or 50),
                    "ataque": int(row["base_ataque"] or 50),
                    "defesa": int(row["base_defesa"] or 50),
                    "velocidade": int(row["base_velocidade"] or 50),
                }

                xp = max(0, int(row["xp"] or 0))
                nivel = calcular_nivel_pokemon(xp)
                stats = calcular_stats_pokemon(base, ivs, nivel)

                db.execute(
                    """
                    UPDATE pokemon
                    SET nivel = ?, hp = ?, ataque = ?, defesa = ?,
                        velocidade = ?, base_hp = ?, base_ataque = ?,
                        base_defesa = ?, base_velocidade = ?
                    WHERE id = ?
                    """,
                    (
                        nivel, stats["hp"], stats["ataque"], stats["defesa"],
                        stats["velocidade"], int(base["hp"]), int(base["ataque"]),
                        int(base["defesa"]), int(base["velocidade"]), pid
                    )
                )
                db.commit()

                row2 = db.execute(
                    "SELECT * FROM pokemon WHERE id = ?",
                    (pid,)
                ).fetchone()
                return dict(row2) if row2 else None

        return await self.executar(operacao)

    async def adicionar_xp_pokemon(
        self,
        usuario_id,
        pokemon_db_id,
        quantidade
    ):
        uid = int(usuario_id)
        pid = int(pokemon_db_id)
        quantidade = max(0, int(quantidade))

        def operacao():
            with self.conectar() as db:
                row = db.execute(
                    """
                    SELECT *
                    FROM pokemon
                    WHERE id = ?
                    AND treinador_id = ?
                    """,
                    (pid, uid)
                ).fetchone()

                if row is None:
                    return None

                xp_antigo = max(0, int(row["xp"] or 0))
                nivel_antigo = calcular_nivel_pokemon(xp_antigo)
                novo_xp = xp_antigo + quantidade
                novo_nivel = calcular_nivel_pokemon(novo_xp)

                ivs = {
                    "iv_hp": int(row["iv_hp"] or 15),
                    "iv_ataque": int(row["iv_ataque"] or 15),
                    "iv_defesa": int(row["iv_defesa"] or 15),
                    "iv_velocidade": int(row["iv_velocidade"] or 15),
                }
                base = {
                    "hp": int(row["base_hp"] or 50),
                    "ataque": int(row["base_ataque"] or 50),
                    "defesa": int(row["base_defesa"] or 50),
                    "velocidade": int(row["base_velocidade"] or 50),
                }
                stats = calcular_stats_pokemon(base, ivs, novo_nivel)

                db.execute(
                    """
                    UPDATE pokemon
                    SET xp = ?, nivel = ?, hp = ?, ataque = ?,
                        defesa = ?, velocidade = ?
                    WHERE id = ? AND treinador_id = ?
                    """,
                    (
                        novo_xp, novo_nivel, stats["hp"], stats["ataque"],
                        stats["defesa"], stats["velocidade"], pid, uid
                    )
                )
                db.commit()

                return {
                    "pokemon_id": pid,
                    "xp_ganho": quantidade,
                    "xp": novo_xp,
                    "nivel_antes": nivel_antigo,
                    "nivel_depois": novo_nivel,
                    "level_up": novo_nivel > nivel_antigo,
                    "stats": stats,
                }

        return await self.executar(operacao)

    # ========================================================
    # POKÉMON
    # ========================================================

    def listar_pokemon(
        self,
        usuario_id
    ):

        self.garantir_treinador(
            usuario_id
        )

        with self.conectar() as db:

            rows = db.execute(
                """
                SELECT *

                FROM pokemon

                WHERE treinador_id = ?

                ORDER BY

                    equipe DESC,

                    favorito DESC,

                    nivel DESC,

                    id ASC
                """,
                (
                    int(
                        usuario_id
                    ),
                )
            ).fetchall()

            return [
                dict(row)
                for row in rows
            ]

    def obter_pokemon(
        self,
        pokemon_db_id
    ):

        with self.conectar() as db:

            row = db.execute(
                """
                SELECT *

                FROM pokemon

                WHERE id = ?
                """,
                (
                    int(
                        pokemon_db_id
                    ),
                )
            ).fetchone()

            return (
                dict(row)
                if row
                else None
            )

    # ========================================================
    # EQUIPA
    # ========================================================

    async def adicionar_equipe(
        self,
        usuario_id,
        pokemon_db_id
    ):

        uid = int(
            usuario_id
        )

        pid = int(
            pokemon_db_id
        )

        def operacao():

            with self.conectar() as db:

                quantidade = db.execute(
                    """
                    SELECT COUNT(*) AS total

                    FROM pokemon

                    WHERE treinador_id = ?

                    AND equipe = 1
                    """,
                    (
                        uid,
                    )
                ).fetchone()

                if int(
                    quantidade["total"]
                ) >= LIMITE_EQUIPE:

                    return False

                pokemon = db.execute(
                    """
                    SELECT id

                    FROM pokemon

                    WHERE id = ?

                    AND treinador_id = ?
                    """,
                    (
                        pid,
                        uid
                    )
                ).fetchone()

                if pokemon is None:

                    return False

                db.execute(
                    """
                    UPDATE pokemon

                    SET equipe = 1

                    WHERE id = ?
                    """,
                    (
                        pid,
                    )
                )

                db.commit()

                return True

        return await self.executar(
            operacao
        )

    async def remover_equipe(
        self,
        usuario_id,
        pokemon_db_id
    ):

        uid = int(
            usuario_id
        )

        pid = int(
            pokemon_db_id
        )

        def operacao():

            with self.conectar() as db:

                cursor = db.execute(
                    """
                    UPDATE pokemon

                    SET equipe = 0

                    WHERE id = ?

                    AND treinador_id = ?
                    """,
                    (
                        pid,
                        uid
                    )
                )

                desbloqueou = cursor.rowcount > 0

                # A recompensa é aplicada SOMENTE quando o INSERT realmente criou
                # a conquista. Assim, repetir o evento nunca paga duas vezes.
                if desbloqueou:
                    recompensa = RECOMPENSAS_CONQUISTAS.get(chave)
                    if recompensa:
                        tipo = recompensa.get("tipo")
                        quantidade = int(recompensa.get("quantidade", 0))
                        agora = agora_iso()

                        if tipo == "coins":
                            db.execute(
                                "UPDATE treinadores SET pokecoins = pokecoins + ?, ultima_atividade = ? WHERE id = ?",
                                (quantidade, agora, uid)
                            )

                        elif tipo == "xp_treinador":
                            row_xp = db.execute(
                                "SELECT xp FROM treinadores WHERE id = ?", (uid,)
                            ).fetchone()
                            xp_atual = int(row_xp["xp"] or 0) if row_xp else 0
                            novo_xp = xp_atual + quantidade
                            novo_nivel = (novo_xp // XP_POR_NIVEL) + 1
                            db.execute(
                                "UPDATE treinadores SET xp = ?, nivel = ?, ultima_atividade = ? WHERE id = ?",
                                (novo_xp, novo_nivel, agora, uid)
                            )

                        elif tipo == "item":
                            item_id = recompensa.get("item_id")
                            if item_id == "random_evolution_stone":
                                item_id = random.choice([
                                    "fire_stone", "water_stone", "thunder_stone",
                                    "leaf_stone", "moon_stone", "sun_stone",
                                    "shiny_stone", "dusk_stone", "dawn_stone", "ice_stone"
                                ])
                            if item_id:
                                db.execute(
                                    """
                                    INSERT INTO itens_jornada (treinador_id, item_id, quantidade, atualizado_em)
                                    VALUES (?, ?, ?, ?)
                                    ON CONFLICT(treinador_id, item_id) DO UPDATE SET
                                        quantidade = quantidade + excluded.quantidade,
                                        atualizado_em = excluded.atualizado_em
                                    """,
                                    (uid, item_id, quantidade, agora)
                                )

                db.commit()

                return desbloqueou

        return await self.executar(
            operacao
        )

    # ========================================================
    # EXPLORAÇÃO • PROGRESSO DO PvE
    # ========================================================

    async def registrar_exploracao(self, usuario_id):
        """Conta uma exploração concluída e arma o próximo encontro PvE."""
        uid = int(usuario_id)

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                row = db.execute(
                    """
                    SELECT exploracoes, proxima_batalha_pve, batalha_pve_pendente
                    FROM treinadores
                    WHERE id = ?
                    """,
                    (uid,)
                ).fetchone()
                if row is None:
                    return None

                exploracoes = max(0, int(row["exploracoes"] or 0)) + 1
                meta = max(1, int(row["proxima_batalha_pve"] or 5))
                pendente = bool(int(row["batalha_pve_pendente"] or 0))
                disparou = False

                if not pendente and exploracoes >= meta:
                    pendente = True
                    disparou = True

                db.execute(
                    """
                    UPDATE treinadores
                    SET exploracoes = ?, batalha_pve_pendente = ?,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (exploracoes, int(pendente), agora_iso(), uid)
                )
                db.commit()
                return {
                    "exploracoes": exploracoes,
                    "meta": meta,
                    "disparou": disparou,
                    "pendente": pendente,
                }

        return await self.executar(operacao)

    def possui_batalha_pve_pendente(self, usuario_id):
        self.garantir_treinador(usuario_id)
        with self.conectar() as db:
            row = db.execute(
                "SELECT batalha_pve_pendente FROM treinadores WHERE id = ?",
                (int(usuario_id),)
            ).fetchone()
            return bool(row and int(row["batalha_pve_pendente"] or 0))

    async def concluir_batalha_pve(self, usuario_id):
        """Agenda o próximo PvE em 4 ou 5 explorações."""
        uid = int(usuario_id)

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                row = db.execute(
                    "SELECT exploracoes FROM treinadores WHERE id = ?",
                    (uid,)
                ).fetchone()
                if row is None:
                    return None

                exploracoes = max(0, int(row["exploracoes"] or 0))
                intervalo = random.randint(EXPLORACOES_PVE_MIN, EXPLORACOES_PVE_MAX)
                proxima = exploracoes + intervalo

                db.execute(
                    """
                    UPDATE treinadores
                    SET batalha_pve_pendente = 0,
                        proxima_batalha_pve = ?,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (proxima, agora_iso(), uid)
                )
                db.commit()
                return proxima

        return await self.executar(operacao)

    async def registrar_resultado_batalha_pve(self, usuario_id, venceu):
        """Registra somente o treinador real; o NPC não vira usuário."""
        uid = int(usuario_id)

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                agora = agora_iso()
                db.execute(
                    """
                    UPDATE treinadores
                    SET batalhas = batalhas + 1,
                        vitorias = vitorias + ?,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (1 if venceu else 0, agora, uid)
                )
                db.commit()
                return True

        return await self.executar(operacao)

    # ========================================================
    # GINÁSIOS / INSÍGNIAS / ELITE 4
    # ========================================================

    def listar_insignias(self, usuario_id, regiao=None):
        self.garantir_treinador(usuario_id)
        with self.conectar() as db:
            if regiao:
                rows = db.execute(
                    """
                    SELECT numero, nome, lider, conquistada_em
                    FROM insignias
                    WHERE treinador_id = ? AND regiao = ?
                    ORDER BY numero
                    """,
                    (int(usuario_id), regiao)
                ).fetchall()
            else:
                rows = db.execute(
                    """
                    SELECT regiao, numero, nome, lider, conquistada_em
                    FROM insignias
                    WHERE treinador_id = ?
                    ORDER BY regiao, numero
                    """,
                    (int(usuario_id),)
                ).fetchall()
            return [dict(row) for row in rows]

    def possui_insignia(self, usuario_id, regiao, numero):
        with self.conectar() as db:
            row = db.execute(
                """
                SELECT 1 FROM insignias
                WHERE treinador_id = ? AND regiao = ? AND numero = ?
                """,
                (int(usuario_id), regiao, int(numero))
            ).fetchone()
            return row is not None

    async def conquistar_insignia(self, usuario_id, regiao, numero):
        uid = int(usuario_id)
        numero = int(numero)
        dados_regiao = GINASIOS.get(regiao)
        if not dados_regiao or numero < 1 or numero > 8:
            return False

        ginasio = dados_regiao["ginasios"][numero - 1]

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                agora = agora_iso()
                cur = db.execute(
                    """
                    INSERT OR IGNORE INTO insignias
                    (treinador_id, regiao, numero, nome, lider, conquistada_em)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid, regiao, numero, ginasio["insignia"],
                        ginasio["lider"], agora
                    )
                )
                db.commit()
                return cur.rowcount > 0

        return await self.executar(operacao)

    def obter_progresso_liga(self, usuario_id, regiao):
        uid = int(usuario_id)
        if regiao not in REGIOES:
            return None
        self.garantir_treinador(uid)

        with self.conectar() as db:
            agora = agora_iso()
            db.execute(
                """
                INSERT OR IGNORE INTO liga_progresso
                (treinador_id, regiao, elite_etapa, elite_concluida, atualizado_em)
                VALUES (?, ?, 0, 0, ?)
                """,
                (uid, regiao, agora)
            )
            db.commit()
            row = db.execute(
                """
                SELECT *
                FROM liga_progresso
                WHERE treinador_id = ? AND regiao = ?
                """,
                (uid, regiao)
            ).fetchone()
            return dict(row) if row else None

    async def avancar_elite4(self, usuario_id, regiao):
        uid = int(usuario_id)
        if regiao not in GINASIOS:
            return None

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                agora = agora_iso()
                db.execute(
                    """
                    INSERT OR IGNORE INTO liga_progresso
                    (treinador_id, regiao, elite_etapa, elite_concluida, atualizado_em)
                    VALUES (?, ?, 0, 0, ?)
                    """,
                    (uid, regiao, agora)
                )
                row = db.execute(
                    """
                    SELECT elite_etapa, elite_concluida
                    FROM liga_progresso
                    WHERE treinador_id = ? AND regiao = ?
                    """,
                    (uid, regiao)
                ).fetchone()
                etapa = int(row["elite_etapa"]) + 1
                concluida = 1 if etapa >= 4 else 0
                etapa = min(etapa, 4)
                db.execute(
                    """
                    UPDATE liga_progresso
                    SET elite_etapa = ?, elite_concluida = ?, atualizado_em = ?
                    WHERE treinador_id = ? AND regiao = ?
                    """,
                    (etapa, concluida, agora, uid, regiao)
                )
                db.commit()
                return {
                    "etapa": etapa,
                    "concluida": bool(concluida)
                }

        return await self.executar(operacao)

    # ========================================================
    # DEX
    # ========================================================

    def contar_dex(
        self,
        usuario_id
    ):

        self.garantir_treinador(
            usuario_id
        )

        with self.conectar() as db:

            row = db.execute(
                """
                SELECT COUNT(*) AS total

                FROM dex

                WHERE treinador_id = ?
                """,
                (
                    int(
                        usuario_id
                    ),
                )
            ).fetchone()

            return int(
                row["total"]
            )

    # ========================================================
    # CONQUISTAS
    # ========================================================

    async def desbloquear_conquista(
        self,
        usuario_id,
        chave
    ):

        if chave not in CONQUISTAS:
            return False

        uid = int(
            usuario_id
        )

        def operacao():

            self.garantir_treinador(
                uid
            )

            with self.conectar() as db:

                cursor = db.execute(
                    """
                    INSERT OR IGNORE INTO conquistas (

                        treinador_id,

                        chave,

                        desbloqueada_em

                    )

                    VALUES (
                        ?, ?, ?
                    )
                    """,
                    (
                        uid,
                        chave,
                        agora_iso()
                    )
                )

                db.commit()

                return (
                    cursor.rowcount > 0
                )

        return await self.executar(
            operacao
        )

    async def resgatar_recompensa_poketop(
        self,
        guild_id,
        usuario_id,
        periodo,
        posicao,
        recompensa
    ):
        """Registra e entrega uma recompensa do PokéTop uma única vez por período."""
        gid = int(guild_id)
        uid = int(usuario_id)
        posicao = int(posicao)
        periodo = str(periodo)
        coins = max(0, int(recompensa.get("pokecoins", 0)))
        xp = max(0, int(recompensa.get("xp", 0)))
        item_id = str(recompensa.get("item_id") or "")
        quantidade = max(0, int(recompensa.get("quantidade", 0)))

        def operacao():
            self.garantir_treinador(uid)
            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")
                existe = db.execute(
                    "SELECT id, posicao, pokecoins, xp, item_id, quantidade FROM poketop_recompensas "
                    "WHERE guild_id = ? AND periodo = ? AND treinador_id = ?",
                    (gid, periodo, uid)
                ).fetchone()
                if existe:
                    db.rollback()
                    return {
                        "status": "ja_resgatada",
                        "posicao": int(existe["posicao"]),
                        "pokecoins": int(existe["pokecoins"]),
                        "xp": int(existe["xp"]),
                        "item_id": existe["item_id"],
                        "quantidade": int(existe["quantidade"]),
                    }

                agora = agora_iso()
                db.execute(
                    "UPDATE treinadores SET pokecoins = pokecoins + ?, xp = xp + ?, ultima_atividade = ? WHERE id = ?",
                    (coins, xp, agora, uid)
                )

                if xp:
                    row = db.execute("SELECT xp FROM treinadores WHERE id = ?", (uid,)).fetchone()
                    novo_xp = int(row["xp"] or 0) if row else xp
                    novo_nivel = (novo_xp // XP_POR_NIVEL) + 1
                    db.execute("UPDATE treinadores SET nivel = ? WHERE id = ?", (novo_nivel, uid))

                if item_id and quantidade:
                    colunas_itens = {
                        "pokeball": "pokeballs",
                        "greatball": "greatballs",
                        "ultraball": "ultraballs",
                    }
                    coluna = colunas_itens.get(item_id)
                    if coluna:
                        db.execute(
                            f"UPDATE treinadores SET {coluna} = {coluna} + ? WHERE id = ?",
                            (quantidade, uid)
                        )
                    else:
                        db.execute(
                            """
                            INSERT INTO itens_jornada (treinador_id, item_id, quantidade, atualizado_em)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(treinador_id, item_id) DO UPDATE SET
                                quantidade = quantidade + excluded.quantidade,
                                atualizado_em = excluded.atualizado_em
                            """,
                            (uid, item_id, quantidade, agora)
                        )

                db.execute(
                    """
                    INSERT INTO poketop_recompensas
                    (guild_id, periodo, treinador_id, posicao, pokecoins, xp, item_id, quantidade, resgatado_em)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (gid, periodo, uid, posicao, coins, xp, item_id, quantidade, agora)
                )
                db.commit()
                return {
                    "status": "resgatada",
                    "posicao": posicao,
                    "pokecoins": coins,
                    "xp": xp,
                    "item_id": item_id,
                    "quantidade": quantidade,
                }

        return await self.executar(operacao)

    def obter_recompensa_poketop_resgatada(self, guild_id, usuario_id, periodo):
        with self.conectar() as db:
            row = db.execute(
                "SELECT posicao, pokecoins, xp, item_id, quantidade, resgatado_em "
                "FROM poketop_recompensas WHERE guild_id = ? AND periodo = ? AND treinador_id = ?",
                (int(guild_id), str(periodo), int(usuario_id))
            ).fetchone()
            return dict(row) if row else None

    def listar_conquistas(
        self,
        usuario_id
    ):

        self.garantir_treinador(
            usuario_id
        )

        with self.conectar() as db:

            rows = db.execute(
                """
                SELECT chave

                FROM conquistas

                WHERE treinador_id = ?
                """,
                (
                    int(
                        usuario_id
                    ),
                )
            ).fetchall()

            return {
                row["chave"]
                for row in rows
            }

    # ========================================================
    # EVOLUIR
    # ========================================================

    async def evoluir_pokemon(
        self,
        usuario_id,
        pokemon_db_id,
        novo_id,
        novo_nome
    ):

        uid = int(
            usuario_id
        )

        pid = int(
            pokemon_db_id
        )

        def operacao():

            with self.conectar() as db:

                pokemon = db.execute(
                    """
                    SELECT *

                    FROM pokemon

                    WHERE id = ?

                    AND treinador_id = ?
                    """,
                    (
                        pid,
                        uid
                    )
                ).fetchone()

                if pokemon is None:
                    return False

                agora = agora_iso()

                db.execute(
                    """
                    UPDATE pokemon

                    SET pokemon_id = ?,

                        nome = ?,

                        evolucoes = evolucoes + 1

                    WHERE id = ?

                    AND treinador_id = ?
                    """,
                    (
                        novo_id,
                        novo_nome,
                        pid,
                        uid
                    )
                )

                db.execute(
                    """
                    INSERT OR IGNORE INTO dex (

                        treinador_id,

                        pokemon_id,

                        nome,

                        encontrado_em

                    )

                    VALUES (
                        ?, ?, ?, ?
                    )
                    """,
                    (
                        uid,
                        novo_id,
                        novo_nome,
                        agora
                    )
                )

                db.commit()

                return True

        return await self.executar(
            operacao
        )

    async def registrar_resultado_pokemon_batalha(
        self,
        equipe_vencedora,
        equipe_derrotada
    ):
        vencedora = [dict(p) for p in equipe_vencedora]
        derrotada = [dict(p) for p in equipe_derrotada]

        def operacao():
            with self.conectar() as db:
                try:
                    db.execute("BEGIN IMMEDIATE")
                    resultados = []

                    for pokemon, ganho, venceu in (
                        [(p, random.randint(35, 60), True) for p in vencedora]
                        + [(p, random.randint(15, 30), False) for p in derrotada]
                    ):
                        pid = int(pokemon["id"])
                        row = db.execute(
                            """
                            SELECT xp, nivel, base_hp, base_ataque,
                                   base_defesa, base_velocidade,
                                   iv_hp, iv_ataque, iv_defesa,
                                   iv_velocidade
                            FROM pokemon
                            WHERE id = ?
                            """,
                            (pid,)
                        ).fetchone()

                        if not row:
                            continue

                        xp_antigo = max(0, int(row["xp"] or 0))
                        nivel_antigo = calcular_nivel_pokemon(xp_antigo)
                        novo_xp = xp_antigo + ganho
                        novo_nivel = calcular_nivel_pokemon(novo_xp)

                        ivs = {
                            "iv_hp": int(row["iv_hp"] or 15),
                            "iv_ataque": int(row["iv_ataque"] or 15),
                            "iv_defesa": int(row["iv_defesa"] or 15),
                            "iv_velocidade": int(row["iv_velocidade"] or 15),
                        }
                        base = {
                            "hp": int(row["base_hp"] or 50),
                            "ataque": int(row["base_ataque"] or 50),
                            "defesa": int(row["base_defesa"] or 50),
                            "velocidade": int(row["base_velocidade"] or 50),
                        }
                        stats = calcular_stats_pokemon(base, ivs, novo_nivel)

                        db.execute(
                            """
                            UPDATE pokemon
                            SET xp = ?, nivel = ?, hp = ?, ataque = ?,
                                defesa = ?, velocidade = ?,
                                batalhas = batalhas + 1,
                                vitorias = vitorias + ?
                            WHERE id = ?
                            """,
                            (
                                novo_xp, novo_nivel, stats["hp"], stats["ataque"],
                                stats["defesa"], stats["velocidade"],
                                1 if venceu else 0, pid
                            )
                        )

                        resultados.append({
                            "id": pid,
                            "nome": pokemon["nome"],
                            "xp": ganho,
                            "level_up": novo_nivel > nivel_antigo,
                            "nivel": novo_nivel
                        })

                    db.commit()
                    return resultados

                except Exception:
                    db.rollback()
                    raise

        return await self.executar(operacao)

    # ========================================================
    # RESULTADO DE BATALHA
    # ========================================================

    async def registrar_resultado_batalha(
        self,
        vencedor_id,
        derrotado_id
    ):

        vencedor_id = int(vencedor_id)
        derrotado_id = int(derrotado_id)

        def operacao():
            self.garantir_treinador(vencedor_id)
            self.garantir_treinador(derrotado_id)

            with self.conectar() as db:
                db.execute("BEGIN IMMEDIATE")

                agora = agora_iso()

                db.execute(
                    """
                    UPDATE treinadores
                    SET batalhas = batalhas + 1,
                        vitorias = vitorias + 1,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (agora, vencedor_id)
                )

                db.execute(
                    """
                    UPDATE treinadores
                    SET batalhas = batalhas + 1,
                        ultima_atividade = ?
                    WHERE id = ?
                    """,
                    (agora, derrotado_id)
                )

                db.commit()
                return True

        return await self.executar(operacao)


# ============================================================
# POKÉAPI
# ============================================================

class PokeAPI:

    def __init__(
        self
    ):

        self.session = None

        self.cache = {}

    async def iniciar(
        self
    ):

        if self.session is None:

            self.session = (
                aiohttp.ClientSession(
                    timeout=(
                        aiohttp.ClientTimeout(
                            total=10
                        )
                    )
                )
            )

    async def fechar(
        self
    ):

        if self.session:

            await self.session.close()

            self.session = None

    async def get(
        self,
        endpoint
    ):

        await self.iniciar()

        chave = str(
            endpoint
        ).lower()

        if chave in self.cache:

            return self.cache[
                chave
            ]

        try:

            async with self.session.get(
                f"{POKEAPI}/{endpoint}"
            ) as response:

                if response.status != 200:

                    return None

                dados = await response.json()

                self.cache[
                    chave
                ] = dados

                return dados

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError
        ):

            return None

    async def pokemon(
        self,
        pokemon
    ):

        return await self.get(
            f"pokemon/{pokemon}"
        )

    async def especie(
        self,
        pokemon_id
    ):

        return await self.get(
            f"pokemon-species/{pokemon_id}"
        )


    async def movimento(self, movimento):
        return await self.get(f"move/{movimento}")

# ============================================================
# DADOS DE COMBATE
# ============================================================

async def extrair_movimentos_combate(api, dados, limite=4, nivel=None):
    """Carrega golpes reais e prioriza os que o Pokémon já aprendeu."""
    candidatos = []

    for entrada in dados.get("moves", []):
        url = entrada.get("move", {}).get("url", "")
        if not url:
            continue
        detalhes_aprendizado = entrada.get("version_group_details", [])
        niveis = [
            int(d.get("level_learned_at", 0) or 0)
            for d in detalhes_aprendizado
            if d.get("move_learn_method", {}).get("name") in {"level-up", "machine", "egg", "tutor"}
        ]
        nivel_golpe = min(niveis) if niveis else 0
        if nivel is not None and nivel_golpe > int(nivel):
            continue

        endpoint = url.rstrip("/").split("/api/v2/")[-1]
        detalhe = await api.get(endpoint)
        if not detalhe:
            continue

        poder = detalhe.get("power")
        if not poder or int(poder) <= 0:
            continue

        candidatos.append({
            "nome": detalhe.get("name", "tackle").replace("-", " ").title(),
            "id": int(detalhe.get("id", 0) or 0),
            "tipo": detalhe.get("type", {}).get("name", "normal"),
            "poder": int(poder),
            "precisao": int(detalhe.get("accuracy") or 100),
            "prioridade": int(detalhe.get("priority") or 0),
            "nivel_aprendizado": nivel_golpe,
        })

    candidatos.sort(key=lambda m: (m["nivel_aprendizado"], m["poder"]), reverse=True)
    unicos = []
    vistos = set()
    for movimento in candidatos:
        if movimento["id"] in vistos:
            continue
        vistos.add(movimento["id"])
        unicos.append(movimento)
        if len(unicos) >= limite:
            break

    if not unicos:
        unicos = [{
            "nome": "Tackle", "id": 33, "tipo": "normal",
            "poder": 40, "precisao": 100, "prioridade": 0, "nivel_aprendizado": 1
        }]
    return unicos[:limite]


# ============================================================
# VIEW STARTER
# ============================================================

AJUDA_POKEMON_PAGINAS = [
    {"titulo": "🌟 JORNADA", "texto": "`/starters` • Escolha seu inicial.\n`/perfil` • Perfil e personalização.\n`/equipe` • Equipe e ficha dos Pokémon.\n`/pokedex` • Pokédex dos 1025 Pokémon.\n`/insignias` • Insígnias por região.\n`/ginasios` • Ginásios e Elite 4."},
    {"titulo": "🌿 EXPLORAÇÃO", "texto": "`/explorar` • Encontre Pokémon e eventos PvE.\n`/c <nome>` ou `/capturar <nome>` • Capture o encontro.\n`/pokecaixa` • Recompensa diária e streak.\n`/pokecoins` • Consulte seu saldo.\n`/pokemart` • Loja de jornada e cosméticos.\n`/comprar` • Compre itens disponíveis."},
    {"titulo": "⚔️ BATALHAS", "texto": "`/batalhar @treinador` • Batalha PvP.\n`/evoluir` • Evoluções por nível, item ou regra especial.\n`/equipeadd` / `/equiperemover` • Organize a equipe.\n`/trocar` • Troca entre treinadores.\nIVs, nível, XP, tipos, golpes e stats influenciam as batalhas."},
    {"titulo": "🎨 PERFIL & CONQUISTAS", "texto": "`/perfilbio` • Altere sua bio.\n`/personalizar` • Abra a personalização.\n`/pokeconquistas` • Veja conquistas e recompensas.\n`/poketop` • Ranking de treinadores.\nCosméticos do PokéMart podem ser equipados no perfil."},
    {"titulo": "📖 POKÉDEX", "texto": "A Pokédex usa menus de seleção para navegar por região, faixa de IDs e Pokémon.\nCada ficha mostra ID, ícone, tipagem, raridade, golpes e linha evolutiva completa.\nA área da Pokédex também possui abas próprias para **Conquistas** e **Ginásios/Eventos**."},
]

POKELOG_ENTRADAS = [
    ("2.3v", "🏆 PokéTop • Atualização automática", "O Top 100 passa a trabalhar com atualização do ranking a cada 2 horas, mantendo o snapshot estável entre as atualizações."),
    ("2.2v", "📘 PokémonHelp • Catálogo automático de comandos", "A Central Pokémon agora lê automaticamente os comandos registrados neste Cog. Ao adicionar um novo comando Pokémon, ele aparece na ajuda sem precisar editar a lista manualmente."),
    ("2.1v", "🏆 PokéTop • Registro manual", "Agora o treinador precisa usar !poketopregistrar e possuir exatamente 6 Pokémon na equipe para entrar no ranking."),
    ("1.9v", "🏆 PokéTop • Registro automático", "Treinadores entram automaticamente no ranking; contas antigas, inclusive starters escolhidos antes do sistema, são reconhecidas sem cadastro manual."),
    ("1.8v", "🎁 PokéTop • Recompensas", "Top 100 agora possui recompensas semanais por colocação, com resgate único e proteção contra duplicação."),
    ("1.7v", "🏆 PokéTop • Top 100", "Ranking por nível do treinador e força da equipe, com seleção por ranking para visualizar o time completo."),
    ("1.6v", "🏆 Conquistas com recompensas reais", "Recompensas automáticas e únicas por conquista, com evolução especial vinculada a objetivos do treinador."),
    ("1.5v", "🧬 Evoluções", "Requisitos exibidos de forma compacta: nível, pedra/item, troca e condições especiais."),
    ("1.5v", "👤 Perfil corrigido", "Banco SQLite ganhou os métodos de perfil usados por !perfil e !personalizar."),
    ("1.5v", "📖 Pokédex reorganizada", "Menus modernos, aba de linha evolutiva completa e área de Pokémon especiais."),
    ("1.4v", "🛠️ Ajuda renovada", "Navegação por menu de seleção e botão dedicado para o PokeLog."),
    ("1.4v", "✨ Interface", "Identidade visual mais limpa, compacta e preparada para os 1025 Pokémon."),
    ("1.3v", "🧬 Ficha completa", "Tipos, golpes, raridade e evolução passaram a aparecer na Pokédex."),
]


def emoji_interface(chave, fallback):
    # O bot não pode usar arbitrariamente emojis de outros servidores.
    # Caso o administrador cadastre um emoji customizado depois, basta
    # substituir o valor neste mapa por uma string `<:nome:id>`.
    return fallback


class AjudaPaginaSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, pagina=0):
        self.cog = cog
        self.usuario_id = int(usuario_id)
        paginas = cog.obter_paginas_ajuda()
        icones = ["🌟", "🌿", "⚔️", "🎨", "📖", "🆕"]
        options = [
            discord.SelectOption(
                label=d["titulo"].replace("🌟 ", "").replace("🌿 ", "").replace("⚔️ ", "").replace("🎨 ", "").replace("📖 ", "").replace("🆕 ", ""),
                value=str(i),
                description=f"Página {i + 1}",
                default=i == int(pagina),
                emoji=icones[i] if i < len(icones) else "📘"
            )
            for i, d in enumerate(paginas)
        ]
        super().__init__(placeholder="📚 Escolha uma página...", options=options, row=0)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        pagina = int(self.values[0])
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_ajuda(pagina, interaction.user),
            view=AjudaPokemonView(self.cog, self.usuario_id, pagina)
        )


class AjudaPokemonView(discord.ui.View):
    def __init__(self, cog, usuario_id, pagina=0, log=False):
        super().__init__(timeout=300)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.pagina = int(pagina)
        if not log:
            self.add_item(AjudaPaginaSelect(cog, usuario_id, pagina))
        log_button = discord.ui.Button(
            label="PokeLog", emoji="🛠️", style=discord.ButtonStyle.primary if not log else discord.ButtonStyle.secondary, row=1
        )
        log_button.callback = self.abrir_log
        self.add_item(log_button)
        if log:
            voltar = discord.ui.Button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.secondary, row=1)
            voltar.callback = self.voltar
            self.add_item(voltar)
        fechar = discord.ui.Button(label="Fechar", emoji="✖️", style=discord.ButtonStyle.danger, row=1)
        fechar.callback = self.fechar
        self.add_item(fechar)

    async def abrir_log(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokelog(interaction.user),
            view=AjudaPokemonView(self.cog, self.usuario_id, self.pagina, log=True)
        )

    async def voltar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_ajuda(self.pagina, interaction.user),
            view=AjudaPokemonView(self.cog, self.usuario_id, self.pagina)
        )

    async def fechar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(content="📕 Central Pokémon fechada.", embed=None, view=None)
        self.stop()


class ConquistasPaginaSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, pagina=0):
        self.cog = cog
        self.usuario_id = int(usuario_id)
        total = max(1, (len(CONQUISTAS) + 4) // 5)
        options = [
            discord.SelectOption(
                label=f"Página {i + 1}",
                value=str(i),
                description=f"Conquistas {i * 5 + 1}–{min((i + 1) * 5, len(CONQUISTAS))}",
                emoji="🏆",
                default=i == int(pagina)
            ) for i in range(total)
        ]
        super().__init__(placeholder="🏆 Navegar pelas conquistas...", options=options, row=0)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        pagina = int(self.values[0])
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_conquistas(interaction.user, pagina),
            view=ConquistasView(self.cog, self.usuario_id, pagina)
        )


class ConquistasView(discord.ui.View):
    def __init__(self, cog, usuario_id, pagina=0):
        super().__init__(timeout=300)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.pagina = int(pagina)
        self.add_item(ConquistasPaginaSelect(cog, usuario_id, pagina))
        fechar = discord.ui.Button(label="Fechar", emoji="✖️", style=discord.ButtonStyle.danger, row=1)
        fechar.callback = self.fechar
        self.add_item(fechar)

    async def fechar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(content=None, embed=None, view=None)
        self.stop()


class PokedexRegiaoSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, regiao_atual):
        self.cog, self.usuario_id = cog, int(usuario_id)
        options = [discord.SelectOption(label=d["nome"], value=r, emoji=d["emoji"], description=f"#{d['min_id']:03d}–#{d['max_id']:04d}", default=r == regiao_atual) for r, d in REGIOES.items()]
        super().__init__(placeholder="🌎 Região da Pokédex...", options=options, row=0)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True); return
        r = self.values[0]
        total = self.cog.banco.contar_dex(self.usuario_id)
        t = self.cog.banco.obter_treinador(self.usuario_id)
        await interaction.response.edit_message(embed=self.cog.criar_embed_pokedex_indice(interaction.user, r, 0, total, t), view=PokedexView(self.cog, self.usuario_id, r, 0))


class PokedexFaixaSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, regiao, pagina_atual):
        self.cog, self.usuario_id, self.regiao = cog, int(usuario_id), regiao
        d = REGIOES[regiao]
        total = ((d["max_id"] - d["min_id"]) // 25) + 1
        options = []
        for p in range(total):
            ini = d["min_id"] + p * 25; fim = min(ini + 24, d["max_id"])
            options.append(discord.SelectOption(label=f"#{ini:03d} — #{fim:03d}", value=str(p), description=f"Página {p + 1}", default=p == pagina_atual))
        super().__init__(placeholder="📚 Faixa de IDs...", options=options, row=1)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True); return
        p = int(self.values[0]); total = self.cog.banco.contar_dex(self.usuario_id); t = self.cog.banco.obter_treinador(self.usuario_id)
        await interaction.response.edit_message(embed=self.cog.criar_embed_pokedex_indice(interaction.user, self.regiao, p, total, t), view=PokedexView(self.cog, self.usuario_id, self.regiao, p))


class PokedexPokemonSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, regiao, pagina):
        self.cog, self.usuario_id, self.regiao, self.pagina = cog, int(usuario_id), regiao, int(pagina)
        d = REGIOES[regiao]; ini = d["min_id"] + self.pagina * 25; fim = min(ini + 24, d["max_id"])
        options = [discord.SelectOption(label=f"#{pid:03d}", value=str(pid), description="Abrir ficha completa") for pid in range(ini, fim + 1)]
        super().__init__(placeholder="🔎 Escolha um Pokémon...", options=options, row=2)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True); return
        pid = int(self.values[0]); dados = await self.cog.api.pokemon(pid); especie = await self.cog.api.especie(pid)
        if not dados:
            await interaction.response.send_message("❌ A PokéAPI não respondeu agora.", ephemeral=True); return
        total = self.cog.banco.contar_dex(self.usuario_id)
        embed = await self.cog.criar_embed_pokedex_detalhe_async(interaction.user, dados, especie, total)
        await interaction.response.edit_message(embed=embed, view=PokedexView(self.cog, self.usuario_id, self.regiao, self.pagina, pid, "ficha"))


class PokedexModoSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, regiao, pagina, pokemon_id=None, modo="ficha"):
        self.cog, self.usuario_id = cog, int(usuario_id); self.regiao, self.pagina, self.pokemon_id = regiao, int(pagina), pokemon_id
        opcoes = [
            discord.SelectOption(label="Ficha do Pokémon", value="ficha", emoji="📋", description="Dados, tipos, golpes e raridade", default=modo == "ficha"),
            discord.SelectOption(label="Linha evolutiva", value="evolucao", emoji="🧬", description="Veja toda a cadeia e requisitos", default=modo == "evolucao"),
            discord.SelectOption(label="Conquistas", value="conquistas", emoji="🏆", description="Objetivos e recompensas especiais", default=modo == "conquistas"),
            discord.SelectOption(label="Ginásios & especiais", value="ginasios", emoji="🏟️", description="Pokémon obtidos em ginásios/eventos", default=modo == "ginasios"),
        ]
        super().__init__(placeholder="✨ Área da Pokédex...", options=opcoes, row=3)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True); return
        modo = self.values[0]
        if modo == "conquistas":
            embed = self.cog.criar_embed_conquistas(interaction.user, 0)
            await interaction.response.edit_message(embed=embed, view=ConquistasView(self.cog, self.usuario_id, 0))
            return
        elif modo == "ginasios":
            embed = self.cog.criar_embed_pokedex_ginasios(interaction.user)
        elif modo == "evolucao":
            if not self.pokemon_id:
                await interaction.response.send_message("🔎 Primeiro selecione um Pokémon no menu acima para ver sua linha evolutiva.", ephemeral=True); return
            dados = await self.cog.api.pokemon(self.pokemon_id); especie = await self.cog.api.especie(self.pokemon_id)
            embed = await self.cog.criar_embed_pokedex_evolucao_async(interaction.user, dados, especie)
        else:
            dados = await self.cog.api.pokemon(self.pokemon_id) if self.pokemon_id else None
            if not dados:
                embed = self.cog.criar_embed_pokedex_indice(interaction.user, self.regiao, self.pagina, self.cog.banco.contar_dex(self.usuario_id), self.cog.banco.obter_treinador(self.usuario_id))
            else:
                especie = await self.cog.api.especie(self.pokemon_id); embed = await self.cog.criar_embed_pokedex_detalhe_async(interaction.user, dados, especie, self.cog.banco.contar_dex(self.usuario_id))
        await interaction.response.edit_message(embed=embed, view=PokedexView(self.cog, self.usuario_id, self.regiao, self.pagina, self.pokemon_id, modo))


class PokedexVoltarButton(discord.ui.Button):
    def __init__(self, cog, usuario_id, regiao, pagina):
        self.cog, self.usuario_id, self.regiao, self.pagina = cog, int(usuario_id), regiao, int(pagina)
        super().__init__(label="Índice", emoji="↩️", style=discord.ButtonStyle.secondary, row=4)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True); return
        total = self.cog.banco.contar_dex(self.usuario_id); t = self.cog.banco.obter_treinador(self.usuario_id)
        await interaction.response.edit_message(embed=self.cog.criar_embed_pokedex_indice(interaction.user, self.regiao, self.pagina, total, t), view=PokedexView(self.cog, self.usuario_id, self.regiao, self.pagina))


class PokedexView(discord.ui.View):
    def __init__(self, cog, usuario_id, regiao="kanto", pagina=0, pokemon_id=None, modo="indice"):
        super().__init__(timeout=300)
        self.cog, self.usuario_id, self.regiao, self.pagina, self.pokemon_id, self.modo = cog, int(usuario_id), regiao, int(pagina), pokemon_id, modo
        self.add_item(PokedexRegiaoSelect(cog, usuario_id, regiao))
        self.add_item(PokedexFaixaSelect(cog, usuario_id, regiao, int(pagina)))
        self.add_item(PokedexPokemonSelect(cog, usuario_id, regiao, int(pagina)))
        self.add_item(PokedexModoSelect(cog, usuario_id, regiao, int(pagina), pokemon_id, modo))
        self.add_item(PokedexVoltarButton(cog, usuario_id, regiao, int(pagina)))


class StarterRegiaoSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, regiao_atual="kanto"):
        self.cog = cog
        self.usuario_id = int(usuario_id)
        options = []
        for regiao, dados in REGIOES.items():
            nivel_req = NIVEIS_REGIAO[regiao]
            options.append(discord.SelectOption(
                label=dados["nome"], value=regiao, emoji=dados["emoji"],
                description=f"Iniciais da geração • desbloqueia no nível {nivel_req}",
                default=regiao == regiao_atual
            ))
        super().__init__(placeholder="🌎 Escolha a região dos iniciais...", options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
            return
        treinador = self.cog.banco.obter_treinador(self.usuario_id)
        if treinador.get("starter"):
            await interaction.response.send_message(
                f"🌟 Você já escolheu **{treinador['starter']}** como seu inicial.", ephemeral=True
            )
            return
        regiao = self.values[0]
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_starters(interaction.user, regiao),
            view=StarterView(self.cog, self.usuario_id, regiao)
        )


class StarterView(discord.ui.View):
    def __init__(self, cog, usuario_id, regiao="kanto"):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.regiao = regiao

        self.add_item(StarterRegiaoSelect(cog, usuario_id, regiao))

        for starter in STARTERS_POR_REGIAO.get(regiao, STARTERS_POR_REGIAO["kanto"]):
            botao = discord.ui.Button(
                label=starter["nome"], emoji=starter["emoji"],
                style=discord.ButtonStyle.primary, row=1
            )
            botao.callback = self._callback_starter(starter)
            self.add_item(botao)

    def _callback_starter(self, starter_base):
        async def callback(interaction):
            if interaction.user.id != self.usuario_id:
                await interaction.response.send_message("❌ Esse painel pertence a outro treinador.", ephemeral=True)
                return
            treinador = self.cog.banco.obter_treinador(self.usuario_id)
            if treinador.get("starter"):
                await interaction.response.send_message(
                    f"❌ Você já possui **{treinador['starter']}** como starter.", ephemeral=True
                )
                return

            dados = await self.cog.api.pokemon(starter_base["id"])
            if not dados:
                await interaction.response.send_message("❌ Não consegui carregar esse inicial agora.", ephemeral=True)
                return

            base = extrair_base_stats_pokeapi(dados)
            tipos = [x.get("type", {}).get("name", "normal") for x in dados.get("types", [])]
            movimentos = await extrair_movimentos_combate(self.cog.api, dados, nivel=5)
            starter = dict(starter_base)
            starter.update({
                "regiao": self.regiao,
                "base_stats": base,
                "tipos": tipos,
                "movimentos": movimentos,
                "ivs": gerar_ivs(),
            })

            sucesso = await self.cog.banco.escolher_starter(
                interaction.user.id, starter
            )
            if not sucesso:
                await interaction.response.send_message("❌ Você já escolheu um starter.", ephemeral=True)
                return

            await self.cog.banco.desbloquear_conquista(
                interaction.user.id, "primeiro_pokemon"
            )

            sprite = dados.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default")
            embed = discord.Embed(
                title=f"{starter['emoji']} STARTER ESCOLHIDO!",
                description=(
                    f"**{interaction.user.display_name}**, seu parceiro será **{starter['nome']}**!\n\n"
                    f"🌎 Região: **{REGIOES[self.regiao]['nome']}**\n"
                    "🎒 Sua jornada começou. Boa sorte, treinador!"
                ), color=COR_VERDE
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            if sprite:
                embed.set_image(url=sprite)
            embed.set_footer(text=POKEMON_AVISO)
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
        return callback




def aplicar_fonte(texto, fonte):
    texto = str(texto)
    if fonte == "bold":
        mapa = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇")
        return texto.translate(mapa)
    if fonte == "mono":
        mapa = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣")
        return texto.translate(mapa)
    return texto


class PerfilView(discord.ui.View):
    def __init__(self, cog, usuario_id, pode_personalizar=True):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.pode_personalizar = pode_personalizar

        personalizar = discord.ui.Button(
            label="Personalizar",
            emoji="🎨",
            style=discord.ButtonStyle.primary,
            disabled=not pode_personalizar
        )
        personalizar.callback = self.personalizar
        self.add_item(personalizar)

        atualizar = discord.ui.Button(
            label="Atualizar",
            emoji="🔄",
            style=discord.ButtonStyle.secondary
        )
        atualizar.callback = self.atualizar
        self.add_item(atualizar)

        mart = discord.ui.Button(
            label="PokéMart",
            emoji="🛒",
            style=discord.ButtonStyle.success,
            disabled=not pode_personalizar
        )
        mart.callback = self.mart
        self.add_item(mart)

    async def personalizar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎨 PERSONALIZAR PERFIL",
            description=(
                "Escolha uma categoria abaixo.\n\n"
                "🖼️ **Banners**\n"
                "✍️ **Fontes da bio**\n"
                "🏅 **Emblemas**\n\n"
                "O menu mostra somente os cosméticos que você "
                "já comprou no **PokéMart**."
            ),
            color=COR_ROXO
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.edit_message(
            embed=embed,
            view=PerfilPersonalizarView(self.cog, self.usuario_id)
        )

    async def atualizar(self, interaction):
        treinador = self.cog.banco.obter_perfil(self.usuario_id)
        membro = interaction.guild.get_member(self.usuario_id)

        if membro is None:
            await interaction.response.send_message(
                "❌ Não encontrei esse treinador no servidor.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_perfil(membro, treinador),
            view=self
        )

    async def mart(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Você não pode personalizar o perfil de outro treinador.",
                ephemeral=True
            )
            return

        treinador = self.cog.banco.obter_perfil(self.usuario_id)

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemart(
                treinador,
                "perfil"
            ),
            view=PokeMartView(
                self.cog,
                "perfil"
            )
        )


class PerfilPersonalizarView(discord.ui.View):
    def __init__(self, cog, usuario_id):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)

        for label, emoji, tipo, style in [
            ("Banners", "🖼️", "banner", discord.ButtonStyle.primary),
            ("Fontes", "✍️", "fonte", discord.ButtonStyle.secondary),
            ("Emblemas", "🏅", "emblema", discord.ButtonStyle.success),
        ]:
            button = discord.ui.Button(
                label=label,
                emoji=emoji,
                style=style
            )
            button.callback = self.criar_callback(tipo)
            self.add_item(button)

        voltar = discord.ui.Button(
            label="Voltar ao Perfil",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        voltar.callback = self.voltar
        self.add_item(voltar)

        mart = discord.ui.Button(
            label="PokéMart",
            emoji="🛒",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        mart.callback = self.mart
        self.add_item(mart)

    def criar_callback(self, tipo):
        async def callback(interaction):
            if interaction.user.id != self.usuario_id:
                await interaction.response.send_message(
                    "❌ Esse painel pertence a outro treinador.",
                    ephemeral=True
                )
                return

            await self.mostrar_categoria(interaction, tipo)

        return callback

    async def mostrar_categoria(self, interaction, tipo):
        nomes = {
            "banner": "🖼️ SEUS BANNERS",
            "fonte": "✍️ SUAS FONTES",
            "emblema": "🏅 SEUS EMBLEMAS"
        }

        itens = [
            (item_id, PERFIL_LOJA[item_id])
            for item_id in self.cog.banco.listar_itens_perfil(
                self.usuario_id
            )
            if item_id in PERFIL_LOJA
            and PERFIL_LOJA[item_id]["tipo"] == tipo
        ]

        embed = discord.Embed(
            title=nomes[tipo],
            description=(
                "Selecione um item abaixo para visualizar sua imagem "
                "e equipá-lo.\n\n"
                "💡 Apenas itens **já comprados** aparecem aqui."
            ),
            color=COR_ROXO
        )

        if not itens:
            embed.description += (
                "\n\n📭 Você ainda não possui nenhum item dessa categoria."
            )

        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.edit_message(
            embed=embed,
            view=PerfilCategoriaView(
                self.cog,
                self.usuario_id,
                tipo
            )
        )

    async def voltar(self, interaction):
        treinador = self.cog.banco.obter_perfil(self.usuario_id)
        membro = interaction.guild.get_member(self.usuario_id)

        if membro is None:
            await interaction.response.send_message(
                "❌ Não encontrei esse treinador.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_perfil(membro, treinador),
            view=PerfilView(
                self.cog,
                self.usuario_id,
                True
            )
        )

    async def mart(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        treinador = self.cog.banco.obter_perfil(self.usuario_id)

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemart(
                treinador,
                "perfil"
            ),
            view=PokeMartView(
                self.cog,
                "perfil"
            )
        )


class PerfilCategoriaSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, tipo):
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.tipo = tipo

        owned = self.cog.banco.listar_itens_perfil(
            self.usuario_id
        )

        itens = [
            (item_id, PERFIL_LOJA[item_id])
            for item_id in owned
            if item_id in PERFIL_LOJA
            and PERFIL_LOJA[item_id]["tipo"] == tipo
        ]

        if itens:
            options = [
                discord.SelectOption(
                    label=item["nome"][:100],
                    value=item_id,
                    description="Comprado • selecione para visualizar"
                )
                for item_id, item in itens[:25]
            ]
        else:
            # Discord exige pelo menos uma option.
            options = [
                discord.SelectOption(
                    label="Nenhum item comprado",
                    value="__nenhum__",
                    description="Compre cosméticos no PokéMart",
                    default=True
                )
            ]

        super().__init__(
            placeholder="Selecione um cosmético...",
            min_values=1,
            max_values=1,
            options=options,
            disabled=not bool(itens)
        )

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        item_id = self.values[0]

        if item_id == "__nenhum__":
            await interaction.response.send_message(
                "📭 Você ainda não possui cosméticos dessa categoria.",
                ephemeral=True
            )
            return

        item = PERFIL_LOJA[item_id]

        embed = discord.Embed(
            title=f"🎨 {item['nome']}",
            description=(
                f"{item['descricao']}\n\n"
                "✅ **Item adquirido**\n"
                "✨ Você pode equipá-lo no seu perfil."
            ),
            color=COR_ROXO
        )

        embed.set_image(url=item["imagem"])
        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.edit_message(
            embed=embed,
            view=PerfilItemView(
                self.cog,
                self.usuario_id,
                self.tipo,
                item_id
            )
        )


class PerfilCategoriaView(discord.ui.View):
    def __init__(self, cog, usuario_id, tipo):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.tipo = tipo

        self.add_item(
            PerfilCategoriaSelect(
                cog,
                usuario_id,
                tipo
            )
        )

        voltar = discord.ui.Button(
            label="Voltar",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        voltar.callback = self.voltar
        self.add_item(voltar)

    async def voltar(self, interaction):
        embed = discord.Embed(
            title="🎨 PERSONALIZAR PERFIL",
            description="Escolha uma categoria.",
            color=COR_ROXO
        )
        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.edit_message(
            embed=embed,
            view=PerfilPersonalizarView(
                self.cog,
                self.usuario_id
            )
        )


class PerfilItemView(discord.ui.View):
    def __init__(self, cog, usuario_id, tipo, item_id):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.tipo = tipo
        self.item_id = item_id

        equipar = discord.ui.Button(
            label="Equipar",
            emoji="✨",
            style=discord.ButtonStyle.success
        )
        equipar.callback = self.equipar
        self.add_item(equipar)

        voltar = discord.ui.Button(
            label="Voltar",
            emoji="↩️",
            style=discord.ButtonStyle.secondary
        )
        voltar.callback = self.voltar
        self.add_item(voltar)

    async def equipar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        item = PERFIL_LOJA.get(self.item_id)

        if not item:
            await interaction.response.send_message(
                "❌ Cosmético inválido.",
                ephemeral=True
            )
            return

        resultado = await self.cog.banco.equipar_perfil(
            self.usuario_id,
            self.item_id
        )

        ok, motivo = resultado

        if not ok:
            await interaction.response.send_message(
                "❌ Você não possui esse cosmético.",
                ephemeral=True
            )
            return

        membro = interaction.guild.get_member(self.usuario_id)

        if membro is None:
            await interaction.response.send_message(
                "❌ Não encontrei seu perfil no servidor.",
                ephemeral=True
            )
            return

        treinador = self.cog.banco.obter_perfil(
            self.usuario_id
        )

        embed = self.cog.criar_embed_perfil(
            membro,
            treinador
        )

        await interaction.response.edit_message(
            embed=embed,
            view=PerfilView(
                self.cog,
                self.usuario_id,
                True
            )
        )

    async def voltar(self, interaction):
        embed = discord.Embed(
            title="🎨 PERSONALIZAR PERFIL",
            description="Escolha uma categoria.",
            color=COR_ROXO
        )
        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.edit_message(
            embed=embed,
            view=PerfilPersonalizarView(
                self.cog,
                self.usuario_id
            )
        )


class PokeMartSelect(discord.ui.Select):
    def __init__(self, cog, categoria):
        self.cog = cog
        self.categoria = categoria

        if categoria == "perfil":
            catalogo = PERFIL_LOJA
        else:
            catalogo = {
                k: v for k, v in LOJA.items()
                if v.get("categoria") == "jornada"
            }

        options = [
            discord.SelectOption(
                label=item["nome"][:100],
                value=chave,
                description=(
                    f"{item['preco']} Pokécoins • "
                    f"{item['descricao']}"
                )[:100]
            )
            for chave, item in catalogo.items()
        ]

        super().__init__(
            placeholder=(
                "Escolha um item da jornada..."
                if categoria == "jornada"
                else "Escolha um item de perfil..."
            ),
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        item_id = self.values[0]
        treinador = self.cog.banco.obter_treinador(
            interaction.user.id
        )

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemart(
                treinador,
                self.categoria,
                item_id
            ),
            view=PokeMartView(
                self.cog,
                self.categoria,
                item_id
            )
        )


class PokeMartView(discord.ui.View):
    def __init__(self, cog, categoria="jornada", item_id=None):
        super().__init__(timeout=180)

        self.cog = cog
        self.categoria = categoria
        self.item_id = item_id

        self.add_item(
            PokeMartSelect(
                cog,
                categoria
            )
        )

        comprar = discord.ui.Button(
            label="Comprar",
            emoji="🛒",
            style=discord.ButtonStyle.success,
            row=1,
            disabled=item_id is None
        )
        comprar.callback = self.comprar_callback
        self.add_item(comprar)

        jornada = discord.ui.Button(
            label="Jornada",
            style=discord.ButtonStyle.primary,
            row=1
        )
        jornada.callback = self.jornada_callback
        self.add_item(jornada)

        perfil = discord.ui.Button(
            label="Perfil",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        perfil.callback = self.perfil_callback
        self.add_item(perfil)

        estoque = discord.ui.Button(
            label="Estoque",
            style=discord.ButtonStyle.secondary,
            row=2
        )
        estoque.callback = self.estoque_callback
        self.add_item(estoque)

    async def comprar_callback(self, interaction):
        if not self.item_id:
            await interaction.response.send_message(
                "❌ Selecione um item primeiro.",
                ephemeral=True
            )
            return

        if self.categoria == "perfil":
            item = PERFIL_LOJA.get(self.item_id)

            if not item:
                await interaction.response.send_message(
                    "❌ Item inválido.",
                    ephemeral=True
                )
                return

            ok, motivo = await self.cog.banco.comprar_item_perfil(
                interaction.user.id,
                self.item_id,
                item["preco"]
            )

            if not ok:
                await interaction.response.send_message(
                    (
                        "✨ Você já possui esse cosmético."
                        if motivo == "possui"
                        else "❌ Você não possui Pokécoins suficientes."
                    ),
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="✨ COSMÉTICO ADQUIRIDO!",
                description=(
                    f"**{item['nome']}**\n\n"
                    f"💰 Custo: **{item['preco']} Pokécoins**\n"
                    "🎨 Você já pode equipá-lo no perfil."
                ),
                color=COR_ROXO
            )
        else:
            item = LOJA.get(self.item_id)

            if not item:
                await interaction.response.send_message(
                    "❌ Item inválido.",
                    ephemeral=True
                )
                return

            # Balls continuam usando as colunas legadas do treinador.
            if self.item_id in ("pokeball", "greatball", "ultraball"):
                treinador = self.cog.banco.obter_treinador(
                    interaction.user.id
                )
                custo = item["preco"]

                if treinador["pokecoins"] < custo:
                    await interaction.response.send_message(
                        "❌ Você não possui Pokécoins suficientes.",
                        ephemeral=True
                    )
                    return

                pago = await self.cog.banco.alterar_pokecoins(
                    interaction.user.id,
                    -custo
                )
                recebido = await self.cog.banco.alterar_ball(
                    interaction.user.id,
                    self.item_id,
                    1
                )

                if not pago or not recebido:
                    if pago:
                        await self.cog.banco.alterar_pokecoins(
                            interaction.user.id,
                            custo
                        )
                    await interaction.response.send_message(
                        "❌ A compra foi revertida.",
                        ephemeral=True
                    )
                    return
                custo_final = custo
            else:
                ok, resultado = await self.cog.banco.comprar_item_jornada(
                    interaction.user.id,
                    self.item_id,
                    item["preco"],
                    1
                )

                if not ok:
                    await interaction.response.send_message(
                        (
                            "❌ Você não possui Pokécoins suficientes."
                            if resultado == "saldo"
                            else "❌ Não foi possível concluir a compra."
                        ),
                        ephemeral=True
                    )
                    return

                custo_final = resultado

            embed = discord.Embed(
                title="🛒 ITEM DA JORNADA ADQUIRIDO!",
                description=(
                    f"**1x {item['nome']}**\n\n"
                    f"💰 Custo: **{custo_final} Pokécoins**\n"
                    "🎒 O item foi adicionado ao seu estoque."
                ),
                color=COR_VERDE
            )

        embed.set_image(url=item["imagem"])
        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    async def jornada_callback(self, interaction):
        treinador = self.cog.banco.obter_treinador(
            interaction.user.id
        )
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemart(
                treinador,
                "jornada"
            ),
            view=PokeMartView(
                self.cog,
                "jornada"
            )
        )

    async def perfil_callback(self, interaction):
        treinador = self.cog.banco.obter_treinador(
            interaction.user.id
        )
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemart(
                treinador,
                "perfil"
            ),
            view=PokeMartView(
                self.cog,
                "perfil"
            )
        )

    async def estoque_callback(self, interaction):
        treinador = self.cog.banco.obter_treinador(
            interaction.user.id
        )

        linhas = [
            f"Poké Ball: **{treinador['pokeballs']}**",
            f"Great Ball: **{treinador['greatballs']}**",
            f"Ultra Ball: **{treinador['ultraballs']}**",
        ]

        for row in self.cog.banco.listar_itens_jornada(
            interaction.user.id
        ):
            item = LOJA.get(row["item_id"])
            if item:
                linhas.append(
                    f"{item['nome']}: **{row['quantidade']}**"
                )

        embed = discord.Embed(
            title="📦 SEU ESTOQUE",
            description="\n".join(linhas),
            color=COR_AZUL
        )
        embed.set_footer(text=POKEMON_AVISO)

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class InsigniasRegiaoSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, regiao_atual):
        self.cog = cog
        self.usuario_id = int(usuario_id)

        options = []
        for regiao, dados in REGIOES.items():
            requisito = NIVEIS_REGIAO[regiao]
            treinador = self.cog.banco.obter_treinador(usuario_id)
            desbloqueada = int(treinador["nivel"]) >= requisito

            badges = len(
                self.cog.banco.listar_insignias(usuario_id, regiao)
            )

            options.append(
                discord.SelectOption(
                    label=dados["nome"],
                    value=regiao,
                    emoji=dados["emoji"],
                    description=(
                        f"{badges}/8 insígnias • "
                        f"Nível {requisito}"
                        if desbloqueada
                        else f"Bloqueada • Nível {requisito}"
                    ),
                    default=regiao == regiao_atual
                )
            )

        super().__init__(
            placeholder="🌎 Escolha uma região...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        regiao = self.values[0]
        treinador = self.cog.banco.obter_treinador(self.usuario_id)

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_insignias(
                interaction.user,
                regiao,
                treinador
            ),
            view=InsigniasRegiaoView(
                self.cog,
                self.usuario_id,
                regiao
            )
        )


class InsigniasRegiaoView(discord.ui.View):
    def __init__(self, cog, usuario_id, regiao):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.regiao = regiao
        self.add_item(
            InsigniasRegiaoSelect(cog, usuario_id, regiao)
        )

        ginasios = discord.ui.Button(
            label="Ginásios",
            emoji="🏟️",
            style=discord.ButtonStyle.primary,
            row=1
        )
        ginasios.callback = self.abrir_ginasios
        self.add_item(ginasios)

    async def abrir_ginasios(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_ginasios(
                interaction.user,
                self.regiao
            ),
            view=GinasiosView(
                self.cog,
                self.usuario_id,
                self.regiao
            )
        )


class GinasiosView(discord.ui.View):
    def __init__(self, cog, usuario_id, regiao):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.regiao = regiao

        desafiar = discord.ui.Button(
            label="Desafiar próximo ginásio",
            emoji="⚔️",
            style=discord.ButtonStyle.danger
        )
        desafiar.callback = self.desafiar
        self.add_item(desafiar)

        elite = discord.ui.Button(
            label="Elite 4",
            emoji="👑",
            style=discord.ButtonStyle.primary
        )
        elite.callback = self.desafiar_elite
        self.add_item(elite)

        voltar = discord.ui.Button(
            label="Insígnias",
            emoji="🏅",
            style=discord.ButtonStyle.secondary
        )
        voltar.callback = self.voltar
        self.add_item(voltar)

    async def desafiar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        treinador = self.cog.banco.obter_treinador(self.usuario_id)
        nivel = int(treinador["nivel"])
        requisito = NIVEIS_REGIAO[self.regiao]

        if nivel < requisito:
            await interaction.response.send_message(
                f"🔒 Essa região abre no nível **{requisito}**.",
                ephemeral=True
            )
            return

        badges = self.cog.banco.listar_insignias(
            self.usuario_id,
            self.regiao
        )
        proximo = len(badges) + 1

        if proximo > 8:
            await interaction.response.send_message(
                "👑 Você já conquistou as 8 insígnias desta região.",
                ephemeral=True
            )
            return

        await self.cog.iniciar_batalha_ginasio(
            interaction,
            self.regiao,
            proximo
        )

    async def desafiar_elite(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        await self.cog.iniciar_batalha_elite(
            interaction,
            self.regiao
        )

    async def voltar(self, interaction):
        treinador = self.cog.banco.obter_treinador(self.usuario_id)
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_insignias(
                interaction.user,
                self.regiao,
                treinador
            ),
            view=InsigniasRegiaoView(
                self.cog,
                self.usuario_id,
                self.regiao
            )
        )


class GinasioBattleView(discord.ui.View):
    def __init__(self, cog, estado):
        super().__init__(timeout=900)
        self.cog = cog
        self.estado = estado

        for indice in range(4):
            botao = discord.ui.Button(
                label=f"Golpe {indice + 1}",
                emoji="⚔️",
                style=discord.ButtonStyle.primary,
                row=0
            )
            botao.callback = self.criar_ataque_callback(indice)
            self.add_item(botao)

        trocar = discord.ui.Button(
            label="Trocar Pokémon",
            emoji="🔄",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        trocar.callback = self.trocar
        self.add_item(trocar)

        desistir = discord.ui.Button(
            label="Desistir",
            emoji="🏳️",
            style=discord.ButtonStyle.danger,
            row=1
        )
        desistir.callback = self.desistir
        self.add_item(desistir)

        self.atualizar_botoes()

    def atualizar_botoes(self):
        pokemon = self.estado["equipe"][self.estado["ativo"]]
        movimentos = self.estado["movimentos_jogador"].get(
            int(pokemon["id"]),
            []
        )
        pokemon_vivo = self.estado["hp_jogador"][self.estado["ativo"]] > 0
        for i, item in enumerate(self.children[:4]):
            if i < len(movimentos) and pokemon_vivo:
                movimento = movimentos[i]
                item.label = movimento["nome"][:80]
                item.emoji = obter_emoji_tipo(movimento["tipo"])
                item.disabled = False
            else:
                item.label = "Troque o Pokémon" if not pokemon_vivo else "Sem golpe"
                item.emoji = "🔄" if not pokemon_vivo else "⚔️"
                item.disabled = True

    def criar_ataque_callback(self, indice):
        async def callback(interaction):
            await self.cog.processar_turno_ginasio(
                interaction,
                self,
                indice
            )
        return callback

    async def trocar(self, interaction):
        if interaction.user.id != self.estado["usuario_id"]:
            await interaction.response.send_message(
                "❌ Essa batalha pertence a outro treinador.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔄 Use o menu abaixo para escolher um Pokémon vivo.",
            view=TrocaPokemonView(
                self.cog,
                self.estado
            ),
            ephemeral=True
        )

    async def desistir(self, interaction):
        if interaction.user.id != self.estado["usuario_id"]:
            await interaction.response.send_message(
                "❌ Essa batalha pertence a outro treinador.",
                ephemeral=True
            )
            return

        self.cog.gym_battles.pop(
            self.estado["usuario_id"],
            None
        )
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_batalha_ginasio(
                self.estado,
                "🏳️ Você desistiu da batalha."
            ),
            view=self
        )
        self.stop()


class TrocaPokemonSelect(discord.ui.Select):
    def __init__(self, cog, estado):
        self.cog = cog
        self.estado = estado

        options = []
        for idx, pokemon in enumerate(estado["equipe"]):
            if estado["hp_jogador"][idx] <= 0:
                continue
            if idx == estado["ativo"]:
                continue
            options.append(
                discord.SelectOption(
                    label=f"{pokemon['nome']} • Nv. {pokemon['nivel']}",
                    value=str(idx),
                    description=f"HP {int(estado['hp_jogador'][idx])}/{pokemon['hp']}"
                )
            )

        super().__init__(
            placeholder="Escolha seu próximo Pokémon...",
            min_values=1,
            max_values=1,
            options=options[:25],
            disabled=not options
        )

    async def callback(self, interaction):
        if interaction.user.id != self.estado["usuario_id"]:
            await interaction.response.send_message(
                "❌ Essa batalha pertence a outro treinador.",
                ephemeral=True
            )
            return

        idx = int(self.values[0])
        self.estado["ativo"] = idx
        self.estado["log"].append(
            f"🔄 Você enviou **{self.estado['equipe'][idx]['nome']}**!"
        )

        await interaction.response.edit_message(
            content="",
            embed=self.cog.criar_embed_batalha_ginasio(
                self.estado,
                "🔄 Pokémon trocado!"
            ),
            view=GinasioBattleView(
                self.cog,
                self.estado
            )
        )


class TrocaPokemonView(discord.ui.View):
    def __init__(self, cog, estado):
        super().__init__(timeout=60)
        self.add_item(TrocaPokemonSelect(cog, estado))


# ============================================================
# COG
# ============================================================

class EquipeSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, pokemons):
        self.cog = cog
        self.usuario_id = int(usuario_id)

        options = [
            discord.SelectOption(
                label=f"{p['nome']} • Nv. {p['nivel']}"[:100],
                value=str(p["id"]),
                description=(
                    f"IV {int(p['iv_hp']) + int(p['iv_ataque']) + int(p['iv_defesa']) + int(p['iv_velocidade'])}/124"
                )[:100]
            )
            for p in pokemons[:25]
        ]

        super().__init__(
            placeholder="🔎 Selecione um Pokémon da equipe...",
            min_values=1,
            max_values=1,
            options=options,
            disabled=not options
        )

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        pokemon = self.cog.banco.obter_pokemon(int(self.values[0]))
        if not pokemon or int(pokemon["treinador_id"]) != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse Pokémon não pertence a você.",
                ephemeral=True
            )
            return

        pokemon = await self.cog.sincronizar_pokemon_com_api(pokemon)

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemon_detalhado(pokemon),
            view=PokemonDetalheView(
                self.cog,
                self.usuario_id,
                pokemon["id"]
            )
        )


class EquipeView(discord.ui.View):
    def __init__(self, cog, usuario_id, pokemons):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)

        self.add_item(
            EquipeSelect(cog, usuario_id, pokemons)
        )

        atualizar = discord.ui.Button(
            label="Atualizar equipe",
            emoji="🔄",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        atualizar.callback = self.atualizar
        self.add_item(atualizar)

    async def atualizar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        pokemons = [
            p for p in self.cog.banco.listar_pokemon(self.usuario_id)
            if p["equipe"]
        ][:6]

        sincronizados = []
        for pokemon in pokemons:
            sincronizados.append(
                await self.cog.sincronizar_pokemon_com_api(pokemon)
            )
        pokemons = sincronizados

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_equipe(
                interaction.user,
                pokemons
            ),
            view=EquipeView(
                self.cog,
                self.usuario_id,
                pokemons
            )
        )


class PokemonDetalheView(discord.ui.View):
    def __init__(self, cog, usuario_id, pokemon_id):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.pokemon_id = int(pokemon_id)

        voltar = discord.ui.Button(
            label="Voltar para equipe",
            emoji="↩️",
            style=discord.ButtonStyle.primary
        )
        voltar.callback = self.voltar
        self.add_item(voltar)

        atualizar = discord.ui.Button(
            label="Atualizar",
            emoji="🔄",
            style=discord.ButtonStyle.secondary
        )
        atualizar.callback = self.atualizar
        self.add_item(atualizar)

    async def voltar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        pokemons = [
            p for p in self.cog.banco.listar_pokemon(self.usuario_id)
            if p["equipe"]
        ][:6]

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_equipe(
                interaction.user,
                pokemons
            ),
            view=EquipeView(
                self.cog,
                self.usuario_id,
                pokemons
            )
        )

    async def atualizar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message(
                "❌ Esse painel pertence a outro treinador.",
                ephemeral=True
            )
            return

        pokemon = self.cog.banco.obter_pokemon(self.pokemon_id)
        if not pokemon or int(pokemon["treinador_id"]) != self.usuario_id:
            await interaction.response.send_message(
                "❌ Pokémon não encontrado.",
                ephemeral=True
            )
            return

        pokemon = await self.cog.sincronizar_pokemon_com_api(pokemon)

        await interaction.response.edit_message(
            embed=self.cog.criar_embed_pokemon_detalhado(pokemon),
            view=self
        )


# ============================================================
# RECOMPENSAS DO POKÉTOP
# ============================================================

POKETOP_RECOMPENSAS = [
    (1, 1, {"pokecoins": 10000, "xp": 2000, "item_id": "ultraball", "quantidade": 10}),
    (2, 2, {"pokecoins": 7500, "xp": 1500, "item_id": "ultraball", "quantidade": 7}),
    (3, 3, {"pokecoins": 5000, "xp": 1200, "item_id": "ultraball", "quantidade": 5}),
    (4, 10, {"pokecoins": 3000, "xp": 800, "item_id": "greatball", "quantidade": 5}),
    (11, 25, {"pokecoins": 2000, "xp": 500, "item_id": "greatball", "quantidade": 3}),
    (26, 50, {"pokecoins": 1000, "xp": 300, "item_id": "greatball", "quantidade": 2}),
    (51, 100, {"pokecoins": 500, "xp": 150, "item_id": "pokeball", "quantidade": 5}),
]


def periodo_poketop_atual():
    # Recompensa semanal: segunda-feira a domingo, usando UTC para manter
    # o período consistente entre servidores e evitar dupla premiação.
    agora = datetime.now(timezone.utc)
    iso = agora.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def recompensa_poketop(posicao):
    posicao = int(posicao)
    for minimo, maximo, recompensa in POKETOP_RECOMPENSAS:
        if minimo <= posicao <= maximo:
            return dict(recompensa)
    return None


def texto_recompensa_poketop(recompensa):
    partes = []
    if recompensa.get("pokecoins"):
        partes.append(f"🪙 +{int(recompensa['pokecoins']):,} Pokécoins")
    if recompensa.get("xp"):
        partes.append(f"⭐ +{int(recompensa['xp']):,} XP")
    if recompensa.get("item_id") and recompensa.get("quantidade"):
        nomes = {"pokeball": "Poké Balls", "greatball": "Great Balls", "ultraball": "Ultra Balls"}
        partes.append(f"🎒 +{int(recompensa['quantidade'])} {nomes.get(recompensa['item_id'], recompensa['item_id'])}")
    return " • ".join(partes) if partes else "Sem recompensa"


# ============================================================
# VIEWS DO POKÉTOP
# ============================================================


class PoketopSelect(discord.ui.Select):
    def __init__(self, cog, usuario_id, ranking, pagina=0):
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.ranking = ranking
        self.pagina = pagina
        inicio = pagina * 10
        itens = ranking[inicio:inicio + 10]
        options = []
        medalhas = {1: "🥇", 2: "🥈", 3: "🥉"}
        for item in itens:
            posicao = item["posicao"]
            options.append(discord.SelectOption(
                label=f"#{posicao} • {str(item['equipe'][0]['nome']).title()}",
                description=(f"Nv. {item['nivel']} • Poder {item['poder']} • {item['quantidade']}/6 Pokémon")[:100],
                emoji=medalhas.get(posicao, "🏆"),
                value=str(posicao),
            ))
        super().__init__(
            placeholder="🔎 Escolha um ranking para ver a equipe...",
            min_values=1, max_values=1,
            options=options or [discord.SelectOption(label="Nenhuma equipe disponível", value="0")],
            disabled=not options, row=0,
        )

    async def callback(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        posicao = int(self.values[0])
        if posicao <= 0 or posicao > len(self.ranking):
            await interaction.response.send_message("❌ Ranking inválido.", ephemeral=True)
            return
        item = self.ranking[posicao - 1]
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_poketop_equipe(interaction.guild, item),
            view=PoketopEquipeView(self.cog, self.usuario_id, self.ranking, self.pagina),
        )


class PoketopView(discord.ui.View):
    def __init__(self, cog, usuario_id, ranking, pagina=0):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.ranking = ranking
        self.pagina = pagina
        self.total_paginas = max(1, (len(ranking) + 9) // 10)
        self.add_item(PoketopSelect(cog, usuario_id, ranking, pagina))
        anterior = discord.ui.Button(label="Anterior", emoji="◀️", style=discord.ButtonStyle.secondary, row=1, disabled=pagina <= 0)
        anterior.callback = self.voltar
        self.add_item(anterior)
        pagina_btn = discord.ui.Button(label=f"{pagina + 1}/{self.total_paginas}", emoji="🏆", style=discord.ButtonStyle.primary, row=1, disabled=True)
        self.add_item(pagina_btn)
        proxima = discord.ui.Button(label="Próxima", emoji="▶️", style=discord.ButtonStyle.secondary, row=1, disabled=pagina >= self.total_paginas - 1)
        proxima.callback = self.avancar
        self.add_item(proxima)
        recompensas = discord.ui.Button(label="Recompensas", emoji="🎁", style=discord.ButtonStyle.success, row=2)
        recompensas.callback = self.abrir_recompensas
        self.add_item(recompensas)

    async def abrir_recompensas(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        ranking_atual = await self.cog.obter_ranking_poketop(interaction.guild)
        posicao = next((int(item["posicao"]) for item in ranking_atual if int(item["id"]) == self.usuario_id), None)
        periodo = periodo_poketop_atual()
        ja = self.cog.banco.obter_recompensa_poketop_resgatada(interaction.guild.id, self.usuario_id, periodo)
        if posicao:
            recompensa = recompensa_poketop(posicao)
            descricao = (
                f"🏆 Sua posição atual: **#{posicao}**\n"
                f"📅 Temporada: **{periodo}**\n\n"
                f"🎁 **Recompensa da colocação**\n{texto_recompensa_poketop(recompensa)}\n\n"
                + ("✅ **Você já resgatou a recompensa desta semana.**" if ja else "🎁 Você pode resgatar sua recompensa uma vez nesta semana." )
            )
        else:
            descricao = (
                f"📅 Temporada: **{periodo}**\n\n"
                "Você ainda não está no Top 100.\n"
                "Monte uma equipe mais forte e tente novamente!"
            )
        embed = discord.Embed(title="🎁 ROYALT • RECOMPENSAS DO POKÉTOP", description=descricao, color=COR_AMARELO)
        embed.set_footer(text=POKEMON_AVISO)
        await interaction.response.edit_message(embed=embed, view=PoketopRecompensasView(self.cog, self.usuario_id, self.ranking, self.pagina))

    async def voltar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(embed=self.cog.criar_embed_poketop(interaction.guild, self.ranking, self.pagina - 1), view=PoketopView(self.cog, self.usuario_id, self.ranking, self.pagina - 1))

    async def avancar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(embed=self.cog.criar_embed_poketop(interaction.guild, self.ranking, self.pagina + 1), view=PoketopView(self.cog, self.usuario_id, self.ranking, self.pagina + 1))


class PoketopRecompensasView(discord.ui.View):
    def __init__(self, cog, usuario_id, ranking, pagina):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.ranking = ranking
        self.pagina = pagina
        resgatar = discord.ui.Button(label="Resgatar recompensa", emoji="🎁", style=discord.ButtonStyle.success)
        resgatar.callback = self.resgatar
        self.add_item(resgatar)
        voltar = discord.ui.Button(label="Voltar ao ranking", emoji="🏆", style=discord.ButtonStyle.primary)
        voltar.callback = self.voltar
        self.add_item(voltar)
        fechar = discord.ui.Button(label="Fechar", emoji="✖️", style=discord.ButtonStyle.danger)
        fechar.callback = self.fechar
        self.add_item(fechar)

    async def resgatar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        ranking_atual = await self.cog.obter_ranking_poketop(interaction.guild)
        item = next((x for x in ranking_atual if int(x["id"]) == self.usuario_id), None)
        if not item:
            await interaction.response.send_message("❌ Você não está no Top 100 desta semana.", ephemeral=True)
            return
        posicao = int(item["posicao"])
        recompensa = recompensa_poketop(posicao)
        if not recompensa:
            await interaction.response.send_message("❌ Esta colocação não possui recompensa configurada.", ephemeral=True)
            return
        resultado = await self.cog.banco.resgatar_recompensa_poketop(
            interaction.guild.id, self.usuario_id, periodo_poketop_atual(), posicao, recompensa
        )
        if resultado["status"] == "ja_resgatada":
            texto = (
                f"⚠️ Você já resgatou a recompensa desta semana na posição **#{resultado['posicao']}**.\n"
                f"🎁 {texto_recompensa_poketop(resultado)}"
            )
        else:
            texto = (
                f"🎉 **Recompensa resgatada!**\n\n"
                f"🏆 Posição: **#{posicao}**\n"
                f"🎁 {texto_recompensa_poketop(recompensa)}"
            )
        embed = discord.Embed(title="🎁 RECOMPENSA DO POKÉTOP", description=texto, color=COR_VERDE)
        embed.set_footer(text=POKEMON_AVISO)
        await interaction.response.edit_message(embed=embed, view=self)

    async def voltar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(
            embed=self.cog.criar_embed_poketop(interaction.guild, self.ranking, self.pagina),
            view=PoketopView(self.cog, self.usuario_id, self.ranking, self.pagina)
        )

    async def fechar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(content="🏆 PokéTop fechado.", embed=None, view=None)


class PoketopEquipeView(discord.ui.View):
    def __init__(self, cog, usuario_id, ranking, pagina):
        super().__init__(timeout=180)
        self.cog = cog
        self.usuario_id = int(usuario_id)
        self.ranking = ranking
        self.pagina = pagina
        voltar = discord.ui.Button(label="Voltar ao ranking", emoji="🏆", style=discord.ButtonStyle.primary)
        voltar.callback = self.voltar
        self.add_item(voltar)
        fechar = discord.ui.Button(label="Fechar", emoji="✖️", style=discord.ButtonStyle.danger)
        fechar.callback = self.fechar
        self.add_item(fechar)

    async def voltar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(embed=self.cog.criar_embed_poketop(interaction.guild, self.ranking, self.pagina), view=PoketopView(self.cog, self.usuario_id, self.ranking, self.pagina))

    async def fechar(self, interaction):
        if interaction.user.id != self.usuario_id:
            await interaction.response.send_message("❌ Este painel pertence a outro treinador.", ephemeral=True)
            return
        await interaction.response.edit_message(content="🏆 PokéTop fechado.", embed=None, view=None)


class Pokemon(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.banco = BancoPokemon(
            BANCO_POKEMON
        )

        self.api = PokeAPI()

        self.encontros = {}

        # Batalhas manuais de ginásio/Elite 4 por usuário.
        self.gym_battles = {}

        # Snapshot do PokéTop. O ranking é recalculado no máximo a cada 2 horas.
        self.poketop_cache = {}
        self.poketop_atualizacao.start()

        print(
            "[POKEMON] "
            f"🐾 Royalt Pokémon v{VERSAO}"
        )

    async def cog_unload(
        self
    ):

        self.poketop_atualizacao.cancel()
        await self.api.fechar()

    async def cog_before_invoke(self, ctx):
        # Versão e aviso em todas as respostas dos comandos deste Cog,
        # inclusive mensagens sem embed.
        if getattr(ctx, "_pokemon_alpha_wrapped", False):
            return

        original_send = ctx.send

        async def send_with_alpha(*args, **kwargs):
            texto = kwargs.get("content")
            if texto is not None and POKEMON_AVISO not in str(texto):
                kwargs["content"] = f"{texto}\n\n{POKEMON_AVISO}"

            embed = kwargs.get("embed")
            if embed is not None:
                embed.set_footer(text=POKEMON_AVISO)

            embeds = kwargs.get("embeds")
            if embeds:
                for item in embeds:
                    item.set_footer(text=POKEMON_AVISO)

            return await original_send(*args, **kwargs)

        ctx.send = send_with_alpha
        ctx._pokemon_alpha_wrapped = True

    # ========================================================
    # COOLdown
    # ========================================================

    def segundos_cooldown(
        self,
        data,
        segundos
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
                -
                ultima
            ).total_seconds()

            return max(
                0,
                int(
                    segundos
                    -
                    passado
                )
            )

        except (
            ValueError,
            TypeError
        ):

            return 0

    # ========================================================
    # !POKEMON
    # ========================================================

    def criar_embed_insignias(self, membro, regiao, treinador=None):
        treinador = treinador or self.banco.obter_treinador(membro.id)
        dados = GINASIOS[regiao]
        nivel = int(treinador["nivel"])
        requisito = NIVEIS_REGIAO[regiao]
        badges = {
            int(item["numero"]): item
            for item in self.banco.listar_insignias(membro.id, regiao)
        }

        linhas = []
        for gym in dados["ginasios"]:
            numero = gym["numero"]
            if numero in badges:
                linhas.append(
                    f"🏅 **{numero}. {gym['insignia']}** — "
                    f"👑 {gym['lider']} • ✅ Conquistada"
                )
            else:
                linhas.append(
                    f"🔒 **{numero}. {gym['insignia']}** — "
                    f"👑 {gym['lider']} • 🔒 Bloqueada"
                )

        elite = self.banco.obter_progresso_liga(membro.id, regiao)
        etapa = int(elite["elite_etapa"]) if elite else 0

        desbloqueada = nivel >= requisito

        embed = discord.Embed(
            title=f"{dados['emoji']} ROYALT • INSÍGNIAS • {dados['nome']}",
            description=(
                f"**Treinador:** {membro.mention}\n"
                f"⭐ Nível: **{nivel}**\n"
                f"🔓 Região disponível a partir do nível **{requisito}**\n\n"
                + (
                    "🟢 **Região desbloqueada!**\n\n"
                    if desbloqueada
                    else f"🔒 **Região bloqueada.** Faltam "
                         f"**{max(0, requisito - nivel)} níveis**.\n\n"
                )
                + "\n".join(linhas)
                + "\n\n"
                f"🏛️ **Elite 4:** {etapa}/4 membros derrotados"
                + (
                    " • 👑 Liga concluída!"
                    if elite and elite["elite_concluida"]
                    else ""
                )
            ),
            color=COR_AMARELO if desbloqueada else COR_CINZA
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.set_footer(
            text=(
                "Selecione uma região no menu para visualizar suas insígnias. "
                + POKEMON_AVISO
            )
        )
        return embed

    def obter_paginas_ajuda(self):
        """Monta a central de ajuda diretamente dos comandos deste Cog.

        Isso evita uma lista manual que fica desatualizada quando um novo
        comando Pokémon é criado. Comandos conhecidos recebem uma seção;
        qualquer comando novo que não tenha categoria cai automaticamente
        em "Novos comandos".
        """
        comandos = {}
        for comando in self.get_commands():
            nome = getattr(comando, "name", None)
            if not nome:
                continue
            comandos[nome] = comando

        grupos = {
            "🌟 JORNADA": {"icon": "🌟", "nomes": {
                "starters", "perfil", "personalizar", "pokedex", "insignias", "ginasios",
            }},
            "🌿 EXPLORAÇÃO": {"icon": "🌿", "nomes": {
                "explorar", "capturar", "c", "pokecaixa", "pokecoins", "pokemart", "comprar",
            }},
            "⚔️ BATALHAS": {"icon": "⚔️", "nomes": {
                "batalhar", "evoluir", "equipe", "equipeadd", "equiperemover", "trocar",
            }},
            "🎨 PERFIL & CONQUISTAS": {"icon": "🎨", "nomes": {
                "perfilbio", "pokeconquistas", "poketop", "poketopregistrar",
            }},
            "📖 POKÉDEX": {"icon": "📖", "nomes": {
                "pokemonhelp", "phelp", "pokemonajuda",
            }},
        }

        paginas = []
        usados = set()

        for titulo, dados in grupos.items():
            linhas = []
            for nome in sorted(dados["nomes"]):
                comando = comandos.get(nome)
                if not comando or nome in usados:
                    continue
                usados.add(nome)
                descricao = getattr(comando, "description", None) or "Comando da área Pokémon."
                linhas.append(f"`/{nome}` • {descricao}")

            if linhas:
                paginas.append({
                    "titulo": titulo,
                    "texto": "\n".join(linhas),
                })

        novos = []
        for nome, comando in sorted(comandos.items()):
            if nome in usados:
                continue
            descricao = getattr(comando, "description", None) or "Comando da área Pokémon."
            novos.append(f"`/{nome}` • {descricao}")

        if novos:
            paginas.append({
                "titulo": "🆕 NOVOS COMANDOS",
                "texto": (
                    "Estes comandos foram detectados automaticamente e ainda não possuem "
                    "uma categoria específica na central.\n\n" + "\n".join(novos)
                ),
            })

        if not paginas:
            paginas = AJUDA_POKEMON_PAGINAS
        return paginas

    def criar_embed_ajuda(self, pagina, membro):
        paginas = self.obter_paginas_ajuda()
        pagina = max(0, min(len(paginas) - 1, int(pagina)))
        dados = paginas[pagina]
        embed = discord.Embed(
            title=f"📘 ROYALT • POKÉMON • CENTRAL • {pagina + 1}/{len(paginas)}",
            description=dados["texto"], color=COR_AZUL
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(
            name=dados["titulo"],
            value="Navegue pelo menu para trocar de seção. Esta central é atualizada automaticamente com os comandos do Cog Pokémon.",
            inline=False
        )
        embed.add_field(
            name="✨ Interface",
            value="📚 **Páginas** pelo menu • 🛠️ **PokeLog** no botão • ✖️ **Fechar**",
            inline=False
        )
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    def criar_embed_pokelog(self, membro):
        embed = discord.Embed(
            title="🛠️ ROYALT • POKÉMON • POKELOG",
            description="Histórico visual das atualizações da área Pokémon.", color=COR_CIANO
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        for versao, titulo, texto in POKELOG_ENTRADAS:
            embed.add_field(name=f"`{versao}` • {titulo}", value=texto, inline=False)
        embed.add_field(name="📌 Próximas versões", value="Novos recursos serão adicionados aqui conforme a área Pokémon evoluir.", inline=False)
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    @commands.hybrid_command(
        name="pokemonhelp",
        aliases=["phelp", "pokemonajuda"],
        description="Abre a central de ajuda da área Pokémon."
    )
    @commands.guild_only()
    async def pokemonhelp(self, ctx):
        await ctx.send(
            embed=self.criar_embed_ajuda(0, ctx.author),
            view=AjudaPokemonView(self, ctx.author.id, 0)
        )

    @commands.hybrid_command(
        name="insignias",
        aliases=["poke"],
        description="Mostra suas insígnias e o progresso por região."
    )
    @commands.guild_only()
    async def pokemon(self, ctx):
        treinador = self.banco.obter_treinador(ctx.author.id)

        embed = self.criar_embed_insignias(
            ctx.author,
            "kanto",
            treinador
        )

        await ctx.send(
            embed=embed,
            view=InsigniasRegiaoView(
                self,
                ctx.author.id,
                "kanto"
            )
        )

    # ========================================================
    # !STARTER
    # ========================================================

    def criar_embed_starters(self, membro, regiao):
        dados_regiao = REGIOES[regiao]
        starters = STARTERS_POR_REGIAO.get(regiao, [])
        linhas = []
        for starter in starters:
            linhas.append(f"{starter['emoji']} **{starter['nome']}** • Pokédex #{starter['id']}")

        embed = discord.Embed(
            title=f"🌟 STARTERS • {dados_regiao['nome']}",
            description=(
                f"{membro.mention}\n\n"
                f"Escolha um dos três iniciais da região **{dados_regiao['nome']}**.\n\n"
                + "\n".join(linhas)
                + "\n\n"
                "🌎 Use o menu abaixo para trocar de região.\n"
                "⚠️ O starter só pode ser escolhido **uma vez**."
            ),
            color=COR_VERDE
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        if starters:
            embed.set_image(url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{starters[0]['id']}.png")
        embed.set_footer(text=f"Nível de acesso da região: {NIVEIS_REGIAO[regiao]} • {POKEMON_AVISO}")
        return embed

    @commands.hybrid_command(
        name="starters",
        aliases=["starter", "inicial"],
        description="Escolhe seu Pokémon inicial entre as 9 regiões."
    )
    @commands.guild_only()
    async def starters(self, ctx):
        treinador = self.banco.obter_treinador(ctx.author.id)
        if treinador["starter"]:
            embed = discord.Embed(
                title="🌟 SEU STARTER",
                description=f"Seu Pokémon inicial é **{treinador['starter']}**.",
                color=COR_VERDE
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text=POKEMON_AVISO)
            await ctx.send(embed=embed)
            return

        await ctx.send(
            embed=self.criar_embed_starters(ctx.author, "kanto"),
            view=StarterView(self, ctx.author.id, "kanto")
        )

    # ========================================================
    # !POKECAIXA
    # ========================================================

    @commands.command(
        name="pokecaixa",
        aliases=["caixa", "bonus"],
        description="Resgata sua recompensa diária e mantém seu streak."
    )
    @commands.guild_only()
    async def pokecaixa(self, ctx):

        resultado = await self.banco.resgatar_pokecaixa(ctx.author.id)

        if resultado is None:
            await ctx.send(
                "❌ Não foi possível abrir sua PokéCaixa agora."
            )
            return

        if not resultado["ok"]:
            embed = discord.Embed(
                title="📦 POKÉCAIXA FECHADA",
                description=(
                    "Você já abriu sua PokéCaixa hoje!\n\n"
                    f"🔥 **Streak atual:** {resultado['streak']} dias\n"
                    f"⏳ Volte em **{formatar_tempo(resultado['restante'])}**.\n\n"
                    f"🪙 Saldo: **{resultado['saldo']} Pokécoins**"
                ),
                color=COR_CINZA
            )
            embed.set_footer(text="Mantenha seu streak para aumentar as recompensas!")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="📦✨ POKÉCAIXA ABERTA!",
            description=(
                f"**{ctx.author.display_name}**, sua recompensa chegou!\n\n"
                f"🪙 Recompensa base: **+{resultado['recompensa']}**\n"
                f"🔥 Bônus de streak: **+{resultado['bonus_streak']}**\n"
                f"🎁 Bônus semanal: **+{resultado['bonus_semana']}**\n\n"
                f"💰 **Total recebido: +{resultado['total']} Pokécoins**\n"
                f"💳 Saldo: **{resultado['saldo']} Pokécoins**\n\n"
                f"🔥 **Streak: {resultado['streak']} dias**"
            ),
            color=COR_AMARELO
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text="Volte amanhã para continuar sua sequência!")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="ginasios",
        aliases=["ginasio", "liga"],
        description="Abre os ginásios e a Elite 4 Pokémon."
    )
    @commands.guild_only()
    async def ginasios(self, ctx):
        treinador = self.banco.obter_treinador(ctx.author.id)
        nivel = int(treinador["nivel"])

        regiao = "kanto"
        for candidata in REGIOES:
            if nivel >= NIVEIS_REGIAO[candidata]:
                regiao = candidata
            else:
                break

        await ctx.send(
            embed=self.criar_embed_ginasios(
                ctx.author,
                regiao
            ),
            view=GinasiosView(
                self,
                ctx.author.id,
                regiao
            )
        )

    # !SALDO
    # ========================================================

    @commands.command(name="pokecoins", description="Mostra seu saldo de Pokécoins.")
    @commands.guild_only()
    async def pokecoins(self, ctx):
        treinador = self.banco.obter_treinador(ctx.author.id)
        embed = discord.Embed(
            title="🪙 CARTEIRA DO TREINADOR",
            description=(
                f"## {ctx.author.display_name}\n\n"
                f"💰 **{treinador['pokecoins']} Pokécoins**\n\n"
                "🎁 Use `!pokecaixa` para receber sua recompensa diária.\n"
                "🌿 Explore, capture Pokémon e batalhe para ganhar mais."
            ), color=COR_AMARELO
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    # ========================================================
    # CAPTURA POR COMANDO
    # ========================================================

    @commands.command(
        name="c",
        aliases=[
            "capturar",
            "capture"
        ],
        description="Tenta capturar o Pokémon selvagem atual."
    )
    @commands.guild_only()
    async def capturar_comando(
        self,
        ctx,
        *,
        nome=""
    ):
        # O !explorar mantém o listener wait_for para aceitar o nome
        # direto. Este comando é registrado para que !c/!capturar
        # não sejam tratados como CommandNotFound.
        if not nome.strip():
            await ctx.send(
                "🎯 Use `!c <nome do Pokémon>` "
                "ou `!capturar <nome do Pokémon>`."
            )

    # ========================================================
    # !EXPLORAR
    # ========================================================

    # ========================================================

    @commands.command(
        name="explorar",
        aliases=[
            "explore"
        ],
        description="Explora uma região em busca de Pokémon."
    )
    @commands.guild_only()
    async def explorar(
        self,
        ctx
    ):

        treinador = (
            self.banco.obter_treinador(
                ctx.author.id
            )
        )

        if not treinador["starter"]:

            await ctx.send(
                "❌ Escolha seu starter com `!starter` primeiro."
            )

            return

        restante = self.segundos_cooldown(
            treinador["ultimo_explorar"],
            COOLDOWN_EXPLORAR
        )

        if restante > 0:

            await ctx.send(
                (
                    f"⏳ Você pode explorar novamente "
                    f"em **{formatar_tempo(restante)}**."
                )
            )

            return

        if ctx.channel.id in self.encontros:

            await ctx.send(
                "👀 Já existe um Pokémon selvagem neste canal!"
            )

            return

        regiao = escolher_regiao()

        config_regiao = REGIOES[
            regiao
        ]

        raridade = escolher_raridade()

        pokemon_id = random.randint(
            config_regiao["min_id"],
            config_regiao["max_id"]
        )

        dados = (
            await self.api.pokemon(
                pokemon_id
            )
        )

        if dados is None:

            await ctx.send(
                "❌ A PokéAPI não respondeu agora."
            )

            return

        nome = nome_formatado(
            dados["name"]
        )

        nivel = random.randint(
            3,
            15
        )

        shiny = (
            random.randint(
                1,
                4096
            )
            == 1
        )

        progresso_pve = await self.banco.registrar_exploracao(
            ctx.author.id
        )

        self.encontros[
            ctx.channel.id
        ] = {

            "pokemon_id":
                pokemon_id,

            "nome":
                nome,

            "nivel":
                nivel,

            "raridade":
                raridade,

            "regiao":
                regiao,

            "shiny":
                shiny
        }

        recompensa_explorar = random.randint(RECOMPENSA_EXPLORAR_MIN, RECOMPENSA_EXPLORAR_MAX)

        raridade_config = RARIDADES[
            raridade
        ]

        if shiny:

            raridade_emoji = "✨"

            raridade_nome = "SHINY"

        else:

            raridade_emoji = (
                raridade_config["emoji"]
            )

            raridade_nome = (
                raridade_config["nome"]
            )

        sprite = (
            dados["sprites"].get(
                "front_default"
            )
        )

        embed = discord.Embed(

            title="🌿 POKÉMON SELVAGEM APARECEU!",

            description=(

                f"## {raridade_emoji} "
                f"{nome} surgiu!\n\n"

                f"{config_regiao['emoji']} "
                f"**Região:** "
                f"{config_regiao['nome']}\n\n"

                f"⭐ **Nível:** "
                f"{nivel}\n"

                f"💎 **Raridade:** "
                f"{raridade_nome}\n\n"

                "🎯 **Digite o nome do Pokémon "
                "para tentar capturá-lo!**\n\n"

                f"🪙 Recompensa: **+{recompensa_explorar} Pokécoins**\n\n"
                f"⏰ Você tem **{TEMPO_ENCONTRO}s**."
            ),

            color=(
                COR_ROSA
                if shiny
                else COR_ROXO
            )
        )

        if sprite:

            embed.set_thumbnail(
                url=sprite
            )

        await ctx.send(
            embed=embed
        )

        await self.banco.salvar_cooldown(ctx.author.id, "ultimo_explorar")
        await self.banco.alterar_pokecoins(ctx.author.id, recompensa_explorar)

        def verificar(
            mensagem
        ):

            return (
                mensagem.guild
                and
                mensagem.guild.id == ctx.guild.id
                and
                mensagem.channel.id == ctx.channel.id
                and
                not mensagem.author.bot
            )

        try:

            while True:

                resposta = (
                    await self.bot.wait_for(
                        "message",
                        timeout=TEMPO_ENCONTRO,
                        check=verificar
                    )
                )

                encontro = (
                    self.encontros.get(
                        ctx.channel.id
                    )
                )

                if encontro is None:
                    return

                # Aceita tanto o nome direto quanto comandos:
                # !capturar deoxys / !c deoxys / !capture deoxys
                conteudo = resposta.content.strip()

                partes = conteudo.split(maxsplit=1)

                if (
                    partes
                    and partes[0].lower() in (
                        "!capturar",
                        "!capture",
                        "!c"
                    )
                ):
                    if len(partes) < 2:
                        await ctx.send(
                            f"🎯 {resposta.author.mention}, "
                            "digite o nome do Pokémon após o comando!",
                            delete_after=3
                        )
                        continue

                    conteudo = partes[1].strip()

                def normalizar_nome(valor):
                    import unicodedata

                    valor = (
                        unicodedata.normalize("NFKD", valor)
                        .encode("ascii", "ignore")
                        .decode("ascii")
                        .lower()
                        .strip()
                    )

                    for caractere in (
                        " ",
                        "-",
                        "_",
                        ".",
                        "'",
                        '"',
                        "♀",
                        "♂",
                    ):
                        valor = valor.replace(caractere, "")

                    return valor

                digitado = normalizar_nome(conteudo)
                esperado = normalizar_nome(encontro["nome"])

                if digitado != esperado:

                    await ctx.send(
                        (
                            f"❌ {resposta.author.mention}, "
                            "esse não é o Pokémon!"
                        ),
                        delete_after=3
                    )

                    continue

                treinador = (
                    self.banco.obter_treinador(
                        resposta.author.id
                    )
                )

                if (
                    treinador["pokeballs"] <= 0
                    and
                    treinador["greatballs"] <= 0
                    and
                    treinador["ultraballs"] <= 0
                ):

                    await ctx.send(
                        (
                            f"🔴 {resposta.author.mention}, "
                            "você não possui nenhuma Poké Ball."
                        )
                    )

                    return

                if treinador["ultraballs"] > 0:

                    ball = "ultraball"

                    chance = 88

                elif treinador["greatballs"] > 0:

                    ball = "greatball"

                    chance = 72

                else:

                    ball = "pokeball"

                    chance = 55

                multiplicadores = {

                    "comum": 1.00,

                    "incomum": 0.90,

                    "raro": 0.75,

                    "epico": 0.55,

                    "lendario": 0.30
                }

                chance = int(
                    chance
                    *
                    multiplicadores[
                        encontro["raridade"]
                    ]
                )

                if encontro["shiny"]:

                    chance = max(
                        1,
                        chance // 2
                    )

                capturou = (
                    random.randint(
                        1,
                        100
                    )
                    <=
                    chance
                )

                await self.banco.salvar_cooldown(
                    resposta.author.id,
                    "ultimo_captura"
                )

                if not capturou:

                    await self.banco.alterar_ball(
                        resposta.author.id,
                        ball,
                        -1
                    )

                    await ctx.send(
                        embed=discord.Embed(
                            title="💨 O POKÉMON ESCAPOU!",
                            description=(
                                f"{resposta.author.mention} "
                                f"acertou o nome!\n\n"
                                f"🔴 {ball.title()} lançada...\n\n"
                                f"💨 **{encontro['nome']} "
                                "escapou!**"
                            ),
                            color=COR_CINZA
                        )
                    )

                    return

                base_stats = extrair_base_stats_pokeapi(dados)

                captura_resultado = (
                    await self.banco.capturar(
                        resposta.author.id,
                        encontro["pokemon_id"],
                        encontro["nome"],
                        encontro["nivel"],
                        encontro["raridade"],
                        encontro["regiao"],
                        encontro["shiny"],
                        ball,
                        base_stats=base_stats
                    )
                )

                pokemon_db_id = (
                    captura_resultado["id"]
                    if isinstance(captura_resultado, dict)
                    else captura_resultado
                )

                if pokemon_db_id is None:

                    await ctx.send(
                        "❌ Não consegui registrar a captura."
                    )

                    return

                faixa = RECOMPENSA_CAPTURA.get(
                    encontro["raridade"], RECOMPENSA_CAPTURA["comum"]
                )
                recompensa_captura = random.randint(faixa[0], faixa[1])
                if encontro["shiny"]:
                    recompensa_captura += BONUS_SHINY
                await self.banco.alterar_pokecoins(
                    resposta.author.id, recompensa_captura
                )

                xp = random.randint(
                    20,
                    60
                )

                resultado_xp = (
                    await self.banco.adicionar_xp(
                        resposta.author.id,
                        xp
                    )
                )

                await self.banco.desbloquear_conquista(
                    resposta.author.id,
                    "primeira_captura"
                )

                lista = (
                    self.banco.listar_pokemon(
                        resposta.author.id
                    )
                )

                if len(lista) >= 5:

                    await self.banco.desbloquear_conquista(
                        resposta.author.id,
                        "cinco_pokemon"
                    )

                if len(lista) >= 10:

                    await self.banco.desbloquear_conquista(
                        resposta.author.id,
                        "dez_pokemon"
                    )

                if encontro["shiny"]:

                    await self.banco.desbloquear_conquista(
                        resposta.author.id,
                        "shiny"
                    )

                if encontro["raridade"] == "lendario":

                    await self.banco.desbloquear_conquista(
                        resposta.author.id,
                        "lendario"
                    )

                nivel_texto = ""

                if (
                    resultado_xp
                    and
                    resultado_xp[
                        "nivel_depois"
                    ]
                    >
                    resultado_xp[
                        "nivel_antes"
                    ]
                ):

                    nivel_texto = (
                        f"\n🎉 Treinador nível "
                        f"{resultado_xp['nivel_depois']}!"
                    )

                await ctx.send(
                    embed=discord.Embed(

                        title="🎯 CAPTURA REALIZADA!",

                        description=(

                            f"{resposta.author.mention}\n\n"

                            f"🎉 Você capturou "
                            f"**{encontro['nome']}**!\n\n"

                            f"⭐ Nível: "
                            f"**{encontro['nivel']}**\n"

                            f"💎 Raridade: "
                            f"**{raridade_nome}**\n"

                            f"🌎 Região: "
                            f"**{config_regiao['nome']}**\n\n"

                            f"🔴 Bola usada: "
                            f"**{ball.title()}**\n"

                            f"✨ XP: **+{xp}**\n\n"
                            f"🪙 Pokécoins: **+{recompensa_captura}**"
                            f"{nivel_texto}"
                        ),

                        color=(
                            COR_ROSA
                            if encontro["shiny"]
                            else COR_VERDE
                        )
                    )
                )

                return

        except asyncio.TimeoutError:

            await ctx.send(
                embed=discord.Embed(
                    title="🌫️ O POKÉMON FUGIU",
                    description=(
                        f"**{nome}** desapareceu "
                        "antes de ser capturado."
                    ),
                    color=COR_CINZA
                )
            )

        finally:

            self.encontros.pop(
                ctx.channel.id,
                None
            )

            # O combate PvE acontece depois que o encontro selvagem termina.
            try:
                if self.banco.possui_batalha_pve_pendente(ctx.author.id):
                    await self.batalha_pve(ctx)
            except Exception as erro:
                print(f"[POKEMON] ❌ Erro no evento PvE: {erro}")

    # ========================================================
    # !PERFIL
    # ========================================================

    def criar_embed_perfil(self, membro, treinador):
        fonte = treinador.get("perfil_fonte", "normal")
        nome = aplicar_fonte(membro.display_name, fonte)
        emblema = treinador.get("perfil_emblema") or "🎒"
        bio = treinador.get(
            "perfil_bio"
        ) or "Treinador em busca de novos Pokémon!"

        embed = discord.Embed(
            title=f"{emblema} PERFIL • {nome}",
            description=f"> {aplicar_fonte(bio, fonte)}",
            color=COR_AZUL
        )

        embed.set_thumbnail(url=membro.display_avatar.url)

        banner = treinador.get("perfil_banner")
        if banner:
            embed.set_image(url=banner)

        pokemons = self.banco.listar_pokemon(membro.id)
        equipe = [p for p in pokemons if p["equipe"]][:6]
        poder = sum(self.poder_pokemon(p) for p in equipe)

        xp = int(treinador.get("xp", 0))
        nivel = nivel_treinador(xp)

        embed.add_field(
            name="🧢 Treinador",
            value=(
                f"⭐ Nível **{nivel}**\n"
                f"🪙 **{treinador['pokecoins']}** Pokécoins\n"
                f"🎯 **{treinador['capturas']}** capturas"
            ),
            inline=True
        )

        embed.add_field(
            name="⚔️ Jornada",
            value=(
                f"⚔️ **{treinador['batalhas']}** batalhas\n"
                f"🏆 **{treinador['vitorias']}** vitórias\n"
                f"🔥 Streak **{treinador.get('streak_pokecaixa', 0)}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🎒 Equipe",
            value=(
                f"**{len(equipe)}/6** Pokémon\n"
                f"⚡ Poder **{poder}**\n"
                f"📚 Coleção **{len(pokemons)}**"
            ),
            inline=True
        )

        itens = self.banco.listar_itens_perfil(membro.id)

        embed.add_field(
            name="✨ Personalização",
            value=(
                f"🎨 **{len(itens)}** cosméticos\n"
                f"🖼️ Banner: **{'equipado' if banner else 'nenhum'}**\n"
                f"{emblema} Emblema equipado"
            ),
            inline=False
        )

        embed.set_footer(text=POKEMON_AVISO)
        return embed

    @commands.hybrid_command(
        name="perfil",
        aliases=["profile", "card"],
        description="Mostra seu perfil e abre a personalização."
    )
    @commands.guild_only()
    async def perfil(self, ctx, membro: discord.Member = None):
        membro = membro or ctx.author
        treinador = self.banco.obter_perfil(membro.id)

        if not treinador:
            await ctx.send("❌ Não foi possível carregar o perfil.")
            return

        embed = self.criar_embed_perfil(membro, treinador)

        # Somente o dono do perfil pode personalizar.
        pode_personalizar = membro.id == ctx.author.id

        await ctx.send(
            embed=embed,
            view=PerfilView(
                self,
                membro.id,
                pode_personalizar=pode_personalizar
            )
        )

    # ========================================================
    # !PERFILBIO
    # ========================================================

    @commands.command(
        name="perfilbio",
        aliases=["bioperfil"],
        description="Define a bio do seu perfil Pokémon."
    )
    @commands.guild_only()
    async def perfilbio(self, ctx, *, bio: str = ""):
        if not bio.strip():
            await ctx.send("✏️ Use `!perfilbio sua bio aqui`.")
            return
        await self.banco.salvar_bio(ctx.author.id, bio)
        embed = discord.Embed(
            title="📝 BIO ATUALIZADA!",
            description=f"> {bio[:250]}",
            color=COR_VERDE
        )
        embed.set_footer(text=POKEMON_AVISO)
        await ctx.send(embed=embed)

    # ========================================================
    # !PERSONALIZAR
    # ========================================================

    @commands.command(
        name="personalizar",
        aliases=["customizar", "custom"]
    )
    @commands.guild_only()
    async def personalizar(self, ctx):
        # Compatibilidade: o sistema agora fica todo dentro de !perfil / /perfil.
        treinador = self.banco.obter_perfil(ctx.author.id)
        embed = self.criar_embed_perfil(ctx.author, treinador)

        await ctx.send(
            embed=embed,
            view=PerfilView(
                self,
                ctx.author.id,
                pode_personalizar=True
            )
        )

    # ========================================================
    # !POKELISTA

    # ========================================================

    @commands.command(
        name="pokelista",
        aliases=[
            "pokemons",
            "lista"
        ],
        description="Lista seus Pokémon."
    )
    @commands.guild_only()
    async def pokelista(
        self,
        ctx
    ):

        pokemons = (
            self.banco.listar_pokemon(
                ctx.author.id
            )
        )

        if not pokemons:

            await ctx.send(
                "🎒 Você ainda não possui Pokémon."
            )

            return

        embed = discord.Embed(
            title="🎒 ROYALT • SEUS POKÉMON",
            description=(
                f"Você possui "
                f"**{len(pokemons)} Pokémon**."
            ),
            color=COR_VERDE
        )

        for pokemon in pokemons[:20]:

            shiny = (
                "✨ "
                if pokemon["shiny"]
                else ""
            )

            raridade = RARIDADES.get(
                pokemon["raridade"],
                RARIDADES["comum"]
            )

            local = (
                "🟢 EQUIPE"
                if pokemon["equipe"]
                else "⚪ BOX"
            )

            embed.add_field(

                name=(
                    f"{shiny}"
                    f"{raridade['emoji']} "
                    f"{pokemon['nome']}"
                ),

                value=(

                    f"⭐ Nível "
                    f"**{pokemon['nivel']}**\n"

                    f"{local}\n"

                    f"🆔 ID "
                    f"`{pokemon['id']}`"
                ),

                inline=True
            )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # !EQUIPE
    # ========================================================

    async def sincronizar_pokemon_com_api(self, pokemon):
        """Atualiza stats, tipagens e golpes de um Pokémon pela PokéAPI."""
        dados = await self.api.pokemon(pokemon["pokemon_id"])
        if not dados:
            return pokemon

        atualizado = await self.banco.atualizar_stats_pokemon(
            pokemon["id"],
            extrair_base_stats_pokeapi(dados)
        )
        atualizado = atualizado or pokemon

        tipos = [
            item.get("type", {}).get("name", "normal")
            for item in dados.get("types", [])
        ]
        movimentos = await extrair_movimentos_combate(
            self.api, dados, nivel=int(atualizado.get("nivel", pokemon.get("nivel", 5)))
        )

        atualizado = await self.banco.atualizar_dados_combate_pokemon(
            pokemon["id"],
            tipos,
            movimentos
        )
        if len(movimentos) >= 4:
            await self.banco.desbloquear_conquista(
                pokemon["treinador_id"], "mestre_golpes"
            )
        return atualizado or pokemon

    def sprite_pokemon(self, pokemon):
        return (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            "sprites/pokemon/other/official-artwork/"
            f"{pokemon['pokemon_id']}.png"
        )

    def criar_embed_equipe(self, membro, pokemons):
        treinador = self.banco.obter_treinador(membro.id)

        embed = discord.Embed(
            title="🧢 ROYALT • EQUIPE POKÉMON",
            description=(
                f"**Treinador:** {membro.mention}\n"
                f"📊 **{len(pokemons)}/6 Pokémon**\n"
                f"⚔️ **{treinador['vitorias']} vitórias** • "
                f"🔥 **Streak {treinador.get('streak_pokecaixa', 0)}**\n\n"
                "Selecione um Pokémon abaixo para abrir a ficha completa."
            ),
            color=COR_AZUL
        )
        embed.set_thumbnail(url=membro.display_avatar.url)

        if not pokemons:
            embed.add_field(
                name="📭 Sua equipe está vazia",
                value="Use `!equipeadd <id>` para colocar um Pokémon na equipe.",
                inline=False
            )
            embed.set_footer(text=POKEMON_AVISO)
            return embed

        total_poder = 0
        for posicao, pokemon in enumerate(pokemons, start=1):
            raridade = RARIDADES.get(
                pokemon["raridade"],
                {"nome": pokemon["raridade"], "emoji": "💎"}
            )
            shiny = "✨ " if pokemon["shiny"] else ""
            poder = self.poder_pokemon(pokemon)
            total_poder += poder

            embed.add_field(
                name=f"{posicao}️⃣ {shiny}{raridade['emoji']} {pokemon['nome']} • Nv. {pokemon['nivel']}",
                value=(
                    f"⚔️ Poder: **{poder}**\n"
                    f"❤️ HP: **{pokemon['hp']}**\n"
                    f"💥 ATK: **{pokemon['ataque']}**\n"
                    f"🛡️ DEF: **{pokemon['defesa']}**\n"
                    f"💨 SPD: **{pokemon['velocidade']}**\n"
                    f"✨ XP: **{xp_atual_pokemon(pokemon['xp'])}/100**\n"
                    f"🆔 ID `{pokemon['id']}`"
                ),
                inline=True
            )

        embed.add_field(
            name="📈 Poder total da equipe",
            value=f"⚡ **{total_poder}**",
            inline=False
        )
        embed.set_image(url=self.sprite_pokemon(pokemons[0]))
        embed.set_footer(
            text=f"Selecione um Pokémon para ver IVs, stats, XP e histórico. {POKEMON_AVISO}"
        )
        return embed

    def criar_embed_pokemon_detalhado(self, pokemon):
        raridade = RARIDADES.get(
            pokemon["raridade"],
            {"nome": pokemon["raridade"], "emoji": "💎"}
        )
        shiny = "✨ " if pokemon["shiny"] else ""

        iv_total = sum(
            int(pokemon[chave])
            for chave in ("iv_hp", "iv_ataque", "iv_defesa", "iv_velocidade")
        )
        iv_percentual = (iv_total / (IV_MAX * 4)) * 100

        if iv_percentual >= 90:
            qualidade_iv = "🌟 PERFEITO"
        elif iv_percentual >= 75:
            qualidade_iv = "💎 EXCELENTE"
        elif iv_percentual >= 50:
            qualidade_iv = "🔷 BOM"
        elif iv_percentual >= 25:
            qualidade_iv = "🔹 NORMAL"
        else:
            qualidade_iv = "⚪ FRACO"

        embed = discord.Embed(
            title=f"{shiny}{raridade['emoji']} {pokemon['nome']} • Nv. {pokemon['nivel']}",
            description=(
                f"**ID da coleção:** `{pokemon['id']}`\n"
                f"**Pokédex:** `#{pokemon['pokemon_id']}`\n"
                f"🌍 Região: **{pokemon['regiao'].title()}**\n"
                f"💎 Raridade: **{raridade['nome']}**"
            ),
            color=COR_AMARELO
        )
        embed.set_image(url=self.sprite_pokemon(pokemon))

        embed.add_field(
            name="📊 STATUS",
            value=(
                f"❤️ HP: **{pokemon['hp']}**\n"
                f"⚔️ ATK: **{pokemon['ataque']}**\n"
                f"🛡️ DEF: **{pokemon['defesa']}**\n"
                f"💨 SPD: **{pokemon['velocidade']}**\n"
                f"⚡ Poder: **{self.poder_pokemon(pokemon)}**"
            ),
            inline=True
        )
        try:
            tipos = json.loads(pokemon.get("tipos") or "[]")
        except (TypeError, json.JSONDecodeError):
            tipos = []

        try:
            movimentos = json.loads(pokemon.get("movimentos") or "[]")
        except (TypeError, json.JSONDecodeError):
            movimentos = []

        if tipos:
            texto_tipos = " • ".join(
                f"{obter_emoji_tipo(t)} {t.title()}" for t in tipos
            )
        else:
            texto_tipos = "❔ Não sincronizado"

        texto_golpes = "\n".join(
            f"{obter_emoji_tipo(m.get('tipo', 'normal'))} "
            f"**{m.get('nome', 'Tackle')}** • "
            f"{m.get('poder', 40)} POW"
            for m in movimentos[:4]
        ) or "⚪ Tackle • 40 POW"

        embed.add_field(
            name="🧪 TIPO",
            value=texto_tipos,
            inline=False
        )
        embed.add_field(
            name="⚔️ ATAQUES",
            value=texto_golpes,
            inline=False
        )

        embed.add_field(
            name="🧬 IVs",
            value=(
                f"❤️ HP: **{pokemon['iv_hp']}/{IV_MAX}**\n"
                f"⚔️ ATK: **{pokemon['iv_ataque']}/{IV_MAX}**\n"
                f"🛡️ DEF: **{pokemon['iv_defesa']}/{IV_MAX}**\n"
                f"💨 SPD: **{pokemon['iv_velocidade']}/{IV_MAX}**\n"
                f"🌟 Total: **{iv_total}/124** ({iv_percentual:.1f}%)\n"
                f"🏅 Qualidade: **{qualidade_iv}**"
            ),
            inline=True
        )
        embed.add_field(
            name="📈 TREINAMENTO",
            value=(
                f"✨ XP: **{xp_atual_pokemon(pokemon['xp'])}/100**\n"
                f"{barra_xp_pokemon(pokemon['xp'])}\n"
                f"⚔️ Batalhas: **{pokemon['batalhas']}**\n"
                f"🏆 Vitórias: **{pokemon['vitorias']}**\n"
                f"🎒 Na equipe: **{'Sim' if pokemon['equipe'] else 'Não'}**\n"
                f"🧬 Evoluções realizadas: **{pokemon.get('evolucoes', 0)}**"
            ),
            inline=False
        )
        embed.add_field(
            name="🧱 BASE",
            value=(
                f"❤️ {pokemon['base_hp']}  • "
                f"⚔️ {pokemon['base_ataque']}  • "
                f"🛡️ {pokemon['base_defesa']}  • "
                f"💨 {pokemon['base_velocidade']}"
            ),
            inline=False
        )
        embed.set_footer(
            text=f"IV máximo = 31 por atributo • {POKEMON_AVISO}"
        )
        return embed

    @commands.hybrid_command(
        name="equipe",
        aliases=["time", "timepokemon"],
        description="Mostra sua equipe e permite ver cada Pokémon em detalhes."
    )
    @commands.guild_only()
    async def equipe(self, ctx):
        pokemons = [
            p for p in self.banco.listar_pokemon(ctx.author.id)
            if p["equipe"]
        ][:6]

        sincronizados = []
        for pokemon in pokemons:
            sincronizados.append(
                await self.sincronizar_pokemon_com_api(pokemon)
            )
        pokemons = sincronizados

        await ctx.send(
            embed=self.criar_embed_equipe(
                ctx.author,
                pokemons
            ),
            view=EquipeView(
                self,
                ctx.author.id,
                pokemons
            )
        )

    # ========================================================
    # !EQUIPEADD
    # ========================================================

    @commands.command(
        name="equipeadd",
        description="Adiciona um Pokémon à equipe."
    )
    @commands.guild_only()
    async def equipeadd(
        self,
        ctx,
        pokemon_id: int
    ):

        sucesso = (
            await self.banco.adicionar_equipe(
                ctx.author.id,
                pokemon_id
            )
        )

        if not sucesso:

            await ctx.send(
                (
                    "❌ Não foi possível adicionar esse Pokémon. "
                    "Talvez sua equipe esteja cheia ou o ID seja inválido."
                )
            )

            return

        await ctx.send(
            f"✅ Pokémon `{pokemon_id}` entrou para sua equipe!"
        )

    # ========================================================
    # !EQUIPEREMOVER
    # ========================================================

    @commands.command(
        name="equiperemover",
        aliases=[
            "equireremover"
        ],
        description="Remove um Pokémon da equipe."
    )
    @commands.guild_only()
    async def equiperemover(
        self,
        ctx,
        pokemon_id: int
    ):

        sucesso = (
            await self.banco.remover_equipe(
                ctx.author.id,
                pokemon_id
            )
        )

        if not sucesso:

            await ctx.send(
                "❌ Pokémon não encontrado."
            )

            return

        await ctx.send(
            f"✅ Pokémon `{pokemon_id}` saiu da equipe."
        )

    def criar_embed_pokemart(
        self,
        treinador,
        categoria="jornada",
        item_id=None
    ):
        if categoria == "perfil":
            catalogo = PERFIL_LOJA
            titulo = "🎨 ROYALT • POKÉMART • PERFIL"
            descricao = (
                "Banners, fontes e emblemas para personalizar seu perfil."
            )
            cor = COR_ROXO
        else:
            catalogo = {
                k: v for k, v in LOJA.items()
                if v.get("categoria") == "jornada"
            }
            titulo = "🎒 ROYALT • POKÉMART • JORNADA"
            descricao = (
                "Poké Balls, itens de cura e recursos especiais para sua jornada."
            )
            cor = COR_AZUL

        embed = discord.Embed(
            title=titulo,
            description=(
                f"🪙 **Saldo:** {treinador['pokecoins']} Pokécoins\n\n"
                f"{descricao}\n\n"
                "Selecione um item abaixo para visualizar sua imagem e detalhes."
            ),
            color=cor
        )

        if item_id and item_id in catalogo:
            item = catalogo[item_id]
            embed.add_field(
                name=item["nome"],
                value=(
                    f"{item['descricao']}\n\n"
                    f"💰 **{item['preco']} Pokécoins**"
                ),
                inline=False
            )
            embed.set_image(url=item["imagem"])
        else:
            for chave, item in catalogo.items():
                embed.add_field(
                    name=item["nome"],
                    value=f"💰 **{item['preco']}**",
                    inline=True
                )

        embed.set_footer(text=POKEMON_AVISO)
        return embed

    @app_commands.command(
        name="pokemart",
        description="Abre a PokéMart Pokémon."
    )
    @app_commands.guild_only()
    async def pokemart_slash(
        self,
        interaction: discord.Interaction
    ):
        treinador = self.banco.obter_treinador(
            interaction.user.id
        )

        await interaction.response.send_message(
            embed=self.criar_embed_pokemart(
                treinador,
                "jornada"
            ),
            view=PokeMartView(
                self,
                "jornada"
            )
        )

    # ========================================================
    # !POKELOJA
    # ========================================================

    @commands.command(
        name="pokeloja",
        aliases=[
            "lojapokemon",
            "pokemart"
        ],
        description="Abre a PokéMart."
    )
    @commands.guild_only()
    async def pokeloja(
        self,
        ctx
    ):
        treinador = self.banco.obter_treinador(ctx.author.id)

        await ctx.send(
            embed=self.criar_embed_pokemart(
                treinador,
                "jornada"
            ),
            view=PokeMartView(
                self,
                "jornada"
            )
        )

    # ========================================================
    # !COMPRAR
    # ========================================================

    @commands.command(
        name="comprar",
        aliases=[
            "buy"
        ],
        description="Compra itens na PokéMart."
    )
    @commands.guild_only()
    async def comprar(
        self,
        ctx,
        item: str,
        quantidade: int = 1
    ):

        item = item.lower().strip()

        if item not in LOJA and item not in PERFIL_LOJA:

            await ctx.send(
                "❌ Item inválido. Use `/pokemart`."
            )

            return

        if quantidade <= 0:

            await ctx.send(
                "❌ A quantidade precisa ser maior que zero."
            )

            return

        if item in PERFIL_LOJA:
            config = PERFIL_LOJA[item]
            if quantidade != 1:
                await ctx.send("❌ Cosméticos de perfil só podem ser comprados de 1 em 1.")
                return
            resultado = await self.banco.comprar_item_perfil(
                ctx.author.id,
                item,
                config["preco"]
            )
            ok, motivo = resultado
            if not ok:
                if motivo == "possui":
                    await ctx.send("✨ Você já possui esse cosmético!")
                else:
                    await ctx.send(
                        embed=discord.Embed(
                            title="❌ POKÉCOINS INSUFICIENTES",
                            description=(
                                f"Você precisa de **{config['preco']} Pokécoins** "
                                "para comprar esse cosmético."
                            ),
                            color=COR_VERMELHO
                        )
                    )
                return
            embed = discord.Embed(
                title="🛍️ COSMÉTICO ADQUIRIDO!",
                description=(
                    f"**{config['nome']}**\n\n"
                    f"💸 Custo: **{config['preco']} Pokécoins**\n\n"
                    f"✨ Use `!personalizar {item}` para equipar."
                ),
                color=COR_ROXO
            )
            if config["tipo"] == "banner":
                embed.set_image(url=config["valor"])
            embed.set_footer(text=POKEMON_AVISO)
            await ctx.send(embed=embed)
            return

        config = LOJA[item]
        custo = int(config["preco"]) * quantidade

        if item in ("pokeball", "greatball", "ultraball"):
            treinador = self.banco.obter_treinador(ctx.author.id)
            if treinador["pokecoins"] < custo:
                await ctx.send(embed=discord.Embed(
                    title="❌ POKÉCOINS INSUFICIENTES",
                    description=(
                        f"Você precisa de **{custo}**.\n"
                        f"Você possui **{treinador['pokecoins']}**."
                    ), color=COR_VERMELHO
                ))
                return
            pago = await self.banco.alterar_pokecoins(ctx.author.id, -custo)
            recebido = await self.banco.alterar_ball(ctx.author.id, item, quantidade) if pago else False
            if not recebido:
                if pago:
                    await self.banco.alterar_pokecoins(ctx.author.id, custo)
                await ctx.send("❌ A compra foi revertida.")
                return
        else:
            # comprar_item_jornada faz a transação de saldo + estoque atomicamente.
            ok, resultado = await self.banco.comprar_item_jornada(
                ctx.author.id, item, config["preco"], quantidade
            )
            if not ok:
                if resultado == "saldo":
                    treinador = self.banco.obter_treinador(ctx.author.id)
                    await ctx.send(embed=discord.Embed(
                        title="❌ POKÉCOINS INSUFICIENTES",
                        description=(
                            f"Você precisa de **{custo}**.\n"
                            f"Você possui **{treinador['pokecoins']}**."
                        ), color=COR_VERMELHO
                    ))
                else:
                    await ctx.send("❌ Não foi possível concluir a compra.")
                return

        emoji = config.get("emoji", "🪨")
        embed = discord.Embed(
            title="🛒 COMPRA REALIZADA!",
            description=(
                f"{emoji} **{quantidade}x {config['nome']}**\n\n"
                f"💸 Custo: **{custo} Pokécoins**"
            ), color=COR_VERDE
        )
        embed.set_image(url=config["imagem"])
        embed.set_footer(text=POKEMON_AVISO)
        await ctx.send(embed=embed)

    # ========================================================
    # !POKEDEX
    # ========================================================

    def regiao_por_pokemon_id(self, pokemon_id):
        pid = int(pokemon_id)
        for regiao, dados in REGIOES.items():
            if dados["min_id"] <= pid <= dados["max_id"]:
                return regiao
        return "paldea"

    def pagina_por_pokemon_id(self, pokemon_id):
        pid = int(pokemon_id)
        regiao = self.regiao_por_pokemon_id(pid)
        return max(0, (pid - REGIOES[regiao]["min_id"]) // 25)

    def raridade_dex(self, especie):
        if not especie:
            return {"nome": "Desconhecida", "emoji": "❔"}
        if especie.get("is_mythical") or especie.get("is_legendary"):
            return {"nome": "Lendário", "emoji": "🟡"}
        try:
            captura = int(especie.get("capture_rate") or 0)
        except (TypeError, ValueError):
            captura = 0
        if captura >= 200:
            return {"nome": "Comum", "emoji": "⚪"}
        if captura >= 100:
            return {"nome": "Incomum", "emoji": "🟢"}
        if captura >= 45:
            return {"nome": "Raro", "emoji": "🔵"}
        return {"nome": "Épico", "emoji": "🟣"}

    @staticmethod
    def nome_pokedex(nome):
        return str(nome or "Pokémon").replace("-", " ").title()

    def extrair_golpes_pokedex(self, dados):
        por_nivel = {}
        for entrada in dados.get("moves", []):
            nome = self.nome_pokedex(entrada.get("move", {}).get("name"))
            niveis = []
            for detalhe in entrada.get("version_group_details", []):
                if detalhe.get("move_learn_method", {}).get("name") != "level-up":
                    continue
                try:
                    niveis.append(int(detalhe.get("level_learned_at") or 0))
                except (TypeError, ValueError):
                    pass
            if niveis:
                por_nivel.setdefault(min(niveis), []).append(nome)
        for nivel in por_nivel:
            por_nivel[nivel] = list(dict.fromkeys(por_nivel[nivel]))
        return por_nivel

    def formatar_requisito_evolucao(self, detalhe):
        partes = []
        if detalhe.get("min_level") is not None:
            partes.append(f"Nível {detalhe['min_level']}")
        item = detalhe.get("item") or {}
        if item.get("name"):
            partes.append(f"Item: {self.nome_pokedex(item['name'])}")
        held = detalhe.get("held_item") or {}
        if held.get("name"):
            partes.append(f"Segurando: {self.nome_pokedex(held['name'])}")
        trigger = (detalhe.get("trigger") or {}).get("name")
        if trigger == "trade":
            partes.append("Troca")
        elif trigger and trigger not in ("level-up", "use-item"):
            partes.append(trigger.replace("-", " ").title())
        if detalhe.get("min_happiness"):
            partes.append(f"Amizade ≥ {detalhe['min_happiness']}")
        if detalhe.get("min_affection"):
            partes.append(f"Afeição ≥ {detalhe['min_affection']}")
        if detalhe.get("min_beauty"):
            partes.append(f"Beleza ≥ {detalhe['min_beauty']}")
        if detalhe.get("known_move", {}).get("name"):
            partes.append(f"Golpe: {self.nome_pokedex(detalhe['known_move']['name'])}")
        if detalhe.get("known_move_type", {}).get("name"):
            partes.append(f"Golpe do tipo {self.nome_pokedex(detalhe['known_move_type']['name'])}")
        if detalhe.get("location"):
            partes.append(f"Local: {self.nome_pokedex(detalhe['location']['name'])}")
        if detalhe.get("time_of_day"):
            partes.append(f"Horário: {detalhe['time_of_day'].title()}")
        if detalhe.get("gender") is not None:
            partes.append("Gênero específico")
        if detalhe.get("turn_upside_down"):
            partes.append("Console invertido")
        if detalhe.get("party_species", {}).get("name"):
            partes.append(f"Na equipe: {self.nome_pokedex(detalhe['party_species']['name'])}")
        if detalhe.get("party_type", {}).get("name"):
            partes.append(f"Na equipe: tipo {self.nome_pokedex(detalhe['party_type']['name'])}")
        if detalhe.get("relative_physical_stats") is not None:
            rel = detalhe["relative_physical_stats"]
            partes.append({1: "Ataque > Defesa", -1: "Defesa > Ataque", 0: "Ataque = Defesa"}.get(rel, "Stats específicos"))
        if detalhe.get("needs_overworld_rain"):
            partes.append("Chuva")
        if detalhe.get("trade_species", {}).get("name"):
            partes.append(f"Troca por {self.nome_pokedex(detalhe['trade_species']['name'])}")
        if detalhe.get("turn_upside_down"):
            partes.append("Virar console")
        return " • ".join(dict.fromkeys(partes)) or "Método especial"

    def extrair_evolucoes_dex(self, cadeia):
        resultado = []
        if not cadeia:
            return resultado

        def andar(no, anterior_nome=None):
            especie = no.get("species", {})
            atual_nome = self.nome_pokedex(especie.get("name"))
            if anterior_nome:
                for detalhe in no.get("evolution_details", []):
                    resultado.append({
                        "de": anterior_nome,
                        "para": atual_nome,
                        "requisito": self.formatar_requisito_evolucao(detalhe),
                    })
            for proximo in no.get("evolves_to", []):
                andar(proximo, atual_nome)

        andar(cadeia)
        return resultado

    def criar_embed_pokedex_indice(self, membro, regiao, pagina, total, treinador=None):
        d = REGIOES[regiao]
        pagina = max(0, int(pagina))
        inicio = min(d["min_id"] + pagina * 25, d["max_id"])
        fim = min(inicio + 24, d["max_id"])
        paginas = ((d["max_id"] - d["min_id"]) // 25) + 1
        treinador = treinador or self.banco.obter_treinador(membro.id)
        embed = discord.Embed(
            title=f"📖 ROYALT • POKÉDEX • {d['nome']}",
            description=(
                f"**Treinador:** {membro.mention}\n"
                f"📚 Registrados: **{total}/1025** • **{(total / 1025) * 100:.2f}%**\n"
                f"🌎 Região: **{d['nome']}** • ⭐ Nível **{int(treinador.get('nivel', 1))}**\n\n"
                f"Mostrando **#{inicio:03d} — #{fim:03d}**\n"
                "Use os três menus para região, faixa e Pokémon."
            ), color=COR_AZUL
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="🧭 Navegação", value=f"Página **{pagina + 1}/{paginas}** • 25 Pokémon por página", inline=False)
        embed.add_field(name="🔎 Ficha", value="ID • ícone • tipagem • golpes • níveis • evolução • raridade de encontro.", inline=False)
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    def criar_embed_pokedex_detalhe(self, membro, dados, especie, total=None):
        pid = int(dados.get("id", 0)); nome = self.nome_pokedex(dados.get("name"))
        tipos = [x.get("type", {}).get("name", "normal") for x in dados.get("types", [])]
        raridade = self.raridade_dex(especie)
        captura = especie.get("capture_rate", "?") if especie else "?"
        embed = discord.Embed(
            title=f"📖 #{pid:03d} • {nome}",
            description=(
                f"**Pokédex ID:** `#{pid:03d}`\n"
                f"🌎 Região: **{self.regiao_por_pokemon_id(pid).title()}**\n"
                f"{raridade['emoji']} Raridade de encontro: **{raridade['nome']}**\n"
                f"🎯 Taxa base de captura: **{captura}**"
                + (f"\n📚 Seu registro: **{total}/1025**" if total is not None else "")
            ), color=COR_AMARELO if raridade["nome"] == "Lendário" else COR_AZUL
        )
        icon = dados.get("sprites", {}).get("front_default")
        artwork = dados.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default")
        embed.set_thumbnail(url=icon or artwork or membro.display_avatar.url)
        if artwork: embed.set_image(url=artwork)
        embed.add_field(name="🧪 TIPAGEM", value=" • ".join(f"{obter_emoji_tipo(t)} **{t.title()}**" for t in tipos) or "❔ Desconhecido", inline=False)

        por_nivel = self.extrair_golpes_pokedex(dados)
        iniciais = list(dict.fromkeys(por_nivel.get(0, []) + por_nivel.get(1, [])))[:6]
        embed.add_field(name="🥚 GOLPES INICIAIS", value="\n".join(f"⚔️ **{x}**" for x in iniciais) or "⚪ Não disponível", inline=True)
        aprendizados = []
        for nivel in sorted(por_nivel):
            if nivel <= 1: continue
            aprendizados.append(f"**Nv. {nivel}** → {', '.join(por_nivel[nivel][:3])}")
            if len(aprendizados) >= 10: break
        embed.add_field(name="📈 APRENDE POR NÍVEL", value="\n".join(aprendizados) or "Nenhum golpe por nível encontrado.", inline=True)
        embed.add_field(name="🧬 EVOLUÇÃO", value="Carregando cadeia evolutiva...", inline=False)
        embed.add_field(name="📌 RESUMO", value=(f"📏 Altura: **{dados.get('height', 0) / 10:.1f} m**\n" f"⚖️ Peso: **{dados.get('weight', 0) / 10:.1f} kg**\n" f"⚔️ Golpes catalogados: **{sum(len(v) for v in por_nivel.values())}**"), inline=False)
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    async def criar_embed_pokedex_detalhe_async(self, membro, dados, especie, total=None):
        embed = self.criar_embed_pokedex_detalhe(membro, dados, especie, total)
        cadeia = None
        if especie:
            url = especie.get("evolution_chain", {}).get("url")
            if url: cadeia = await self.api.get(url.rstrip("/").split("/api/v2/")[-1])
        evolucoes = self.extrair_evolucoes_dex(cadeia)
        texto = "\n".join(f"`{e['de']}`  →  **{e['para']}**\n└ {e['requisito']}" for e in evolucoes) if evolucoes else "Sem evolução registrada."
        # Campos do Discord possuem limite de 1024 caracteres; divide a linha evolutiva sem truncar.
        partes = [texto[i:i + 950] for i in range(0, len(texto), 950)] or [texto]
        for field in list(embed.fields):
            if field.name == "🧬 EVOLUÇÃO":
                embed.remove_field(embed.fields.index(field))
                break
        for indice, parte in enumerate(partes):
            embed.add_field(name="🧬 LINHA EVOLUTIVA" if indice == 0 else "🧬 CONTINUAÇÃO", value=parte, inline=False)
        return embed

    async def criar_embed_pokedex_evolucao_async(self, membro, dados, especie):
        cadeia = None
        if especie:
            url = especie.get("evolution_chain", {}).get("url")
            if url:
                cadeia = await self.api.get(url.rstrip("/").split("/api/v2/")[-1])
        evolucoes = self.extrair_evolucoes_dex(cadeia)
        nome = self.nome_pokedex((dados or {}).get("name"))
        pid = int((dados or {}).get("id", 0) or 0)
        embed = discord.Embed(title=f"🧬 #{pid:03d} • LINHA EVOLUTIVA", description=f"**{nome}** • cadeia evolutiva completa", color=COR_ROXO)
        embed.set_thumbnail(url=membro.display_avatar.url)
        if evolucoes:
            linhas = [f"**{e['de']}**  →  **{e['para']}**\n└─ {e['requisito']}" for e in evolucoes]
            texto = "\n".join(linhas)
        else:
            texto = "Este Pokémon não possui uma evolução registrada."
        for i in range(0, len(texto), 950):
            embed.add_field(name="🧬 EVOLUÇÃO" if i == 0 else "🧬 CONTINUAÇÃO", value=texto[i:i+950], inline=False)
        artwork = (dados or {}).get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default")
        if artwork:
            embed.set_image(url=artwork)
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    def criar_embed_pokedex_especiais(self, membro):
        itens = POKEDEX_ESPECIAIS.get("conquistas", [])
        embed = discord.Embed(
            title="🏆 ROYALT • POKÉDEX • CONQUISTAS",
            description="Pokémon e evoluções especiais vinculados a conquistas do Royalt.",
            color=COR_AMARELO
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        for item in itens[:12]:
            embed.add_field(
                name=f"🏆 #{int(item['pokemon_id']):03d} • {item['nome']}",
                value=item['regra'],
                inline=True
            )
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    def criar_embed_pokedex_ginasios(self, membro):
        itens = POKEDEX_ESPECIAIS.get("ginasios", [])
        embed = discord.Embed(
            title="🏟️ ROYALT • POKÉDEX • GINÁSIOS",
            description=(
                "Pokémon vinculados a ginásios, ligas ou eventos especiais do Royalt.\n"
                "A obtenção depende da regra indicada em cada entrada."
            ),
            color=COR_ROXO
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        for item in itens[:12]:
            embed.add_field(
                name=f"🏟️ #{int(item['pokemon_id']):03d} • {item['nome']}",
                value=item['regra'],
                inline=True
            )
        embed.set_footer(text=POKEMON_AVISO)
        return embed


    @commands.hybrid_command(
        name="pokedex",
        aliases=["dex"],
        description="Abre a Pokédex completa com navegação por região e Pokémon."
    )
    @commands.guild_only()
    async def pokedex(self, ctx, *, pokemon: str = None):
        total = self.banco.contar_dex(ctx.author.id)
        treinador = self.banco.obter_treinador(ctx.author.id)

        if pokemon and pokemon.strip():
            dados = await self.api.pokemon(pokemon.strip().lower())
            if not dados:
                await ctx.send("❌ Não encontrei esse Pokémon. Use o número da Pokédex ou o nome oficial.")
                return
            especie = await self.api.especie(dados.get("id"))
            embed = await self.criar_embed_pokedex_detalhe_async(ctx.author, dados, especie, total)
            pid = int(dados["id"])
            await ctx.send(
                embed=embed,
                view=PokedexView(self, ctx.author.id, self.regiao_por_pokemon_id(pid), self.pagina_por_pokemon_id(pid), pid)
            )
            return

        await ctx.send(
            embed=self.criar_embed_pokedex_indice(ctx.author, "kanto", 0, total, treinador),
            view=PokedexView(self, ctx.author.id, "kanto", 0)
        )

    # ========================================================
    # !POKECONQUISTAS
    # ========================================================

    @commands.hybrid_command(
        name="pokeconquistas",
        aliases=["conquistaspokemon"],
        description="Mostra suas conquistas, objetivos e recompensas Pokémon."
    )
    @commands.guild_only()
    async def pokeconquistas(self, ctx):
        desbloqueadas = self.banco.listar_conquistas(ctx.author.id)
        await ctx.send(
            embed=self.criar_embed_conquistas(ctx.author, 0, desbloqueadas),
            view=ConquistasView(self, ctx.author.id, 0)
        )

    def criar_embed_conquistas(self, membro, pagina, desbloqueadas=None):
        desbloqueadas = set(desbloqueadas if desbloqueadas is not None else self.banco.listar_conquistas(membro.id))
        itens = list(CONQUISTAS.items())
        por_pagina = 5
        paginas = max(1, (len(itens) + por_pagina - 1) // por_pagina)
        pagina = max(0, min(int(pagina), paginas - 1))
        bloco = itens[pagina * por_pagina:(pagina + 1) * por_pagina]
        feitas = len(desbloqueadas.intersection(CONQUISTAS.keys()))

        embed = discord.Embed(
            title=f"🏆 ROYALT • POKE CONQUISTAS • {pagina + 1}/{paginas}",
            description=(
                f"{membro.mention} • **{feitas}/{len(CONQUISTAS)}** concluídas\n"
                "Complete objetivos durante a jornada para desbloquear recompensas.\n"
                "━━━━━━━━━━━━━━━━━━━━"
            ),
            color=COR_AMARELO
        )
        embed.set_thumbnail(url=membro.display_avatar.url)

        for chave, (emoji, nome, como_fazer, recompensa) in bloco:
            concluida = chave in desbloqueadas
            status = "✅ CONCLUÍDA" if concluida else "🔒 EM PROGRESSO"
            embed.add_field(
                name=f"{emoji} {nome}  •  {status}",
                value=(
                    f"**Como conseguir:** {como_fazer}\n"
                    f"**Recompensa:** {recompensa}"
                ),
                inline=False
            )

        embed.set_footer(text=POKEMON_AVISO)
        return embed

    # ========================================================
    # !EVOLUIR
    # ========================================================

    @commands.command(
        name="evoluir",
        aliases=["evolution"],
        description="Evolui um Pokémon por nível, item ou requisito especial."
    )
    @commands.guild_only()
    async def evoluir(self, ctx, pokemon_db_id: int, item: str = ""):
        pokemon = self.banco.obter_pokemon(pokemon_db_id)
        if pokemon is None or int(pokemon["treinador_id"]) != ctx.author.id:
            await ctx.send("❌ Pokémon não encontrado ou não pertence a você.")
            return

        especie = await self.api.especie(pokemon["pokemon_id"])
        if not especie or not especie.get("evolution_chain", {}).get("url"):
            await ctx.send("❌ Não consegui consultar a evolução desse Pokémon.")
            return

        cadeia_url = especie["evolution_chain"]["url"]
        try:
            await self.api.iniciar()
            async with self.api.session.get(cadeia_url) as response:
                if response.status != 200:
                    await ctx.send("❌ Não consegui carregar a cadeia evolutiva.")
                    return
                cadeia = await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            await ctx.send("❌ Erro de conexão com a PokéAPI.")
            return

        def encontrar_no_no(no, alvo):
            if no.get("species", {}).get("name") == alvo:
                return no
            for filho in no.get("evolves_to", []):
                achado = encontrar_no_no(filho, alvo)
                if achado:
                    return achado
            return None

        no_atual = encontrar_no_no(cadeia.get("chain", {}), especie.get("name"))
        if not no_atual or not no_atual.get("evolves_to"):
            await ctx.send(embed=discord.Embed(
                title="🛑 SEM EVOLUÇÃO",
                description=f"**{pokemon['nome']}** não possui uma evolução disponível.",
                color=COR_CINZA
            ))
            return

        item_normalizado = item.strip().lower().replace(" ", "-").replace("_", "-")
        possiveis = []
        conquistas_usuario = self.banco.listar_conquistas(ctx.author.id)

        for filho in no_atual.get("evolves_to", []):
            detalhes = filho.get("evolution_details", []) or [{}]
            for detalhe in detalhes:
                trigger = detalhe.get("trigger", {}).get("name")
                item_api = (detalhe.get("item") or {}).get("name")
                min_level = detalhe.get("min_level")
                ok = False
                requisito = ""

                # Regra especial do Royalt tem prioridade para o alvo configurado.
                try:
                    alvo_id = int((filho.get("species", {}).get("url") or "").rstrip("/").split("/")[-1])
                except (TypeError, ValueError):
                    alvo_id = 0
                regra_especial = EVOLUCOES_ESPECIAIS_ROYALT.get((int(pokemon["pokemon_id"]), alvo_id))
                if regra_especial:
                    trigger = "royalt-achievement"
                    requisito = regra_especial["descricao"]
                    ok = regra_especial["conquista"] in conquistas_usuario
                elif trigger == "level-up" and min_level:
                    requisito = f"nível {min_level}"
                    ok = int(pokemon["nivel"]) >= int(min_level)
                elif trigger == "use-item" and item_api:
                    requisito = f"item {item_api}"
                    ok = item_normalizado == item_api
                elif trigger == "trade":
                    requisito = "Link Cable"
                    ok = item_normalizado in {"link-cable", "linking-cord"}

                possiveis.append((filho, detalhe, ok, trigger, item_api, requisito))

        escolhida = next((x for x in possiveis if x[2]), None)
        if not escolhida:
            linhas = []
            for _, detalhe, _, trigger, item_api, requisito in possiveis:
                if trigger == "use-item":
                    nome_item = LOJA.get(item_api.replace("-", "_"), {}).get("nome", item_api or "item")
                    linhas.append(f"🪨 **{nome_item}** — use `!evoluir {pokemon_db_id} {item_api}`")
                elif trigger == "trade":
                    linhas.append(f"🔗 **Link Cable** — use `!evoluir {pokemon_db_id} link-cable`")
                elif trigger == "royalt-achievement":
                    linhas.append(f"🏆 **Conquista:** {requisito}")
                elif requisito:
                    linhas.append(f"📈 **{requisito}**")
            descricao = "\n".join(linhas) or "Requisito especial não suportado ainda."
            embed = discord.Embed(
                title=f"🧬 EVOLUÇÃO • {pokemon['nome']}",
                description=f"Você ainda não atende ao requisito.\n\n{descricao}",
                color=COR_AMARELO
            )
            embed.set_thumbnail(url=self.sprite_pokemon(pokemon))
            embed.set_footer(text=POKEMON_AVISO)
            await ctx.send(embed=embed)
            return

        filho, detalhe, _, trigger, item_api, requisito = escolhida
        nome_novo_api = filho["species"]["name"]

        if trigger == "use-item":
            item_db = item_api.replace("-", "_")
            if item_db not in LOJA:
                await ctx.send(f"❌ O item evolutivo **{item_api}** ainda não está disponível no PokéMart.")
                return
            possui = any(
                r["item_id"] == item_db and int(r["quantidade"]) > 0
                for r in self.banco.listar_itens_jornada(ctx.author.id)
            )
            if not possui:
                config = LOJA[item_db]
                await ctx.send(embed=discord.Embed(
                    title="🪨 ITEM NECESSÁRIO",
                    description=(
                        f"Você precisa de **{config['nome']}** para evoluir **{pokemon['nome']}**.\n\n"
                        f"🛒 Compre no `!pokemart` por **{config['preco']} Pokécoins**."
                    ), color=COR_AMARELO
                ))
                return
            if not await self.banco.consumir_item_jornada(ctx.author.id, item_db, 1):
                await ctx.send("❌ Não consegui consumir o item evolutivo.")
                return

        novo = await self.api.pokemon(nome_novo_api)
        if not novo:
            await ctx.send("❌ Não consegui carregar os dados da evolução.")
            return

        novo_nome = nome_formatado(novo["name"])
        sucesso = await self.banco.evoluir_pokemon(
            ctx.author.id, pokemon_db_id, int(novo["id"]), novo_nome
        )
        if not sucesso:
            await ctx.send("❌ A evolução falhou.")
            return

        atualizado = self.banco.obter_pokemon(pokemon_db_id)
        atualizado = await self.sincronizar_pokemon_com_api(atualizado)

        await self.banco.desbloquear_conquista(ctx.author.id, "primeira_evolucao")
        if trigger in {"use-item", "trade"}:
            await self.banco.desbloquear_conquista(ctx.author.id, "evolucao_item")

        # Conquista de mestre após cinco evoluções reais registradas.
        todos = self.banco.listar_pokemon(ctx.author.id)
        evoluidos = sum(int(p.get("evolucoes", 0) or 0) for p in todos)
        if evoluidos >= 5:
            await self.banco.desbloquear_conquista(ctx.author.id, "cinco_evolucoes")

        sprite = novo.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default")
        motivo_evolucao = {
            "use-item": "🪨 Item evolutivo utilizado.",
            "trade": "🔗 Evolução de troca realizada com Link Cable.",
            "royalt-achievement": "🏆 Evolução especial desbloqueada por conquista.",
            "level-up": "📈 Evolução por nível.",
        }.get(trigger, "🧬 Evolução especial concluída.")

        embed = discord.Embed(
            title="✨ EVOLUÇÃO!",
            description=(
                f"🎉 **{pokemon['nome']}** evoluiu para **{novo_nome}**!\n\n"
                f"{motivo_evolucao}\n"
                f"📈 Nível: **{atualizado['nivel']}**\n"
                f"🧬 IVs foram preservados.\n"
                f"⚔️ Golpes e tipagens foram atualizados pela PokéAPI."
            ), color=COR_ROXO
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        if sprite:
            embed.set_image(url=sprite)
        embed.set_footer(text=POKEMON_AVISO)
        await ctx.send(embed=embed)

    # ========================================================
    # !TROCAR
    # ========================================================

    @commands.command(
        name="trocar",
        aliases=[
            "trade"
        ],
        description="Propõe uma troca entre dois treinadores."
    )
    @commands.guild_only()
    async def trocar(
        self,
        ctx,
        membro: discord.Member,
        meu_pokemon: int,
        pokemon_recebido: int
    ):

        if membro.bot:

            await ctx.send(
                "❌ Bots não participam de trocas."
            )

            return

        if membro.id == ctx.author.id:

            await ctx.send(
                "❌ Você não pode trocar consigo mesmo."
            )

            return

        meu = (
            self.banco.obter_pokemon(
                meu_pokemon
            )
        )

        outro = (
            self.banco.obter_pokemon(
                pokemon_recebido
            )
        )

        if meu is None or outro is None:

            await ctx.send(
                "❌ Um dos Pokémon não existe."
            )

            return

        if (
            meu["treinador_id"]
            !=
            ctx.author.id
        ):

            await ctx.send(
                "❌ Seu Pokémon não pertence a você."
            )

            return

        if (
            outro["treinador_id"]
            !=
            membro.id
        ):

            await ctx.send(
                "❌ O Pokémon do outro treinador não pertence a ele."
            )

            return

        await ctx.send(
            embed=discord.Embed(
                title="🔄 PROPOSTA DE TROCA",
                description=(
                    f"{ctx.author.mention}\n"
                    f"🎒 **{meu['nome']}**\n\n"
                    "        ⇄\n\n"
                    f"{membro.mention}\n"
                    f"🎒 **{outro['nome']}**\n\n"
                    "⚠️ A confirmação da troca será "
                    "implementada no próximo estágio."
                ),
                color=COR_AZUL
            )
        )

    # ========================================================
    # BATALHA PvE • TREINADOR SELVAGEM
    # ========================================================

    async def criar_equipe_pve(self, nivel_treinador, quantidade):
        """Gera um treinador NPC com Pokémon exatamente no nível do jogador."""
        quantidade = max(1, min(6, int(quantidade)))
        ids = random.sample(range(1, 494), quantidade)
        equipe = []

        for pokemon_id in ids:
            dados = await self.api.pokemon(pokemon_id)
            if not dados:
                continue

            base = extrair_base_stats_pokeapi(dados)
            ivs = gerar_ivs()
            nivel = max(1, int(nivel_treinador))
            stats = calcular_stats_pokemon(base, ivs, nivel)
            equipe.append({
                "id": -pokemon_id,
                "pokemon_id": pokemon_id,
                "nome": nome_formatado(dados["name"]),
                "nivel": nivel,
                "xp": max(0, (nivel - 1) * XP_POKEMON_POR_NIVEL),
                "raridade": "comum",
                "regiao": "pve",
                "shiny": 0,
                "equipe": 1,
                "favorito": 0,
                "hp": stats["hp"],
                "ataque": stats["ataque"],
                "defesa": stats["defesa"],
                "velocidade": stats["velocidade"],
                "iv_hp": ivs["iv_hp"],
                "iv_ataque": ivs["iv_ataque"],
                "iv_defesa": ivs["iv_defesa"],
                "iv_velocidade": ivs["iv_velocidade"],
                "base_hp": base["hp"],
                "base_ataque": base["ataque"],
                "base_defesa": base["defesa"],
                "base_velocidade": base["velocidade"],
                "batalhas": 0,
                "vitorias": 0,
            })

        if not equipe:
            for starter in STARTERS.values():
                base = STARTER_BASE_STATS[starter["id"]]
                ivs = gerar_ivs()
                nivel = max(1, int(nivel_treinador))
                stats = calcular_stats_pokemon(base, ivs, nivel)
                equipe.append({
                    "id": -starter["id"],
                    "pokemon_id": starter["id"],
                    "nome": starter["nome"],
                    "nivel": nivel,
                    "xp": max(0, (nivel - 1) * XP_POKEMON_POR_NIVEL),
                    "raridade": "comum",
                    "regiao": "kanto",
                    "shiny": 0,
                    "equipe": 1,
                    "favorito": 0,
                    "hp": stats["hp"],
                    "ataque": stats["ataque"],
                    "defesa": stats["defesa"],
                    "velocidade": stats["velocidade"],
                    "iv_hp": ivs["iv_hp"],
                    "iv_ataque": ivs["iv_ataque"],
                    "iv_defesa": ivs["iv_defesa"],
                    "iv_velocidade": ivs["iv_velocidade"],
                    "base_hp": base["hp"],
                    "base_ataque": base["ataque"],
                    "base_defesa": base["defesa"],
                    "base_velocidade": base["velocidade"],
                    "batalhas": 0,
                    "vitorias": 0,
                })
                if len(equipe) >= quantidade:
                    break

        return equipe[:quantidade]

    def simular_batalha_pve(self, equipe_jogador, equipe_npc):
        vitorias_jogador = 0
        vitorias_npc = 0
        rodadas = []

        for indice in range(max(len(equipe_jogador), len(equipe_npc))):
            p1 = equipe_jogador[indice] if indice < len(equipe_jogador) else None
            p2 = equipe_npc[indice] if indice < len(equipe_npc) else None

            if p1 is None:
                vitorias_npc += 1
                rodadas.append(f"**{indice + 1}.** 🟥 {p2['nome']} venceu por ausência")
                continue
            if p2 is None:
                vitorias_jogador += 1
                rodadas.append(f"**{indice + 1}.** 🟦 {p1['nome']} venceu por ausência")
                continue

            hp1 = float(p1["hp"])
            hp2 = float(p2["hp"])
            golpes = 0
            primeiro = p1 if p1["velocidade"] >= p2["velocidade"] else p2
            segundo = p2 if primeiro is p1 else p1

            while hp1 > 0 and hp2 > 0 and golpes < 12:
                atacante = primeiro if golpes % 2 == 0 else segundo
                defensor = segundo if golpes % 2 == 0 else primeiro
                dano = max(
                    1,
                    int(
                        atacante["ataque"] * random.uniform(0.85, 1.15)
                        - defensor["defesa"] * 0.35
                    )
                )
                if atacante is p1:
                    hp2 -= dano
                else:
                    hp1 -= dano
                golpes += 1

            if hp1 > 0 and hp2 <= 0:
                vitorias_jogador += 1
                vencedor = p1["nome"]
            elif hp2 > 0 and hp1 <= 0:
                vitorias_npc += 1
                vencedor = p2["nome"]
            elif self.poder_pokemon(p1) >= self.poder_pokemon(p2):
                vitorias_jogador += 1
                vencedor = p1["nome"]
            else:
                vitorias_npc += 1
                vencedor = p2["nome"]

            rodadas.append(
                f"**{indice + 1}.** ⚔️ **{vencedor}** venceu "
                f"{p1['nome']} × {p2['nome']} ({golpes} golpes)"
            )

        venceu = vitorias_jogador >= vitorias_npc
        return venceu, vitorias_jogador, vitorias_npc, rodadas

    # ========================================================
    # GINÁSIOS — BATALHA MANUAL
    # ========================================================

    async def dados_pokemon_batalha(self, pokemon_id, nivel, ivs=None):
        dados = await self.api.pokemon(pokemon_id)
        if not dados:
            return None

        base = extrair_base_stats_pokeapi(dados)
        ivs = ivs or gerar_ivs()
        stats = calcular_stats_pokemon(base, ivs, nivel)

        movimentos = await extrair_movimentos_combate(
            self.api, dados, nivel=nivel
        )
        tipos = [
            item.get("type", {}).get("name", "normal")
            for item in dados.get("types", [])
        ]

        return {
            "pokemon_id": int(pokemon_id),
            "nome": nome_formatado(dados.get("name", "pokemon")),
            "nivel": int(nivel),
            "hp": int(stats["hp"]),
            "ataque": int(stats["ataque"]),
            "defesa": int(stats["defesa"]),
            "velocidade": int(stats["velocidade"]),
            "iv_hp": int(ivs["iv_hp"]),
            "iv_ataque": int(ivs["iv_ataque"]),
            "iv_defesa": int(ivs["iv_defesa"]),
            "iv_velocidade": int(ivs["iv_velocidade"]),
            "tipos": tipos,
            "movimentos": movimentos,
            "sprite": (
                dados.get("sprites", {})
                .get("other", {})
                .get("official-artwork", {})
                .get("front_default")
            ) or self.sprite_pokemon({"pokemon_id": pokemon_id}),
        }

    def tipo_efetividade(self, ataque, defensor_tipos):
        # Tabela compacta de fraquezas/resistências por tipo.
        super_efetivo = {
            "normal": [], "fire": ["grass", "ice", "bug", "steel"],
            "water": ["fire", "ground", "rock"], "electric": ["water", "flying"],
            "grass": ["water", "ground", "rock"], "ice": ["grass", "ground", "flying", "dragon"],
            "fighting": ["normal", "ice", "rock", "dark", "steel"],
            "poison": ["grass", "fairy"], "ground": ["fire", "electric", "poison", "rock", "steel"],
            "flying": ["grass", "fighting", "bug"], "psychic": ["fighting", "poison"],
            "bug": ["grass", "psychic", "dark"], "rock": ["fire", "ice", "flying", "bug"],
            "ghost": ["psychic", "ghost"], "dragon": ["dragon"],
            "dark": ["psychic", "ghost"], "steel": ["ice", "rock", "fairy"],
            "fairy": ["fighting", "dragon", "dark"],
        }
        resist = {
            "fire": ["fire", "water", "rock", "dragon"],
            "water": ["water", "grass", "dragon"],
            "electric": ["electric", "grass", "dragon"],
            "grass": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"],
            "ice": ["fire", "water", "ice", "steel"],
            "fighting": ["poison", "flying", "psychic", "bug", "fairy"],
            "poison": ["poison", "ground", "rock", "ghost"],
            "ground": ["grass", "bug"],
            "flying": ["electric", "rock", "steel"],
            "psychic": ["psychic", "steel"],
            "bug": ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"],
            "rock": ["fighting", "ground", "steel"],
            "ghost": ["dark"],
            "dragon": ["steel"],
            "dark": ["fighting", "dark", "fairy"],
            "steel": ["fire", "water", "electric", "steel"],
            "fairy": ["fire", "poison", "steel"],
            "normal": [],
        }
        imune = {
            ("normal", "ghost"), ("fighting", "ghost"),
            ("poison", "steel"), ("ground", "flying"),
            ("psychic", "dark"), ("electric", "ground"),
            ("dragon", "fairy"),
        }

        mult = 1.0
        for defensor in defensor_tipos:
            if (ataque, defensor) in imune:
                mult *= 0
            elif defensor in super_efetivo.get(ataque, []):
                mult *= 2
            elif defensor in resist.get(ataque, []):
                mult *= 0.5
        return mult

    def calcular_dano_manual(self, atacante, defensor, movimento):
        stab = 1.5 if movimento["tipo"] in atacante["tipos"] else 1.0
        efetividade = self.tipo_efetividade(
            movimento["tipo"],
            defensor["tipos"]
        )
        dano = (
            (
                (2 * atacante["nivel"] / 5 + 2)
                * movimento["poder"]
                * atacante["ataque"]
                / max(1, defensor["defesa"])
            ) / 50
        ) + 2

        critico = random.random() < 0.08
        variacao = random.uniform(0.85, 1.0)

        dano *= stab * efetividade * variacao
        if critico:
            dano *= 1.5

        return max(
            1 if efetividade > 0 else 0,
            int(dano)
        ), efetividade, critico

    def criar_embed_ginasios(self, membro, regiao):
        dados = GINASIOS[regiao]
        treinador = self.banco.obter_treinador(membro.id)
        nivel = int(treinador["nivel"])
        requisito = NIVEIS_REGIAO[regiao]
        badges = {
            int(x["numero"])
            for x in self.banco.listar_insignias(membro.id, regiao)
        }

        linhas = []
        for gym in dados["ginasios"]:
            estado = "✅" if gym["numero"] in badges else "🔒"
            linhas.append(
                f"{estado} **{gym['numero']}. {gym['insignia']}** — "
                f"👑 {gym['lider']} • "
                f"tipo **{TIPOS_GINASIO.get(gym['lider'], 'normal')}**"
            )

        proximo = len(badges) + 1
        if proximo <= 8:
            gym = dados["ginasios"][proximo - 1]
            acao = (
                f"⚔️ Próximo desafio: **{gym['lider']}** "
                f"(Ginásio {proximo}/8)"
            )
        else:
            acao = "👑 Todos os ginásios concluídos. A Elite 4 aguarda."

        embed = discord.Embed(
            title=f"{dados['emoji']} GINÁSIOS • {dados['nome']}",
            description=(
                f"⭐ Seu nível: **{nivel}** • "
                f"🔓 Região: **{requisito}**\n\n"
                + "\n".join(linhas)
                + f"\n\n{acao}\n\n"
                "⚔️ As batalhas são **manuais**: você escolhe os golpes "
                "e pode trocar de Pokémon."
            ),
            color=COR_AZUL
        )
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    async def montar_time_lider(self, regiao, numero, nivel):
        gym = GINASIOS[regiao]["ginasios"][numero - 1]
        # Líderes ficam deliberadamente acima do nível do treinador.
        nivel_lider = max(nivel + 5, NIVEIS_REGIAO[regiao] + numero + 4)
        equipe = []

        for pid in gym["pokemon"]:
            pokemon = await self.dados_pokemon_batalha(
                pid,
                nivel_lider,
                {
                    "iv_hp": random.randint(22, 31),
                    "iv_ataque": random.randint(24, 31),
                    "iv_defesa": random.randint(22, 31),
                    "iv_velocidade": random.randint(24, 31),
                }
            )
            if pokemon:
                equipe.append(pokemon)

        return gym, equipe, nivel_lider

    async def iniciar_batalha_ginasio(self, interaction, regiao, numero):
        uid = interaction.user.id

        if uid in self.gym_battles:
            await interaction.response.send_message(
                "⚔️ Você já está em uma batalha de ginásio.",
                ephemeral=True
            )
            return

        treinador = self.banco.obter_treinador(uid)
        nivel = int(treinador["nivel"])
        requisito = NIVEIS_REGIAO[regiao]

        if nivel < requisito:
            await interaction.response.send_message(
                f"🔒 Você precisa do nível **{requisito}** para essa região.",
                ephemeral=True
            )
            return

        badges = self.banco.listar_insignias(uid, regiao)
        if len(badges) != numero - 1:
            await interaction.response.send_message(
                "🔒 Você precisa conquistar as insígnias anteriores primeiro.",
                ephemeral=True
            )
            return

        equipe = [
            p for p in self.banco.listar_pokemon(uid)
            if p["equipe"]
        ][:6]

        if not equipe:
            await interaction.response.send_message(
                "❌ Você precisa ter pelo menos um Pokémon na equipe.",
                ephemeral=True
            )
            return

        equipe = [
            await self.sincronizar_pokemon_com_api(p)
            for p in equipe
        ]

        gym, inimigos, nivel_lider = await self.montar_time_lider(
            regiao,
            numero,
            nivel
        )

        if not inimigos:
            await interaction.response.send_message(
                "❌ Não consegui carregar o time do líder. Tente novamente.",
                ephemeral=True
            )
            return

        estado = {
            "usuario_id": uid,
            "regiao": regiao,
            "tipo": "ginasio",
            "numero": numero,
            "lider": gym["lider"],
            "insignia": gym["insignia"],
            "nivel_lider": nivel_lider,
            "equipe": equipe,
            "hp_jogador": [float(p["hp"]) for p in equipe],
            "inimigos": inimigos,
            "hp_inimigos": [float(p["hp"]) for p in inimigos],
            "ativo": 0,
            "ativo_inimigo": 0,
            "movimentos_jogador": {
                int(p["id"]): json.loads(p.get("movimentos") or "[]")
                if p.get("movimentos") else []
                for p in equipe
            },
            "log": [
                f"⚔️ **{gym['lider']}** aceitou seu desafio!"
            ],
        }

        # Se algum Pokémon do usuário ainda não tinha golpes salvos,
        # os dados sincronizados já foram usados; carrega um fallback.
        for p in equipe:
            if not estado["movimentos_jogador"][int(p["id"])]:
                estado["movimentos_jogador"][int(p["id"])] = p.get(
                    "movimentos", []
                ) or [{
                    "nome": "Tackle", "tipo": "normal",
                    "poder": 40, "precisao": 100
                }]

        self.gym_battles[uid] = estado

        embed = self.criar_embed_batalha_ginasio(
            estado,
            (
                f"🏟️ **Ginásio {numero}/8 — {gym['lider']}**\n"
                f"🏅 Insígnia em jogo: **{gym['insignia']}**"
            )
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GinasioBattleView(self, estado)
        )

    async def processar_turno_ginasio(self, interaction, view, indice_movimento):
        estado = view.estado
        uid = estado["usuario_id"]

        if interaction.user.id != uid:
            await interaction.response.send_message(
                "❌ Essa batalha pertence a outro treinador.",
                ephemeral=True
            )
            return

        if uid not in self.gym_battles:
            await interaction.response.send_message(
                "❌ Essa batalha já terminou.",
                ephemeral=True
            )
            return

        atacante = estado["equipe"][estado["ativo"]]
        defensor = estado["inimigos"][estado["ativo_inimigo"]]
        movimentos = estado["movimentos_jogador"].get(
            int(atacante["id"]), []
        )

        if indice_movimento >= len(movimentos):
            await interaction.response.send_message(
                "❌ Esse golpe não está disponível.",
                ephemeral=True
            )
            return

        movimento = movimentos[indice_movimento]

        dano, efetividade, critico = self.calcular_dano_manual(
            atacante,
            defensor,
            movimento
        )
        estado["hp_inimigos"][estado["ativo_inimigo"]] -= dano

        mensagem = (
            f"⚔️ **{atacante['nome']}** usou **{movimento['nome']}** "
            f"e causou **{dano}** de dano."
        )

        if efetividade >= 2:
            mensagem += " 💥 **Super efetivo!**"
        elif 0 < efetividade < 1:
            mensagem += " 🛡️ Não foi muito efetivo..."
        elif efetividade == 0:
            mensagem += " 🚫 Não teve efeito!"
        if critico:
            mensagem += " ✨ **Acerto crítico!**"

        estado["log"].append(mensagem)

        # Derrubou o Pokémon atual do líder.
        if estado["hp_inimigos"][estado["ativo_inimigo"]] <= 0:
            estado["log"].append(
                f"💥 **{defensor['nome']}** foi derrotado!"
            )

            proximo = next(
                (
                    i for i, hp in enumerate(estado["hp_inimigos"])
                    if hp > 0
                ),
                None
            )

            if proximo is None:
                await self.finalizar_batalha_ginasio(
                    interaction,
                    estado,
                    venceu=True
                )
                view.stop()
                return

            estado["ativo_inimigo"] = proximo
            novo = estado["inimigos"][proximo]
            estado["log"].append(
                f"🔴 O líder enviou **{novo['nome']}**!"
            )
        else:
            # IA do líder: escolhe o golpe com maior dano esperado,
            # priorizando golpes super efetivos e STAB.
            await self.ataque_ia_lider(estado)

            if estado["hp_jogador"][estado["ativo"]] <= 0:
                estado["log"].append(
                    f"💥 **{atacante['nome']}** foi derrotado!"
                )
                vivos = [
                    i for i, hp in enumerate(estado["hp_jogador"])
                    if hp > 0
                ]

                if not vivos:
                    await self.finalizar_batalha_ginasio(
                        interaction,
                        estado,
                        venceu=False
                    )
                    view.stop()
                    return

                # Obriga troca: botões de ataque ficam bloqueados até trocar.
                estado["log"].append(
                    "🔄 Escolha outro Pokémon com **Trocar Pokémon**."
                )

        # Limita o log visual aos eventos recentes.
        estado["log"] = estado["log"][-6:]

        view.atualizar_botoes()

        await interaction.response.edit_message(
            embed=self.criar_embed_batalha_ginasio(
                estado,
                "🎯 Seu turno — escolha um golpe."
            ),
            view=view
        )

    async def ataque_ia_lider(self, estado):
        atacante = estado["inimigos"][estado["ativo_inimigo"]]
        defensor = estado["equipe"][estado["ativo"]]
        movimentos = atacante.get("movimentos", []) or [{
            "nome": "Tackle", "tipo": "normal",
            "poder": 40, "precisao": 100
        }]

        melhor = None
        melhor_score = -1

        for movimento in movimentos:
            efetividade = self.tipo_efetividade(
                movimento["tipo"],
                defensor["tipos"]
            )
            stab = 1.5 if movimento["tipo"] in atacante["tipos"] else 1.0
            score = movimento["poder"] * efetividade * stab

            if score > melhor_score:
                melhor_score = score
                melhor = movimento

        dano, efetividade, critico = self.calcular_dano_manual(
            atacante,
            defensor,
            melhor
        )
        estado["hp_jogador"][estado["ativo"]] -= dano

        mensagem = (
            f"🤖 **{atacante['nome']}** usou **{melhor['nome']}** "
            f"e causou **{dano}** de dano."
        )
        if efetividade >= 2:
            mensagem += " 💥 **Super efetivo!**"
        elif 0 < efetividade < 1:
            mensagem += " 🛡️ Não foi muito efetivo..."
        if critico:
            mensagem += " ✨ **Crítico!**"

        estado["log"].append(mensagem)

    def criar_embed_batalha_ginasio(self, estado, mensagem):
        jogador = estado["equipe"][estado["ativo"]]
        inimigo = estado["inimigos"][estado["ativo_inimigo"]]

        hpj = max(0, int(estado["hp_jogador"][estado["ativo"]]))
        hpi = max(0, int(estado["hp_inimigos"][estado["ativo_inimigo"]]))

        embed = discord.Embed(
            title=(
                f"🏟️ {estado['lider']} • "
                f"{REGIOES[estado['regiao']]['nome']}"
            ),
            description=(
                f"**{estado['lider']}**\n"
                f"🧢 Líder • Nv. **{estado['nivel_lider']}**\n\n"
                f"🔴 **{inimigo['nome']}** • Nv. {inimigo['nivel']}\n"
                f"{' '.join(obter_emoji_tipo(t) for t in inimigo['tipos'])}\n"
                f"❤️ HP: **{hpi}/{inimigo['hp']}**\n\n"
                f"🔵 **{jogador['nome']}** • Nv. {jogador['nivel']}\n"
                f"{' '.join(obter_emoji_tipo(t) for t in jogador['tipos'])}\n"
                f"❤️ HP: **{hpj}/{jogador['hp']}**\n\n"
                f"**{mensagem}**\n\n"
                + "\n".join(estado["log"][-6:])
            ),
            color=COR_VERMELHO
        )
        embed.set_thumbnail(url=inimigo["sprite"])
        embed.set_image(url=jogador["sprite"])
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    async def finalizar_batalha_ginasio(self, interaction, estado, venceu):
        uid = estado["usuario_id"]
        self.gym_battles.pop(uid, None)

        if estado.get("tipo") == "elite4":
            if venceu:
                resultado = await self.banco.avancar_elite4(
                    uid,
                    estado["regiao"]
                )
                recompensa = 800 + (
                    NIVEIS_REGIAO[estado["regiao"]] * 8
                )
                xp = 250 + estado["numero"] * 40

                await self.banco.alterar_pokecoins(uid, recompensa)
                await self.banco.adicionar_xp(uid, xp)
                await self.banco.registrar_resultado_pokemon_batalha(
                    estado["equipe"],
                    []
                )

                conclusao = (
                    "👑 Você derrotou toda a Elite 4 desta região!"
                    if resultado["concluida"]
                    else (
                        f"👑 Próximo membro da Elite 4: "
                        f"**{GINASIOS[estado['regiao']]['elite4'][resultado['etapa']]}**"
                    )
                )

                embed = discord.Embed(
                    title="👑 ELITE 4 DERROTADA!",
                    description=(
                        f"Você venceu **{estado['lider']}**!\\n\\n"
                        f"🏆 Etapa: **{resultado['etapa']}/4**\\n"
                        f"🪙 **+{recompensa} Pokécoins**\\n"
                        f"✨ **+{xp} XP treinador**\\n\\n"
                        f"{conclusao}"
                    ),
                    color=COR_AMARELO
                )
            else:
                await self.banco.registrar_resultado_pokemon_batalha(
                    [],
                    estado["equipe"]
                )
                embed = discord.Embed(
                    title="💨 DERROTA NA ELITE 4",
                    description=(
                        f"**{estado['lider']}** venceu.\\n\\n"
                        "Sua sequência da Elite 4 não avança até você vencer este membro."
                    ),
                    color=COR_CINZA
                )

            embed.set_footer(text=POKEMON_AVISO)
            await interaction.response.edit_message(
                embed=embed,
                view=GinasiosView(self, uid, estado["regiao"])
            )
            return

        if venceu:
            nova = await self.banco.conquistar_insignia(
                uid,
                estado["regiao"],
                estado["numero"]
            )
            recompensa = 350 + (
                NIVEIS_REGIAO[estado["regiao"]] * 5
            ) + estado["numero"] * 75

            xp = 100 + estado["numero"] * 20

            await self.banco.alterar_pokecoins(uid, recompensa)
            await self.banco.adicionar_xp(uid, xp)

            await self.banco.registrar_resultado_pokemon_batalha(
                estado["equipe"],
                []
            )

            titulo = "🏅 INSÍGNIA CONQUISTADA!"
            descricao = (
                f"Você derrotou **{estado['lider']}**!\n\n"
                f"🏅 **{estado['insignia']}**\n"
                f"🪙 **+{recompensa} Pokécoins**\n"
                f"✨ **+{xp} XP treinador**\n\n"
                "O próximo ginásio já está disponível."
                if nova else
                "Você já possuía essa insígnia."
            )
            cor = COR_AMARELO
        else:
            await self.banco.registrar_resultado_pokemon_batalha(
                [],
                estado["equipe"]
            )
            titulo = "💨 DERROTA NO GINÁSIO"
            descricao = (
                f"**{estado['lider']}** venceu desta vez.\n\n"
                "Treine sua equipe, melhore seus golpes e tente novamente."
            )
            cor = COR_CINZA

        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=cor
        )
        embed.set_footer(text=POKEMON_AVISO)
        await interaction.response.edit_message(
            embed=embed,
            view=GinasiosView(
                self,
                uid,
                estado["regiao"]
            )
        )

    async def iniciar_batalha_elite(self, interaction, regiao):
        uid = interaction.user.id
        treinador = self.banco.obter_treinador(uid)
        nivel = int(treinador["nivel"])
        requisito = NIVEIS_REGIAO[regiao]

        if nivel < requisito:
            await interaction.response.send_message(
                f"🔒 Essa região abre no nível **{requisito}**.",
                ephemeral=True
            )
            return

        badges = self.banco.listar_insignias(uid, regiao)
        if len(badges) < 8:
            await interaction.response.send_message(
                "🔒 Conquiste as 8 insígnias da região antes da Elite 4.",
                ephemeral=True
            )
            return

        progresso = self.banco.obter_progresso_liga(uid, regiao)
        etapa = int(progresso["elite_etapa"])

        if etapa >= 4:
            await interaction.response.send_message(
                "👑 Você já concluiu a Elite 4 desta região!",
                ephemeral=True
            )
            return

        # Elite 4 usa equipes próprias baseadas no tipo do membro.
        nome = GINASIOS[regiao]["elite4"][etapa]
        tipo = ELITE4_TIPOS.get(nome, "normal")

        candidatos = [
            pid for pid in range(
                REGIOES[regiao]["min_id"],
                REGIOES[regiao]["max_id"] + 1
            )
        ]
        random.shuffle(candidatos)

        equipe = []
        for pid in candidatos:
            dados = await self.api.pokemon(pid)
            if not dados:
                continue
            tipos = [
                x.get("type", {}).get("name")
                for x in dados.get("types", [])
            ]
            if tipo not in tipos:
                continue
            pokemon = await self.dados_pokemon_batalha(
                pid,
                max(nivel + 8, requisito + 10),
                {
                    "iv_hp": random.randint(26, 31),
                    "iv_ataque": random.randint(26, 31),
                    "iv_defesa": random.randint(26, 31),
                    "iv_velocidade": random.randint(26, 31),
                }
            )
            if pokemon:
                equipe.append(pokemon)
            if len(equipe) >= 4:
                break

        if not equipe:
            await interaction.response.send_message(
                "❌ Não consegui montar a equipe da Elite 4 agora.",
                ephemeral=True
            )
            return

        player_team = [
            p for p in self.banco.listar_pokemon(uid)
            if p["equipe"]
        ][:6]

        if not player_team:
            await interaction.response.send_message(
                "❌ Você precisa ter Pokémon na equipe.",
                ephemeral=True
            )
            return

        player_team = [
            await self.sincronizar_pokemon_com_api(p)
            for p in player_team
        ]

        estado = {
            "usuario_id": uid,
            "regiao": regiao,
            "tipo": "elite4",
            "numero": etapa + 1,
            "lider": nome,
            "insignia": f"Elite 4 • {nome}",
            "nivel_lider": max(nivel + 8, requisito + 10),
            "equipe": player_team,
            "hp_jogador": [float(p["hp"]) for p in player_team],
            "inimigos": equipe,
            "hp_inimigos": [float(p["hp"]) for p in equipe],
            "ativo": 0,
            "ativo_inimigo": 0,
            "movimentos_jogador": {
                int(p["id"]): json.loads(p.get("movimentos") or "[]")
                if p.get("movimentos") else []
                for p in player_team
            },
            "log": [
                f"👑 **{nome}** da Elite 4 aceitou o desafio!"
            ],
        }

        for p in player_team:
            if not estado["movimentos_jogador"][int(p["id"])]:
                estado["movimentos_jogador"][int(p["id"])] = [{
                    "nome": "Tackle", "tipo": "normal",
                    "poder": 40, "precisao": 100
                }]

        self.gym_battles[uid] = estado

        await interaction.response.edit_message(
            embed=self.criar_embed_batalha_ginasio(
                estado,
                f"👑 **Elite 4 — {etapa + 1}/4 • {nome}**"
            ),
            view=GinasioBattleView(self, estado)
        )

    async def batalha_pve(self, ctx):
        treinador = self.banco.obter_treinador(ctx.author.id)
        nivel = max(1, int(treinador["nivel"]))

        equipe = [
            p for p in self.banco.listar_pokemon(ctx.author.id)
            if p["equipe"]
        ][:6]
        if not equipe:
            equipe = self.banco.listar_pokemon(ctx.author.id)[:1]

        if not equipe:
            await self.banco.concluir_batalha_pve(ctx.author.id)
            return

        equipe = [
            await self.sincronizar_pokemon_com_api(p)
            for p in equipe
        ]

        # 1 Pokémon nos níveis iniciais, 2 a partir do nível 10 e 3 a partir do 20.
        quantidade_npc = min(3, max(1, 1 + (nivel - 1) // 10))
        equipe_npc = await self.criar_equipe_pve(nivel, quantidade_npc)

        nomes_npc = [
            "Kai", "Maya", "Ryu", "Luna", "Theo", "Nina",
            "Milo", "Iris", "Zane", "Ayla", "Noah", "Sora"
        ]
        nome_npc = random.choice(nomes_npc)

        venceu, vj, vn, rodadas = self.simular_batalha_pve(
            equipe, equipe_npc
        )

        if venceu:
            recompensa = random.randint(90, 150) + nivel * 10
            xp_treinador = random.randint(45, 75) + nivel * 2
        else:
            recompensa = random.randint(30, 70) + nivel * 4
            xp_treinador = random.randint(20, 40) + nivel

        await self.banco.alterar_pokecoins(ctx.author.id, recompensa)
        resultado_xp = await self.banco.adicionar_xp(
            ctx.author.id, xp_treinador
        )

        resultados_pokemon = await self.banco.registrar_resultado_pokemon_batalha(
            equipe if venceu else [],
            [] if venceu else equipe
        )
        await self.banco.registrar_resultado_batalha_pve(
            ctx.author.id, venceu
        )
        await self.banco.salvar_cooldown(
            ctx.author.id, "ultimo_batalha"
        )
        await self.banco.concluir_batalha_pve(ctx.author.id)
        await self.banco.desbloquear_conquista(
            ctx.author.id, "primeira_batalha"
        )

        xp_pokemon = sum(r["xp"] for r in resultados_pokemon)
        destaque = max(equipe, key=self.poder_pokemon)
        titulo = "🏆 BATALHA PvE VENCIDA!" if venceu else "💨 BATALHA PvE PERDIDA"
        cor = COR_VERDE if venceu else COR_CINZA

        embed = discord.Embed(
            title=titulo,
            description=(
                f"### {ctx.author.display_name} VS Treinador {nome_npc}\n\n"
                f"🎓 **Nível do adversário:** {nivel}\n"
                f"⚔️ **Resultado:** {vj} × {vn}\n"
                f"🌟 **Destaque:** {destaque['nome']}\n\n"
                f"💰 **Pokécoins:** +{recompensa}\n"
                f"✨ **XP treinador:** +{xp_treinador}\n"
                f"🐾 **XP da equipe:** +{xp_pokemon}\n\n"
                + "\n".join(rodadas)
            ),
            color=cor
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        if resultado_xp and resultado_xp["nivel_depois"] > resultado_xp["nivel_antes"]:
            embed.add_field(
                name="🎉 LEVEL UP!",
                value=f"Você alcançou o nível **{resultado_xp['nivel_depois']}**!",
                inline=False
            )

        embed.set_footer(
            text=f"⚔️ O próximo combate PvE virá após novas explorações. {POKEMON_AVISO}"
        )
        await ctx.send(embed=embed)

    # ========================================================
    # !BATALHAR
    # ========================================================

    @commands.command(
        name="batalhar",
        aliases=["battle", "duelo"],
        description="Desafia outro treinador em uma batalha de equipes."
    )
    @commands.guild_only()
    async def batalhar(self, ctx, membro: discord.Member):

        if membro.bot:
            await ctx.send("❌ Bots não podem batalhar.")
            return

        if membro.id == ctx.author.id:
            await ctx.send("❌ Você não pode batalhar consigo mesmo.")
            return

        treinador1 = self.banco.obter_treinador(ctx.author.id)
        treinador2 = self.banco.obter_treinador(membro.id)

        restante = self.segundos_cooldown(
            treinador1["ultimo_batalha"],
            COOLDOWN_BATALHA
        )

        if restante > 0:
            await ctx.send(
                embed=discord.Embed(
                    title="⏳ DESAFIO EM COOLDOWN",
                    description=(
                        f"Você poderá desafiar novamente em "
                        f"**{formatar_tempo(restante)}**."
                    ),
                    color=COR_CINZA
                )
            )
            return

        equipe1 = [
            p for p in self.banco.listar_pokemon(ctx.author.id)
            if p["equipe"]
        ][:6]

        equipe2 = [
            p for p in self.banco.listar_pokemon(membro.id)
            if p["equipe"]
        ][:6]

        if not equipe1:
            await ctx.send("❌ Você não possui Pokémon na equipe.")
            return

        if not equipe2:
            await ctx.send("❌ O outro treinador não possui Pokémon na equipe.")
            return

        # Atualiza os stats com a base real da PokéAPI antes do duelo.
        equipes_sincronizadas = []
        for equipe in (equipe1, equipe2):
            nova = []
            for pokemon in equipe:
                dados_poke = await self.api.pokemon(pokemon["pokemon_id"])
                if dados_poke:
                    atualizado = await self.banco.atualizar_stats_pokemon(
                        pokemon["id"],
                        extrair_base_stats_pokeapi(dados_poke)
                    )
                    if atualizado:
                        pokemon = atualizado
                nova.append(pokemon)

            equipes_sincronizadas.append(nova)

        equipe1, equipe2 = equipes_sincronizadas

        rodadas = []
        vitorias1 = 0
        vitorias2 = 0

        for indice in range(max(len(equipe1), len(equipe2))):
            p1 = equipe1[indice] if indice < len(equipe1) else None
            p2 = equipe2[indice] if indice < len(equipe2) else None

            if p1 is None:
                vitorias2 += 1
                rodadas.append(
                    f"**{indice + 1}.** 🟦 {p2['nome']} venceu por ausência"
                )
                continue

            if p2 is None:
                vitorias1 += 1
                rodadas.append(
                    f"**{indice + 1}.** 🟥 {p1['nome']} venceu por ausência"
                )
                continue

            hp1 = float(p1["hp"])
            hp2 = float(p2["hp"])
            ataques = 0

            primeiro = p1 if p1["velocidade"] >= p2["velocidade"] else p2
            segundo = p2 if primeiro is p1 else p1

            while hp1 > 0 and hp2 > 0 and ataques < 12:
                atacante = primeiro if ataques % 2 == 0 else segundo
                defensor = segundo if ataques % 2 == 0 else primeiro

                dano = max(
                    1,
                    int(
                        atacante["ataque"] * random.uniform(0.85, 1.15)
                        - defensor["defesa"] * 0.35
                    )
                )

                if atacante is p1:
                    hp2 -= dano
                else:
                    hp1 -= dano

                ataques += 1

            if hp1 > 0 and hp2 <= 0:
                vitorias1 += 1
                marcador = f"🟥 **{p1['nome']}**"
            elif hp2 > 0 and hp1 <= 0:
                vitorias2 += 1
                marcador = f"🟦 **{p2['nome']}**"
            else:
                poder1 = self.poder_pokemon(p1)
                poder2 = self.poder_pokemon(p2)
                if poder1 >= poder2:
                    vitorias1 += 1
                    marcador = f"🟥 **{p1['nome']}**"
                else:
                    vitorias2 += 1
                    marcador = f"🟦 **{p2['nome']}**"

            rodadas.append(
                f"**{indice + 1}.** {marcador} venceu "
                f"**{p1['nome']}** × **{p2['nome']}** "
                f"({ataques} golpes)"
            )

        if vitorias1 == vitorias2:
            poder_total1 = sum(self.poder_pokemon(p) for p in equipe1)
            poder_total2 = sum(self.poder_pokemon(p) for p in equipe2)
            if poder_total1 >= poder_total2:
                vencedor = ctx.author
                derrotado = membro
                equipe_vencedora = equipe1
            else:
                vencedor = membro
                derrotado = ctx.author
                equipe_vencedora = equipe2
            criterio = "desempate pelo poder total da equipe"
        elif vitorias1 > vitorias2:
            vencedor = ctx.author
            derrotado = membro
            equipe_vencedora = equipe1
            criterio = "maior número de vitórias nas rodadas"
        else:
            vencedor = membro
            derrotado = ctx.author
            equipe_vencedora = equipe2
            criterio = "maior número de vitórias nas rodadas"

        pokemon_destaque = max(
            equipe_vencedora,
            key=self.poder_pokemon
        )

        recompensa_vencedor = random.randint(*RECOMPENSA_BATALHA_VITORIA)
        recompensa_derrotado = random.randint(*RECOMPENSA_BATALHA_DERROTA)

        await self.banco.alterar_pokecoins(
            vencedor.id,
            recompensa_vencedor
        )
        await self.banco.alterar_pokecoins(
            derrotado.id,
            recompensa_derrotado
        )

        # O cooldown pertence aos dois participantes, evitando spam
        # alternando quem inicia o desafio.
        await self.banco.salvar_cooldown(
            ctx.author.id,
            "ultimo_batalha"
        )
        await self.banco.salvar_cooldown(
            membro.id,
            "ultimo_batalha"
        )

        await self.banco.registrar_resultado_batalha(
            vencedor.id,
            derrotado.id
        )

        xp_vencedor = random.randint(50, 90)
        xp_derrotado = random.randint(15, 35)

        resultado_xp_v = await self.banco.adicionar_xp(
            vencedor.id,
            xp_vencedor
        )
        await self.banco.adicionar_xp(
            derrotado.id,
            xp_derrotado
        )

        resultados_pokemon = await self.banco.registrar_resultado_pokemon_batalha(
            equipe1 if vencedor.id == ctx.author.id else equipe2,
            equipe2 if vencedor.id == ctx.author.id else equipe1
        )

        ids_vencedores = {int(p["id"]) for p in equipe_vencedora}
        xp_pokemon_vencedor = sum(
            r["xp"] for r in resultados_pokemon
            if int(r["id"]) in ids_vencedores
        )
        xp_pokemon_derrotado = sum(
            r["xp"] for r in resultados_pokemon
            if int(r["id"]) not in ids_vencedores
        )

        await self.banco.desbloquear_conquista(
            ctx.author.id,
            "primeira_batalha"
        )

        embed = discord.Embed(
            title="⚔️ DUELO POKÉMON FINALIZADO!",
            description=(
                f"### {ctx.author.display_name} VS {membro.display_name}\n\n"
                f"🏆 **Vencedor:** {vencedor.mention}\n"
                f"✨ Destaque: **{pokemon_destaque['nome']}**\n\n"
                f"🟥 {ctx.author.display_name}: **{vitorias1} vitórias**\n"
                f"🟦 {membro.display_name}: **{vitorias2} vitórias**\n\n"
                f"📌 Critério: {criterio}"
            ),
            color=COR_AMARELO
        )

        embed.add_field(
            name="📋 Rodadas",
            value="\n".join(rodadas),
            inline=False
        )

        embed.add_field(
            name="🏆 Recompensa",
            value=(
                f"{vencedor.mention}: **+{recompensa_vencedor} 🪙** + **{xp_vencedor} XP treinador**\n"
                f"{derrotado.mention}: **+{recompensa_derrotado} 🪙** + **{xp_derrotado} XP treinador**\n"
                f"🐾 XP dos Pokémon: **+{xp_pokemon_vencedor}** vencedora • **+{xp_pokemon_derrotado}** derrotada"
            ),
            inline=False
        )

        if resultado_xp_v and resultado_xp_v["nivel_depois"] > resultado_xp_v["nivel_antes"]:
            embed.add_field(
                name="🎉 LEVEL UP!",
                value=(
                    f"{vencedor.mention} alcançou o nível "
                    f"**{resultado_xp_v['nivel_depois']}**!"
                ),
                inline=False
            )

        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(
            text="⚡ Treine sua equipe, suba de nível e volte para o próximo duelo!"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # PODER DO POKÉMON
    # ========================================================

    def poder_pokemon(self, pokemon):
        raridade_bonus = {
            "comum": 0,
            "incomum": 10,
            "raro": 25,
            "epico": 50,
            "lendario": 100
        }

        return int(
            pokemon["nivel"] * 10
            + pokemon["hp"] * 0.30
            + pokemon["ataque"] * 1.20
            + pokemon["defesa"] * 0.90
            + pokemon["velocidade"] * 0.60
            + raridade_bonus.get(pokemon["raridade"], 0)
        )

    # ========================================================
    # !POKETOP • TOP 100
    # ========================================================

    async def registrar_no_poketop(self, guild_id, usuario_id):
        """Registra manualmente um treinador no PokéTop.

        Requisito obrigatório: exatamente 6 Pokémon marcados como equipe.
        O registro é por servidor e permanece salvo no SQLite.
        """
        gid = int(guild_id)
        uid = int(usuario_id)

        def operacao():
            self.banco.garantir_treinador(uid)
            with self.banco.conectar() as db:
                equipe = db.execute(
                    "SELECT id FROM pokemon WHERE treinador_id = ? AND equipe = 1 ORDER BY id ASC",
                    (uid,)
                ).fetchall()
                quantidade = len(equipe)

                if quantidade != 6:
                    return {
                        "status": "equipe_invalida",
                        "quantidade": quantidade,
                    }

                agora = agora_iso()
                cursor = db.execute(
                    """
                    INSERT OR IGNORE INTO poketop_registros
                    (guild_id, treinador_id, registrado_em)
                    VALUES (?, ?, ?)
                    """,
                    (gid, uid, agora)
                )
                db.commit()

                if cursor.rowcount == 0:
                    return {"status": "ja_registrado", "quantidade": 6}

                return {"status": "registrado", "quantidade": 6}

        return await self.banco.executar(operacao)

    async def remover_do_poketop(self, guild_id, usuario_id):
        """Remove o registro do treinador no servidor, se existir."""
        gid = int(guild_id)
        uid = int(usuario_id)

        def operacao():
            with self.banco.conectar() as db:
                cursor = db.execute(
                    "DELETE FROM poketop_registros WHERE guild_id = ? AND treinador_id = ?",
                    (gid, uid)
                )
                db.commit()
                return cursor.rowcount > 0

        return await self.banco.executar(operacao)

    def calcular_poder_equipe(self, pokemons):
        return int(sum(self.poder_pokemon(p) for p in pokemons))

    async def _calcular_ranking_poketop(self, guild):
        """Calcula o snapshot do Top 100 a partir do SQLite."""
        membros = {int(m.id): m for m in guild.members}
        if not membros:
            return []

        ids = tuple(membros.keys())
        placeholders = ','.join('?' for _ in ids)

        def buscar():
            with self.banco.conectar() as db:
                rows = db.execute(
                    f"""
                    SELECT t.id, t.nivel, t.xp, t.vitorias, t.capturas,
                           p.id AS pokemon_db_id, p.pokemon_id, p.nome,
                           p.nivel AS pokemon_nivel, p.raridade, p.hp,
                           p.ataque, p.defesa, p.velocidade, p.equipe
                    FROM poketop_registros r
                    INNER JOIN treinadores t ON t.id = r.treinador_id
                    INNER JOIN pokemon p
                        ON p.treinador_id = t.id AND p.equipe = 1
                    WHERE r.guild_id = ?
                      AND t.id IN ({placeholders})
                    ORDER BY t.nivel DESC, t.xp DESC, p.id ASC
                    """,
                    (int(guild.id), *ids)
                ).fetchall()
                return [dict(row) for row in rows]

        rows = await self.banco.executar(buscar)
        agrupado = {}
        for row in rows:
            uid = int(row["id"])
            item = agrupado.setdefault(uid, {
                "id": uid,
                "nivel": int(row["nivel"] or 1),
                "xp": int(row["xp"] or 0),
                "vitorias": int(row["vitorias"] or 0),
                "capturas": int(row["capturas"] or 0),
                "equipe": [],
            })
            item["equipe"].append(row)

        ranking = []
        for item in agrupado.values():
            # Regra absoluta do PokéTop: 6 Pokémon na equipe.
            if len(item["equipe"]) != 6:
                continue

            poder = self.calcular_poder_equipe(item["equipe"])
            nivel = item["nivel"]
            media_nivel = sum(
                int(p["pokemon_nivel"] or 1) for p in item["equipe"]
            ) / 6
            score = int(
                (nivel * 500)
                + (poder * 2)
                + (media_nivel * 100)
                + item["vitorias"] * 5
            )
            item.update({
                "poder": poder,
                "score": score,
                "quantidade": 6,
            })
            ranking.append(item)

        ranking.sort(
            key=lambda x: (
                x["score"], x["nivel"], x["poder"],
                x["xp"], x["vitorias"], x["capturas"]
            ),
            reverse=True,
        )

        for posicao, item in enumerate(ranking[:100], start=1):
            item["posicao"] = posicao

        return ranking[:100]

    async def obter_ranking_poketop(self, guild):
        """Retorna o snapshot do PokéTop, atualizado no máximo a cada 2 horas."""
        gid = int(guild.id)
        agora = datetime.now(timezone.utc)
        cache = self.poketop_cache.get(gid)

        if cache:
            idade = (agora - cache["atualizado_em"]).total_seconds()
            if idade < 7200:
                return cache["ranking"]

        ranking = await self._calcular_ranking_poketop(guild)
        self.poketop_cache[gid] = {
            "ranking": ranking,
            "atualizado_em": agora,
        }
        return ranking

    @tasks.loop(hours=2)
    async def poketop_atualizacao(self):
        """Atualiza automaticamente os rankings de servidores já consultados."""
        if not self.poketop_cache:
            return

        agora = datetime.now(timezone.utc)
        for gid in list(self.poketop_cache.keys()):
            guild = self.bot.get_guild(gid)
            if guild is None:
                self.poketop_cache.pop(gid, None)
                continue

            try:
                ranking = await self._calcular_ranking_poketop(guild)
                self.poketop_cache[gid] = {
                    "ranking": ranking,
                    "atualizado_em": agora,
                }
            except Exception as erro:
                print(f"[POKEMON] ❌ Falha atualizando PokéTop {gid}: {erro}")

    @poketop_atualizacao.before_loop
    async def antes_atualizar_poketop(self):
        await self.bot.wait_until_ready()

    def criar_embed_poketop(self, guild, ranking, pagina=0):
        por_pagina = 10
        inicio = pagina * por_pagina
        itens = ranking[inicio:inicio + por_pagina]
        total_paginas = max(1, (len(ranking) + 9) // 10)
        embed = discord.Embed(
            title="🏆 ROYALT • POKÉTOP",
            description=(
                "**Top 100 treinadores com as equipes mais fortes.**\n"
                "O ranking considera **nível do treinador + força da equipe**, "
                "com vitórias e nível médio dos Pokémon como critérios adicionais.\n"
                "🎁 **Os colocados no Top 100 recebem recompensas semanais conforme a posição.**\n\n"
                "🔽 **Selecione um ranking abaixo para abrir a equipe completa.**"
            ), color=COR_AMARELO,
        )
        medalhas = {1: "🥇", 2: "🥈", 3: "🥉"}
        for item in itens:
            posicao = item["posicao"]
            membro = guild.get_member(item["id"])
            mention = membro.mention if membro else f"<@{item['id']}>"
            equipe_texto = " • ".join(f"{str(p['nome']).title()} Nv.{int(p['pokemon_nivel'])}" for p in item["equipe"][:6])
            embed.add_field(
                name=f"{medalhas.get(posicao, f'🏆 #{posicao}')} {mention}",
                value=(
                    f"👤 Treinador **Nv.{item['nivel']}**  •  ⚡ Poder **{item['poder']}**\n"
                    f"👥 Equipe **{item['quantidade']}/6**  •  🏆 **{item['vitorias']}** vitórias\n"
                    f"🐾 {equipe_texto}"
                ), inline=False,
            )
        if not itens:
            embed.description += "\n\n📭 Não existem equipes suficientes nesta página."
        cache = self.poketop_cache.get(int(guild.id))
        atualizado = cache["atualizado_em"] if cache else datetime.now(timezone.utc)
        proxima = atualizado.timestamp() + 7200
        restante = max(0, int(proxima - datetime.now(timezone.utc).timestamp()))
        horas = restante // 3600
        minutos = (restante % 3600) // 60
        embed.set_footer(
            text=(
                f"Página {pagina + 1}/{total_paginas} • {len(ranking)}/100 posições • "
                f"🔄 Atualização em até {horas}h {minutos}min • {POKEMON_AVISO}"
            )
        )
        return embed

    def criar_embed_poketop_equipe(self, guild, item):
        membro = guild.get_member(item["id"])
        nome = membro.display_name if membro else f"Treinador {item['id']}"
        mention = membro.mention if membro else f"<@{item['id']}>"
        embed = discord.Embed(
            title=f"🏆 #{item['posicao']} • EQUIPE POKÉTOP",
            description=(
                f"**{nome}** • {mention}\n⭐ Treinador **Nível {item['nivel']}**\n"
                f"⚡ Poder total da equipe: **{item['poder']}**\n🏆 Vitórias: **{item['vitorias']}**"
            ), color=COR_AMARELO,
        )
        if membro:
            embed.set_thumbnail(url=membro.display_avatar.url)
        for indice, pokemon in enumerate(item["equipe"][:6], start=1):
            embed.add_field(
                name=f"{indice}. {str(pokemon['nome']).title()}",
                value=(f"⭐ Nível **{int(pokemon['pokemon_nivel'])}**\n"
                       f"⚡ Poder **{self.poder_pokemon(pokemon)}**\n"
                       f"💎 {str(pokemon['raridade']).title()}"), inline=True,
            )
        embed.add_field(
            name="📊 Resumo",
            value=(f"🐾 Pokémon na equipe: **{item['quantidade']}/6**\n"
                   f"✨ XP do treinador: **{item['xp']}**\n🎯 Capturas: **{item['capturas']}**"),
            inline=False,
        )
        embed.set_footer(text=POKEMON_AVISO)
        return embed

    @commands.hybrid_command(
        name="poketopregistrar",
        aliases=["registrarpoketop", "registrar_poketop"],
        description="Registra sua equipe de 6 Pokémon no PokéTop do servidor.",
    )
    @commands.guild_only()
    async def poketopregistrar(self, ctx):
        resultado = await self.registrar_no_poketop(ctx.guild.id, ctx.author.id)

        if resultado["status"] == "equipe_invalida":
            quantidade = resultado["quantidade"]
            await ctx.send(
                embed=discord.Embed(
                    title="🏆 POKÉTOP • REGISTRO",
                    description=(
                        "Para entrar no PokéTop você precisa ter **exatamente 6 Pokémon na equipe**.\n\n"
                        f"🐾 Sua equipe atual: **{quantidade}/6**\n\n"
                        "Use `!equipe` para organizar seus Pokémon e tente novamente."
                    ),
                    color=COR_AMARELO,
                )
            )
            return

        if resultado["status"] == "ja_registrado":
            await ctx.send(
                embed=discord.Embed(
                    title="🏆 POKÉTOP • JÁ REGISTRADO",
                    description=(
                        "Você já está registrado no ranking deste servidor.\n\n"
                        "Seu lugar será calculado automaticamente conforme a força da sua equipe."
                    ),
                    color=COR_AMARELO,
                )
            )
            return

        await ctx.send(
            embed=discord.Embed(
                title="🏆 POKÉTOP • REGISTRO CONCLUÍDO",
                description=(
                    "Sua equipe foi registrada com sucesso no PokéTop!\n\n"
                    "🐾 Equipe registrada: **6/6**\n"
                    "📊 Seu ranking será calculado pela força da equipe e pelo nível do treinador.\n\n"
                    "Boa sorte na disputa pelo Top 100! 🏆"
                ),
                color=COR_AMARELO,
            )
        )

    @commands.hybrid_command(name="poketop", aliases=["pokemonrank", "rankpokemon"], description="Mostra o Top 100 das equipes Pokémon do servidor.")
    @commands.guild_only()
    async def poketop(self, ctx):
        ranking = await self.obter_ranking_poketop(ctx.guild)
        if not ranking:
            await ctx.send("📭 Ainda não existem treinadores registrados no PokéTop com uma equipe completa de 6 Pokémon. Use `!poketopregistrar` para se registrar.")
            return
        await ctx.send(
            embed=self.criar_embed_poketop(ctx.guild, ranking, 0),
            view=PoketopView(self, ctx.author.id, ranking, 0),
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Pokemon(
            bot
        )
    )