import os
import sqlite3
import random
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = os.getenv("PICKONE_DB_PATH", "pickone.db")
JWT_SECRET = os.getenv("PICKONE_JWT_SECRET", "dev-secret-change-me")
JWT_TTL_HOURS = int(os.getenv("PICKONE_JWT_TTL_HOURS", "24"))
POLL_COOLDOWN_DAYS = int(os.getenv("PICKONE_POLL_COOLDOWN_DAYS", "3"))

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            auth_provider TEXT NOT NULL DEFAULT 'email',
            is_verified INTEGER NOT NULL DEFAULT 0,
            verification_code TEXT,
            code_expires_at TEXT,
            created_at TEXT NOT NULL,
            last_poll_created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            choice TEXT NOT NULL CHECK(choice IN ('A','B')),
            created_at TEXT NOT NULL,
            UNIQUE(poll_id, user_id),
            FOREIGN KEY (poll_id) REFERENCES polls(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS poll_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (poll_id) REFERENCES polls(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()
    db.close()


def make_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_TTL_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing bearer token"}), 401
        token = auth.replace("Bearer ", "", 1)
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "invalid token"}), 401

        user_id = int(payload["sub"])
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return jsonify({"error": "user not found"}), 401
        g.current_user = row
        return fn(*args, **kwargs)

    return wrapper


@app.get("/health")
def health():
    return {"ok": True, "time": now_iso()}


@app.post("/auth/register/request-code")
def request_code():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()

    if not email or "@" not in email:
        return jsonify({"error": "email inválido"}), 400

    code = f"{random.randint(0, 999999):06d}"
    expires = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    db = get_db()

    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        db.execute(
            "UPDATE users SET verification_code = ?, code_expires_at = ? WHERE email = ?",
            (code, expires, email),
        )
    else:
        db.execute(
            """
            INSERT INTO users (email, auth_provider, is_verified, verification_code, code_expires_at, created_at)
            VALUES (?, 'email', 0, ?, ?, ?)
            """,
            (email, code, expires, now_iso()),
        )
    db.commit()

    return {
        "message": "Código generado. En producción se enviaría por email.",
        "dev_code": code,
        "expires_at": expires,
    }


@app.post("/auth/register/verify")
def verify_code_and_set_password():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()
    password = data.get("password") or ""

    if len(password) < 8:
        return jsonify({"error": "la contraseña debe tener al menos 8 caracteres"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"error": "usuario no encontrado"}), 404

    if user["verification_code"] != code:
        return jsonify({"error": "código incorrecto"}), 400

    exp = parse_iso(user["code_expires_at"])
    if not exp or datetime.now(timezone.utc) > exp:
        return jsonify({"error": "código expirado"}), 400

    db.execute(
        """
        UPDATE users
        SET is_verified = 1,
            password_hash = ?,
            verification_code = NULL,
            code_expires_at = NULL
        WHERE id = ?
        """,
        (generate_password_hash(password), user["id"]),
    )
    db.commit()

    token = make_token(user["id"], email)
    return {"message": "Cuenta verificada", "token": token}


@app.post("/auth/login")
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        return jsonify({"error": "credenciales inválidas"}), 401

    if not user["is_verified"]:
        return jsonify({"error": "cuenta no verificada"}), 403

    if not user["password_hash"] or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "credenciales inválidas"}), 401

    return {"token": make_token(user["id"], user["email"])}


@app.post("/polls")
@auth_required
def create_poll():
    data = request.get_json(force=True)
    q = (data.get("question") or "").strip()
    a = (data.get("option_a") or "").strip()
    b = (data.get("option_b") or "").strip()

    if not q or not a or not b:
        return jsonify({"error": "question, option_a y option_b son obligatorios"}), 400

    if len(q) > 120:
        return jsonify({"error": "question excede 120 caracteres"}), 400

    last = parse_iso(g.current_user["last_poll_created_at"])
    if last:
        next_allowed = last + timedelta(days=POLL_COOLDOWN_DAYS)
        if datetime.now(timezone.utc) < next_allowed:
            return jsonify({"error": "cooldown activo", "next_allowed_at": next_allowed.isoformat()}), 429

    db = get_db()
    created_at = now_iso()
    db.execute(
        "INSERT INTO polls (author_id, question, option_a, option_b, created_at) VALUES (?, ?, ?, ?, ?)",
        (g.current_user["id"], q, a, b, created_at),
    )
    db.execute(
        "UPDATE users SET last_poll_created_at = ? WHERE id = ?",
        (created_at, g.current_user["id"]),
    )
    db.commit()

    poll_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    return {"id": poll_id, "created_at": created_at}, 201


@app.get("/polls/feed")
def feed():
    limit = min(int(request.args.get("limit", 10)), 50)
    cursor = request.args.get("cursor")
    db = get_db()

    if cursor:
        rows = db.execute(
            """
            SELECT id, question, option_a, option_b, created_at
            FROM polls
            WHERE status = 'active' AND id < ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (cursor, limit),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT id, question, option_a, option_b, created_at
            FROM polls
            WHERE status = 'active'
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    items = [dict(r) for r in rows]
    next_cursor = str(items[-1]["id"]) if items else None
    return {"items": items, "next_cursor": next_cursor}


@app.post("/polls/<int:poll_id>/vote")
@auth_required
def vote(poll_id: int):
    data = request.get_json(force=True)
    choice = (data.get("choice") or "").upper()
    if choice not in {"A", "B"}:
        return jsonify({"error": "choice debe ser A o B"}), 400

    db = get_db()
    exists = db.execute("SELECT id FROM polls WHERE id = ? AND status='active'", (poll_id,)).fetchone()
    if not exists:
        return jsonify({"error": "encuesta no encontrada"}), 404

    try:
        db.execute(
            "INSERT INTO votes (poll_id, user_id, choice, created_at) VALUES (?, ?, ?, ?)",
            (poll_id, g.current_user["id"], choice, now_iso()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "ya votaste en esta encuesta"}), 409

    return poll_results(poll_id)


@app.get("/polls/<int:poll_id>/results")
def poll_results(poll_id: int):
    db = get_db()
    r = db.execute(
        """
        SELECT
            SUM(CASE WHEN choice='A' THEN 1 ELSE 0 END) AS votes_a,
            SUM(CASE WHEN choice='B' THEN 1 ELSE 0 END) AS votes_b,
            COUNT(*) AS total
        FROM votes
        WHERE poll_id = ?
        """,
        (poll_id,),
    ).fetchone()

    votes_a = r["votes_a"] or 0
    votes_b = r["votes_b"] or 0
    total = r["total"] or 0

    pct_a = round((votes_a / total) * 100, 2) if total else 0
    pct_b = round((votes_b / total) * 100, 2) if total else 0

    return {
        "poll_id": poll_id,
        "votes_a": votes_a,
        "votes_b": votes_b,
        "total": total,
        "pct_a": pct_a,
        "pct_b": pct_b,
    }


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
