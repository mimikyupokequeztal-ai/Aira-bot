from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_DATA = BASE_DIR / "data"
PASTA_DATA.mkdir(parents=True, exist_ok=True)
DB_PATH = PASTA_DATA / "aira_permissions.sqlite3"

try:
    AIRA_OWNER_ID = int(os.getenv("AIRA_OWNER_ID", "0"))
except ValueError:
    AIRA_OWNER_ID = 0

SISTEMAS = {
    "updates": {"nome": "Updates", "emoji": "🛠️", "descricao": "Gerenciamento das atualizações da Aira."},
    "updates_logger": {"nome": "Updates Logger", "emoji": "📋", "descricao": "Gerenciamento do registro de atualizações."},
    "sorteios": {"nome": "Sorteios", "emoji": "🎉", "descricao": "Gerenciamento dos sorteios."},
    "tickets": {"nome": "Tickets", "emoji": "🎫", "descricao": "Gerenciamento do sistema de tickets."},
    "desabafos": {"nome": "Desabafos", "emoji": "💭", "descricao": "Gerenciamento do sistema de desabafos."},
    "desabafos_config": {"nome": "Desabafos Config", "emoji": "⚙️", "descricao": "Configuração do sistema de desabafos."},
    "desabafos_pesquisa": {"nome": "Desabafos Pesquisa", "emoji": "🔎", "descricao": "Pesquisa e consulta dos desabafos."},
    "moderation": {"nome": "Moderation", "emoji": "🛡️", "descricao": "Gerenciamento das funções de moderação."},
}

TIPO_USUARIO = "user"
TIPO_CARGO = "role"

def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class PermissionsManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db: Optional[sqlite3.Connection] = None
        self.inicializar()

    def conectar(self) -> sqlite3.Connection:
        if self.db is None:
            self.db = sqlite3.connect(self.db_path, timeout=15, check_same_thread=False)
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA foreign_keys=ON")
        return self.db

    def inicializar(self):
        db = self.conectar()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                system TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (guild_id, system, target_type, target_id),
                FOREIGN KEY (guild_id) REFERENCES guilds(guild_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_permissions_guild
            ON permissions(guild_id);

            CREATE INDEX IF NOT EXISTS idx_permissions_system
            ON permissions(guild_id, system);

            CREATE INDEX IF NOT EXISTS idx_permissions_target
            ON permissions(guild_id, target_type, target_id);
        """)

        # Migração importante para bancos antigos:
        # corrige linhas que foram criadas com created_at/updated_at nulos.
        agora = agora_iso()
        db.execute(
            "UPDATE guilds SET created_at = COALESCE(created_at, ?), "
            "updated_at = COALESCE(updated_at, ?)",
            (agora, agora),
        )
        db.commit()

    def fechar(self):
        if self.db is not None:
            try:
                self.db.close()
            except sqlite3.Error:
                pass
            finally:
                self.db = None

    def sistema_existe(self, sistema: str) -> bool:
        return str(sistema).strip().lower() in SISTEMAS

    def nome_sistema(self, sistema: str) -> str:
        dados = SISTEMAS.get(str(sistema).strip().lower())
        return dados["nome"] if dados else sistema

    def emoji_sistema(self, sistema: str) -> str:
        dados = SISTEMAS.get(str(sistema).strip().lower())
        return dados["emoji"] if dados else "⚙️"

    def registrar_guild(self, guild_id: int, owner_id: int):
        guild_id = int(guild_id)
        owner_id = int(owner_id)
        agora = agora_iso()
        db = self.conectar()
        db.execute(
            """
            INSERT INTO guilds (guild_id, owner_id, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                owner_id = excluded.owner_id,
                updated_at = excluded.updated_at
            """,
            (guild_id, owner_id, agora, agora),
        )
        db.commit()

    def garantir_guild(self, guild_id: int, owner_id: int):
        guild_id = int(guild_id)
        owner_id = int(owner_id)
        db = self.conectar()
        agora = agora_iso()
        registro = db.execute(
            "SELECT guild_id, created_at, updated_at FROM guilds WHERE guild_id = ?",
            (guild_id,),
        ).fetchone()

        if registro is None:
            self.registrar_guild(guild_id, owner_id)
            return

        # Corrige NULLs existentes antes do UPDATE.
        created_at = registro["created_at"] or agora
        db.execute(
            """
            UPDATE guilds
            SET owner_id = ?, created_at = ?, updated_at = ?
            WHERE guild_id = ?
            """,
            (owner_id, created_at, agora, guild_id),
        )
        db.commit()

    def adicionar_permissao(
        self,
        guild_id: int,
        sistema: str,
        target_type: str,
        target_id: int,
        owner_id: Optional[int] = None,
    ) -> bool:
        guild_id = int(guild_id)
        target_id = int(target_id)
        sistema = str(sistema).strip().lower()
        target_type = str(target_type).strip().lower()

        if not self.sistema_existe(sistema):
            raise ValueError(f"Sistema inválido: {sistema}")
        if target_type not in {TIPO_USUARIO, TIPO_CARGO}:
            raise ValueError(f"Tipo de alvo inválido: {target_type}")

        if owner_id is None:
            registro = self.obter_guild(guild_id)
            if registro is None:
                raise ValueError("Servidor não registrado.")
            owner_id = int(registro["owner_id"])
        else:
            self.garantir_guild(guild_id, int(owner_id))

        db = self.conectar()
        try:
            cursor = db.execute(
                """
                INSERT OR IGNORE INTO permissions
                    (guild_id, system, target_type, target_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (guild_id, sistema, target_type, target_id, agora_iso()),
            )
            db.commit()
            return cursor.rowcount > 0
        except sqlite3.Error:
            db.rollback()
            raise

    def remover_permissao(self, guild_id: int, sistema: str, target_type: str, target_id: int) -> bool:
        db = self.conectar()
        cursor = db.execute(
            """
            DELETE FROM permissions
            WHERE guild_id = ? AND system = ? AND target_type = ? AND target_id = ?
            """,
            (int(guild_id), str(sistema).strip().lower(), str(target_type).strip().lower(), int(target_id)),
        )
        db.commit()
        return cursor.rowcount > 0

    def limpar_sistema(self, guild_id: int, sistema: str) -> int:
        sistema = str(sistema).strip().lower()
        if not self.sistema_existe(sistema):
            raise ValueError(f"Sistema inválido: {sistema}")
        db = self.conectar()
        cursor = db.execute(
            "DELETE FROM permissions WHERE guild_id = ? AND system = ?",
            (int(guild_id), sistema),
        )
        db.commit()
        return cursor.rowcount

    def limpar_guild(self, guild_id: int):
        db = self.conectar()
        db.execute("DELETE FROM permissions WHERE guild_id = ?", (int(guild_id),))
        db.commit()

    def obter_guild(self, guild_id: int):
        db = self.conectar()
        return db.execute(
            """
            SELECT guild_id, owner_id, created_at, updated_at
            FROM guilds WHERE guild_id = ?
            """,
            (int(guild_id),),
        ).fetchone()

    def obter_permissoes(self, guild_id: int, sistema: str) -> list[sqlite3.Row]:
        sistema = str(sistema).strip().lower()
        if not self.sistema_existe(sistema):
            raise ValueError(f"Sistema inválido: {sistema}")
        db = self.conectar()
        return list(
            db.execute(
                """
                SELECT id, guild_id, system, target_type, target_id, created_at
                FROM permissions
                WHERE guild_id = ? AND system = ?
                ORDER BY target_type ASC, target_id ASC
                """,
                (int(guild_id), sistema),
            ).fetchall()
        )

    def contar_permissoes(self, guild_id: int, sistema: str) -> dict:
        db = self.conectar()
        rows = db.execute(
            """
            SELECT target_type, COUNT(*) AS quantidade
            FROM permissions
            WHERE guild_id = ? AND system = ?
            GROUP BY target_type
            """,
            (int(guild_id), str(sistema).strip().lower()),
        ).fetchall()
        usuarios = sum(int(r["quantidade"]) for r in rows if r["target_type"] == TIPO_USUARIO)
        cargos = sum(int(r["quantidade"]) for r in rows if r["target_type"] == TIPO_CARGO)
        return {"usuarios": usuarios, "cargos": cargos, "total": usuarios + cargos}

    def verificar_id(self, guild_id: int, sistema: str, user_id: int, role_ids: Optional[list[int]] = None) -> bool:
        sistema = str(sistema).strip().lower()
        if not self.sistema_existe(sistema):
            return False

        db = self.conectar()
        row = db.execute(
            """
            SELECT 1 FROM permissions
            WHERE guild_id = ? AND system = ? AND target_type = ? AND target_id = ?
            LIMIT 1
            """,
            (int(guild_id), sistema, TIPO_USUARIO, int(user_id)),
        ).fetchone()
        if row:
            return True

        role_ids = [int(x) for x in (role_ids or [])]
        if not role_ids:
            return False

        placeholders = ",".join("?" for _ in role_ids)
        row = db.execute(
            f"""
            SELECT 1 FROM permissions
            WHERE guild_id = ? AND system = ? AND target_type = ?
            AND target_id IN ({placeholders})
            LIMIT 1
            """,
            [int(guild_id), sistema, TIPO_CARGO, *role_ids],
        ).fetchone()
        return row is not None

    def verificar(
        self,
        guild_id: int,
        sistema: str,
        user_id: int,
        role_ids: Optional[list[int]] = None,
        owner_id: Optional[int] = None,
    ) -> bool:
        if owner_id is not None and int(user_id) == int(owner_id):
            return True

        registro = self.obter_guild(guild_id)
        if owner_id is None and registro is not None and int(user_id) == int(registro["owner_id"]):
            return True

        return self.verificar_id(guild_id, sistema, user_id, role_ids)

    async def tem_permissao(self, interaction, sistema: str) -> bool:
        guild = getattr(interaction, "guild", None)
        user = getattr(interaction, "user", None)
        if guild is None or user is None:
            return False
        if user.id == guild.owner_id:
            return True
        if AIRA_OWNER_ID > 0 and user.id == AIRA_OWNER_ID:
            return True

        role_ids = [int(role.id) for role in getattr(user, "roles", [])]
        self.garantir_guild(guild.id, guild.owner_id)
        return self.verificar(guild.id, sistema, user.id, role_ids, guild.owner_id)

    async def pode_abrir_painel(self, interaction) -> bool:
        guild = getattr(interaction, "guild", None)
        user = getattr(interaction, "user", None)
        if guild is None or user is None:
            return False
        return user.id == guild.owner_id or (AIRA_OWNER_ID > 0 and user.id == AIRA_OWNER_ID)


permissions = PermissionsManager()

async def tem_permissao(interaction, sistema: str) -> bool:
    return await permissions.tem_permissao(interaction, sistema)

async def pode_abrir_painel(interaction) -> bool:
    return await permissions.pode_abrir_painel(interaction)
