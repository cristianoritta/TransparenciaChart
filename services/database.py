import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "transparencia.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL,
                cpf_mascarado TEXT,
                nome TEXT,
                total_servicos INTEGER DEFAULT 0,
                total_positivos INTEGER DEFAULT 0,
                total_registros INTEGER DEFAULT 0,
                categorias INTEGER DEFAULT 0,
                resultados_json TEXT NOT NULL,
                criado_em TEXT NOT NULL
            );
        """)
        _migrar_env(conn)


def _migrar_env(conn):
    row = conn.execute(
        "SELECT valor FROM configuracoes WHERE chave = 'api_key'"
    ).fetchone()
    if row:
        return

    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GOV_VALUE", "")
    if api_key:
        agora = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO configuracoes (chave, valor, atualizado_em) VALUES (?, ?, ?)",
            ("api_key", api_key, agora),
        )
        header = os.getenv("GOV_KEY", "chave-api-dados")
        conn.execute(
            "INSERT INTO configuracoes (chave, valor, atualizado_em) VALUES (?, ?, ?)",
            ("api_header", header, agora),
        )


def get_config(chave: str, default: str = "") -> str:
    with _connect() as conn:
        row = conn.execute(
            "SELECT valor FROM configuracoes WHERE chave = ?",
            (chave,),
        ).fetchone()
        return row["valor"] if row else default


def set_config(chave: str, valor: str):
    agora = datetime.now().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO configuracoes (chave, valor, atualizado_em)
            VALUES (?, ?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor, atualizado_em = excluded.atualizado_em
            """,
            (chave, valor, agora),
        )


def get_api_credentials() -> tuple[str, str]:
    return get_config("api_header", "chave-api-dados"), get_config("api_key", "")


def get_api_key_masked() -> str:
    key = get_config("api_key", "")
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"


def salvar_consulta(resultado: dict) -> int:
    categorias = len({r["categoria"] for r in resultado.get("resultados", [])})
    total_registros = sum(r.get("total", 0) for r in resultado.get("resultados", []))
    agora = datetime.now().isoformat()

    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO consultas (
                cpf, cpf_mascarado, nome, total_servicos, total_positivos,
                total_registros, categorias, resultados_json, criado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resultado.get("cpf", ""),
                resultado.get("cpf_mascarado", ""),
                resultado.get("nome", ""),
                resultado.get("total_servicos", 0),
                resultado.get("total_positivos", 0),
                total_registros,
                categorias,
                json.dumps(resultado, ensure_ascii=False),
                agora,
            ),
        )
        return cursor.lastrowid


def listar_consultas(limite: int = 50) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, cpf_mascarado, nome, total_positivos, total_registros,
                   categorias, criado_em
            FROM consultas
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()
        return [dict(row) for row in rows]


def obter_consulta(consulta_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM consultas WHERE id = ?",
            (consulta_id,),
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["resultado"] = json.loads(data.pop("resultados_json"))
        return data
